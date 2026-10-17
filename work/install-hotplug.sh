#!/bin/sh
set -eu
base=/home/dgcarr/Documents/Codex/2026-10-17/do-x20/outputs/daily-verse
install -o root -g root -m 644 "$base/daily-verse-lcd.service" /etc/systemd/system/daily-verse-lcd.service
install -o root -g root -m 644 "$base/99-daily-verse-lcd.rules" /etc/udev/rules.d/99-daily-verse-lcd.rules
systemctl daemon-reload
udevadm control --reload-rules
systemctl start daily-verse-lcd.service
