from __future__ import annotations

import json
import os
import signal
import stat
import subprocess
import tempfile
import textwrap
import time
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
MOBILE = REPO / "bridges/mobile/mobile-cuctl"
ANDROID = REPO / "bridges/android/android-cuctl"
RECONNECT = REPO / "bridges/android/android-auto-reconnect"
INSTALL = REPO / "install.sh"
TUNNELD = REPO / "bridges/ios/ios-tunneld-runner"


def run(command: list[str], *, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(command, text=True, capture_output=True, env=merged, check=check, timeout=30)


def executable(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


class CleanupTests(unittest.TestCase):
    def test_cleanup_has_separate_capture_and_recording_retention(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            android = home / "android-computer-use"
            ios = home / "ios-computer-use"
            old_capture = android / "captures/old.png"
            recent_capture = ios / "verification/recent.xml"
            old_recording = android / "recordings/old.mp4"
            recent_recording = ios / "recordings/recent.mov"
            outside = home / "artifacts/delivery.mp4"
            for path in (old_capture, recent_capture, old_recording, recent_recording, outside):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"test")
            now = time.time()
            os.utime(old_capture, (now - 8 * 86400, now - 8 * 86400))
            os.utime(recent_capture, (now - 6 * 86400, now - 6 * 86400))
            os.utime(old_recording, (now - 15 * 86400, now - 15 * 86400))
            os.utime(recent_recording, (now - 13 * 86400, now - 13 * 86400))
            os.utime(outside, (now - 30 * 86400, now - 30 * 86400))
            env = {
                "MOBILE_CUCTL_USER_HOME": str(home),
                "ANDROID_CUCTL_HOME": str(android),
                "IOS_CUCTL_HOME": str(ios),
                "MOBILE_CUCTL_STATE_DIR": str(home / "state"),
            }

            preview = run([str(MOBILE), "cleanup"], env=env)
            report = json.loads(preview.stdout)
            self.assertEqual(report["mode"], "dry-run")
            self.assertEqual(report["eligible_files"], 2)
            self.assertTrue(old_capture.exists())
            self.assertTrue(old_recording.exists())

            applied = run([str(MOBILE), "cleanup", "--apply"], env=env)
            report = json.loads(applied.stdout)
            self.assertEqual(report["deleted_files"], 2)
            self.assertFalse(old_capture.exists())
            self.assertFalse(old_recording.exists())
            self.assertTrue(recent_capture.exists())
            self.assertTrue(recent_recording.exists())
            self.assertTrue(outside.exists())


class FlowTests(unittest.TestCase):
    def test_flow_dry_run_is_restricted_and_does_not_need_a_device(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            flow = root / "flow.json"
            flow.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "platform": "ios",
                        "steps": [
                            {"action": "activate", "bundle_id": "io.example.app"},
                            {"action": "pause", "seconds": 0.2},
                            {"action": "screenshot", "file": "checkpoint.png"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            result = run(
                [str(MOBILE), "flow", str(flow), "--dry-run"],
                env={
                    "MOBILE_CUCTL_USER_HOME": str(root),
                    "IOS_CUCTL_HOME": str(root / "ios"),
                },
            )
            report = json.loads(result.stdout)
            self.assertEqual(report["platform"], "ios")
            self.assertEqual(len(report["steps"]), 3)
            self.assertIn("activate", report["steps"][0]["command"])
            self.assertEqual(report["steps"][1]["pause_seconds"], 0.2)

    def test_flow_rejects_non_whitelisted_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            flow = Path(temporary) / "flow.json"
            flow.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "platform": "android",
                        "steps": [{"action": "shell", "command": "id"}],
                    }
                ),
                encoding="utf-8",
            )
            result = run([str(MOBILE), "flow", str(flow), "--dry-run"], check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unsupported android flow action", result.stderr)


class SessionTests(unittest.TestCase):
    def test_ios_input_preflight_reuses_one_controller_session(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "calls"
            fake = root / "ios-cuctl"
            executable(
                fake,
                f"""
                #!/usr/bin/env bash
                printf '%s\\n' "$*" >> {log!s}
                case "$1" in
                  tunnel-status)
                    printf '{{"ready":true,"tunnels":{{"device":{{"address":"fd00::1","rsdPort":1234}}}}}}\\n'
                    ;;
                  screenshot)
                    mkdir -p "$(dirname "$2")"
                    printf 'png' > "$2"
                    printf '{{"path":"%s","width":1,"height":1}}\\n' "$2"
                    ;;
                  start|stop)
                    ;;
                esac
                """,
            )
            result = run(
                [str(MOBILE), "start", "ios", "--input", "--no-inhibit"],
                env={
                    "MOBILE_CUCTL_USER_HOME": str(root),
                    "IOS_CUCTL_HOME": str(root / "ios"),
                    "MOBILE_CUCTL_IOS_BIN": str(fake),
                    "MOBILE_CUCTL_STATE_DIR": str(root / "state"),
                },
            )
            report = json.loads(result.stdout)
            self.assertTrue(report["ready"])
            self.assertTrue(report["input_prepared"])
            calls = log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(calls[0], "tunnel-status")
            self.assertTrue(calls[1].startswith("screenshot "))
            self.assertEqual(calls[2], "start")
            self.assertTrue(calls[3].startswith("screenshot "))


class ReconnectTests(unittest.TestCase):
    def test_reconnects_only_when_no_wireless_target_is_online(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "calls"
            fake = root / "android-cuctl"
            executable(
                fake,
                f"""
                #!/usr/bin/env bash
                printf '%s\\n' "$1" >> {log!s}
                if [[ "$1" == devices ]]; then
                  printf 'List of devices attached\\n\\n'
                elif [[ "$1" == connect-auto ]]; then
                  printf 'connected to 192.0.2.1:37000\\n'
                fi
                """,
            )
            result = run([str(RECONNECT), "--once"], env={"ANDROID_CUCTL_BIN": str(fake)})
            self.assertIn("reconnected", result.stdout)
            self.assertEqual(log.read_text(encoding="utf-8").splitlines(), ["devices", "connect-auto"])

    def test_reuses_an_existing_wireless_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "calls"
            fake = root / "android-cuctl"
            executable(
                fake,
                f"""
                #!/usr/bin/env bash
                printf '%s\\n' "$1" >> {log!s}
                printf 'List of devices attached\\n192.0.2.1:37000 device product:test\\n'
                """,
            )
            result = run([str(RECONNECT), "--once"], env={"ANDROID_CUCTL_BIN": str(fake)})
            self.assertIn("connected", result.stdout)
            self.assertEqual(log.read_text(encoding="utf-8").splitlines(), ["devices"])

    def test_does_not_add_a_wireless_duplicate_while_usb_is_online(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "calls"
            fake = root / "android-cuctl"
            executable(
                fake,
                f"""
                #!/usr/bin/env bash
                printf '%s\\n' "$1" >> {log!s}
                printf 'List of devices attached\\nUSB-SERIAL device product:test\\n'
                """,
            )
            result = run([str(RECONNECT), "--once"], env={"ANDROID_CUCTL_BIN": str(fake)})
            self.assertIn("connected", result.stdout)
            self.assertEqual(log.read_text(encoding="utf-8").splitlines(), ["devices"])


class AndroidRecordingTests(unittest.TestCase):
    def test_background_recording_is_finalized_with_sigint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary_dir = root / "bin"
            binary_dir.mkdir()
            executable(
                binary_dir / "adb",
                """
                #!/usr/bin/env bash
                if [[ "$1" == devices ]]; then
                  printf 'List of devices attached\\n192.0.2.1:37000 device product:test\\n'
                elif [[ "$1" == -s && "$3" == get-state ]]; then
                  printf 'device\\n'
                fi
                """,
            )
            executable(
                binary_dir / "scrcpy",
                """
                #!/usr/bin/env bash
                output=''
                while [[ $# -gt 0 ]]; do
                  if [[ "$1" == --record ]]; then
                    output="$2"
                    shift 2
                  else
                    shift
                  fi
                done
                finish() {
                  if [[ -n "$output" ]]; then
                    printf 'fake mp4' > "$output"
                  fi
                  exit 0
                }
                trap finish INT TERM
                while true; do sleep 0.1; done
                """,
            )
            env = {
                "PATH": f"{binary_dir}:{os.environ['PATH']}",
                "ANDROID_CUCTL_HOME": str(root / "android"),
                "ANDROID_CUCTL_STATE_DIR": str(root / "state"),
            }
            try:
                started = run([str(ANDROID), "record-start", "demo.mp4"], env=env)
                self.assertIn("recording: true", started.stdout)
                status_result = run([str(ANDROID), "record-status"], env=env)
                self.assertIn("recording: true", status_result.stdout)
                stopped = run([str(ANDROID), "record-stop"], env=env)
                output = Path(stopped.stdout.strip())
                self.assertEqual(output.read_bytes(), b"fake mp4")
                final_status = run([str(ANDROID), "record-status"], env=env)
                self.assertIn("recording: false", final_status.stdout)
            finally:
                pid_path = root / "state/record.pid"
                if pid_path.exists():
                    os.kill(int(pid_path.read_text(encoding="utf-8")), signal.SIGTERM)


class InstallerTests(unittest.TestCase):
    def test_isolated_install_includes_unified_bridge_and_service_without_enabling(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            result = run(
                [str(INSTALL), "--all", "--enable-android-reconnect"],
                env={"MOBILE_CU_INSTALL_HOME": str(home)},
            )
            self.assertTrue((home / "mobile-cuctl/mobile-cuctl").is_file())
            self.assertTrue((home / "android-computer-use/android-auto-reconnect").is_file())
            self.assertTrue((home / ".config/systemd/user/android-computer-use-reconnect.service").is_file())
            self.assertIn("did not enable it in an isolated install home", result.stdout)


class TunnelSelectionTests(unittest.TestCase):
    """A device can hold both a Wi-Fi and a USB tunnel; publishing the stale one
    breaks every WebDriverAgent launch, so selection must follow reachability."""

    def load(self):
        import importlib.util

        spec = importlib.util.spec_from_loader("ios_tunneld_runner", loader=None)
        module = importlib.util.module_from_spec(spec)
        source = TUNNELD.read_text(encoding="utf-8")
        # Import the selection logic without pulling in pymobiledevice3/fastapi.
        head = source.split("class CompatibleTunneldRunner", 1)[1]
        body = "class CompatibleTunneldRunner" + head.split("    async def _tunnel_reachable", 1)[0]
        exec("from typing import Any\n" + body, module.__dict__)
        return module.CompatibleTunneldRunner

    def build(self, cls, tunnels, preferred=None):
        instance = cls.__new__(cls)
        instance._preferred_tunnel = dict(preferred or {})

        class Task:
            def __init__(self, udid, tunnel):
                self.udid = udid
                self.tunnel = tunnel

        class Core:
            def __init__(self):
                self.tunnel_tasks = {i: Task(u, t) for i, (u, t) in enumerate(tunnels)}

        class Runner:
            def __init__(self):
                self._tunneld_core = Core()

        instance.runner = Runner()
        return instance

    def tunnel(self, address, port, interface):
        class Tunnel:
            def __init__(self):
                self.address = address
                self.port = port
                self.interface = interface

        return Tunnel()

    def test_prefers_the_tunnel_health_checks_confirmed(self) -> None:
        cls = self.load()
        stale = self.tunnel("fd00::1", 100, "tun0")
        live = self.tunnel("fd11::1", 200, "tun1")
        instance = self.build(
            cls,
            [("UDID", stale), ("UDID", live)],
            preferred={"UDID": ("fd11::1", 200)},
        )
        self.assertEqual(instance._active_tunnels()["UDID"].address, "fd11::1")

    def test_falls_back_to_the_first_tunnel_before_any_probe(self) -> None:
        cls = self.load()
        first = self.tunnel("fd00::1", 100, "tun0")
        second = self.tunnel("fd11::1", 200, "tun1")
        instance = self.build(cls, [("UDID", first), ("UDID", second)])
        self.assertEqual(instance._active_tunnels()["UDID"].address, "fd00::1")

    def test_reports_one_entry_per_device(self) -> None:
        cls = self.load()
        instance = self.build(
            cls,
            [
                ("A", self.tunnel("fd00::1", 100, "tun0")),
                ("A", self.tunnel("fd11::1", 200, "tun1")),
                ("B", self.tunnel("fd22::1", 300, "tun2")),
            ],
        )
        self.assertEqual(sorted(instance._active_tunnels()), ["A", "B"])


if __name__ == "__main__":
    unittest.main()
