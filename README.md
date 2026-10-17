[English](README.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md)

<div align="center">

<img src="docs/assets/banner-v2.svg" alt="Bible Smart Display — A daily verse. A quiet moment." width="100%">

# Bible Smart Display

**A daily Bible verse for your desk.**

For a **Turing Smart Screen 3.5-inch or similar** USB display.

These displays are also sold as **“IPS secondary screens”**, including on AliExpress. That listing name alone does not confirm compatibility; check the model table below.

[![Windows download](https://img.shields.io/badge/Download-Windows_x64-2563eb?style=for-the-badge)](https://github.com/dgcarr/bibleSmartDisplay/releases/latest)
[![Build](https://github.com/dgcarr/bibleSmartDisplay/actions/workflows/windows.yml/badge.svg)](https://github.com/dgcarr/bibleSmartDisplay/actions/workflows/windows.yml)
[![Licence](https://img.shields.io/badge/License-GPL_v3-64748b)](LICENSE)

**Choose your translation · Light blue text · Adjustable brightness · Offline restore**

[Windows](#windows) · [Linux](#linux) · [macOS](#macos) · [Drivers](#usb-drivers) · [Help](#need-help)

</div>

---

Bible Smart Display takes [Bible League’s daily reference](https://www.bibleleague.org/verse-of-the-day/), gets your chosen translation from Bible Gateway (default: **CSB**), and puts it on your screen. Text automatically fits the display.

## Choose your screen model

| Model option | Display | Landscape resolution | Status |
| :--- | :--- | :--- | :--- |
| `usbpcmonitor-3.5` | UsbPCMonitor / compatible 3.5-inch | 480 × 320 | Tested on Ubuntu; default |
| `turing-3.5` | Original Turing 3.5-inch | 480 × 320 | Experimental |
| `usbpcmonitor-5` | UsbPCMonitor 5-inch | 800 × 480 | Experimental |
| `usbpcmonitor-7` | UsbPCMonitor 7-inch | 1024 × 600 | Experimental |
| `xuanfang-3.5` | XuanFang Revision B / flagship | 480 × 320 | Experimental |
| `qiye-3.5` | Kipye / Qiye / 奇叶智显 (Revision D) | 480 × 320 | Experimental |

Select the exact model and serial port. **Experimental** means implemented and covered by simulated serial tests, but not physically tested by this project. These names describe protocols, not guaranteed seller brands.

```powershell
.\bibleSmartDisplay.exe --list-models
.\bibleSmartDisplay.exe --model xuanfang-3.5 --port COM3
.\bibleSmartDisplay.exe --model turing-3.5 --port COM3
```

Linux/macOS use the same arguments after `.venv/bin/python outputs/daily-verse/verse_display.py`. Experimental models require an explicit `--port`; no cross-protocol probing is performed. Add `--demo --preview-only` to preview a selected model's layout without hardware.

The original Turing model accepts an empty HELLO response **only when explicitly selected**. UsbPCMonitor models require the matching size response. Do not select original Turing merely to bypass an error. XuanFang brightness is on/off on some revisions; its RGB backplate is not configured here. Qiye has no identity handshake, so correct manual selection matters.

**Not supported:** AX206/AIDA64/USB2LCD, Turing 5-inch Revision C, round screens, Waveshare USB-Monitor, GUITION, Fuldho/SmartMonitor and HDMI displays. AX206 needs a separate direct-USB backend, not a serial-driver switch. UsbPCMonitor 5-inch and Turing 5-inch are different protocols.

## Start here

| Your computer | Install this |
| :--- | :--- |
| **Windows 10/11, x64** | [Download the app](https://github.com/dgcarr/bibleSmartDisplay/releases/latest) — no Python needed |
| **Linux / Raspberry Pi OS** | [Run from source](#linux) with Python 3.10+ |
| **macOS** | [Run from source](#macos) with Python 3.10+ |

Have your screen, a **USB data cable**, and an internet connection ready. Close any vendor display software before starting.

## Windows

### 1 · Download

Open **[the latest release](https://github.com/dgcarr/bibleSmartDisplay/releases/latest)**. Under **Assets**, choose **`bibleSmartDisplay-windows-x64.zip`**.

### 2 · Extract and connect

Extract the ZIP into a folder such as `Documents\bibleSmartDisplay`. Connect the screen to a USB data port.

### 3 · Run

Double-click **`Run-display.cmd`**. Your verse should appear on the screen.

The console stays open so you can read any messages. The app updates the screen once and exits; [set up a schedule](#update-it-every-morning) for daily updates.

<details>
<summary><strong>Screen not found? Select its COM port</strong></summary>

Open PowerShell in the extracted folder and run:

```powershell
.\bibleSmartDisplay.exe --list-ports
.\bibleSmartDisplay.exe --port COM3
```

Replace `COM3` with the port listed for your screen. If no port appears, see [USB drivers](#usb-drivers).

</details>

<details>
<summary><strong>Try it without a screen or internet connection</strong></summary>

```powershell
.\bibleSmartDisplay.exe --demo --preview-only
```

Open `%LOCALAPPDATA%\bibleSmartDisplay\preview.png` to see the test image.

</details>

> [!NOTE]
> The download is a portable console app, not a graphical installer. It is not code-signed. Windows build and preview tests pass; physical Windows/macOS USB testing is still needed. Physical output has been tested on Ubuntu.

## Linux

**1. Install the prerequisites:** Python 3.10+, Git, Python venv support and DejaVu Sans. On Ubuntu/Debian/Raspberry Pi OS, use your package manager to install `python3`, `python3-venv`, `python3-pip`, `git` and `fonts-dejavu-core`.

**2. Download and install:**

```sh
git clone https://github.com/dgcarr/bibleSmartDisplay.git
cd bibleSmartDisplay
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

**3. Connect the screen and run:**

```sh
.venv/bin/python outputs/daily-verse/verse_display.py
```

If automatic detection fails, run with `--list-ports`, then `--port /dev/ttyACM0`, using your actual port. For permission errors, see [Linux serial access](docs/setup.md#linux-including-raspberry-pi-os).

## macOS

**1. Install [Python 3.10+](https://www.python.org/downloads/macos/).** Download this repository using **Code → Download ZIP**, then extract it.

**2. Open Terminal in the extracted folder** containing `requirements.txt` and run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

**3. Connect the screen and run:**

```sh
.venv/bin/python outputs/daily-verse/verse_display.py
```

If automatic detection fails, run with `--list-ports`, then `--port /dev/cu.usbmodem1234`, replacing the example with your actual port. [More macOS help →](docs/setup.md#macos)

## USB drivers

**If your screen already appears as a serial port, try it before installing a driver.**

| Device / system | Official help or download |
| :--- | :--- |
| **Turing/TURZX screen** | [Manufacturer downloads](https://www.turzx.com/en/category/download/) — choose your exact model |
| **Windows USB CDC device** | [Microsoft’s built-in USB serial driver](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/usb-driver-installation-based-on-compatible-ids) — compatible devices install automatically |
| **Windows, confirmed CH340/CH341 chip** | [WCH Windows driver](https://www.wch.cn/downloads/CH341SER_EXE.html) |
| **macOS, supported WCH serial chip** | [WCH Mac driver and instructions](https://github.com/WCHSoftGroup/ch34xser_macos) |
| **Linux** | Compatible devices normally use the kernel’s existing serial drivers |

WCH drivers are **not universal screen drivers**. On Windows, check **Device Manager → Ports (COM & LPT)**. If the device has a warning icon, inspect **Properties → Details → Hardware Ids** and match the driver to that hardware. [Full driver guidance →](docs/setup.md#windows-usb-drivers)

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

## Make it yours

Defaults are **light blue text** and **50% brightness**. To change them, run from PowerShell:

```powershell
.\bibleSmartDisplay.exe --color "#ADD8E6" --brightness 50
```

For Linux/macOS, put the same options after `.venv/bin/python outputs/daily-verse/verse_display.py`.

| Option | What it does |
| :--- | :--- |
| `--brightness 25` | Dim the backlight; accepts 0–100 |
| `--color "#F5F5DC"` | Use beige text instead |
| `--cached` | Restore the last saved verse without internet |
| `--preview-only` | Save a preview without sending it to the screen |
| `--list-ports` | List connected serial devices |

Options apply to that run. Add them to your scheduled task to use them every day. [All settings and saved-file locations →](docs/setup.md#commands-and-settings)

## Update it every morning

Choose your operating system for step-by-step scheduling:

| Windows | Linux | macOS |
| :--- | :--- | :--- |
| [Task Scheduler](docs/setup.md#windows-task-scheduler) | [Cron](docs/setup.md#linux-cron) | [Launchd](docs/setup.md#macos-launchd) |

Your computer must be running and the screen connected. The first verse needs internet; later network failures fall back to the saved verse. The cache is overwritten, so it does not grow into a collection.

## Need help?

| Problem | First thing to try |
| :--- | :--- |
| Screen not found | Check the data cable, then `--list-ports` and [drivers](#usb-drivers) |
| Port busy | Close the vendor display app and other running copies |
| Wrong handshake or scrambled image | Check [hardware compatibility](docs/setup.md#compatible-displays) |
| No saved verse | Run once online without `--cached` |
| Window disappears | Launch with `Run-display.cmd` or from a terminal |

**[Full troubleshooting guide](docs/setup.md#troubleshooting)** · **[Report an issue](https://github.com/dgcarr/bibleSmartDisplay/issues)** · **[Build from source](docs/setup.md#build-the-windows-executable-yourself)**

When reporting a problem, include your OS, display model, hardware IDs and the error message.

---

### Credits & licence

Built with help from the [turing-smart-screen-python](https://github.com/mathoudebine/turing-smart-screen-python) protocol reference by Matthieu Houdebine and contributors. Independent of display manufacturers. Software: **[GPL v3](LICENSE)**; upstream files retain their own notices.

Daily reference: [Bible League](https://www.bibleleague.org/verse-of-the-day/). Passage text: [Bible Gateway](https://www.biblegateway.com/). Christian Standard Bible © 2017 Holman Bible Publishers. Scripture is not covered by the software licence.
