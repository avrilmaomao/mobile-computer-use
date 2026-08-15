# Claude Code 安装与使用

Claude Code 会从 `~/.claude/skills/<skill-name>/SKILL.md` 发现个人技能。本仓库的安装器会把技能放到该目录，并把实际控制脚本放在 home 目录下，避免污染业务项目。

## 一键安装

```bash
git clone https://github.com/avrilmaomao/mobile-computer-use.git
cd mobile-computer-use
./install.sh --claude
```

安装结果：

```text
~/.claude/skills/android-computer-use/SKILL.md
~/.claude/skills/ios-computer-use/SKILL.md
~/android-computer-use/android-cuctl
~/android-computer-use/android-auto-reconnect
~/android-computer-use/AGENTS.md
~/ios-computer-use/ios-cuctl
~/ios-computer-use/wda-runner
~/ios-computer-use/ios-tunneld-runner
~/ios-computer-use/ios-computer-use-tunneld@.service
~/ios-computer-use/AGENTS.md
~/mobile-cuctl/mobile-cuctl
~/.config/systemd/user/android-computer-use-reconnect.service
```

如果 Claude Code 启动时 `~/.claude/skills` 目录尚不存在，安装后重新启动一次 Claude Code。已存在的技能目录通常支持热加载。

## 验证发现

在 Claude Code 中可直接输入：

```text
/android-computer-use 检查已连接的安卓手机
/ios-computer-use 检查已连接的 iPhone
```

也可以用自然语言触发，例如“截一张安卓手机当前屏幕”或“打开 iPhone 上的某个 App 并检查页面”。Claude 应先完整读取安装在 home 目录中的 `AGENTS.md`。日常任务走快速探测：Android 先运行 `devices`，iOS 常驻服务先运行 `tunnel-status`；`doctor` 用于首次配置或故障排查，不必每次执行。

在 shell 中先做只读验证：

```bash
"$HOME/android-computer-use/android-cuctl" --help
"$HOME/android-computer-use/android-cuctl" doctor

"$HOME/ios-computer-use/ios-cuctl" --help
"$HOME/ios-computer-use/ios-cuctl" doctor
"$HOME/mobile-cuctl/mobile-cuctl" status all
```

技能不会绕过 Claude Code 自身的工具授权、操作系统权限、手机 Trust/RSA 提示、锁屏、PIN、Face ID/Touch ID 或 App 登录边界。

## Android 准备

1. 安装 `adb`；需要镜像窗口时再安装 `scrcpy`。
2. 手机上打开开发者选项和 USB debugging，连接数据线并确认 RSA 指纹。
3. Android 11+ 可使用 Wireless debugging：先 `pair`，再用主界面显示的调试端口执行 `connect`。
4. 多设备在线时设置精确的 `ANDROID_SERIAL`，不要让 agent 猜设备。

已配对设备再次上线时，先检查现有连接：

```bash
"$HOME/android-computer-use/android-cuctl" devices
```

如果恰好一个无线 `HOST:PORT` 已处于 `device` 状态，直接复用，不要等待 mDNS。只有没有在线目标时才运行：

```bash
"$HOME/android-computer-use/android-cuctl" discover
"$HOME/android-computer-use/android-cuctl" connect-auto
```

`connect-auto` 会直接复用唯一的在线无线目标；否则只会在局域网中恰好发现一个已配对 connect 服务时继续。mDNS 广播消失不代表已建立的 ADB 连接不可用。多个设备时必须显式选择。

需要后台自动恢复时启用普通用户服务，不需要 sudo：

```bash
systemctl --user enable --now android-computer-use-reconnect.service
```

长流程可以直接使用统一预检，避免每一步重新发现设备：

```bash
"$HOME/mobile-cuctl/mobile-cuctl" start android --keep-awake
"$HOME/mobile-cuctl/mobile-cuctl" stop android
```

每次坐标输入前都先截新图。部分厂商输入法会把 `text-ascii` 留在拼写/候选状态；检查操作后截图，仅在确认需要提交该文本时再发送 `KEYCODE_ENTER`。

完整操作说明见安装后的 `$HOME/android-computer-use/AGENTS.md`。

## iOS 准备

1. 安装 Python 3、`pymobiledevice3`、Node.js、Appium 和 XCUITest driver。
2. 使用 USB 连接并在设备上确认 Trust；需要自动化输入时启用 Developer Mode。
3. 准备一个针对目标设备签名的 WebDriverAgent IPA。仓库不会提供证书、私钥、provisioning profile 或已签名 IPA。
4. 配置实际文件和 bundle ID：

```bash
export IOS_CUCTL_WDA_IPA="$HOME/.local/share/ios-computer-use/artifacts/WebDriverAgentRunner.ipa"
export IOS_CUCTL_WDA_BUNDLE_ID="your.signed.WebDriverAgentRunner.xctrunner"
```

5. iOS 18+ 在 Linux 上使用输入和 accessibility 前需要保持 RemoteXPC tunnel 运行。首次提权会出现系统授权弹窗，这是正常的权限边界。

若是固定使用的 Linux 主机，建议一次性安装受限的 systemd tunnel 服务。服务仍以当前桌面用户运行，只获得创建 TUN 和路由所需的 `CAP_NET_ADMIN`，之后开机自启，Claude Code 日常操作不再出现 sudo/polkit 弹窗：

```bash
sudo install -m 0644 \
  "$HOME/ios-computer-use/ios-computer-use-tunneld@.service" \
  /etc/systemd/system/ios-computer-use-tunneld@.service
sudo systemctl daemon-reload
sudo systemctl enable --now "ios-computer-use-tunneld@$(id -un).service"
```

不要配置全局免密 sudo 或放宽 polkit。`CAP_NET_ADMIN` 仍属于主机网络管理权限，只是明显小于 root 权限；上述安装步骤只需授权一次，之后用普通用户检查：

```bash
"$HOME/ios-computer-use/ios-cuctl" tunnel-status
```

未安装上述 systemd 服务时，完全无线使用需在一个终端持续运行：

```bash
"$HOME/ios-computer-use/ios-cuctl" wifi-tunnel-start
```

显示 ready 后，另一个终端里的 `screenshot`、`press`、WDA/Appium 输入和元素命令会自动复用 Wi‑Fi RSD。用 `wifi-tunnel-status` 确认状态；通过真实截图和一次可逆 Home 键操作验收。首次仍建议保留 USB 完成 Trust、配对、DeveloperDiskImage 和 WDA 安装。

已安装上面的 systemd 服务时，不要再运行 `wifi-tunnel-start`；bridge 会从端口 `49151` 自动发现并复用常驻 tunnel。

长流程使用统一预检；`--input` 会在设备已解锁时预热一次 WDA，后续动作复用该会话：

```bash
"$HOME/mobile-cuctl/mobile-cuctl" start ios --input
"$HOME/mobile-cuctl/mobile-cuctl" stop ios
```

日常无线操作先运行 `tunnel-status`。`ready: true` 且只有一个 tunnel 时，直接使用 `screenshot`、`apps`、`activate` 或 `press`，不要重复发现、启动 tunnel 或启动 WDA；这些 CoreDevice 操作不会显示 Automation Running。`registry_ready: true` 但 `ready: false` 表示后台服务在线、手机 tunnel 不在线，此时让手机保持唤醒且 Wi-Fi 开启，并确认与主机处于同一局域网。

iOS 26 及更早版本的触控、文字输入和 accessibility 仍需要 Appium/WDA，除非已经准备好兼容 persistent preinstalled launch 的 WDA v13+ 包，否则 USB + WDA 最可靠；iOS 27+ 可直接使用 CoreDevice 触控。锁屏时可以尝试 CoreDevice 截图和硬件键，但屏幕休眠可能先得到全黑截图：发送一次可逆的 Home 键、重新截图，再由用户解锁后继续，不能绕过锁屏。

完整操作、环境变量和恢复说明见安装后的 `$HOME/ios-computer-use/AGENTS.md`。

## 录屏和定期清理

Android 可通过 `mobile-cuctl record android start|status|stop` 无窗口录屏；必须用 `stop` 正常封装文件。iOS 系统录屏仍由用户在控制中心授权开启和停止。

清理命令默认只预览，截图/UI dump 保留 7 天，Home bridge 自己的录屏保留 14 天；业务项目的 `artifacts/` 不在扫描范围内：

```bash
"$HOME/mobile-cuctl/mobile-cuctl" cleanup
"$HOME/mobile-cuctl/mobile-cuctl" cleanup --apply
```

## 更新与卸载

更新代码后重新运行：

```bash
git pull --ff-only
./install.sh --claude
```

安装器只替换它管理的控制器、操作指南和技能文件，并为不同内容的旧文件创建带时间戳的备份；不会删除 captures、runtime、状态文件或签名材料。

如需卸载，先停用用户级 Android 重连服务，再手动移除技能和 bridge 目录。删除前先保留其中需要的 captures、recordings、runtime 或本机配置：

```bash
systemctl --user disable --now android-computer-use-reconnect.service
rm "$HOME/.config/systemd/user/android-computer-use-reconnect.service"
systemctl --user daemon-reload
```

```text
~/.claude/skills/android-computer-use
~/.claude/skills/ios-computer-use
~/android-computer-use
~/ios-computer-use
~/mobile-cuctl
```
