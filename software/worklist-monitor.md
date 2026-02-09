# Worklist Monitor

A cross-platform application that monitors a PACS radiology worklist via webcam and sends Telegram alerts when STAT study counts exceed a threshold.

## Features

- 📷 Captures images from USB webcam (Logitech C920 or similar)
- 🔍 Uses OCR to read STAT counts from worklist sidebar
- 📱 Sends Telegram notifications when threshold exceeded
- 🔒 Runs entirely locally — no PHI leaves the machine
- ⏰ Configurable check interval (default: 2 minutes)
- 🖥️ Cross-platform GUI with setup wizard and system tray
- 🔔 Desktop notifications in addition to Telegram alerts

## Monitored Worklists

- **Unread CT Neuro** — STAT count
- **Unread MR Neuro All** — STAT count

Alert triggers when combined STAT count exceeds threshold (default: 5).

## Downloads

Download ready-to-run executables for your platform:

| Platform | Download |
|----------|----------|
| **Linux** (amd64) | [worklist-monitor-linux-amd64](https://github.com/jwprescott/worklist-monitor/releases/latest/download/worklist-monitor-linux-amd64) |
| **macOS** (Apple Silicon) | [worklist-monitor-macos-arm64](https://github.com/jwprescott/worklist-monitor/releases/latest/download/worklist-monitor-macos-arm64) |
| **Windows** (64-bit) | [worklist-monitor-windows-amd64.exe](https://github.com/jwprescott/worklist-monitor/releases/latest/download/worklist-monitor-windows-amd64.exe) |

[View all releases →](https://github.com/jwprescott/worklist-monitor/releases)

## Quick Start

1. Download the executable for your platform
2. Run the application — the Setup Wizard will guide you through:
   - Camera selection and preview
   - Telegram bot configuration
   - Alert threshold setting
   - Worklist region calibration
   - Test run verification
3. The app runs in the system tray with status indicators

## System Tray

After setup, the app runs in the background:

- 🟢 **Green** — Normal operation (below threshold)
- 🟡 **Yellow** — Warning (approaching threshold)
- 🔴 **Red** — Alert (above threshold)
- ⚫ **Gray** — Stopped/Error

**Controls:**
- Double-click to toggle monitoring
- Right-click for settings, wizard, and quit

## Privacy

- All processing happens locally
- Images processed in memory (not stored)
- Only alert counts sent to Telegram
- No PHI transmitted

## Source Code

[github.com/jwprescott/worklist-monitor](https://github.com/jwprescott/worklist-monitor)

## License

MIT
