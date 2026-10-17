#!/usr/bin/env python3
"""Desktop entry point; scheduled mode deliberately does not import Qt."""
import argparse
import sys
from pathlib import Path
from desktop import core


def main():
    p = argparse.ArgumentParser(description='Bible Smart Display desktop app')
    modes = p.add_mutually_exclusive_group()
    modes.add_argument('--tray', action='store_true')
    modes.add_argument('--scheduled', action='store_true')
    modes.add_argument('--update', action='store_true')
    modes.add_argument('--preview', action='store_true')
    modes.add_argument('--remove-setup', action='store_true')
    modes.add_argument('--install', action='store_true')
    p.add_argument('--smoke-test', action='store_true')
    p.add_argument('--data-dir', type=Path, default=core.engine.default_data_dir())
    args = p.parse_args()
    root = args.data_dir.expanduser().resolve()
    if args.scheduled:
        core.scheduled(root)
    elif args.update or args.preview:
        core.run(root, core.load(root), 'preview' if args.preview else 'update')
    elif args.remove_setup:
        from desktop.scheduler import configure
        data = core.load(root)
        data.update(scheduled=False, startup=False)
        core.save(root, data)
        configure(root, data)
    elif args.install:
        from desktop.install import install
        return install()
    else:
        if sys.platform.startswith('linux') and getattr(sys, 'frozen', False) and not args.smoke_test and not args.tray and Path(sys.executable).resolve().parent not in (Path.home() / '.local/opt/bibleSmartDisplay', Path('/opt/biblesmartdisplay')):
            from desktop.install import install
            return install()
        from filelock import FileLock, Timeout
        root.mkdir(parents=True, exist_ok=True)
        try:
            with FileLock(str(root / 'gui.lock'), timeout=0):
                from desktop.gui import start
                return start(root, args.tray, args.smoke_test)
        except Timeout:
            print('Bible Smart Display is already running. Open Settings from its tray icon.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        if sys.stderr is not None:
            print(str(exc), file=sys.stderr)
        else:
            import logging
            logging.exception('Desktop operation failed')
        if not any(arg in sys.argv for arg in ('--scheduled', '--update', '--preview', '--remove-setup', '--smoke-test')):
            from PySide6.QtWidgets import QApplication, QMessageBox
            from desktop.i18n import translator, system_language
            app = QApplication.instance() or QApplication([])
            t = translator(system_language())
            QMessageBox.critical(None, t('Operation failed'), str(exc))
        sys.exit(1)
