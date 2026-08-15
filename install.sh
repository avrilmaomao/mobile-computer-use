#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
install_home="${MOBILE_CU_INSTALL_HOME:-$HOME}"
install_claude=0
install_codex=0
install_agents=0
enable_android_reconnect=0

usage() {
  cat <<'EOF'
Usage: ./install.sh [--claude] [--codex] [--agents] [--all] [--enable-android-reconnect]

  --claude  Install skills into ~/.claude/skills
  --codex   Install skills into ${CODEX_HOME:-~/.codex}/skills
  --agents  Install skills into ~/.agents/skills
  --all     Install all supported skill targets
  --enable-android-reconnect
            Enable the optional per-user Android wireless reconnect service

With no option, --claude is used. Bridge controllers are always installed into
~/ios-computer-use and ~/android-computer-use. Set MOBILE_CU_INSTALL_HOME only
for an isolated test or a deliberately relocated installation.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude)
      install_claude=1
      ;;
    --codex)
      install_codex=1
      ;;
    --agents)
      install_agents=1
      ;;
    --all)
      install_claude=1
      install_codex=1
      install_agents=1
      ;;
    --enable-android-reconnect)
      enable_android_reconnect=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'install.sh: unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [[ "$install_claude" -eq 0 && "$install_codex" -eq 0 && "$install_agents" -eq 0 ]]; then
  install_claude=1
fi

timestamp="$(date +%Y%m%d-%H%M%S)"

install_file() {
  local mode="$1"
  local source="$2"
  local target="$3"

  install -d -m 0755 "$(dirname -- "$target")"
  if [[ -f "$target" ]] && ! cmp -s "$source" "$target"; then
    cp -p -- "$target" "$target.backup-$timestamp"
    printf 'Backed up %s\n' "$target"
  fi
  install -m "$mode" "$source" "$target"
  printf 'Installed %s\n' "$target"
}

install_bridge() {
  local platform="$1"
  local target_dir="$install_home/$platform-computer-use"

  install_file 0644 "$repo_dir/bridges/$platform/AGENTS.md" "$target_dir/AGENTS.md"
  if [[ "$platform" == "ios" ]]; then
    install_file 0755 "$repo_dir/bridges/ios/ios-cuctl" "$target_dir/ios-cuctl"
    install_file 0755 "$repo_dir/bridges/ios/wda-runner" "$target_dir/wda-runner"
    install_file 0755 "$repo_dir/bridges/ios/ios-tunneld-runner" "$target_dir/ios-tunneld-runner"
    install_file 0644 "$repo_dir/bridges/ios/ios-computer-use-tunneld@.service" \
      "$target_dir/ios-computer-use-tunneld@.service"
  else
    install_file 0755 "$repo_dir/bridges/android/android-cuctl" "$target_dir/android-cuctl"
    install_file 0755 "$repo_dir/bridges/android/android-auto-reconnect" \
      "$target_dir/android-auto-reconnect"
    install_file 0644 "$repo_dir/bridges/android/android-computer-use-reconnect.service" \
      "$install_home/.config/systemd/user/android-computer-use-reconnect.service"
  fi
}

install_mobile_bridge() {
  install_file 0755 "$repo_dir/bridges/mobile/mobile-cuctl" \
    "$install_home/mobile-cuctl/mobile-cuctl"
}

install_skill() {
  local skill="$1"
  local skill_root="$2"
  local source_dir="$repo_dir/skills/$skill"
  local target_dir="$skill_root/$skill"

  install_file 0644 "$source_dir/SKILL.md" "$target_dir/SKILL.md"
  if [[ -f "$source_dir/agents/openai.yaml" ]]; then
    install_file 0644 "$source_dir/agents/openai.yaml" "$target_dir/agents/openai.yaml"
  fi
}

install_bridge android
install_bridge ios
install_mobile_bridge

if [[ "$enable_android_reconnect" -eq 1 ]]; then
  if [[ -n "${MOBILE_CU_INSTALL_HOME:-}" ]]; then
    printf 'Installed Android reconnect service but did not enable it in an isolated install home.\n'
  else
    systemctl --user daemon-reload
    systemctl --user enable android-computer-use-reconnect.service
    systemctl --user restart android-computer-use-reconnect.service
    printf 'Enabled Android reconnect service for %s (no sudo).\n' "$(id -un)"
  fi
fi

skill_roots=()
if [[ "$install_claude" -eq 1 ]]; then
  skill_roots+=("$install_home/.claude/skills")
fi
if [[ "$install_codex" -eq 1 ]]; then
  if [[ -n "${MOBILE_CU_INSTALL_HOME:-}" ]]; then
    codex_root="$install_home/.codex"
  else
    codex_root="${CODEX_HOME:-$install_home/.codex}"
  fi
  skill_roots+=("$codex_root/skills")
fi
if [[ "$install_agents" -eq 1 ]]; then
  skill_roots+=("$install_home/.agents/skills")
fi

for skill_root in "${skill_roots[@]}"; do
  install_skill android-computer-use "$skill_root"
  install_skill ios-computer-use "$skill_root"
done

printf '\nInstallation complete. Run the read-only checks:\n'
printf '  %q doctor\n' "$install_home/android-computer-use/android-cuctl"
printf '  %q doctor\n' "$install_home/ios-computer-use/ios-cuctl"
printf '  %q status all\n' "$install_home/mobile-cuctl/mobile-cuctl"
