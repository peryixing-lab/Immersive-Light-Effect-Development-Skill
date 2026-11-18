# HarmonyOS 沉浸光感 Skill

用于在 HarmonyOS ArkTS 工程中接入和排查 HDS 材质、ArkUI 沉浸光感、悬浮底栏与窗口沉浸的 Agent Skill。

- **选对材质接口**。HDS 组件材质从 HarmonyOS 6.1.0（API 23）起支持。标准 ArkUI `uiMaterial` 从 API 26.0.0 起支持，需结合目标 SDK、设备能力和组件生效范围。
- **处理真实布局**。覆盖滚动标题栏、悬浮 `Tabs`、索引条、深浅色、应用材质开关、手机小窗、折叠屏和自由窗口三键区。
- **定位常见问题**。提供只读审计脚本和验收清单，用于检查版本配置、材质冲突和窗口生命周期。

## 安装

[Claude Code](#claude-code) · [DeepSeek Harness](#deepseek-harness) · [OpenCode](#opencode) · [Codex](#codex) · [其他 Agent](#其他-agent) · [DevEco Code](#deveco-code) · [WorkBuddy](#workbuddy)

### Claude Code

在目标工程根目录运行。需要 Node.js 和 npm。

```bash
npx skills add peryixing-lab/immersive-light-effect-development --skill immersive-light-effect-development --agent claude-code
```

加上 `--global` 可安装到 `~/.claude/skills/`。手动安装时，把完整技能目录放入工程的 `.claude/skills/` 或全局 `~/.claude/skills/`。新会话中可输入 `/immersive-light-effect-development`。 [Claude Code Skills 文档](https://code.claude.com/docs/en/skills)

### DeepSeek Harness

将 Skill 安装到 DeepSeek Harness 的全局目录，再通过 `dsh` 打开目标工程。以下命令适用于 macOS/Linux。

```bash
dsh_skill_root="${DSH_HOME:-$HOME/.dsh}/skills"
mkdir -p "$dsh_skill_root"
git clone --depth 1 https://github.com/peryixing-lab/immersive-light-effect-development.git \
  "$dsh_skill_root/immersive-light-effect-development"
```

默认入口为 `~/.dsh/skills/immersive-light-effect-development/SKILL.md`。仅为当前工程安装时，复制完整目录到工程根的 `.dsh/skills/`。重新打开会话后可按名称调用。如果该目录是用上面的 `git clone` 安装的，可用 `git -C "$dsh_skill_root/immersive-light-effect-development" pull --ff-only` 更新。 [DeepSeek Harness 技能目录](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.zh.md)

### OpenCode

```bash
npx skills add peryixing-lab/immersive-light-effect-development --skill immersive-light-effect-development --agent opencode
```

手动安装可以把完整目录放入工程的 `.opencode/skills/`，或全局 `~/.config/opencode/skills/`。在 OpenCode 新会话里指明技能名称。 [OpenCode Skills 文档](https://opencode.ai/docs/skills/)

### Codex

```bash
npx skills add peryixing-lab/immersive-light-effect-development --skill immersive-light-effect-development --agent codex
```

工程级安装目录是 `.agents/skills/`，全局目录是 `~/.agents/skills/`。打开目标工程后可用 `$immersive-light-effect-development` 点名。 [Codex Skills 文档](https://developers.openai.com/codex/skills)

### 其他 Agent

在工程根目录执行下列命令并选择 Agent。需要在多个工程中使用时，加上 `--global`。

```bash
npx skills add peryixing-lab/immersive-light-effect-development --skill immersive-light-effect-development
```

自动化或脚本安装可显式指定 `--agent`。以下示例任选一行。

```bash
skill_repo=peryixing-lab/immersive-light-effect-development
skill_name=immersive-light-effect-development

npx skills add "$skill_repo" --skill "$skill_name" --agent cursor          # Cursor
npx skills add "$skill_repo" --skill "$skill_name" --agent gemini-cli      # Gemini CLI
npx skills add "$skill_repo" --skill "$skill_name" --agent github-copilot  # GitHub Copilot
npx skills add "$skill_repo" --skill "$skill_name" --agent windsurf        # Windsurf
npx skills add "$skill_repo" --skill "$skill_name" --agent antigravity     # Antigravity
npx skills add "$skill_repo" --skill "$skill_name" --agent kiro-cli        # Kiro CLI
npx skills add "$skill_repo" --skill "$skill_name" --agent trae            # Trae
npx skills add "$skill_repo" --skill "$skill_name" --agent trae-cn         # Trae 中国版
npx skills add "$skill_repo" --skill "$skill_name" --agent codebuddy       # CodeBuddy
npx skills add "$skill_repo" --skill "$skill_name" --agent qoder           # Qoder
npx skills add "$skill_repo" --skill "$skill_name" --agent qoder-cn        # Qoder 中国版
npx skills add "$skill_repo" --skill "$skill_name" --agent cline           # Cline
npx skills add "$skill_repo" --skill "$skill_name" --agent roo             # Roo Code
npx skills add "$skill_repo" --skill "$skill_name" --agent amp             # Amp
npx skills add "$skill_repo" --skill "$skill_name" --agent zed             # Zed
```

Gemini CLI 也可直接运行 `gemini skills install https://github.com/peryixing-lab/immersive-light-effect-development.git`，随后用 `/skills list` 核对。其他支持 Agent Skills 的工具可查看 CLI 的支持列表，或把完整目录复制到工具的 Skill 目录。 [Vercel Skills CLI 支持列表](https://github.com/vercel-labs/skills/blob/main/docs/agents.md) · [Gemini CLI Skills 文档](https://geminicli.com/docs/cli/skills/)

### DevEco Code

下载或克隆本仓库，将完整 Skill 复制到 HarmonyOS 工程的 `.deveco/skills/immersive-light-effect-development/`。以下命令从目标工程根目录运行，要求 Git、tar 和 POSIX Shell。

```bash
skill_checkout="$(mktemp -d)"
git clone --depth 1 https://github.com/peryixing-lab/immersive-light-effect-development.git "$skill_checkout"
mkdir -p .deveco/skills
git -C "$skill_checkout" archive --prefix=immersive-light-effect-development/ HEAD \
  | tar -x -C .deveco/skills
```

重新打开工程后，在 DevEco Code 中按名称调用。如果工具使用自定义 Skill 路径，可按它的配置将同一目录注册到 `skills.paths`。

### WorkBuddy

在 WorkBuddy 打开「技能 → 添加技能 → 上传技能」，选择包含 `SKILL.md` 的本地技能文件夹或 ZIP 包。克隆本仓库后，可从仓库根目录生成 ZIP。

```bash
git archive --format=zip --output=../immersive-light-effect-development.zip HEAD
```

上传生成的 ZIP 后，在已安装技能中搜索 `immersive-light-effect-development`。 [WorkBuddy 技能文档](https://cloud.tencent.com/document/product/1831/134432)

## 使用示例

打开 HarmonyOS 工程，发出类似请求。

> 使用 immersive-light-effect-development 检查当前工程的 SDK 和材质配置。为首页实现原生滚动标题栏和悬浮底部页签，保留现有导航结构，并说明小窗与低版本的降级方式。

> 排查当前 `Tabs` 浮栏上移或拉满的问题。先核对安全区、悬浮条件和底栏锚点，然后给出最小修改。

也可以用 Python 3 单独运行静态审计。

```bash
python3 scripts/audit_hds_effects.py /path/to/harmonyos-project
python3 scripts/audit_hds_effects.py /path/to/harmonyos-project --json
```

脚本提示需要人工核查的代码位置。材质实际效果、系统光感偏好、小窗和性能仍需在目标设备或模拟器上验证。

## 仓库内容

- [SKILL.md](SKILL.md) 提供接入步骤和按场景加载的参考。
- [材质接入与排障](references/hds-material.md) 覆盖 HDS、ArkUI、兼容、功耗及导航布局。
- [窗口沉浸](references/immersive-window.md) 覆盖安全区、浮窗避让和窗口装饰。
- [验收清单](references/quality-checklist.md) 与 [官方来源](references/sources.md) 用于复测和核对 API。

## 许可证

仓库中的原创文档和审计脚本采用 [MIT 许可证](LICENSE)。参考的官方文档及第三方示例适用各自的版权和许可。
