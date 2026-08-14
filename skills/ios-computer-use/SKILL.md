---
name: ios-computer-use
description: Inspect and operate a user-authorized physical iPhone or iPad from this Linux host using pymobiledevice3, Appium, WebDriverAgent, RemoteXPC, USB, or Wi-Fi pairing. Use for iOS screenshots, accessibility inspection, taps, swipes, text entry, hardware buttons, app activation, WDA sessions, developer-image mounting, signed WDA installation, USB or wireless connections, and physical-device troubleshooting. Do not use for simulators unless the user explicitly includes them.
---

# iOS Computer Use

Use the installed implementation at `${HOME}/ios-computer-use`. Do not copy or reimplement its commands inside a task workspace.

Before the first iOS-device action in every task, read `${HOME}/ios-computer-use/AGENTS.md` completely. It is the authoritative guide for setup, safety, persistent WDA sessions, coordinate conversion, screenshots, and verification.

For an already configured wireless device, start with the lightweight persistent-service probe:

```bash
"$HOME/ios-computer-use/ios-cuctl" tunnel-status
"$HOME/ios-computer-use/ios-cuctl" status
```

If `tunnel-status` reports `ready: true` with exactly one tunnel, reuse it. Do not run raw discovery, start another tunnel, or start WDA for screenshots, app listing/activation, or hardware buttons. Use `doctor` and `devices` for first-time setup, USB work, or troubleshooting.

Use `"$HOME/ios-computer-use/ios-cuctl" --help` for the supported command surface. Prefer this constrained bridge over raw `pymobiledevice3`, Appium HTTP calls, or hand-calculated Retina coordinate conversion.

Take a fresh screenshot before input. If it is black, use the reversible `press home` action and capture again; if a lock screen is visible, ask the user to unlock. On iOS 27+, `tap-image`, `swipe-image`, and typing can use CoreDevice directly. On iOS 26 and earlier, touch, text, source, and element commands require Appium/WDA; prefer USB plus WDA unless the persistent tunnel has a compatible preinstalled WDA build. After WDA is available, reuse one session for repeated UI actions. Use `source` and `tap-element` when stable accessibility data is available.

For fully wireless operation, prefer the optional persistent system tunneld described in `AGENTS.md`; it needs one administrator-approved installation and avoids repeated authorization dialogs. Otherwise run `"$HOME/ios-computer-use/ios-cuctl" wifi-tunnel-start` in a persistent terminal after initial USB pairing. Once a tunnel reports ready, ordinary bridge commands automatically prefer the Wi-Fi RSD connection. Verify with `tunnel-status` and an actual screenshot or reversible hardware-button action.

Never bypass a lock screen, biometric prompt, secure-input restriction, developer trust warning, or iOS permission boundary. Obtain explicit user authorization immediately before consequential actions such as sending messages, placing calls, making purchases or trades, changing accounts or security settings, entering a PIN/password/OTP, installing or removing apps or profiles, changing Developer Mode, trusting an identity, or rebooting the device.
