#!/usr/bin/python3
"""Bible League daily verse for a Turing Revision A 3.5-inch USB LCD.
Protocol reference: https://github.com/mathoudebine/turing-smart-screen-python
Dependencies: Pillow, pyserial (provided by this machine's Python).
"""
import argparse
import os
import sys
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
from PIL import Image, ImageDraw, ImageFont, ImageColor
from serial.tools import list_ports
from filelock import FileLock, Timeout

ROOT = Path(__file__).resolve().parent
URL = 'https://www.bibleleague.org/verse-of-the-day/'
WIDTH, HEIGHT = 480, 320


def default_data_dir():
    if sys.platform == 'win32':
        return Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData/Local')) / 'bibleSmartDisplay'
    if sys.platform == 'darwin':
        return Path.home() / 'Library/Application Support/bibleSmartDisplay'
    return Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'bibleSmartDisplay'


def default_font():
    candidates = [
        Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts/arial.ttf',
        Path('/System/Library/Fonts/Supplemental/Arial.ttf'),
        Path('/Library/Fonts/Arial.ttf'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        Path('/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf'),
    ]
    for font in candidates:
        if font.is_file():
            return str(font)
    raise ValueError('No default font found. Supply --font with a TrueType font file.')


def choose_port():
    # Restrict automatic selection to the known 3.5-inch Revision A identifiers.
    ports = [p.device for p in list_ports.comports()
             if p.serial_number in ('USB35INCHIPS', 'USB35INCHIPSV2')]
    if len(ports) != 1:
        raise ValueError('Could not identify one compatible display. Use --list-ports, then --port.')
    return ports[0]


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

def render(data, font_path=None, color='#ADD8E6'):
    font_path = font_path or default_font()
    image = Image.new('RGB', (WIDTH, HEIGHT), 'black')
    draw = ImageDraw.Draw(image)
    for size in range(30, 9, -1):
        font = ImageFont.truetype(font_path, size)
        ref_font = ImageFont.truetype(font_path, max(14, size - 3))
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
        draw.text((WIDTH // 2, y), line, fill=color, font=font, anchor='mt')
        y += step
    y += 18
    for line in refs:
        draw.text((WIDTH // 2, y), line, fill=color, font=ref_font, anchor='mt')
        y += ref_step
    return image

def command(code, x=0, y=0, ex=0, ey=0):
    return bytes((x >> 2, ((x & 3) << 6) | (y >> 4),
                  ((y & 15) << 4) | (ex >> 6),
                  ((ex & 63) << 2) | (ey >> 8), ey & 255, code))

def display(image, device, brightness=50):
    options = {'exclusive': True} if os.name == 'posix' else {}
    with serial.Serial(device, 115200, timeout=2, write_timeout=15, **options) as port:
        port.reset_input_buffer()
        port.write(bytes([69]) * 6)
        reply = port.read(6)
        if reply != bytes([1]) * 6:
            raise RuntimeError(f'Unexpected screen handshake: {reply.hex()}')
        port.write(command(109))
        port.write(command(110, x=round(255 * (100 - brightness) / 100)))
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
    parser = argparse.ArgumentParser(description='Daily CSB verse for a 3.5-inch Revision A USB smart display.')
    parser.add_argument('--preview-only', action='store_true')
    parser.add_argument('--cached', action='store_true', help='Restore saved verse without a network request')
    parser.add_argument('--demo', action='store_true', help='Render a built-in test message without internet')
    parser.add_argument('--list-ports', action='store_true', help='List serial ports and exit')
    parser.add_argument('--port', help='Serial device, e.g. COM3 or /dev/ttyACM0; defaults to detection')
    parser.add_argument('--font', help='Path to a TrueType font')
    parser.add_argument('--color', default='#ADD8E6', help='Text colour, default: #ADD8E6')
    parser.add_argument('--brightness', type=int, default=50, choices=range(101), metavar='0-100')
    parser.add_argument('--data-dir', type=Path, default=default_data_dir(), help='Cache, preview and log directory')
    args = parser.parse_args()
    if args.list_ports:
        for port in list_ports.comports():
            print(f'{port.device}: {port.description} [{port.hwid}]')
        return
    color = ImageColor.getrgb(args.color)
    font = args.font or default_font()
    device = None if args.preview_only else (args.port or choose_port())
    root = args.data_dir.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(root / 'verse.log', maxBytes=200_000, backupCount=2, encoding='utf-8')
    logging.basicConfig(level=logging.INFO, handlers=[handler, logging.StreamHandler()],
                        format='%(asctime)s %(levelname)s %(message)s')
    lock = FileLock(str(root / '.lock'))
    try:
        lock.acquire(timeout=0)
    except Timeout:
        logging.info('Another instance is running; skipping this update')
        return
    try:
        cache = root / 'last-verse.json'
        if args.demo:
            data = {'verse': 'Your Bible smart display is ready.', 'reference': 'Display test'}
        elif args.cached:
            data = json.loads(cache.read_text(encoding='utf-8'))
        else:
            try:
                data = fetch()
                temp = cache.with_suffix('.tmp')
                temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                temp.replace(cache)
            except Exception:
                logging.exception('Fetch failed; using last saved verse')
                if not cache.exists():
                    raise
                data = json.loads(cache.read_text(encoding='utf-8'))
        image = render(data, font, color)
        image.save(root / 'preview.png')
        if not args.preview_only:
            display(image, device, args.brightness)
        logging.info('Rendered %s; data directory: %s', data['reference'], root)
    finally:
        lock.release()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        logging.exception('Daily verse update failed')
        raise SystemExit(1)
