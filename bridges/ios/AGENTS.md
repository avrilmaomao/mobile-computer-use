# iOS computer use on this Linux host

Use `"$HOME/ios-computer-use/ios-cuctl"` as the stable entry point for a user-authorized physical iPhone or iPad. Do not copy signing assets or reimplement device commands in a task workspace.

Use `"$HOME/mobile-cuctl/mobile-cuctl"` to prepare and stop longer sessions, validate restricted flows, and clean bridge-managed captures. The unified controller delegates to `ios-cuctl`; it does not bypass any iOS boundary.

## Host configuration

The bridge is portable and reads these optional environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `IOS_CUCTL_CONFIG` | `$HOME/.config/ios-computer-use/env` | Optional non-executable file of persistent `IOS_CUCTL_*` assignments |
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

The bridge also detects the tested portable Node/Appium layout under `$IOS_CUCTL_SHARE_DIR/tools/`. Keep machine-specific values in the shell environment or the user-only config file; never commit them with signing assets. The config parser accepts plain `IOS_CUCTL_NAME=value` assignments but does not execute shell code.

## Start a routine task

When the phone has already been paired and the persistent tunnel service is installed, begin with:

```bash
"$HOME/ios-computer-use/ios-cuctl" tunnel-status
"$HOME/ios-computer-use/ios-cuctl" status
```

If `tunnel-status` reports `ready: true` with exactly one tunnel, reuse it. `registry_ready: true` with `ready: false` means the background service is healthy but no phone tunnel is currently active; keep the phone awake with Wi-Fi enabled and confirm it is on the same LAN. Use `wireless-browse` only when the registry has no active phone; its output is deduplicated by device and endpoint. Run `doctor` and `devices` for first-time setup, USB work, or troubleshooting rather than before every routine action.

If more than one tunneled or trusted USB device is present, pass `--udid` before the subcommand. Never guess which device the user intended.

For a longer task, prepare one session without sudo:

```bash
"$HOME/mobile-cuctl/mobile-cuctl" start ios
"$HOME/mobile-cuctl/mobile-cuctl" start ios --input
"$HOME/mobile-cuctl/mobile-cuctl" stop ios
```

The first form verifies the persistent tunnel, saves baseline and ready screenshots, and acquires a host idle/sleep inhibitor without WDA. Add `--input` only when the unlocked phone needs touch, text, or accessibility; it prewarms one reusable WDA session. Inspect the returned screenshot before input. `stop` removes WDA's automation indicator and releases the inhibitor while leaving the persistent tunnel running.

For the simplest no-banner path, keep the RemoteXPC tunnel running and use `screenshot`, `activate`, or hardware `press`. CoreDevice screen capture and app launch do not start XCTest, so iOS does not show the "Automation Running" indicator.

CoreDevice touch/keyboard remote control requires iOS 27 or later. On iOS 26 and earlier, `tap-image`, `swipe-image`, `type`, element commands, and logical-coordinate commands automatically start Appium/WDA on demand. USB plus WDA is the most reliable input path on those versions unless a WDA v13+ artifact compatible with persistent preinstalled launch has been prepared. Hardware `press` uses CoreDevice Indigo HID without WDA on all supported versions. While WDA is active, iOS shows its system-level automation indicator until `stop` or `wda-stop` is run. This version gate was verified against the device-side CoreDevice error 9021 on iOS 26.6.

Start the local Appium/WDA session only when accessibility hierarchy or element-based interaction is needed. Run `tunnel-start` only when `registry_ready` is false and no persistent system service is installed:

```bash
"$HOME/ios-computer-use/ios-cuctl" tunnel-status
"$HOME/ios-computer-use/ios-cuctl" tunnel-start
"$HOME/ios-computer-use/ios-cuctl" wda-status
"$HOME/ios-computer-use/ios-cuctl" start
"$HOME/ios-computer-use/ios-cuctl" status
```

On iOS 18 and later, `tunnel-start` is required on Linux. It synchronizes the registry port into the user-side Appium Strongbox before requesting privilege, then stays in the foreground so the RemoteXPC tunnel remains alive. Reuse a running tunnel; do not start one per action. The privilege prompt is an operating-system boundary and cannot be bypassed.

On Linux with a transient pymobiledevice3 registry, `start` also starts or reuses `"$HOME/ios-computer-use/wda-runner"`. This helper keeps pymobiledevice3's XCTest manager connection alive, while Appium attaches through `webDriverAgentUrl`. With the persistent Appium-compatible registry described below, Appium instead uses its `usePreinstalledWDA` path. While either WDA path is active, iOS shows its system-level "Automation Running" indicator; this cannot be hidden. Use `wda-stop` to remove the indicator and return to CoreDevice/HID mode. CoreDevice screenshots and app launches do not start XCTest and do not show the indicator.

Do not restart Appium or WDA between ordinary screenshots, taps, swipes, text entry, or app changes. Stop only when the user asks, recovery requires it, or the task is complete and no later action is expected.

## Safe interaction loop

For UI actions:

1. Capture a fresh screenshot.
2. Inspect it with the available image-viewing tool. A fully black capture can mean the display is asleep; issue the reversible `press home` action and capture again. If a lock screen is then visible, ask the user to unlock it.
3. Use `tap-image` or `swipe-image`; these automatically choose CoreDevice HID on iOS 27+ or start WDA on older versions, convert coordinates, and save an after-action screenshot.
4. Prefer `source` plus `tap-element` when stable accessibility identifiers or hierarchy inspection are needed; these start WDA on demand.
5. Inspect the after-action screenshot and report the observed result, not just command success.

Examples:

```bash
"$HOME/ios-computer-use/ios-cuctl" screenshot /tmp/iphone-before.png
"$HOME/ios-computer-use/ios-cuctl" activate com.apple.MobileSMS
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

The service invokes the bundled `ios-tunneld-runner` directly because pymobiledevice3's public CLI requires UID 0 even when systemd has already supplied the required capability. The runner exposes both pymobiledevice3's native registry and Appium's `/remotexpc/tunnels` API, including the RSD service catalog Appium needs for its non-macOS preinstalled-WDA strategy. It also probes active RSD endpoints and rebuilds stale tunnels in place, so normal phone disconnect/reconnect recovery does not require another sudo or polkit prompt. The first command after a reconnect can take roughly 30 seconds while one automatic rebuild/retry completes; keep the device awake for the quickest recovery rather than starting another tunnel. The bridge normalizes either registry format, checks the persistent registry before its older per-session registry, prefers a registry containing an active device tunnel, and treats that registry as a device source when USB is disconnected. On a persistent tunnel, WDA is launched by Appium with `usePreinstalledWDA`; do not substitute pymobiledevice3's generic XCTest launcher, because iOS may reject the runner's device-to-host callback with NECP. The installed runner must be a WDA v13+ build prepared for preinstalled launch. If Appium launches a black WDA runner but port 8100 never opens, replace the signed WDA artifact; more host privilege does not fix that package mismatch. Granting `CAP_NET_ADMIN` lets this service manage host TUN interfaces and routes; it is narrower than root but remains a host networking privilege. If the user home is not `/home/<user>` or pymobiledevice3 uses a different Python path, copy the template and adjust `Environment`, `ExecStart`, `ReadWritePaths`, and `ReadOnlyPaths` before installing it.

CoreDevice screenshots and hardware `press` can operate while the display is locked, but a sleeping display can initially produce a black capture. Use `press home`, capture again, and ask the user to unlock before app interaction or input. WDA/Appium accessibility, touch, and text input require the device to be unlocked; if the phone locks during wireless WDA startup, iOS may terminate the XCTest connection. Never attempt to bypass the lock screen—ask the user to unlock and retry.

For a tunnel started outside the bridge, set `IOS_CUCTL_RSD_ADDRESS`, `IOS_CUCTL_RSD_PORT`, `IOS_CUCTL_WIFI_UDID`, and optionally `IOS_CUCTL_WIFI_PLATFORM_VERSION`. Use `IOS_CUCTL_TRANSPORT=usb` to force the original USB tunnel while a Wi-Fi tunnel is running.

Provide a WDA package signed for the target device and set:

```text
export IOS_CUCTL_WDA_IPA="$HOME/.local/share/ios-computer-use/artifacts/WebDriverAgentRunner.ipa"
export IOS_CUCTL_WDA_BUNDLE_ID="your.signed.WebDriverAgentRunner.xctrunner"
```

For settings that must survive bridge upgrades, put the same two assignments in `$HOME/.config/ios-computer-use/env` and set that file to mode `0600`. Environment variables take precedence over the file.

Install it only with the user's explicit authorization:

```bash
"$HOME/ios-computer-use/ios-cuctl" install-wda
```

Keep signing materials outside the repository, preferably under `$HOME/.local/share/ios-computer-use/signing` with user-only permissions. Treat every private key as secret: never print it, copy it into a workspace, attach it to output, or upload it. Certificates, provisioning profiles, device registration, App IDs, app installation/removal, and Developer Mode changes are consequential actions and require explicit user authorization.

Common failures:

- `DeviceLocked`: ask the user to unlock the device and keep the screen on, then retry `mount` or `start`. Never attempt to discover or enter a passcode.
- RemoteXPC registry missing: run `tunnel-status`; only when `registry_ready` is false and no persistent system service is installed, run `tunnel-start`, approve the privilege prompt, and keep that process running. `start` automatically repairs the root/user Strongbox port split when the registry is reachable.
- Preinstalled WDA never opens port 8100: `start` now waits 30 seconds, then falls back to the bridge's own XCTest runner and `webDriverAgentUrl`, so this usually resolves itself. Appium's error blames the WDA build or a locked device even when both are fine, so verify before believing it. If the fallback also fails, confirm WDA v13+, remove embedded `Frameworks/XC*` copies, and install a device-signed runner. On iOS 26 and earlier, CoreDevice touch is not a fallback; it requires iOS 27+.
- Plugging in USB while a Wi-Fi tunnel is running: the service builds a second tunnel for the same device. It now publishes whichever endpoint its health check last reached, so wait one probe interval (about 15 seconds) and retry rather than restarting anything. `tunnel-status` may still list the other device under `interfaces.unassociated`; that is cosmetic once the published address answers.
- WDA fails to launch while screenshots still work: check `tunnel-status` for `interfaces.unassociated`. Cancelled tunnels can leave persistent TUN devices behind, and each keeps a ULA `/64` route. Host-to-device traffic (screenshots, `apps`, `press`, `activate`) still routes correctly, but WebDriverAgent needs the device to connect back to the host, and that callback lands on the wrong interface. The device log shows `Exiting due to IDE disconnection` and the host shows `Connection closed while waiting for proxied service`. Raising `wdaLaunchTimeout` does not help, because the link is broken rather than slow.

  The service repairs this without any administrator action. It deletes the interface behind every tunnel it rebuilds, publishes the endpoint its health check last reached when a device holds more than one tunnel, and exits after two minutes with nothing reachable so systemd restarts it under the capability grant it already has. Wait through one or two probe intervals and retry before escalating; `sudo systemctl restart "ios-computer-use-tunneld@$(id -un).service"` is only needed to load a new build of the runner itself.
- No active wireless tunnel: if `registry_ready` is true but `ready` is false, keep the phone awake, enable Wi-Fi, confirm host and phone are on the same LAN, and run `wireless-browse`; do not start a duplicate tunnel service.
- No USB device: verify USB enumeration and `usbmuxd`, then ask the user to reconnect and approve Trust if needed.
- Developer image missing: run `mount` while unlocked; iOS 17+ uses a personalized DeveloperDiskImage.
- WDA missing or untrusted: confirm explicit authorization, reinstall with `install-wda`, and ask the user to accept any on-device developer trust prompt.
- Stale session: run `stop`, then `start`. Use `server-stop` only when the local Appium server itself must be restarted.

## Safety boundaries

Never bypass a lock screen, biometric prompt, secure-input restriction, developer trust warning, iOS permission prompt, or account boundary.

Obtain explicit user authorization immediately before consequential actions such as sending messages, placing calls, making purchases or trades, changing accounts or security settings, entering a PIN/password/OTP, installing or removing apps or profiles, changing Developer Mode, trusting a developer identity, or rebooting the device.

System screen recording may be operated through Control Center when the user asks and authorizes it. Treat recordings as user data and confirm where the resulting file should be retained or exported.

The bridge intentionally leaves native iOS screen-record start/stop in Control Center because that system UI varies by device and configuration. Use the unified session preflight before recording, then keep the same WDA session for the whole flow. Restricted JSON flows may be dry-run with `mobile-cuctl flow FILE --dry-run`; inspect the entire flow before `--run`, and stop at normal authorization boundaries.

Preview periodic cleanup with:

```bash
"$HOME/mobile-cuctl/mobile-cuctl" cleanup --platform ios
"$HOME/mobile-cuctl/mobile-cuctl" cleanup --platform ios --apply
```

Defaults are bridge captures/UI dumps older than 7 days and files under `$HOME/ios-computer-use/recordings/` older than 14 days. `--apply` is required. The cleaner ignores symlinks, does not touch signing/state files, and never scans project artifact directories.
