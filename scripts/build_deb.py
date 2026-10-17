"""Package the native PyInstaller bundle; run on the target Debian architecture."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--version', default='0.4.3')
args = p.parse_args()
if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', args.version):
    p.error('Version must be major.minor.patch')
arch = subprocess.check_output(['dpkg', '--print-architecture'], text=True).strip()
if arch not in ('amd64', 'arm64'):
    p.error('Only amd64 and arm64 are supported')
root = Path('build/deb')
shutil.rmtree(root, ignore_errors=True)
bundle = root / 'opt/biblesmartdisplay'
shutil.copytree('dist/BibleSmartDisplay', bundle, symlinks=True)
(bundle / 'Install.desktop').unlink(missing_ok=True)
control = root / 'DEBIAN'
control.mkdir()
size = sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink()) // 1024
(control / 'control').write_text(f'''Package: biblesmartdisplay
Version: {args.version}
Section: utils
Priority: optional
Architecture: {arch}
Maintainer: David Carr <daggysheep@gmail.com>
Installed-Size: {size}
Depends: libc6 (>= 2.36), libstdc++6, libgl1, libegl1, libopengl0, libfontconfig1, libglib2.0-0, libdbus-1-3, libxkbcommon-x11-0, libxcb-cursor0, libxcb-icccm4, libxcb-keysyms1, libxcb-shape0, libxcb-xinerama0, fonts-dejavu-core
Recommends: systemd, pkexec, acl
Homepage: https://github.com/dgcarr/bibleSmartDisplay
Description: Daily Bible verses for USB smart displays
 Multilingual desktop app with guided setup, tray controls and per-user
 scheduling for supported Turing and compatible USB serial screens.
 Python and Qt are bundled. A graphical desktop session is required.
''', encoding='utf-8')
applications = root / 'usr/share/applications'
applications.mkdir(parents=True)
(applications / 'biblesmartdisplay.desktop').write_text('''[Desktop Entry]
Type=Application
Name=Bible Smart Display
Comment=Daily Bible verses on your USB screen
Comment[zh_CN]=在 USB 屏幕上显示每日圣经经文
Comment[es]=Versículos bíblicos diarios en tu pantalla USB
Comment[fr]=Versets bibliques quotidiens sur votre écran USB
Exec=/opt/biblesmartdisplay/BibleSmartDisplay
TryExec=/opt/biblesmartdisplay/BibleSmartDisplay
Icon=video-display
Terminal=false
Categories=Utility;
StartupNotify=true
''', encoding='utf-8')
bin_dir = root / 'usr/bin'
bin_dir.mkdir(parents=True)
(bin_dir / 'biblesmartdisplay').symlink_to('/opt/biblesmartdisplay/BibleSmartDisplay')
doc = root / 'usr/share/doc/biblesmartdisplay'
doc.mkdir(parents=True)
shutil.copy2('COPYING', doc / 'copyright')
(doc / 'README.Debian').write_text('''Launch Bible Smart Display from the applications menu.
Scheduling and startup are configured per user, never by this package.
Before removal, choose Remove automatic setup in Settings and quit the app.
Alternatively run biblesmartdisplay --remove-setup as your normal user.
Package removal preserves user settings, caches and custom USB access rules.
See /opt/biblesmartdisplay/docs/desktop.md for details.
''')
Path('artifacts').mkdir(exist_ok=True)
output = Path('artifacts') / f'biblesmartdisplay_{args.version}_{arch}.deb'
subprocess.run(['dpkg-deb', '--root-owner-group', '-Zxz', '--build', str(root), str(output)], check=True)
print(output)
