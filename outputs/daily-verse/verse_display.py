#!/usr/bin/python3
"""Bible League daily verse for a Turing Revision A 3.5-inch USB LCD.
Protocol reference: https://github.com/mathoudebine/turing-smart-screen-python
Dependencies: Pillow, pyserial (provided by this machine's Python).
"""
import argparse
import fcntl
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import re
import struct
import time
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urlencode

import serial
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
URL = 'https://www.bibleleague.org/verse-of-the-day/'
PORT = '/dev/serial/by-id/usb-2017-2-25_UsbMonitor_USB35INCHIPSV2-if00'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
WIDTH, HEIGHT = 480, 320

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def parse_page(html):
    # Limit parsing to the site's explicitly labelled verse, excluding devotion.
    match = re.search(r"Today's Verse</span></h1>(.*?)<h1[^>]*>\s*<span[^>]*>Devotion", html, re.S)
    if not match:
        raise ValueError('Verse section missing: website layout may have changed')
    section = match.group(1)
    verse_html = re.search(r'<p[^>]*>(.*?)</p>', section, re.S)
    if not verse_html:
        raise ValueError('Verse paragraph missing')
    def clean(fragment):
        parser = TextParser()
        parser.feed(fragment)
        return ' '.join(''.join(parser.parts).split())
    verse = clean(verse_html.group(1))
    reference = clean(section[verse_html.end():])
    if not 10 < len(verse) < 4000 or not re.search(r'\d+:\d+', reference) or len(reference) > 120:
        raise ValueError('Unexpected verse or reference')
    return {'verse': verse, 'reference': reference}

class CSBParser(HTMLParser):
    """Read verse spans only; omit verse numbers, footnotes and cross-references."""
    def __init__(self):
        super().__init__()
        self.version_depth = 0
        self.span_depth = 0
        self.sup_depth = 0
        self.parts = []
        self.verse_ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'div':
            if self.version_depth:
                self.version_depth += 1
            elif 'version-CSB' in attrs.get('class', '').split():
                self.version_depth = 1
        if tag == 'span':
            if self.span_depth:
                self.span_depth += 1
            elif self.version_depth and 'text' in attrs.get('class', '').split():
                self.span_depth = 1
                if attrs.get('id', '').startswith('en-CSB-'):
                    self.verse_ids.add(attrs['id'])
        if tag == 'sup' and self.span_depth:
            self.sup_depth += 1
        if tag == 'br' and self.span_depth and not self.sup_depth:
            self.parts.append(' ')

    def handle_endtag(self, tag):
        if tag == 'div' and self.version_depth:
            self.version_depth -= 1
        if tag == 'sup' and self.sup_depth:
            self.sup_depth -= 1
        if tag == 'span' and self.span_depth:
            self.span_depth -= 1
            if not self.span_depth:
                self.parts.append(' ')

    def handle_data(self, data):
        if self.span_depth and not self.sup_depth:
            self.parts.append(data)


def download(url):
    request = Request(url, headers={'User-Agent': 'DailyVerseLCD/1.0', 'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=30) as response:
        return response.read(2_000_000).decode('utf-8')


def fetch():
    selection = parse_page(download(URL))
    # Remove the source translation suffix, keeping the book/chapter/verse range.
    reference = re.sub(r'\s+[A-Z][A-Z0-9]{1,9}\s*$', '', selection['reference']).strip()
    if reference == selection['reference']:
        raise ValueError('Unrecognised translation suffix in source reference')
    csb_url = 'https://www.biblegateway.com/passage/?' + urlencode({'search': reference, 'version': 'CSB'})
    parser = CSBParser()
    parser.feed(download(csb_url))
    verse = ' '.join(''.join(parser.parts).split())
    if not parser.verse_ids or not 10 < len(verse) < 4000:
        raise ValueError('CSB passage missing or unexpected; keeping previous verse')
    return {'verse': verse, 'reference': reference + ' CSB',
            'translation': 'CSB', 'source': csb_url,
            'copyright': 'Christian Standard Bible. Copyright © 2017 by Holman Bible Publishers.'}


def wrap(text, font, draw, width):
    lines = []
    line = ''
    for word in text.split():
        candidate = f'{line} {word}'.strip()
        if draw.textlength(candidate, font=font) <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
            if draw.textlength(word, font=font) > width:
                raise ValueError('Word too wide')
    if line:
        lines.append(line)
    return lines

def render(data):
    image = Image.new('RGB', (WIDTH, HEIGHT), 'black')
    draw = ImageDraw.Draw(image)
    for size in range(30, 9, -1):
        font = ImageFont.truetype(FONT, size)
        ref_font = ImageFont.truetype(FONT, max(14, size - 3))
        try:
            lines = wrap(data['verse'], font, draw, WIDTH - 40)
            refs = wrap(data['reference'], ref_font, draw, WIDTH - 40)
        except ValueError:
            continue
        step = size + 6
        ref_step = ref_font.size + 5
        total = len(lines) * step + 18 + len(refs) * ref_step
        if total <= HEIGHT - 40:
            break
    else:
        raise ValueError('Verse cannot fit on screen without clipping')
    y = (HEIGHT - total) // 2
    for line in lines:
        draw.text((WIDTH // 2, y), line, fill='#ADD8E6', font=font, anchor='mt')
        y += step
    y += 18
    for line in refs:
        draw.text((WIDTH // 2, y), line, fill='#ADD8E6', font=ref_font, anchor='mt')
        y += ref_step
    return image

def command(code, x=0, y=0, ex=0, ey=0):
    return bytes((x >> 2, ((x & 3) << 6) | (y >> 4),
                  ((y & 15) << 4) | (ex >> 6),
                  ((ex & 63) << 2) | (ey >> 8), ey & 255, code))

def display(image):
    with serial.Serial(PORT, 115200, timeout=2, write_timeout=15, exclusive=True) as port:
        port.reset_input_buffer()
        port.write(bytes([69]) * 6)
        reply = port.read(6)
        if reply != bytes([1]) * 6:
            raise RuntimeError(f'Unexpected screen handshake: {reply.hex()}')
        port.write(command(109))
        port.write(command(110, x=128))  # 50% brightness
        # Revision A: 100 portrait, 101 reverse portrait, 102 landscape.
        port.write(command(121) + bytes([102]) + struct.pack('>HH', WIDTH, HEIGHT) + bytes(5))
        time.sleep(0.1)
        pixels = bytearray()
        for r, g, b in zip(*[iter(image.tobytes())] * 3):
            pixels.extend(struct.pack('<H', ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)))
        port.write(command(197, ex=WIDTH - 1, ey=HEIGHT - 1))
        for offset in range(0, len(pixels), WIDTH * 8):
            port.write(pixels[offset:offset + WIDTH * 8])
        port.flush()
        logging.info('Screen handshake confirmed; sent %d image bytes', len(pixels))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview-only', action='store_true')
    parser.add_argument('--cached', action='store_true', help='Restore saved verse without a network request')
    args = parser.parse_args()
    handler = RotatingFileHandler(ROOT / 'verse.log', maxBytes=200_000, backupCount=2)
    logging.basicConfig(level=logging.INFO, handlers=[handler, logging.StreamHandler()],
                        format='%(asctime)s %(levelname)s %(message)s')
    with (ROOT / '.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        cache = ROOT / 'last-verse.json'
        if args.cached:
            data = json.loads(cache.read_text())
        else:
            try:
                data = fetch()
                temp = cache.with_suffix('.tmp')
                temp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
                temp.replace(cache)
            except Exception:
                logging.exception('Fetch failed; using last saved verse')
                if not cache.exists():
                    raise
                data = json.loads(cache.read_text())
        image = render(data)
        image.save(ROOT / 'preview.png')
        if not args.preview_only:
            display(image)
        logging.info('Rendered %s', data['reference'])

if __name__ == '__main__':
    try:
        main()
    except Exception:
        logging.exception('Daily verse update failed; will retry at next scheduled run')
        raise SystemExit(1)
