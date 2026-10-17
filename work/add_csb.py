from pathlib import Path
p=Path('outputs/daily-verse/verse_display.py')
s=p.read_text().replace('from urllib.request import Request, urlopen','from urllib.request import Request, urlopen\nfrom urllib.parse import urlencode')
a=s.index('def fetch():')
b=s.index('\ndef wrap(',a)
s=s[:a]+'''class CSBParser(HTMLParser):
    """Read verse spans only; omit verse numbers, footnotes and cross-references."""
    def __init__(self):
        super().__init__()
        self.span_depth = 0
        self.sup_depth = 0
        self.parts = []
        self.verse_ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'span':
            if self.span_depth:
                self.span_depth += 1
            elif ('text' in attrs.get('class', '').split()
                  and attrs.get('id', '').startswith('en-CSB-')):
                self.span_depth = 1
                self.verse_ids.add(attrs['id'])
        if tag == 'sup' and self.span_depth:
            self.sup_depth += 1
        if tag == 'br' and self.span_depth and not self.sup_depth:
            self.parts.append(' ')

    def handle_endtag(self, tag):
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
    reference = re.sub(r'\\s+[A-Z][A-Z0-9]{1,9}\\s*$', '', selection['reference']).strip()
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

''' + s[b:]
p.write_text(s)
