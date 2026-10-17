"""Narrow USB access repair for the selected serial device only."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def repair(data, port):
    port = Path(port).resolve()
    if not str(port).startswith(('/dev/ttyACM', '/dev/ttyUSB')) or not port.is_char_device():
        raise ValueError('Select a USB serial device first.')
    acl = shutil.which('setfacl')
    if not shutil.which('pkexec') or not acl:
        raise RuntimeError(f'pkexec/setfacl unavailable. Terminal fallback: sudo setfacl -m u:{os.getuid()}:rw {port}')
    ident = data.get('identity')
    if ident and isinstance(ident['vid'], int) and isinstance(ident['pid'], int) and re.fullmatch(r'[A-Za-z0-9_.-]+', ident['serial']):
        rule = f'SUBSYSTEM=="tty", ATTRS{{idVendor}}=="{ident["vid"]:04x}", ATTRS{{idProduct}}=="{ident["pid"]:04x}", ATTRS{{serial}}=="{ident["serial"]}", TAG+="uaccess"\n'
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / '70-biblesmartdisplay.rules'
            source.write_text(rule)
            # All variable values are positional arguments, never shell source.
            script = 'install -m 0644 -- "$1" "$2" && udevadm control --reload-rules && "$3" -m "$4" -- "$5"'
            subprocess.run(['pkexec', '/bin/sh', '-c', script, 'bible-usb-setup', str(source), f'/etc/udev/rules.d/70-biblesmartdisplay-{os.getuid()}.rules', acl, f'u:{os.getuid()}:rw', str(port)], check=True)
    else:
        subprocess.run(['pkexec', acl, '-m', f'u:{os.getuid()}:rw', str(port)], check=True)
