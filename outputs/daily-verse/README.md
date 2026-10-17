# Daily verse application

See the [main README](../../README.md) for current Windows, macOS and Linux installation, USB drivers, commands and scheduling instructions.

`verse_display.py` is the application entry point. Install the root `requirements.txt` in a virtual environment before running it.

The adjacent cron, systemd service and udev rule are legacy examples from the original Ubuntu installation. Their usernames, paths, Python interpreter and device identifiers must be adapted before use. They are not portable installers. The current application uses a per-user data directory; use `--data-dir` to restore an older cache stored beside this script.
