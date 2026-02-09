# Worklist Monitor

A cross-platform application that monitors a PACS radiology worklist via webcam and sends Telegram alerts when STAT study counts exceed a threshold.

## Features

* 📷 Captures images from USB webcam (Logitech C920 or similar)
* 🔍 Uses OCR to read STAT counts from worklist sidebar
* 📱 Sends Telegram notifications when threshold exceeded
* 🔒 Runs entirely locally (no PHI leaves the machine)
* ⏰ Configurable check interval (default: 2 minutes)
* 🖥️ Cross-platform GUI with setup wizard and system tray
* 🔔 Desktop notifications in addition to Telegram alerts

## Monitored Worklists

* **Unread CT Neuro** — STAT count
* **Unread MR Neuro All** — STAT count

Alert triggers when combined STAT count > threshold (default: 5).

## Downloads

Latest version: **v0.1.5**

| Platform | Download |
|----------|----------|
| Windows | [worklist-monitor-windows-amd64.exe](https://github.com/jwprescott-moltbot/worklist-monitor/releases/download/v0.1.5/worklist-monitor-windows-amd64.exe) |
| macOS (Apple Silicon) | [worklist-monitor-macos-arm64](https://github.com/jwprescott-moltbot/worklist-monitor/releases/download/v0.1.5/worklist-monitor-macos-arm64) |
| Linux | [worklist-monitor-linux-amd64](https://github.com/jwprescott-moltbot/worklist-monitor/releases/download/v0.1.5/worklist-monitor-linux-amd64) |

## Source Code

GitHub: [jwprescott-moltbot/worklist-monitor](https://github.com/jwprescott-moltbot/worklist-monitor)
