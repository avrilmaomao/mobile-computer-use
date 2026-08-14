---
name: ios-computer-use
description: Inspect and operate a user-authorized physical iPhone or iPad from this Linux host using pymobiledevice3, Appium, WebDriverAgent, RemoteXPC, USB, or Wi-Fi pairing. Use for iOS screenshots, accessibility inspection, taps, swipes, text entry, hardware buttons, app activation, WDA sessions, developer-image mounting, signed WDA installation, USB or wireless connections, and physical-device troubleshooting. Do not use for simulators unless the user explicitly includes them.
---

# iOS Computer Use

Use the installed implementation at `${HOME}/ios-computer-use`. Do not copy or reimplement its commands inside a task workspace.

Before the first iOS-device action in every task, read `${HOME}/ios-computer-use/AGENTS.md` completely. It is the authoritative guide for setup, safety, persistent WDA sessions, coordinate conversion, screenshots, and verification.

Start with:

```bash
"$HOME/ios-computer-use/ios-cuctl" doctor
"$HOME/ios-computer-use/ios-cuctl" devices
```

Use `"$HOME/ios-computer-use/ios-cuctl" --help` for the supported command surface. Prefer this constrained bridge over raw `pymobiledevice3`, Appium HTTP calls, or hand-calculated Retina coordinate conversion.

Start or reuse one persistent session before repeated UI actions. For coordinate-based actions, take a fresh screenshot, inspect it with the available image-viewing tool, call `tap-image` or `swipe-image`, then inspect the automatically saved after-action screenshot. Use `source` and `tap-element` when stable accessibility data is available.

For fully wireless operation, run `"$HOME/ios-computer-use/ios-cuctl" wifi-tunnel-start` in a persistent terminal after initial USB pairing. Once it reports ready, ordinary bridge commands automatically prefer the Wi-Fi RSD connection. Verify with `wifi-tunnel-status` and an actual screenshot or reversible hardware-button action.

Never bypass a lock screen, biometric prompt, secure-input restriction, developer trust warning, or iOS permission boundary. Obtain explicit user authorization immediately before consequential actions such as sending messages, placing calls, making purchases or trades, changing accounts or security settings, entering a PIN/password/OTP, installing or removing apps or profiles, changing Developer Mode, trusting an identity, or rebooting the device.
