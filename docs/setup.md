# Setup and reference guide

[← Back to the quick start](../README.md)

Display a daily Bible verse on a **Turing Smart Screen 3.5-inch or similar** USB smart display.

BibleSmartDisplay takes the daily passage reference from [Bible League](https://www.bibleleague.org/verse-of-the-day/), retrieves your chosen Bible Gateway translation (default: **CSB**) from Bible Gateway, and displays it in light blue on black. Text automatically fits the selected model’s landscape resolution. Backlight brightness defaults to 50%.

[Windows downloads](https://github.com/dgcarr/bibleSmartDisplay/releases/latest) · [Builds](https://github.com/dgcarr/bibleSmartDisplay/actions/workflows/windows.yml) · [Report a problem](https://github.com/dgcarr/bibleSmartDisplay/issues)

## Compatible displays

See the [current model table](../README.md#choose-your-screen-model) for selectors, resolutions and experimental status. Use `--list-models` to list the same options locally. The default remains the physically tested UsbPCMonitor-compatible 3.5-inch device.

Original Turing 3.5-inch units may not answer HELLO. The explicit `--model turing-3.5 --port PORT` mode accepts only an empty response. The default and larger UsbPCMonitor modes require their exact size-specific replies. No mode treats arbitrary replies as valid.

XuanFang B and Qiye D use [smartscreen-driver](https://github.com/hchargois/smartscreen-driver), pinned to 0.2.3, extracted from the upstream GPL driver library. They are experimental. Some XuanFang units only support backlight on/off. Qiye does not provide an identity handshake. Experimental modes require an explicit port rather than probing other devices.

AX206 uses a different, direct-USB protocol and remains unsupported. Turing 5-inch Revision C is not the same as UsbPCMonitor 5-inch. Waveshare USB-Monitor, GUITION, Fuldho/SmartMonitor and HDMI displays remain unsupported.

Protocol references: [Revision A](https://github.com/mathoudebine/turing-smart-screen-python/blob/main/library/lcd/lcd_comm_rev_a.py), [hardware identification](https://github.com/mathoudebine/turing-smart-screen-python/wiki/Hardware-revisions).

## What you need

- A compatible screen and a **USB data cable** connected to its data port.
- Windows 10/11 x64 for the portable executable, or a desktop Python environment on Linux/macOS/Windows for source installation.
- Internet access for new verses. After a successful fetch, `--cached` can restore the last saved verse offline.
- Close the vendor's display software before running this program: only one application should control the serial port.

Linux hardware output has been tested. The Windows build runs automated executable and preview checks; physical USB operation on Windows and macOS still needs user testing. There is no Android/iOS installer.

## Windows: portable executable (no Python required)

1. Open [Releases](https://github.com/dgcarr/bibleSmartDisplay/releases/latest) and download `bibleSmartDisplay-windows-x64.zip` under **Assets**. This is the application download, not the “Source code” ZIP.
2. Extract the ZIP into a folder you own, such as `Documents\bibleSmartDisplay`.
3. Connect the screen. Check the driver section below if no COM port appears.
4. Double-click **Run-display.cmd**. It runs the executable with automatic detection and leaves the console open so you can read the result.

For manual port selection, open PowerShell in the extracted folder:

```powershell
.\bibleSmartDisplay.exe --list-ports
.\bibleSmartDisplay.exe --port COM3
```

Replace `COM3` with your screen's port. A console executable is provided, not a graphical installer. It runs once, updates the screen, and exits. Ordinary operation does not require administrator privileges. The binary is not code-signed; builds and source are published here for inspection.

Test rendering without the screen or internet:

```powershell
.\bibleSmartDisplay.exe --demo --preview-only
```

Open `%LOCALAPPDATA%\bibleSmartDisplay\preview.png` to see the result.

### Windows USB drivers

First open **Device Manager → Ports (COM & LPT)**. If the connected display already has a COM port without a warning icon, try that port before installing a driver.

| What Windows detects | What to do |
| --- | --- |
| USB CDC serial device | Windows includes `usbser.sys` and can install it automatically for compatible devices; see [Microsoft's USB serial driver documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/usb-driver-installation-based-on-compatible-ids). |
| Confirmed CH340/CH341 USB-to-serial chip needing a driver | Use [WCH's official Windows CH341SER driver](https://www.wch.cn/downloads/CH341SER_EXE.html). This is not a universal Turing-screen driver. |
| Unknown device, warning icon, or another controller | Open **Properties → Details → Hardware Ids**, note VID/PID, and use the exact model's manufacturer/seller driver. For genuine Turing hardware, start with [TURZX official downloads](https://www.turzx.com/en/category/download/). |

Try Windows Update's driver updates and a known data cable. Vendor downloads may contain the display application as well as drivers; close that application before running BibleSmartDisplay. Do not replace the serial driver with WinUSB/Zadig: this program needs a COM port. A driver cannot make an unsupported display protocol compatible.

## Install from source: all three desktop operating systems

Use **Python 3.10 or newer** (the Windows build uses Python 3.12). Download the source using **Code → Download ZIP** on this repository and extract it, or clone it:

```sh
git clone https://github.com/dgcarr/bibleSmartDisplay.git
cd bibleSmartDisplay
```

For ZIP downloads, open a terminal in the extracted folder containing `requirements.txt`. The commands below use a virtual environment directly; activation is optional.

### Windows source installation

Install Python from [python.org](https://www.python.org/downloads/windows/), then run in PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe outputs\daily-verse\verse_display.py --list-ports
.\.venv\Scripts\python.exe outputs\daily-verse\verse_display.py --port COM3
```

The driver guidance above also applies to source installations.

### Linux, including Raspberry Pi OS

Install Python, venv support, and a TrueType font through your distribution's package manager. On Ubuntu/Debian/Raspberry Pi OS, the packages are `python3`, `python3-venv`, `python3-pip`, `git`, and `fonts-dejavu-core`. On other distributions, install their equivalents.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python outputs/daily-verse/verse_display.py --list-ports
.venv/bin/python outputs/daily-verse/verse_display.py --port /dev/ttyACM0
```

Replace `/dev/ttyACM0` with the actual port. A stable `/dev/serial/by-id/...` path is preferable for scheduling. Compatible USB serial devices normally use kernel drivers such as `cdc_acm` or `ch341`; no Windows driver is used on Linux.

If permission is denied, inspect the device's owner/group with `ls -l /dev/ttyACM0`. Add your account to the appropriate serial-access group using your distribution's account-management tools, then log out and back in. On Ubuntu/Debian this is commonly `dialout`. Avoid running the application as root or granting everyone write access to the device.

### macOS

Install Python from [python.org](https://www.python.org/downloads/macos/), then:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python outputs/daily-verse/verse_display.py --list-ports
.venv/bin/python outputs/daily-verse/verse_display.py --port /dev/cu.usbmodem1234
```

Use the actual `/dev/cu.*` device shown by `--list-ports`; the example name is a placeholder. The program looks for Arial in standard macOS locations. Supply `--font /path/to/font.ttf` if it cannot find a font.

**Mac drivers:** try the device first; if a usable serial port appears, a separate driver may be unnecessary. For a variant confirmed to use a supported WCH USB-to-serial chip, use [WCH's official macOS driver repository and installation instructions](https://github.com/WCHSoftGroup/ch34xser_macos). Follow its macOS-version-specific instructions. This driver is not required for every screen and is not a substitute for protocol compatibility. For other controllers, use the manufacturer's driver for the exact device.

If Python reports certificate verification failures after a python.org installation, run the supplied **Install Certificates.command** in its Applications folder; do not disable HTTPS verification.

## Choose a translation

Use `--translation` with a [Bible Gateway version code](https://www.biblegateway.com/versions/):

```powershell
.\bibleSmartDisplay.exe --translation NIV
.\bibleSmartDisplay.exe --translation KJV
.\bibleSmartDisplay.exe --translation RVR1960
```

On Linux/macOS:

```sh
.venv/bin/python outputs/daily-verse/verse_display.py --translation NIV
```

CSB remains the default. Any single Bible Gateway text-version code can be requested; the passage must be available in that version. PDF/audio-only editions are not supported. Non-English text may need `--font` with a font covering that language; complex scripts and long unspaced passages are not fully tested.

Add the option to your scheduled task or edit the executable line in `Run-display.cmd` to keep using your choice. `--cached` restores the last saved translation; add `--translation NIV` to require that exact version. A failed lookup never silently replaces your requested translation with a different one. The cache still keeps only one passage.

## Commands and settings

The examples use the Windows executable. From source, replace `bibleSmartDisplay.exe` with your virtual environment's Python followed by `outputs/daily-verse/verse_display.py`.

```powershell
# Fetch today's selection and show the CSB wording
.\bibleSmartDisplay.exe --port COM3

# Restore the previous verse without a network request
.\bibleSmartDisplay.exe --port COM3 --cached

# Fetch and render without opening a serial port
.\bibleSmartDisplay.exe --preview-only

# Offline test message, without changing the saved verse
.\bibleSmartDisplay.exe --demo --preview-only

# Set text colour and backlight brightness
.\bibleSmartDisplay.exe --port COM3 --color "#ADD8E6" --brightness 50

# Use a different font or data folder
.\bibleSmartDisplay.exe --font "C:\Windows\Fonts\arial.ttf" --data-dir "C:\Users\You\Documents\BibleData"
```

Options are applied on each invocation; they are not saved as preferences. Include your chosen options in shortcuts and scheduled tasks. Brightness accepts 0–100. Keep all invocations controlling the same display on the same data directory so they share the process lock.

## Automatic daily updates

The program runs once and exits. Use your operating system's scheduler to update it every day. The computer must be running, with the screen connected and internet available for a fresh verse. On network errors, an existing cached verse is used; the first run needs a successful fetch. Daily selection follows the source website, which may change at a different time from your local midnight.

### Windows Task Scheduler

Create a task for your user with a **Daily, 06:00** trigger:

- **Program/script:** full path to `bibleSmartDisplay.exe`.
- **Arguments:** `--port COM3 --brightness 50` (use your actual port).
- **Start in:** the folder containing the executable.
- Under Settings, select **Run task as soon as possible after a scheduled start is missed** if desired; choose **Do not start a new instance** if it is already running.

For source installs, set Program/script to the full `.venv\Scripts\python.exe` path, and start Arguments with the quoted full path of `verse_display.py`. Add a separate **At log on** task with `--cached` if you want the saved verse restored at login. These tasks do not automatically handle USB hot-plug events.

### Linux cron

Run `crontab -e` and add a line using your absolute paths:

```cron
0 6 * * * /home/YOU/bibleSmartDisplay/.venv/bin/python /home/YOU/bibleSmartDisplay/outputs/daily-verse/verse_display.py --port /dev/serial/by-id/YOUR-DISPLAY
```

This follows the cron host's timezone and does not catch up missed runs. For paths containing spaces, quote each path. Systemd timers are another option if missed-run handling is needed.

The legacy service, udev rule and installer under `outputs/daily-verse/` and `work/` contain the original author's paths and device identifiers. **Do not install them unchanged.** Adapt the service's user and interpreter path to your virtual environment, and match the rule to your actual device. The service uses `--cached`, so fetch a verse first. Those files are Linux-only examples, not portable installers.

### macOS launchd

Create `~/Library/LaunchAgents/com.biblesmartdisplay.daily.plist` with the following content, replacing `/Users/YOU` and the serial port with your real values. Paths in a plist must be absolute; `~` is not expanded.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.biblesmartdisplay.daily</string>
  <key>ProgramArguments</key><array>
    <string>/Users/YOU/bibleSmartDisplay/.venv/bin/python</string>
    <string>/Users/YOU/bibleSmartDisplay/outputs/daily-verse/verse_display.py</string>
    <string>--port</string><string>/dev/cu.usbmodem1234</string>
  </array>
  <key>StartCalendarInterval</key><dict>
    <key>Hour</key><integer>6</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
</dict></plist>
```

Load it from Terminal:

```sh
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.biblesmartdisplay.daily.plist"
```

This is a per-user launch agent; it needs your login session. To remove the schedule, use `launchctl bootout` with the same domain and plist path. USB reconnection alone does not trigger this schedule.

## Saved files

| Operating system | Default data folder |
| --- | --- |
| Windows | `%LOCALAPPDATA%\bibleSmartDisplay` |
| macOS | `~/Library/Application Support/bibleSmartDisplay` |
| Linux | `$XDG_DATA_HOME/bibleSmartDisplay`, or `~/.local/share/bibleSmartDisplay` |

`last-verse.json` and `preview.png` are overwritten, not accumulated. `verse.log` rotates with two backups of approximately 200 KB each. `--data-dir` overrides the folder. A `.lock` file coordinates concurrent runs. Old installations that saved data beside the script can use `--data-dir` pointing to that directory, or fetch a fresh verse into the new default location.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| No serial port | Data cable, correct USB socket, OS device list, and driver section above. |
| Automatic detection fails | Run `--list-ports` and specify `--port`; multiple connected screens also require selection. |
| Access denied or port busy | Close vendor software and other instances; check Linux serial permissions. |
| Unexpected screen handshake | Verify the port, screen model and protocol. Similar casing does not establish compatibility. |
| Scrambled or blank image | Confirm the selected --model, its protocol and resolution against the model table. |
| Missing cached verse | Run once online without `--cached`; use the same account/data directory for scheduled runs. |
| Font error | Supply `--font` with a readable TrueType font path. |
| Fetch/parser error | Check network and `verse.log`. Bible League or Bible Gateway markup may have changed; a parser update may be needed. |
| Window closes immediately | Use `Run-display.cmd` or run from PowerShell/Terminal to see the error. |

When reporting a problem, include OS, screen model/photo, hardware IDs, `--list-ports` output and relevant log messages. Do not include passwords or tokens.

## Build the Windows executable yourself

Run these commands **on Windows** from the source folder:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt "pyinstaller>=6,<7"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --name bibleSmartDisplay outputs\daily-verse\verse_display.py
.\dist\bibleSmartDisplay.exe --demo --preview-only
```

The output is `dist\bibleSmartDisplay.exe`. [PyInstaller builds for the OS it runs on](https://pyinstaller.org/en/stable/index.html); running it on Linux does not produce a Windows executable. The [Windows workflow](../.github/workflows/windows.yml) builds on a Windows x64 runner, tests offline rendering, and uploads a ZIP and SHA-256 checksum. Tags beginning with `v` also publish the download to Releases. These automated checks cannot verify a physical USB screen attached to a user's PC.

## Source layout and licence

- `outputs/daily-verse/verse_display.py`: application.
- `requirements.txt`: runtime dependencies.
- `tests/`: preview, detection and serial-protocol checks.
- `.github/workflows/windows.yml`: Windows build and release automation.
- `work/add_csb.py`: historical migration helper; do not run on the current application.
- `work/protocol.py`, `work/lcd_comm.py`: upstream reference code; these files require the upstream library and are not standalone applications.

Software is distributed under the GNU GPL v3; see [LICENSE](../LICENSE). Upstream reference files retain their GPL-3.0-or-later notices and copyright attribution to Matthieu Houdebine and [turing-smart-screen-python](https://github.com/mathoudebine/turing-smart-screen-python). `COPYING` also contains the GPL text. Bundled dependencies retain their own licences.

Passage text comes from [Bible Gateway](https://www.biblegateway.com/), selected using Bible League's daily reference. Christian Standard Bible. Copyright © 2017 by Holman Bible Publishers. Scripture text is not covered by this software licence. Generated verse caches and previews are excluded from Git.
