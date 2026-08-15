---
name: android-computer-use
description: Inspect and operate a user-authorized physical Android phone or tablet from this Linux host with ADB and scrcpy. Use for Android screenshots, UI inspection, taps, swipes, text entry, key events, app launching, USB or wireless-debugging connections, device mirroring, and troubleshooting an Android device connection. Do not use for emulators unless the user explicitly includes them.
---

# Android Computer Use

Use the installed implementation at `${HOME}/android-computer-use`. Do not copy or reimplement its commands inside a task workspace.

Before the first Android-device action in every task, read `${HOME}/android-computer-use/AGENTS.md` completely. It is the authoritative guide for setup, safety, device selection, screenshots, and verification.

For an already configured device, start with the lightweight probe:

```bash
"$HOME/android-computer-use/android-cuctl" devices
```

Run `doctor` only for first-time setup or connection/tool troubleshooting. If `devices` shows exactly one wireless `HOST:PORT` target in `device` state, reuse it immediately; do not wait for mDNS or run `discover`/`connect-auto`.

For a longer control or recording task, prefer the unified session preflight. It reuses or uniquely reconnects the paired target, takes baseline and ready screenshots, optionally keeps Android awake through scrcpy, and inhibits host sleep without sudo:

```bash
"$HOME/mobile-cuctl/mobile-cuctl" start android --keep-awake
"$HOME/mobile-cuctl/mobile-cuctl" stop android
```

Use `"$HOME/android-computer-use/android-cuctl" --help` for the supported command surface. Prefer this constrained command over raw `adb shell`.

For wireless debugging with no online target, use `discover` to inspect mDNS advertisements and `connect-auto` only when exactly one already-paired connect target is present. mDNS advertisements may disappear while an existing ADB connection remains fully usable. First-time pairing still requires the phone's displayed pairing address and one-time code.

For coordinate-based actions, take a fresh screenshot, inspect it with the available image-viewing tool, act, then take another screenshot to verify the resulting state. Use `ui-dump` when visible labels or bounds help, but do not assume every UI exposes an accessibility tree.

Take the first fresh screenshot before input. If it shows a lock screen, ask the user to unlock. Some vendor keyboards keep `text-ascii` in an IME composing buffer; inspect the after-screenshot and send `key KEYCODE_ENTER` only when committing that text is the expected reversible action.

Use `android-cuctl record-start`, `record-status`, and `record-stop` for background scrcpy recording, or the equivalent unified `mobile-cuctl record android ...` commands. Always finalize a recording with `record-stop`.

Preview and clean generated files with the unified bridge. `--apply` is required to delete; defaults are 7 days for captures/UI dumps and 14 days for bridge-managed recordings:

```bash
"$HOME/mobile-cuctl/mobile-cuctl" cleanup --platform android
"$HOME/mobile-cuctl/mobile-cuctl" cleanup --platform android --apply
```

Never bypass a lock screen, biometric prompt, secure-window restriction, or Android permission boundary. Obtain explicit user authorization immediately before consequential actions such as sending messages, placing calls, making purchases, changing accounts or security settings, entering a PIN/password/OTP, installing or removing apps, clearing data, or rebooting a device.
