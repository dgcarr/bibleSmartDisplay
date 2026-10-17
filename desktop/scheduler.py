"""Per-user operating-system integration. Never touches unrelated jobs."""
import os
import plistlib
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

NAME = 'BibleSmartDisplay'


def command(root, mode):
    base = [sys.executable] if getattr(sys, 'frozen', False) else [sys.executable, str(Path(__file__).resolve().parents[1] / 'desktop_app.py')]
    return base + [mode, '--data-dir', str(root)]


def call(args):
    subprocess.run(args, check=True, capture_output=True, text=True)


def unit_quote(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%').replace('$', '$$') + '"'


def configure(root, data):
    root.mkdir(parents=True, exist_ok=True)
    if sys.platform == 'win32':
        for suffix, enabled, mode in [('Daily', data['scheduled'], '--scheduled'), ('Tray', data['startup'], '--tray')]:
            name = NAME + suffix
            if not enabled:
                subprocess.run(['schtasks', '/Delete', '/TN', name, '/F'], capture_output=True)
                continue
            import getpass
            user = subprocess.check_output(['whoami'], text=True).strip()
            exe, *args = command(root, mode)
            trigger = '<LogonTrigger><Enabled>true</Enabled></LogonTrigger>'
            if suffix == 'Daily':
                trigger += '<TimeTrigger><Repetition><Interval>PT1M</Interval></Repetition><StartBoundary>2020-01-01T00:00:00</StartBoundary><Enabled>true</Enabled></TimeTrigger>'
            xml = f'''<?xml version="1.0" encoding="UTF-16"?><Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"><Triggers>{trigger}</Triggers><Principals><Principal id="Author"><UserId>{escape(user)}</UserId><LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel></Principal></Principals><Settings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy><DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries><StopIfGoingOnBatteries>false</StopIfGoingOnBatteries><StartWhenAvailable>true</StartWhenAvailable><ExecutionTimeLimit>{"PT10M" if suffix == "Daily" else "PT0S"}</ExecutionTimeLimit></Settings><Actions Context="Author"><Exec><Command>{escape(exe)}</Command><Arguments>{escape(subprocess.list2cmdline(args))}</Arguments></Exec></Actions></Task>'''
            path = root / (suffix + '.xml')
            path.write_text(xml, encoding='utf-16')
            call(['schtasks', '/Create', '/TN', name, '/XML', str(path), '/F'])
    elif sys.platform == 'darwin':
        folder = Path.home() / 'Library/LaunchAgents'
        folder.mkdir(parents=True, exist_ok=True)
        for suffix, enabled, mode in [('daily', data['scheduled'], '--scheduled'), ('tray', data['startup'], '--tray')]:
            label = 'org.biblesmartdisplay.' + suffix
            path = folder / (label + '.plist')
            subprocess.run(['launchctl', 'bootout', f'gui/{os.getuid()}', str(path)], capture_output=True)
            if enabled:
                payload = dict(Label=label, ProgramArguments=command(root, mode), RunAtLoad=True)
                if suffix == 'daily':
                    payload['StartInterval'] = 60
                path.write_bytes(plistlib.dumps(payload))
                call(['launchctl', 'bootstrap', f'gui/{os.getuid()}', str(path)])
            else:
                path.unlink(missing_ok=True)
    else:
        folder = Path.home() / '.config/systemd/user'
        folder.mkdir(parents=True, exist_ok=True)
        unit = 'biblesmartdisplay'
        if data['scheduled']:
            cmd = ' '.join(map(unit_quote, command(root, '--scheduled')))
            (folder / (unit + '.service')).write_text('[Unit]\nDescription=Bible Smart Display update\n[Service]\nType=oneshot\nExecStart=' + cmd + '\n')
            (folder / (unit + '.timer')).write_text('[Unit]\nDescription=Check daily verse schedule\n[Timer]\nOnStartupSec=30\nOnCalendar=*-*-* *:*:00\nPersistent=true\n[Install]\nWantedBy=timers.target\n')
            call(['systemctl', '--user', 'daemon-reload'])
            call(['systemctl', '--user', 'enable', '--now', unit + '.timer'])
        else:
            subprocess.run(['systemctl', '--user', 'disable', '--now', unit + '.timer'], capture_output=True)
            for ext in ('.service', '.timer'):
                (folder / (unit + ext)).unlink(missing_ok=True)
            call(['systemctl', '--user', 'daemon-reload'])
        folder = Path.home() / '.config/autostart'
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / 'biblesmartdisplay.desktop'
        if data['startup']:
            cmd = ' '.join('"' + x.replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%') + '"' for x in command(root, '--tray'))
            path.write_text('[Desktop Entry]\nType=Application\nName=Bible Smart Display\nExec=' + cmd + '\n')
        else:
            path.unlink(missing_ok=True)


def legacy_jobs():
    if sys.platform.startswith('linux'):
        p = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        return '\n'.join(x for x in p.stdout.splitlines() if 'verse_display' in x or 'bibleSmartDisplay' in x)
    if sys.platform == 'darwin':
        return '\n'.join(str(p) for p in (Path.home() / 'Library/LaunchAgents').glob('*bible*') if not p.name.startswith('org.biblesmartdisplay.'))
    p = subprocess.run(['schtasks', '/Query', '/FO', 'CSV'], capture_output=True, text=True)
    return '\n'.join(x for x in p.stdout.splitlines() if ('verse' in x.lower() or 'bible' in x.lower()) and NAME not in x)
