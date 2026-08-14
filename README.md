# Mobile Computer Use

Constrained, agent-friendly bridges for inspecting and operating user-authorized physical Android and iOS devices from Linux.

The repository contains two Agent Skills and their home-directory controllers:

- `android-computer-use`: ADB and scrcpy device discovery, mDNS auto-connect for a unique paired target, screenshots, UI dumps, taps, swipes, text, key events, app launch, and USB/Wi-Fi debugging.
- `ios-computer-use`: pymobiledevice3, RemoteXPC, CoreDevice, Appium, and WebDriverAgent screenshots, accessibility inspection, coordinate conversion, input, app activation, and USB/Wi-Fi setup.

Both skills require explicit user authorization around lock screens, credentials, sensitive permissions, purchases, messages, account changes, app installation, and other consequential actions.

## Install

Clone the repository and install the bridge scripts plus skills for your agent:

```bash
git clone https://github.com/avrilmaomao/mobile-computer-use.git
cd mobile-computer-use

# Claude Code personal skills
./install.sh --claude

# Codex personal skills
./install.sh --codex

# Shared ~/.agents skill catalog used by compatible agent hosts
./install.sh --agents

# Install all three skill targets
./install.sh --all
```

The controllers are installed under:

```text
~/android-computer-use/android-cuctl
~/ios-computer-use/ios-cuctl
```

Existing controller and skill files are backed up before replacement. Captures, runtime binaries, state, signing files, and private configuration are never copied by the installer.

For Claude Code discovery and verification, read [docs/CLAUDE_CODE.md](docs/CLAUDE_CODE.md).

## Host prerequisites

Android requires `adb`; `scrcpy` is required only for live mirroring. The controller can use system commands from `PATH` or an official portable runtime placed under `~/android-computer-use/runtime/`.

iOS requires Python 3, `pymobiledevice3`, Node.js, Appium with the XCUITest driver, a trusted physical device, and a WebDriverAgent IPA signed for that device. iOS signing assets are intentionally not included. Configure the signed IPA and runner bundle ID with `IOS_CUCTL_WDA_IPA` and `IOS_CUCTL_WDA_BUNDLE_ID`, either in the environment or in the non-executable `$HOME/.config/ios-computer-use/env` file. After initial USB pairing, either the optional system service or a foreground `wifi-tunnel-start` provides a Wi-Fi RemoteXPC path that ordinary bridge commands reuse automatically.

On a dedicated Linux host, the bundled `ios-computer-use-tunneld@.service` can be installed once as a constrained system service. It runs as the selected user with only `CAP_NET_ADMIN`, starts at boot, and avoids a new sudo/polkit dialog for each wireless session. See the iOS operations guide for the one-time installation commands.

Run the read-only checks after installation:

```bash
"$HOME/android-computer-use/android-cuctl" doctor
"$HOME/android-computer-use/android-cuctl" devices

"$HOME/ios-computer-use/ios-cuctl" doctor
"$HOME/ios-computer-use/ios-cuctl" devices
```

## Daily fast path

Setup and troubleshooting use `doctor`; routine operation should probe the smallest stable state first:

| Platform | Routine probe | Reuse rule | Main wireless capabilities |
|---|---|---|---|
| Android | `android-cuctl devices` | If exactly one `HOST:PORT` target is already `device`, use it directly; mDNS discovery is unnecessary. | Screenshot, UI dump, tap, swipe, ASCII text, key events, app launch, and scrcpy. |
| iOS | `ios-cuctl tunnel-status` | If `ready` is true with exactly one tunnel, reuse it; do not start another tunnel or WDA merely for screenshots, app launch, or hardware buttons. | CoreDevice screenshot, app list/activation, and hardware buttons without the Automation indicator. |

On iOS 26 and earlier, touch, text, and accessibility inspection require Appium/WDA; USB plus WDA is the most reliable path unless a compatible preinstalled WDA build has been prepared for the persistent tunnel. CoreDevice remote touch is available on iOS 27 and later. A black iOS capture can mean the display is asleep: issue a reversible `press home`, take a new screenshot, and ask the user to unlock if interaction is needed. Never try to bypass the lock screen.

## Operation guides

The detailed command, connection, verification, recovery, and safety instructions live beside each controller:

- [Android operations](bridges/android/AGENTS.md)
- [iOS operations](bridges/ios/AGENTS.md)

The Agent Skills instruct the agent to read the corresponding installed guide completely before the first device action in each task.

## Repository safety

This repository contains source code and documentation only. It excludes device captures, UI dumps, UDIDs, pairing records, Appium state, signed IPA files, provisioning profiles, certificates, private keys, tokens, and bundled third-party binaries. Do not commit those artifacts.
