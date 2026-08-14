# Mobile Computer Use

Constrained, agent-friendly bridges for inspecting and operating user-authorized physical Android and iOS devices from Linux.

The repository contains two Agent Skills and their home-directory controllers:

- `android-computer-use`: ADB and scrcpy device discovery, screenshots, UI dumps, taps, swipes, text, key events, app launch, and USB/Wi-Fi debugging.
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

iOS requires Python 3, `pymobiledevice3`, Node.js, Appium with the XCUITest driver, a trusted physical device, and a WebDriverAgent IPA signed for that device. iOS signing assets are intentionally not included. Configure the signed IPA and runner bundle ID with `IOS_CUCTL_WDA_IPA` and `IOS_CUCTL_WDA_BUNDLE_ID`.

Run the read-only checks after installation:

```bash
"$HOME/android-computer-use/android-cuctl" doctor
"$HOME/android-computer-use/android-cuctl" devices

"$HOME/ios-computer-use/ios-cuctl" doctor
"$HOME/ios-computer-use/ios-cuctl" devices
```

## Operation guides

The detailed command, connection, verification, recovery, and safety instructions live beside each controller:

- [Android operations](bridges/android/AGENTS.md)
- [iOS operations](bridges/ios/AGENTS.md)

The Agent Skills instruct the agent to read the corresponding installed guide completely before the first device action in each task.

## Repository safety

This repository contains source code and documentation only. It excludes device captures, UI dumps, UDIDs, pairing records, Appium state, signed IPA files, provisioning profiles, certificates, private keys, tokens, and bundled third-party binaries. Do not commit those artifacts.
