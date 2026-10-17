[English](README.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md)

![Bible Smart Display](docs/assets/banner-v2.svg)

# Bible Smart Display

**让每日经文常伴你的书桌。**

适用于 **Turing Smart Screen 3.5 英寸或类似的 USB 智能屏幕**。

[下载 Windows 版](https://github.com/dgcarr/bibleSmartDisplay/releases/latest) · [构建状态](https://github.com/dgcarr/bibleSmartDisplay/actions/workflows/windows.yml) · [GPL v3](LICENSE)

**可选译本 · 浅蓝色文字 · 可调亮度 · 离线恢复**

本程序读取 [Bible League 的每日经文出处](https://www.bibleleague.org/verse-of-the-day/)，从 Bible Gateway 获取所选译本的经文（默认 **CSB**），再显示到屏幕上。字号会根据内容自动调整。

> [!IMPORTANT]
> **请先确认硬件兼容性。** 当前支持 **3.5 英寸、480 × 320、Revision A USB 串口协议**。外观相似并不代表协议相同；不支持其他尺寸、Revision B 或 HDMI 显示器。[硬件识别指南（英文）](docs/setup.md#compatible-displays)

## 选择安装方式

| 系统 | 安装方式 |
| :--- | :--- |
| Windows 10/11 x64 | 下载便携版，无需安装 Python |
| Linux / Raspberry Pi OS | 使用 Python 3.10 或更新版本运行源码 |
| macOS | 使用 Python 3.10 或更新版本运行源码 |

请准备好屏幕、**支持数据传输的 USB 线**和网络连接。运行前关闭厂商自带的屏幕软件。

## Windows：三步开始

1. 打开[最新发布页面](https://github.com/dgcarr/bibleSmartDisplay/releases/latest)，在 **Assets** 下下载 `bibleSmartDisplay-windows-x64.zip`，不要选择源码 ZIP。
2. 解压到自己的文件夹，例如 `Documents\bibleSmartDisplay`，然后连接屏幕的数据接口。
3. 双击 **`Run-display.cmd`**。程序更新一次屏幕后退出，控制台会保留运行信息。

<details>
<summary><strong>找不到屏幕？手动选择 COM 端口</strong></summary>

在解压目录打开 PowerShell：

```powershell
.\bibleSmartDisplay.exe --list-ports
.\bibleSmartDisplay.exe --port COM3
```

把 `COM3` 替换为实际端口。如果没有列出端口，请查看下方驱动说明。

</details>

<details>
<summary><strong>没有屏幕或网络也能预览</strong></summary>

```powershell
.\bibleSmartDisplay.exe --demo --preview-only
```

打开 `%LOCALAPPDATA%\bibleSmartDisplay\preview.png` 查看测试图片。

</details>

> [!NOTE]
> Windows 下载版是未签名的便携式控制台程序，并非图形化安装程序。已通过 Windows 自动构建和预览测试；Windows/macOS 实机 USB 测试仍待完成。已在 Ubuntu 上验证实机显示。

## Linux

先安装 Python 3.10+、Git、venv 支持和 DejaVu Sans 字体。Ubuntu/Debian/Raspberry Pi OS 对应软件包为 `python3`、`python3-venv`、`python3-pip`、`git` 和 `fonts-dejavu-core`。

```sh
git clone https://github.com/dgcarr/bibleSmartDisplay.git
cd bibleSmartDisplay
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python outputs/daily-verse/verse_display.py
```

自动识别失败时，添加 `--list-ports` 查看端口，再用 `--port /dev/ttyACM0` 指定实际端口。权限问题请参阅 [Linux 串口访问说明（英文）](docs/setup.md#linux-including-raspberry-pi-os)。

## macOS

安装 [Python 3.10+](https://www.python.org/downloads/macos/)。在本仓库点击 **Code → Download ZIP**，解压后在包含 `requirements.txt` 的目录打开终端：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python outputs/daily-verse/verse_display.py
```

自动识别失败时先用 `--list-ports`，再添加 `--port /dev/cu.usbmodem1234`，并替换为实际端口。[macOS 帮助（英文）](docs/setup.md#macos)

## USB 驱动

**如果屏幕已显示为可用串口，请先尝试运行，无需急于安装驱动。**

| 设备 / 系统 | 官方资源 |
| :--- | :--- |
| Turing/TURZX 屏幕 | [厂商下载页](https://www.turzx.com/en/category/download/)，请选择对应型号 |
| Windows USB CDC 设备 | [微软内置 USB 串口驱动说明](https://learn.microsoft.com/en-us/windows-hardware/drivers/usbcon/usb-driver-installation-based-on-compatible-ids)，兼容设备可自动安装 |
| Windows，已确认采用 CH340/CH341 | [WCH Windows 驱动](https://www.wch.cn/downloads/CH341SER_EXE.html) |
| macOS，受支持的 WCH 串口芯片 | [WCH macOS 驱动及安装说明](https://github.com/WCHSoftGroup/ch34xser_macos) |
| Linux | 兼容设备通常使用内核自带串口驱动 |

WCH 驱动**不是通用屏幕驱动**。Windows 中打开“设备管理器 → 端口 (COM 和 LPT)”。若有警告图标，在“属性 → 详细信息 → 硬件 ID”中确认型号，再选择对应驱动。[完整驱动说明（英文）](docs/setup.md#windows-usb-drivers)

## 选择圣经译本

使用 [Bible Gateway 译本代码](https://www.biblegateway.com/versions/)：

```powershell
.\bibleSmartDisplay.exe --translation NIV
.\bibleSmartDisplay.exe --translation KJV
```

Linux/macOS 示例：

```sh
.venv/bin/python outputs/daily-verse/verse_display.py --translation NIV
```

默认译本仍为 CSB。可以指定一个 Bible Gateway 文本译本代码，但该译本必须包含所请求的经文。不支持仅提供 PDF 或音频的版本。

**中文显示说明：** 中文 README 不代表中文经文排版已完成验证。显示中文时，需要用 `--font` 指定包含中文字形的字体；当前按空格换行，较长且无空格的中文段落可能无法排版。复杂文字和无空格长段落仍需进一步测试。

参数不会自动保存。要持续使用某个译本，请将参数加入计划任务，或修改 `Run-display.cmd` 中调用程序的那一行。`--cached` 恢复最近保存的译本；同时添加 `--translation NIV` 可要求缓存必须为 NIV。获取失败不会悄悄改用其他译本，缓存始终只保留一段经文。

## 调整外观

默认为**浅蓝色文字、50% 亮度**：

```powershell
.\bibleSmartDisplay.exe --color "#ADD8E6" --brightness 50
```

Linux/macOS 将相同参数放在 `.venv/bin/python outputs/daily-verse/verse_display.py` 后面。

| 参数 | 用途 |
| :--- | :--- |
| `--brightness 25` | 设置背光，范围 0–100 |
| `--color "#F5F5DC"` | 改为米色文字 |
| `--cached` | 离线恢复最近保存的经文 |
| `--preview-only` | 只生成预览，不向屏幕发送图片 |
| `--list-ports` | 列出串口设备 |

参数仅对本次运行生效。需要每日使用时，请加入计划任务。[全部设置和文件位置（英文）](docs/setup.md#commands-and-settings)

## 每日自动更新

程序每次只更新一次；自动每日更新需要设置系统计划任务：

[Windows 任务计划程序（英文）](docs/setup.md#windows-task-scheduler) · [Linux cron（英文）](docs/setup.md#linux-cron) · [macOS launchd（英文）](docs/setup.md#macos-launchd)

电脑必须运行且屏幕已连接。首次获取需要网络；之后网络故障时可使用同译本的已保存经文。缓存会覆盖，不会不断积累。

## 遇到问题？

| 问题 | 先检查 |
| :--- | :--- |
| 找不到屏幕 | 数据线、`--list-ports` 和 USB 驱动 |
| 端口被占用 | 关闭厂商软件及其他运行实例 |
| 握手错误或画面错乱 | 确认型号、尺寸和协议兼容性 |
| 没有缓存经文 | 联网运行一次，不加 `--cached` |
| 窗口一闪而过 | 使用 `Run-display.cmd` 或在终端运行 |

[完整排错指南（英文）](docs/setup.md#troubleshooting) · [提交问题](https://github.com/dgcarr/bibleSmartDisplay/issues) · [自行构建（英文）](docs/setup.md#build-the-windows-executable-yourself)

提交问题时请提供操作系统、屏幕型号、硬件 ID 和错误信息。

---

### 致谢与许可

本项目参考 Matthieu Houdebine 及贡献者维护的 [turing-smart-screen-python](https://github.com/mathoudebine/turing-smart-screen-python) 协议实现，与屏幕厂商无隶属关系。软件采用 **[GPL v3](LICENSE)**；上游文件保留其原有版权声明。

每日出处来自 [Bible League](https://www.bibleleague.org/verse-of-the-day/)，经文来自 [Bible Gateway](https://www.biblegateway.com/)。默认 CSB 译本：Christian Standard Bible © 2017 Holman Bible Publishers。其他译本的版权归相应权利人所有；经文不受本软件许可证覆盖。
