# Android Computer Use

This directory is the canonical implementation for operating a user-authorized physical Android device from this Linux host. Skills and agents should call the command here instead of duplicating ADB logic.

## Paths

- Controller: `"$HOME/android-computer-use/android-cuctl"`
- Captures and UI dumps: `$HOME/android-computer-use/captures/`
- Agent skill: install `skills/android-computer-use/SKILL.md` into the agent's personal skill directory

Run `"$HOME/android-computer-use/android-cuctl" --help` to see the supported command surface.

Set `ANDROID_CUCTL_HOME` only when the bridge is installed outside `$HOME/android-computer-use`. Set `ANDROID_SERIAL` to the exact authorized device serial whenever more than one ADB target is online.

## Bundled runtime

The controller uses `adb` and `scrcpy` from `PATH`. It also supports an optional portable runtime under `$HOME/android-computer-use/runtime/`, which it prepends to `PATH` without requiring root access or global PATH changes.

- Tested scrcpy release: 4.1
- Tested bundled ADB: 37.0.0
- Tested upstream archive: `https://github.com/Genymobile/scrcpy/releases/download/v4.1/scrcpy-linux-x86_64-v4.1.tar.gz`
- Tested archive SHA-256: `ad56ae8bfeedf41e824945c11dbf55fcb092b3e615b9b486f48a50e30d389635`

If using that portable archive, retain its upstream `LICENSE`. Do not use binaries from an unofficial mirror.

## Start a routine task

For a host and phone that have already been configured, begin with:

```bash
"$HOME/android-computer-use/android-cuctl" devices
```

If exactly one wireless `HOST:PORT` target is already in `device` state, use it directly. Do not run `doctor`, `discover`, or `connect-auto` on every task. Use `doctor` for first-time setup or tool/connection troubleshooting; take a fresh screenshot next so a lock screen or changed UI is visible before input.

## First-time phone setup

Wireless debugging needs no additional host installation. USB debugging may require the Ubuntu Android udev rules; if `android-cuctl devices` cannot see a USB-connected phone, run this once in a visible terminal and enter the local sudo password there:

```bash
sudo apt update
sudo apt install android-udev-rules
```

On the phone:

1. Open **Settings > About phone** and tap **Build number** seven times.
2. Open **Developer options** and enable **USB debugging**.
3. Connect a data-capable USB cable, unlock the phone, and accept the RSA fingerprint prompt. Enable “Always allow” only if this is a trusted personal computer.
4. Run `android-cuctl devices`; the state must be `device`, not `unauthorized` or `offline`.

If USB discovery fails, reconnect the cable, change the USB mode to file transfer, and run:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
adb kill-server
adb start-server
```

Do not disable Android's RSA authorization or weaken the lock screen to make automation easier.

## Wireless debugging

Prefer Android 11 or newer's **Wireless debugging** pairing flow. Keep the phone and host on the same trusted network.

1. On the phone, open **Developer options > Wireless debugging > Pair device with pairing code**.
2. Run `android-cuctl pair PHONE_IP:PAIR_PORT` and enter the six-digit code when prompted.
3. Use the separate address shown on the main Wireless debugging screen with `android-cuctl connect PHONE_IP:DEBUG_PORT`.
4. Confirm with `android-cuctl devices`.

The host can discover advertised services without copying addresses manually:

```bash
"$HOME/android-computer-use/android-cuctl" discover
"$HOME/android-computer-use/android-cuctl" connect-auto
```

`connect-auto` proceeds only when exactly one already-paired `_adb-tls-connect` target is visible. If multiple targets appear, inspect `discover` and connect the intended address explicitly.

Android may stop advertising an mDNS service while the already-established ADB connection remains online. Check `devices` first: an existing wireless target in `device` state remains usable, and `connect-auto` reuses it without reconnecting. Run discovery only when no usable target is online.

Do not expose legacy unauthenticated ADB-over-TCP port 5555 to a LAN or the Internet.

## Device selection

The controller proceeds automatically only when exactly one authorized device is attached. If more than one physical device or emulator appears, select the exact serial for the task:

```bash
export ANDROID_SERIAL='SERIAL_FROM_DEVICES'
```

Never guess which device the user means. Do not run concurrent agents against the same device because their input and screenshots can race.

## Inspect, act, verify

For any coordinate-based action:

1. Run `android-cuctl screenshot` and inspect the returned absolute PNG path with the image-viewing tool.
2. Optionally run `android-cuctl ui-dump` to obtain labels, resource IDs, and element bounds.
3. Use the smallest necessary action: `tap`, `swipe`, `key`, `text-ascii`, or `launch`.
4. Capture and inspect a new screenshot after each state-changing action.
5. Stop when the displayed state is ambiguous, unexpected, or sensitive.

Screens can change due to animation, rotation, dialogs, the keyboard, or notifications, so never reuse old coordinates without a fresh screenshot. UIAutomator dumps may omit WebViews, games, videos, secure windows, or custom-rendered controls.

`text-ascii` deliberately accepts only conservative ASCII. Some vendor keyboards leave injected text in an IME composing buffer instead of committing it immediately. Inspect the after-action screenshot; use `key KEYCODE_ENTER` only when committing that text is the intended reversible action. For Unicode text, use the on-screen keyboard through inspected taps, paste manually with the user's awareness, or install a trusted input-method helper only after explicit approval. Never place passwords, PINs, or one-time codes in command history or logs.

Use `android-cuctl mirror` for live scrcpy viewing. If an agent must control the scrcpy window itself, it must also load the `wayland-computer-use` skill and follow that skill's desktop-control rules.

## Safety boundary

Routine reversible navigation, inspection, scrolling, and opening an app the user named are allowed within the requested task. Pause and obtain explicit confirmation immediately before:

- sending a message, email, post, form, or file;
- placing a call or accepting a charge;
- purchasing, transferring money, subscribing, or confirming an order;
- changing an account, password, lock screen, security, privacy, or device-admin setting;
- entering or exposing a password, PIN, recovery code, or OTP;
- installing, uninstalling, disabling, or clearing data for an app;
- deleting user content or resetting/rebooting the device;
- granting a sensitive permission or enabling accessibility/device-admin access.

Do not attempt to bypass the Android lock screen, biometrics, `FLAG_SECURE`, work-profile policy, MDM, or app authorization. The constrained controller intentionally exposes no arbitrary shell, package removal, data-clearing, reboot, root, or fastboot commands.

## Disconnect and revoke

For wireless debugging, run `android-cuctl disconnect` when finished. The user can remove paired hosts under **Developer options > Wireless debugging > Paired devices**. To revoke all USB-debugging trust, use **Developer options > Revoke USB debugging authorizations**.
