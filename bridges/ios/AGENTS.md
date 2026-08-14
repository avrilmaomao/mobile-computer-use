# iOS computer use on this Linux host

Use `"$HOME/ios-computer-use/ios-cuctl"` as the stable entry point for a user-authorized physical iPhone or iPad. Do not copy signing assets or reimplement device commands in a task workspace.

## Host configuration

The bridge is portable and reads these optional environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `IOS_CUCTL_HOME` | `$HOME/ios-computer-use` | Bridge directory containing `wda-runner` |
| `IOS_CUCTL_SHARE_DIR` | `$HOME/.local/share/ios-computer-use` | Tools and signed WDA artifacts |
| `IOS_CUCTL_STATE_DIR` | `$HOME/.local/state/ios-computer-use` | Session files and logs |
| `IOS_CUCTL_PMD3` | `pymobiledevice3` from `PATH` | pymobiledevice3 executable |
| `IOS_CUCTL_WDA_PYTHON` | Python interpreter from the pymobiledevice3 launcher | Interpreter used by `wda-runner` |
| `IOS_CUCTL_APPIUM_BIN` | `appium` from `PATH` | Appium executable |
| `IOS_CUCTL_NODE_BIN_DIR` | directory containing `node` | Node.js binary directory |
| `IOS_CUCTL_WDA_IPA` | `$IOS_CUCTL_SHARE_DIR/artifacts/WebDriverAgentRunner.ipa` | Signed WDA IPA |
| `IOS_CUCTL_WDA_BUNDLE_ID` | `com.facebook.WebDriverAgentRunner.xctrunner` | Actual signed WDA runner bundle ID |
| `IOS_CUCTL_TRANSPORT` | `auto` | Force `usb` or `wifi`; `auto` prefers a running bridge-managed Wi-Fi tunnel |
| `IOS_CUCTL_RSD_ADDRESS` / `IOS_CUCTL_RSD_PORT` | unset | Reuse a manually created RSD tunnel |
| `IOS_CUCTL_SYSTEM_TUNNEL_PORT` | `49151` | Registry port of the optional persistent system tunneld |

The bridge also detects the tested portable Node/Appium layout under `$IOS_CUCTL_SHARE_DIR/tools/`. Keep machine-specific values in the shell environment; never commit them with signing assets.

## Start every task

Run:

```bash
"$HOME/ios-computer-use/ios-cuctl" doctor
"$HOME/ios-computer-use/ios-cuctl" devices
```

If more than one trusted USB device is present, pass `--udid` before the subcommand. Never guess which device the user intended.

For the simplest no-banner path, keep the RemoteXPC tunnel running and use `screenshot`. CoreDevice screen capture does not start XCTest, so iOS does not show the "Automation Running" indicator.

CoreDevice touch/keyboard remote control requires iOS 27 or later. On iOS 26 and earlier, `tap-image`, `swipe-image`, `type`, element commands, and logical-coordinate commands automatically start Appium/WDA on demand. Hardware `press` uses CoreDevice Indigo HID without WDA on all supported versions. While WDA is active, iOS shows its system-level automation indicator until `stop` or `wda-stop` is run. This version gate was verified against the device-side CoreDevice error 9021 on iOS 26.6.

Start the local Appium/WDA session only when accessibility hierarchy or element-based interaction is needed:

```bash
"$HOME/ios-computer-use/ios-cuctl" tunnel-status
"$HOME/ios-computer-use/ios-cuctl" tunnel-start
"$HOME/ios-computer-use/ios-cuctl" wda-status
"$HOME/ios-computer-use/ios-cuctl" start
"$HOME/ios-computer-use/ios-cuctl" status
```

On iOS 18 and later, `tunnel-start` is required on Linux. It synchronizes the registry port into the user-side Appium Strongbox before requesting privilege, then stays in the foreground so the RemoteXPC tunnel remains alive. Reuse a running tunnel; do not start one per action. The privilege prompt is an operating-system boundary and cannot be bypassed.

On Linux, `start` also starts or reuses `"$HOME/ios-computer-use/wda-runner"`. This helper keeps pymobiledevice3's XCTest manager connection alive, while Appium attaches through `webDriverAgentUrl`. While it is active, iOS shows its system-level "Automation Running" indicator; this cannot be hidden. Use `wda-stop` to remove the indicator and return to CoreDevice/HID mode. CoreDevice screenshots do not start XCTest and do not show the indicator.

Do not restart Appium or WDA between ordinary screenshots, taps, swipes, text entry, or app changes. Stop only when the user asks, recovery requires it, or the task is complete and no later action is expected.

## Safe interaction loop

For UI actions:

1. Capture a fresh screenshot.
2. Inspect it with the available image-viewing tool.
3. Use `tap-image` or `swipe-image`; these automatically choose CoreDevice HID on iOS 27+ or start WDA on older versions, convert coordinates, and save an after-action screenshot.
4. Prefer `source` plus `tap-element` when stable accessibility identifiers or hierarchy inspection are needed; these start WDA on demand.
5. Inspect the after-action screenshot and report the observed result, not just command success.

Examples:

```bash
"$HOME/ios-computer-use/ios-cuctl" screenshot /tmp/iphone-before.png
"$HOME/ios-computer-use/ios-cuctl" source --output /tmp/iphone-source.xml
"$HOME/ios-computer-use/ios-cuctl" tap-element "Positions" --using "accessibility id"
"$HOME/ios-computer-use/ios-cuctl" tap-image 590 2200 --image /tmp/iphone-before.png
"$HOME/ios-computer-use/ios-cuctl" swipe-image 590 1900 590 700 --image /tmp/iphone-before.png
```

`tap` and `swipe` accept WDA logical-point coordinates and require an Appium session. `tap-image` and `swipe-image` accept coordinates from the specified PNG and automatically choose WDA or CoreDevice HID. If `--image` is omitted they capture a fresh before-image automatically. Never hand-calculate Retina or HID scaling when the bridge can do it.

## Setup and recovery

Initial setup requires an unlocked USB connection and the user's Trust approval. Then run, as needed:

```bash
"$HOME/ios-computer-use/ios-cuctl" pair
"$HOME/ios-computer-use/ios-cuctl" wireless-on
"$HOME/ios-computer-use/ios-cuctl" mount
```

`wireless-on` enables lockdownd Wi-Fi connections and bootstraps RemotePairing over the already-trusted USB channel. Later wireless use requires the host and phone on the same LAN. Keep USB available for first setup, signing/profile recovery, and the most reliable long sessions.

To prove and use a fully wireless RemoteXPC path, keep this command running in a dedicated terminal:

```bash
"$HOME/ios-computer-use/ios-cuctl" wifi-tunnel-start
```

Linux shows one administrator authorization prompt because the tunnel creates a TUN interface. Once the command prints that the Wi-Fi tunnel is ready, ordinary `screenshot`, `press`, `start`, `source`, `tap-image`, `swipe-image`, and element commands automatically prefer that Wi-Fi RSD connection. Check it from another terminal with `wifi-tunnel-status`. Stop it with `Ctrl+C`; the bridge removes its transient state file. If USB is already unplugged, pass the known `--udid` before the subcommand and `--platform-version` after it when WDA/Appium input will be used.

### Avoid repeated administrator prompts

WDA/XCTest needs a kernel-routable TUN interface because the iPhone opens an inbound TCP connection back to the host. A root-free userspace tunnel can handle screenshots and other host-initiated services, but it cannot provide this WDA callback path. Do not replace the prompt with broad passwordless sudo or a permissive polkit rule.

For a dedicated Linux host, install the bundled systemd template once. The service runs as the selected desktop user and receives only `CAP_NET_ADMIN`; it listens on loopback port `49151`, monitors USB and Wi-Fi devices, and starts at boot:

```bash
sudo install -m 0644 \
  "$HOME/ios-computer-use/ios-computer-use-tunneld@.service" \
  /etc/systemd/system/ios-computer-use-tunneld@.service
sudo systemctl daemon-reload
sudo systemctl enable --now "ios-computer-use-tunneld@$(id -un).service"
```

These are the only administrator-authorized installation steps. Afterward, agents should reuse the service without `sudo` or `wifi-tunnel-start`:

```bash
systemctl status "ios-computer-use-tunneld@$(id -un).service" --no-pager
"$HOME/ios-computer-use/ios-cuctl" tunnel-status
```

The bridge checks this registry before its older per-session registry and prefers a registry containing an active device tunnel. Granting `CAP_NET_ADMIN` lets this service manage host TUN interfaces and routes; it is narrower than root but remains a host networking privilege. If the user home is not `/home/<user>` or `pymobiledevice3` is installed outside the template's `PATH`, copy the template and adjust `Environment` and `ReadWritePaths` before installing it.

CoreDevice screenshots and hardware `press` can operate while the display is locked. WDA/Appium accessibility, touch, and text input require the device to be unlocked; if the phone locks during wireless WDA startup, iOS may terminate the XCTest connection. Never attempt to bypass the lock screen—ask the user to unlock and retry.

For a tunnel started outside the bridge, set `IOS_CUCTL_RSD_ADDRESS`, `IOS_CUCTL_RSD_PORT`, `IOS_CUCTL_WIFI_UDID`, and optionally `IOS_CUCTL_WIFI_PLATFORM_VERSION`. Use `IOS_CUCTL_TRANSPORT=usb` to force the original USB tunnel while a Wi-Fi tunnel is running.

Provide a WDA package signed for the target device and set:

```text
export IOS_CUCTL_WDA_IPA="$HOME/.local/share/ios-computer-use/artifacts/WebDriverAgentRunner.ipa"
export IOS_CUCTL_WDA_BUNDLE_ID="your.signed.WebDriverAgentRunner.xctrunner"
```

Install it only with the user's explicit authorization:

```bash
"$HOME/ios-computer-use/ios-cuctl" install-wda
```

Keep signing materials outside the repository, preferably under `$HOME/.local/share/ios-computer-use/signing` with user-only permissions. Treat every private key as secret: never print it, copy it into a workspace, attach it to output, or upload it. Certificates, provisioning profiles, device registration, App IDs, app installation/removal, and Developer Mode changes are consequential actions and require explicit user authorization.

Common failures:

- `DeviceLocked`: ask the user to unlock the device and keep the screen on, then retry `mount` or `start`. Never attempt to discover or enter a passcode.
- RemoteXPC registry missing: run `tunnel-status`; if it is not ready, run `tunnel-start`, approve the privilege prompt, and keep that process running. `start` automatically repairs the root/user Strongbox port split when the registry is reachable.
- No device: verify USB enumeration and `usbmuxd`, then ask the user to reconnect and approve Trust if needed.
- Developer image missing: run `mount` while unlocked; iOS 17+ uses a personalized DeveloperDiskImage.
- WDA missing or untrusted: confirm explicit authorization, reinstall with `install-wda`, and ask the user to accept any on-device developer trust prompt.
- Stale session: run `stop`, then `start`. Use `server-stop` only when the local Appium server itself must be restarted.

## Safety boundaries

Never bypass a lock screen, biometric prompt, secure-input restriction, developer trust warning, iOS permission prompt, or account boundary.

Obtain explicit user authorization immediately before consequential actions such as sending messages, placing calls, making purchases or trades, changing accounts or security settings, entering a PIN/password/OTP, installing or removing apps or profiles, changing Developer Mode, trusting a developer identity, or rebooting the device.

System screen recording may be operated through Control Center when the user asks and authorizes it. Treat recordings as user data and confirm where the resulting file should be retained or exported.
