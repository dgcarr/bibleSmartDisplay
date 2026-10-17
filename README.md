# bibleSmartDisplay

Display a daily Bible verse in the Christian Standard Bible (CSB) on a Turing Revision A 3.5-inch USB LCD.

The Python script takes the daily passage reference from Bible League, retrieves the CSB wording from Bible Gateway, renders a 480×320 image, and sends it over USB serial. Text automatically fits the screen. Current styling is light blue on black with 50% backlight brightness.

## Run

Requires Linux, Python 3, Pillow, pyserial, and the DejaVu Sans font. Configure `PORT` and `FONT` in `outputs/daily-verse/verse_display.py` for your machine, and ensure your user has access to the serial device.

```sh
python3 -m pip install Pillow pyserial
python3 outputs/daily-verse/verse_display.py
```

Use `--preview-only` to generate an image without accessing the screen. Use `--cached` to restore the last saved verse without a network request; this requires a successful previous fetch. Generated previews, cached passages, and logs are not tracked in Git.

## Files

- `outputs/daily-verse/verse_display.py`: current standalone display program.
- `outputs/daily-verse/`: cron, systemd and udev setup examples, with further documentation.
- `work/install-hotplug.sh`: installer for the USB reconnect service.
- `work/add_csb.py`: historical migration helper; do not run against the current script, which already supports CSB.
- `work/protocol.py` and `work/lcd_comm.py`: upstream protocol reference files, not standalone runnable programs; they depend on the upstream library.

The setup files retain the original machine's absolute paths and username. Adapt these before installation. The cron example runs at 06:00 in the machine's timezone. The reconnect service restores the cached verse. Website markup changes may require parser maintenance.

This repository is a copy of the working installation; the existing display service currently runs from the original location.

## Attribution

Protocol reference files are from [turing-smart-screen-python](https://github.com/mathoudebine/turing-smart-screen-python), copyright Matthieu Houdebine, under GPL-3.0-or-later. Their copyright notices are retained; the licence text is included in `COPYING`.

Passage selection: [Bible League](https://www.bibleleague.org/verse-of-the-day/). CSB passage source: [Bible Gateway](https://www.biblegateway.com/). Christian Standard Bible. Copyright © 2017 by Holman Bible Publishers. Scripture text is not covered by the software licence.
