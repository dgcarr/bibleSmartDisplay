import os
from pathlib import Path
import subprocess
import sys
import tempfile

exe = Path('dist/BibleSmartDisplay/BibleSmartDisplay' + ('.exe' if sys.platform == 'win32' else '')).resolve()
if sys.platform == 'darwin':
    exe = Path('dist/BibleSmartDisplay.app/Contents/MacOS/BibleSmartDisplay').resolve()
with tempfile.TemporaryDirectory(prefix='Bible smoke space ') as temp:
    for mode in ('--help', '--preview', '--scheduled', '--smoke-test'):
        subprocess.run([str(exe), mode, '--data-dir', temp], check=True, timeout=90)
    if not (Path(temp) / 'preview.png').exists():
        raise RuntimeError('Packaged preview missing')
