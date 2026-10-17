"""Build on the target OS; Python and Qt are included in the output."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir',
        '--name', 'BibleSmartDisplay', '--paths', 'outputs/daily-verse',
        '--hidden-import', 'smartscreen_driver', '--collect-submodules', 'smartscreen_driver',
        '--hidden-import', 'PIL.ImageFont', '--hidden-import', 'PIL.ImageDraw']
if sys.platform in ('win32', 'darwin'):
    args += ['--windowed']
if sys.platform == 'darwin':
    args += ['--osx-bundle-identifier', 'org.biblesmartdisplay.desktop']
subprocess.run(args + ['desktop_app.py'], check=True)
subprocess.run([sys.executable, 'scripts/collect_licenses.py'], check=True)
folder = Path('dist/BibleSmartDisplay.app/Contents/Resources') if sys.platform == 'darwin' else Path('dist/BibleSmartDisplay')
shutil.copytree('dist/licenses', folder / 'licenses', dirs_exist_ok=True)
for path in [*Path('.').glob('README*.md'), Path('LICENSE'), Path('COPYING')]:
    shutil.copy2(path, folder / path.name)
shutil.copytree('docs', folder / 'docs', dirs_exist_ok=True)
if sys.platform.startswith('linux'):
    path = folder / 'Install.desktop'
    command = 'exec "$(dirname "$1")/BibleSmartDisplay" --install'
    quoted = command.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$').replace('`', '\\`')
    path.write_text('[Desktop Entry]\nType=Application\nName=Install Bible Smart Display\nExec=/bin/sh -c "' + quoted + '" sh %k\nIcon=video-display\nTerminal=false\n')
    path.chmod(0o755)

if sys.platform == 'darwin':
    subprocess.run(['codesign', '--force', '--deep', '--sign', '-', 'dist/BibleSmartDisplay.app'], check=True)
