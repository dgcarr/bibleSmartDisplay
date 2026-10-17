"""Shared settings, device selection and execution for GUI and scheduler."""
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from .system import host_environment
from PIL import ImageColor
from filelock import FileLock

if not getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'outputs/daily-verse'))
import verse_display as engine

DEFAULTS = dict(version=1, model='usbpcmonitor-3.5', port='', identity=None,
                color='#ADD8E6', brightness=50, translation='CSB', font='',
                time='06:00', scheduled=False, startup=False, language='auto')


def validate(data):
    result = dict(DEFAULTS, **data)
    if result['language'] not in ('auto', 'en', 'zh', 'es', 'fr'):
        raise ValueError('Unknown interface language')
    if result['version'] != 1:
        raise ValueError('Unsupported settings version')
    if result['model'] not in engine.MODELS:
        raise ValueError('Unknown screen model')
    for key in ('port', 'color', 'translation', 'font', 'time'):
        if not isinstance(result[key], str):
            raise ValueError(f'{key} must be text')
    if result['identity'] is not None:
        ident = result['identity']
        if not isinstance(ident, dict) or set(ident) != {'vid', 'pid', 'serial'} or not isinstance(ident['serial'], str) or not ident['serial']:
            raise ValueError('Invalid USB identity')
    ImageColor.getrgb(result['color'])
    if type(result['brightness']) is not int or not 0 <= result['brightness'] <= 100:
        raise ValueError('Brightness must be 0–100')
    result['translation'] = engine.version_code(result['translation'])
    import datetime
    datetime.datetime.strptime(result['time'], '%H:%M')
    for key in ('scheduled', 'startup'):
        if type(result[key]) is not bool:
            raise ValueError(f'{key} must be boolean')
    return result


def load(root):
    path = root / 'settings.json'
    return validate(json.loads(path.read_text('utf-8'))) if path.exists() else dict(DEFAULTS)


def save(root, data):
    data = validate(data)
    root.mkdir(parents=True, exist_ok=True)
    with FileLock(str(root / 'settings.lock')):
        temp = root / 'settings.json.tmp'
        temp.write_text(json.dumps(data, indent=2), encoding='utf-8')
        temp.replace(root / 'settings.json')


def identity(port):
    return dict(vid=port.vid, pid=port.pid, serial=port.serial_number) if port.serial_number else None


def resolve(data, ports=None):
    ports = list(engine.list_ports.comports()) if ports is None else ports
    if data['identity']:
        matches = [p.device for p in ports if identity(p) == data['identity']]
    else:
        matches = [p.device for p in ports if p.device == data['port']]
    if len(matches) != 1:
        raise ValueError('Screen missing or ambiguous. Select its USB port in Settings.')
    return matches[0]


def run(root, data, mode='update'):
    """Use the existing CLI engine, including its cache and interprocess lock."""
    args = ['bibleSmartDisplay', '--data-dir', str(root), '--model', data['model'],
            '--color', data['color'], '--brightness', str(data['brightness']),
            '--translation', data['translation']]
    if data['font']:
        args += ['--font', data['font']]
    if mode == 'preview':
        args += ['--demo', '--preview-only']
    else:
        args += ['--port', resolve(data)]
        if mode == 'test':
            args += ['--demo']
        elif mode == 'restore':
            args += ['--cached']
    import logging
    try:
        if engine.main(args[1:]) is False:
            raise RuntimeError('Another update is already running; try again shortly.')
    except Exception:
        logging.exception('Desktop display operation failed')
        raise
    finally:
        # The GUI is long-lived; release files between operations (especially Windows).
        for handler in logging.getLogger().handlers[:]:
            handler.close()
            logging.getLogger().removeHandler(handler)


def due(root, data, now=None):
    from datetime import datetime
    now = now or datetime.now()
    if not data['scheduled'] or now.strftime('%H:%M') < data['time']:
        return False
    path = root / 'last-scheduled.json'
    try:
        return json.loads(path.read_text())['date'] != now.date().isoformat()
    except (OSError, ValueError, KeyError):
        return True


def scheduled(root):
    from datetime import datetime
    root.mkdir(parents=True, exist_ok=True)
    if not load(root)['scheduled']:
        return
    if sys.platform.startswith('linux'):
        import subprocess
        status = subprocess.run(['loginctl', 'show-user', str(os.getuid()), '-p', 'State', '--value'], capture_output=True, text=True, env=host_environment())
        if status.returncode != 0:
            raise RuntimeError('Cannot check login session: ' + status.stderr.strip())
        if status.stdout.strip() not in ('active', 'online'):
            return
    with FileLock(str(root / 'scheduler.lock'), timeout=0):
        data = load(root)
        if not due(root, data):
            return
        for attempt, delay in enumerate((0, 30, 120)):
            time.sleep(delay)
            data = load(root)
            if not data['scheduled']:
                return
            try:
                run(root, data)
                path = root / 'last-scheduled.json'
                temp = path.with_suffix('.tmp')
                temp.write_text(json.dumps({'date': datetime.now().date().isoformat()}))
                temp.replace(path)
                return
            except Exception:
                if attempt == 2:
                    raise
