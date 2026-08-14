---
name: android-computer-use
description: Inspect and operate a user-authorized physical Android phone or tablet from this Linux host with ADB and scrcpy. Use for Android screenshots, UI inspection, taps, swipes, text entry, key events, app launching, USB or wireless-debugging connections, device mirroring, and troubleshooting an Android device connection. Do not use for emulators unless the user explicitly includes them.
---

# Android Computer Use

Use the installed implementation at `${HOME}/android-computer-use`. Do not copy or reimplement its commands inside a task workspace.

Before the first Android-device action in every task, read `${HOME}/android-computer-use/AGENTS.md` completely. It is the authoritative guide for setup, safety, device selection, screenshots, and verification.

Start with:

```bash
"$HOME/android-computer-use/android-cuctl" doctor
"$HOME/android-computer-use/android-cuctl" devices
```

Use `"$HOME/android-computer-use/android-cuctl" --help` for the supported command surface. Prefer this constrained command over raw `adb shell`.

For coordinate-based actions, take a fresh screenshot, inspect it with the available image-viewing tool, act, then take another screenshot to verify the resulting state. Use `ui-dump` when visible labels or bounds help, but do not assume every UI exposes an accessibility tree.

Never bypass a lock screen, biometric prompt, secure-window restriction, or Android permission boundary. Obtain explicit user authorization immediately before consequential actions such as sending messages, placing calls, making purchases, changing accounts or security settings, entering a PIN/password/OTP, installing or removing apps, clearing data, or rebooting a device.
