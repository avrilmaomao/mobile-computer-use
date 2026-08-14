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
~/android-computer-use/AGENTS.md
~/ios-computer-use/ios-cuctl
~/ios-computer-use/wda-runner
~/ios-computer-use/AGENTS.md
```

如果 Claude Code 启动时 `~/.claude/skills` 目录尚不存在，安装后重新启动一次 Claude Code。已存在的技能目录通常支持热加载。

## 验证发现

在 Claude Code 中可直接输入：

```text
/android-computer-use 检查已连接的安卓手机
/ios-computer-use 检查已连接的 iPhone
```

也可以用自然语言触发，例如“截一张安卓手机当前屏幕”或“打开 iPhone 上的某个 App 并检查页面”。Claude 应先读取安装在 home 目录中的 `AGENTS.md`，再运行 `doctor` 和 `devices`。

在 shell 中先做只读验证：

```bash
"$HOME/android-computer-use/android-cuctl" --help
"$HOME/android-computer-use/android-cuctl" doctor

"$HOME/ios-computer-use/ios-cuctl" --help
"$HOME/ios-computer-use/ios-cuctl" doctor
```

技能不会绕过 Claude Code 自身的工具授权、操作系统权限、手机 Trust/RSA 提示、锁屏、PIN、Face ID/Touch ID 或 App 登录边界。

## Android 准备

1. 安装 `adb`；需要镜像窗口时再安装 `scrcpy`。
2. 手机上打开开发者选项和 USB debugging，连接数据线并确认 RSA 指纹。
3. Android 11+ 可使用 Wireless debugging：先 `pair`，再用主界面显示的调试端口执行 `connect`。
4. 多设备在线时设置精确的 `ANDROID_SERIAL`，不要让 agent 猜设备。

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

完整操作、环境变量和恢复说明见安装后的 `$HOME/ios-computer-use/AGENTS.md`。

## 更新与卸载

更新代码后重新运行：

```bash
git pull --ff-only
./install.sh --claude
```

安装器只替换它管理的控制器、操作指南和技能文件，并为不同内容的旧文件创建带时间戳的备份；不会删除 captures、runtime、状态文件或签名材料。

如需卸载，手动移除以下两个技能目录和两个 bridge 目录。删除前先保留其中需要的 captures、runtime 或本机配置：

```text
~/.claude/skills/android-computer-use
~/.claude/skills/ios-computer-use
~/android-computer-use
~/ios-computer-use
```
