# Daily Bible verse USB display

Fetches https://www.bibleleague.org/verse-of-the-day/ and displays the verse and reference in light blue on black, with 50% backlight brightness, in 480×320 landscape. Font size adjusts to fit. Requires the existing system Python packages Pillow and pyserial.

Run manually:

```sh
/usr/bin/python3 /home/dgcarr/Documents/Codex/2026-10-17/do-x20/outputs/daily-verse/verse_display.py
```

Add `--preview-only` to fetch and save preview.png without accessing the LCD.

The user crontab fetches and displays the verse once daily at 6:00 am Australia/Sydney (system timezone). There are no hourly or startup jobs. The PC must be on and the screen connected at that time; cron does not catch up missed runs. The last successful verse is cached for network outages. Logs rotate automatically in verse.log. A serial handshake validates the 3.5-inch screen before any image is sent.

Files: verse_display.py (code), preview.png (most recent rendering), last-verse.json (cached verse), verse.log (diagnostics), cron.txt (installed job definitions).

To disable, run `crontab -e` and remove the block between BEGIN and END daily-bible-verse-lcd. Keep this folder in place while the job is enabled.

Serial protocol reference: https://github.com/mathoudebine/turing-smart-screen-python

## Automatic restore after plugging in

A udev rule (`/etc/udev/rules.d/99-daily-verse-lcd.rules`) starts `daily-verse-lcd.service` when this USB screen connects. It runs as dgcarr, waits two seconds for the device, and displays the cached verse with `--cached`. It makes no website request. The daily 6:00 am cron job still fetches the new verse. Service failures retry up to the configured start limit.

The rule and service source files are included in this folder. Inspect status with `systemctl status daily-verse-lcd.service` or `journalctl -u daily-verse-lcd.service`. A successful oneshot service normally returns to inactive after sending the image.

## CSB translation

The daily run takes the passage reference from Bible League, removes its translation suffix, and requests the same passage in the Christian Standard Bible from Bible Gateway. Only the scripture text is displayed; verse numbers and footnote/cross-reference markers are removed. The screen reference ends in CSB. The cache stores the CSB wording, source URL and copyright attribution. Failed lookups preserve the previous saved verse. Both sites' HTML structures are dependencies and may require parser updates if their layouts change.

Christian Standard Bible. Copyright © 2017 by Holman Bible Publishers.
