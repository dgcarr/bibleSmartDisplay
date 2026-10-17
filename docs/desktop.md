# Desktop app

The desktop app includes English, 简体中文, Español and Français. Its interface initially follows the computer's language; choose **Language** in Settings and restart to change it. Bible translation is a separate setting: enter a Bible Gateway code such as CSB, CUVS, RVR1960 or LSG. Translation availability and font coverage vary.

![Setup steps](assets/desktop-setup.svg)

## Install

Download the matching desktop asset from [Releases](https://github.com/dgcarr/bibleSmartDisplay/releases). Desktop downloads are separate from the older command-line ZIP. If a release has only the ZIP, use a release with desktop assets or build from source below.

| Computer | Download | Install |
| --- | --- | --- |
| Windows 10/11, x64 | `bibleSmartDisplay-windows-x64-setup.exe` | Run the installer; installation is per user. |
| Mac, Intel | `bibleSmartDisplay-macos-x64.dmg` | Drag the app into Applications, then open it. |
| Mac, Apple Silicon | `bibleSmartDisplay-macos-arm64.dmg` | Drag the app into Applications, then open it. |
| Linux, x64 | `bibleSmartDisplay-linux-x64.tar.gz` | Extract; open the extracted `BibleSmartDisplay` executable to launch the graphical installer. |
| Raspberry Pi / Linux, ARM64 | `bibleSmartDisplay-linux-arm64.tar.gz` | Same graphical installer; requires a 64-bit desktop OS. |

If your file manager does not launch executables, run `./BibleSmartDisplay --install` from the extracted folder. The Linux bundle also contains `Install.desktop`; desktops that allow trusted local launchers can open it directly. Some file managers require marking the launcher executable/trusted first. The terminal fallback is `./BibleSmartDisplay --install`. No Python installation is required for any packaged download.

Linux targets Debian 12+, Ubuntu 24.04+ and 64-bit Raspberry Pi OS Bookworm+. A graphical desktop, systemd user services and standard Qt/X11/Wayland runtime libraries are required. Minimal distributions may need `libegl1`, `libopengl0`, `libxcb-cursor0`, `libxkbcommon-x11-0` and a TrueType font installed. macOS targets version 13+. Not for iPhone/iPad, Windows ARM or 32-bit Raspberry Pi OS.

The initial builds are not publisher-signed or Apple-notarized. Platform security may warn or block launch; use your organization's normal trust policy. Checksums detect download corruption, but do not replace publisher signing. Hardware testing is currently Ubuntu with UsbPCMonitor 3.5-inch only; the other model/platform combinations remain experimental or hardware-untested.

## Debian packages

For Debian 12+, Ubuntu 24.04+ and 64-bit Raspberry Pi OS Bookworm+, the `.deb` is the simplest installation. Choose `amd64` for Intel/AMD PCs or `arm64` for 64-bit Raspberry Pi/ARM systems. Open the downloaded file with your graphical package installer. If no installer is associated with `.deb` files, use a terminal in the download directory:

```sh
sudo apt install ./biblesmartdisplay_0.4.2_amd64.deb
# Raspberry Pi / ARM64 instead:
sudo apt install ./biblesmartdisplay_0.4.2_arm64.deb
```

Launch **Bible Smart Display** from the applications menu, or run `biblesmartdisplay`. The package installs under `/opt/biblesmartdisplay` and includes Python and Qt. It installs for all users, but each user's preferences, scheduling and startup choices remain separate. Installation does not automatically enable startup or schedule tasks.

If replacing a portable installation, first remove its automatic setup and quit it, then open the packaged app and save your scheduling choices again. Existing default preferences remain available; old shortcuts to the portable copy should be removed manually.

Before removing the package, choose **Remove automatic setup** in Settings and quit, or run `biblesmartdisplay --remove-setup` as your normal desktop user. Then remove it through your software manager or:

```sh
sudo apt remove biblesmartdisplay
```

The package does not modify other users' sessions or delete personal settings, caches, or previously configured USB access rules. Each user who enabled scheduling should remove their automatic setup before uninstalling. Upgrades preserve settings and keep the executable path stable. No administrator prompt is needed for everyday use; USB permission repair may still require authentication.

## Set up your screen

1. Connect a USB **data** cable and close the vendor's display software.
2. Select the interface language, exact screen model and USB port. Experimental labels mean the project has not physically tested that hardware. Do not choose another model just to bypass a handshake error.
3. Choose text colour, brightness, Bible translation and optionally a font. Use a font covering your chosen language; the renderer does not yet provide full complex-script shaping or automatic CJK font fallback.
4. Click **Test screen**. A successful transfer is required to continue. Check the physical screen too: an acknowledgement alone cannot establish that every untested model renders correctly.
5. Choose the daily update time (default **06:00**), enable daily updates and optionally start the tray at login. Finish saves preferences and registers the OS jobs.
6. Click **Update now** to fetch the first verse. Subsequent network failures can restore the saved verse, provided its translation matches.

If Linux reports permission denied, **Fix Linux USB access** opens a graphical administrator-authentication prompt. It grants access to the selected port; when USB VID/PID/serial identity is available it also installs a device-specific `uaccess` rule for future connections. Without a stable identity, access is temporary. The app never requests a password itself. If `pkexec` or `setfacl` is unavailable, the error provides a terminal fallback; install the distro's `policykit-1`/`polkit` and `acl` packages as appropriate.

Windows and macOS normally provide USB CDC serial support. Devices using other USB bridges may require a manufacturer driver: see [USB driver guidance](../README.md#usb-drivers). The app does not silently install third-party drivers.

## Everyday use

Open Settings from the tray/menu bar to change the screen, colour, brightness, language, translation, font or time. **Save settings** persists changes; **Update now** sends the chosen settings to the screen. Preview renders an offline sample. On desktops without a tray, the settings window remains available as a normal application.

The tray provides Update now, Restore saved verse, Pause/resume scheduled updates, Open logs and Quit. Closing the settings window hides it when a tray exists. **Quit stops reconnection monitoring but leaves OS scheduling enabled.** Use Pause or Remove automatic setup to stop scheduled updates.

The OS checks the saved daily schedule every minute and on login/startup. A missed update runs when the user's session is available after the configured time. There is no wake-from-sleep or logged-out service. A successful scheduled run is recorded once per local calendar day; reconnect restores cached content while the tray app is running. Failures retry after 30 and 120 seconds, then the next OS check can retry. A cached offline fallback counts as a successful display update for the day. Manual Update now always allows another fetch.

Windows uses per-user interactive Task Scheduler jobs; Linux uses a systemd user timer plus desktop autostart; macOS uses per-user LaunchAgents. Settings and job arguments support paths containing spaces. Only this app's named jobs are replaced or removed. Older cron jobs or legacy tasks are reported when detected, but detection is best-effort: inspect older installations to prevent duplicate updates.

A screen with a stable, unique USB serial identity can move between ports. Ambiguous identity or missing devices require reselection; the app never tries all screen protocols. Keep only one display controller active. Concurrent GUI/CLI/scheduled transfers share the existing data-directory lock.

## Remove or repair

Choose **Remove automatic setup** to remove the app's schedule and login startup. It keeps preferences, logs and the saved verse. `BibleSmartDisplay --remove-setup` does the same without the GUI. Then quit the app.

- Windows: uninstall through Installed apps; the uninstaller also removes the default user's app jobs.
- macOS: remove automatic setup before moving the app to Trash.
- Linux: remove automatic setup, then delete `~/.local/opt/bibleSmartDisplay`, any `bibleSmartDisplay.old` backup beside it, and `~/.local/share/applications/biblesmartdisplay.desktop`. If you enabled USB repair, an administrator can remove `/etc/udev/rules.d/70-biblesmartdisplay-<uid>.rules` and reload udev rules.

Data lives in the [same per-user data directory as the CLI](setup.md#saved-files). To reset completely, delete that directory after quitting. A custom `--data-dir` needs to be supplied again when removing its setup.

Settings errors, a blocked USB port, or a mismatched handshake appear as visible errors; technical details may remain in English. Use Open logs when reporting an issue. If the app is already running, open its existing tray icon instead of launching another copy.

## Build from source

```sh
python3 -m venv .venv
# Windows: .venv\Scripts\python.exe for the following commands
.venv/bin/python -m pip install -r requirements-desktop.txt
.venv/bin/python desktop_app.py
.venv/bin/python scripts/build_desktop.py
```

The desktop workflow builds natively for five OS/architecture combinations. Linux binaries are built inside Debian 12 for a compatible glibc baseline. The original CLI and its arguments remain available separately; they do not adopt desktop preferences automatically. `desktop_app.py --update` uses saved preferences, and `--scheduled` respects the saved schedule.
