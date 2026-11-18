# HarmonyOS 沉浸光感 Skill

> 专治鸿蒙液态玻璃与窗口沉浸开发中的各种「玄学现场」——让你的 Coding Agent 先查 SDK 再写代码，写完还能自带静态体检。

想在 HarmonyOS 6.1+（API 23）到 API 26 之间给应用加上通透的**沉浸光感（Immersive Light）**、空间化导航和自适应窗口避让，实际写起来却常常画风突变：

- 写完 `.systemMaterial(...)` 信心满满一运行，效果纹丝不动，日志里冷冷飘来一句 `Material inactive: out of scope`；
- 想关掉某个组件自带的默认光感，传了个 `undefined` 以为收工，结果它反而倔强地恢复了默认材质（真想关，得请出 `uiMaterial.Material.empty`）；
- 给悬浮 `Tabs` 顺手加了 `.barWidth('100%')` 或漏配 `ignoreLayoutSafeArea` / `expandSafeArea`，胶囊底栏直接拉成大板砖，或者向上「起飞」一个状态栏高度；
- `hdsMaterial`（API 23+）和 `uiMaterial`（API 26.0.0+）接口傻傻分不清，旧版本忘了套 `deviceInfo.apiAvailable(...)` 保护；
- 自由窗口三键区明明写了避让，却把本来就是 `vp` 的 `TitleButtonRect` 又拿 `px2vp` 除了一遍，按钮成功撞在一起；
- 一不小心在播放视频上糊玻璃、同一背板叠两层模糊、或者在 `build()` 里反复 `new` 材质实例，GPU 功耗原地起飞。

**`immersive-light-effect-development`** 就是给你的 AI 编程搭档配好的「鸿蒙光感防踩坑领航员」——把官方双体系规范、实战布局套路和只读审计脚本打包成一份可直接调度的 Agent Skill。

---

## 这个 Skill 能帮你搞定什么？

- **双体系选型不迷路**：分清 HarmonyOS 6.1.0（API 23+）`@kit.UIDesignKit` 的 `hdsMaterial` 与 API 26.0.0+ `@kit.ArkUI` 的 `uiMaterial`，自动补齐 `deviceInfo.apiAvailable(...)`、`getSystemMaterialTypes()` 与 `isImmersiveMaterialSupported()` 探测及低版本降级分支。
- **材质与安全区协同到位**：覆盖 `HdsNavigation` / `Navigation` 滚动渐进模糊、`HdsTabs` / `Tabs` 悬浮胶囊底栏、`MiniBar` 与智感握姿（`adaptToHandedness`）、索引条气泡、`.background()` / `.expandSafeArea()` / `.ignoreLayoutSafeArea()` 组合拳，以及手机小窗（`FLOATING`）、折叠屏、挖孔屏和自由窗口三键区避让。
- **把性能和细节焊在规范里**：自动规避子树嵌套材质、同背板重复模糊、不透明 `materialColor` 遮挡、`colorInvert` 反色条件、`applyShadow: false` 阴影冲突，并通过静态缓存复用材质实例。
- **自带静态「体检报告」**：内置只读脚本 [`scripts/audit_hds_effects.py`](scripts/audit_hds_effects.py)，一键扫描工程的 SDK 版本配置、材质/窗口信号以及 18 条高频翻车模式（支持 Markdown 与 `--json` 输出）。

---

## 安装

> 仓库地址：`peryixing-lab/Immersive-Light-Effect-Development-Skill`
> 安装后技能名称：`immersive-light-effect-development`

### 1. 一行命令极速安装（推荐）

只要你的环境安装了 **Node.js 22.20+**，在终端运行一条命令即可自动识别本机已安装的 Coding Agent 并完成配置：

```bash
# 全局安装（推荐：所有 HarmonyOS 工程直接可用）
npx skills add peryixing-lab/Immersive-Light-Effect-Development-Skill -g

# 仅安装到当前工程（适合团队随仓库共享）
npx skills add peryixing-lab/Immersive-Light-Effect-Development-Skill
```

想先白嫖体验一次、不落盘安装？也可以直接临时生成上下文 Prompt 或拉起 Agent：

```bash
npx skills use peryixing-lab/Immersive-Light-Effect-Development-Skill@immersive-light-effect-development
```

自动化脚本或只想装给指定工具时，加上 `-a <agent>` 和 `-y` 跳过交互确认，例如：

```bash
npx skills add peryixing-lab/Immersive-Light-Effect-Development-Skill -g -a claude-code -y
```

### 2. 主流 Coding Agent 对号入座

下表列出常用工具对应的 `--agent` 参数、默认目录与会话中的唤醒方式（完整支持列表见 [Vercel Skills CLI 文档](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)）：

| 工具 | `--agent` 参数 | 工程目录 | 全局目录（`-g`） | 会话中怎么叫它 |
|---|---|---|---|---|
| **Claude Code** | `claude-code` | `.claude/skills/` | `~/.claude/skills/` | 输入 `/immersive-light-effect-development` 或直接提问 |
| **Codex** | `codex` | `.agents/skills/` | `~/.agents/skills/` | 输入 `$immersive-light-effect-development` 点名 |
| **Cursor** | `cursor` | `.agents/skills/` | `~/.cursor/skills/` | 对话中提及技能或描述光感需求自动触发 |
| **OpenCode** | `opencode` | `.agents/skills/` | `~/.config/opencode/skills/` | 在新会话中说明使用该技能名称 |
| **Antigravity** | `antigravity` | `.agents/skills/` | `~/.gemini/config/skills/` | 直接描述鸿蒙光感需求，或点名该技能 |
| **Gemini CLI** | `gemini-cli` | `.agents/skills/` | `~/.gemini/skills/` | 自动触发，可用 `/skills list` 核对 |
| **GitHub Copilot** | `github-copilot` | `.agents/skills/` | `~/.copilot/skills/` | 在对话中点名技能或描述相关任务 |
| **Trae / Trae 中国版** | `trae` / `trae-cn` | `.trae/skills/` | `~/.trae/skills/` | 新会话中按名称或关键词触发 |
| **Cline / Zed** | `cline` / `zed` | `.agents/skills/` | `~/.agents/skills/` | 对话中提及技能或直接提问 |
| **其他工具** | `windsurf`、`kiro-cli`、`codebuddy`、`qoder`、`qoder-cn`、`roo`、`amp` 等 | 见[官方支持列表](https://github.com/vercel-labs/skills/blob/main/docs/agents.md) | 见[官方支持列表](https://github.com/vercel-labs/skills/blob/main/docs/agents.md) | 新会话中按名称或关键词触发 |

> 小提示：现代工具大多会同时扫描共享的 `.agents/skills/` 或 `~/.agents/skills/`。如果你用 `-g` 装在了 `~/.agents/skills/` 或 `~/.claude/skills/`，包括 **DevEco Code**、**DeepSeek Harness** 在内的多个工具都能直接复用，不必重复拷贝。

### 3. 特定工具 / 图形化 / 手动安装

如果你使用的是 HarmonyOS 专项工具或不想依赖 `npx`，可按对应方式快速接入：

[DevEco Code](#deveco-code) · [DeepSeek Harness](#deepseek-harness) · [Gemini CLI](#gemini-cli) · [WorkBuddy](#workbuddy) · [通用手动安装](#通用手动安装)

#### DevEco Code

- **方式 A（推荐，零重复配置）**：如果你已通过 `npx skills add ... -g` 安装到 `~/.agents/skills/` 或 `~/.claude/skills/`，DevEco Code 启动时会自动扫描并加载，无需额外操作。
- **方式 B（全局专属目录）**：克隆到 `~/.config/deveco/skills/`（注意是 `~/.config/deveco/`，而不是 `~/.deveco/`）：

  ```bash
  mkdir -p ~/.config/deveco/skills
  git clone --depth 1 https://github.com/peryixing-lab/Immersive-Light-Effect-Development-Skill.git \
    ~/.config/deveco/skills/immersive-light-effect-development
  ```

- **方式 C（仅当前 HarmonyOS 工程）**：从目标工程根目录执行（使用 `git archive` 导出，避免在工程内留下嵌套 `.git` 目录）：

  ```bash
  skill_checkout="$(mktemp -d)"
  git clone --depth 1 https://github.com/peryixing-lab/Immersive-Light-Effect-Development-Skill.git "$skill_checkout"
  mkdir -p .deveco/skills
  git -C "$skill_checkout" archive --prefix=immersive-light-effect-development/ HEAD \
    | tar -x -C .deveco/skills
  rm -rf "$skill_checkout"
  ```

> **生效提示**：DevEco Code 在启动时加载技能配置，安装或更新后请**重启 DevEco Code**。若目录放在其他位置，也可在 `deveco.json` 的 `skills.paths` 中追加路径。

#### DeepSeek Harness

如果你已安装到工程 `.agents/skills/` 或全局 `~/.agents/skills/`，DeepSeek Harness（`dsh`）会自动扫描识别；也可单独安装到 `$DSH_HOME/skills`（默认 `~/.dsh/skills/`）：

```bash
dsh_skill_root="${DSH_HOME:-$HOME/.dsh}/skills"
mkdir -p "$dsh_skill_root"
git clone --depth 1 https://github.com/peryixing-lab/Immersive-Light-Effect-Development-Skill.git \
  "$dsh_skill_root/immersive-light-effect-development"
```

仅限当前工程时，把完整目录复制到工程根目录的 `.dsh/skills/immersive-light-effect-development/`。详见 [DeepSeek Harness 技能目录文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.zh.md)。

#### Gemini CLI

除了 `npx skills add ... -a gemini-cli`，也可以直接使用 Gemini CLI 原生命令安装：

```bash
gemini skills install https://github.com/peryixing-lab/Immersive-Light-Effect-Development-Skill.git
```

安装完成后，在会话中输入 `/skills list` 核对即可。参考 [Gemini CLI Skills 文档](https://geminicli.com/docs/cli/skills/)。

#### WorkBuddy

适合纯图形界面上传：

1. 在 GitHub 仓库页面点击 **Code → Download ZIP**（或在本地克隆后运行下方的打包命令）：
   ```bash
   git archive --format=zip --output=../immersive-light-effect-development.zip HEAD
   ```
2. 在 WorkBuddy 中打开「技能 → 添加技能 → 上传技能」，选择本地技能目录或 ZIP 压缩包。
3. 上传完成后，在已安装技能中搜索 `immersive-light-effect-development`。参考 [WorkBuddy 技能文档](https://cloud.tencent.com/document/product/1831/134432)。

#### 通用手动安装

任何兼容 [Agent Skills 规范](https://agentskills.io) 的工具，只需把包含 `SKILL.md`、`references/`、`scripts/` 的完整目录重命名为 `immersive-light-effect-development`，放入该工具的技能根目录即可。

### 4. 检查、更新与卸载

```bash
# 查看已安装技能（全局加 -g）
npx skills list
npx skills list -g

# 检查远端是否有新版本
npx skills check

# 更新 / 卸载本技能（若之前是全局安装，卸载时需加 -g，更新可加 -g）
npx skills update immersive-light-effect-development
npx skills update -g
npx skills remove immersive-light-effect-development
npx skills remove -g immersive-light-effect-development
```

如果采用 `git clone` 方式安装在全局目录（如 `~/.config/deveco/skills/` 或 `~/.dsh/skills/`），直接拉取更新即可：

```bash
git -C ~/.config/deveco/skills/immersive-light-effect-development pull --ff-only
```

---

## 怎么用？试试这样向 Agent 提问

装好技能后，打开你的 HarmonyOS 工程，直接把下面这些真实开发场景丢给 Agent：

- **从零接入 + 版本兜底**
  > 使用 `immersive-light-effect-development` 检查当前工程的 SDK 与材质配置。为首页实现原生滚动标题栏和悬浮底部页签，保留现有导航结构，并说明手机小窗与低版本的降级方式。
- **救火排障（底栏飞走 / 材质不生效）**
  > 排查当前 `Tabs` 悬浮底栏上移、被拉满或报 `Material inactive: out of scope` 的问题。先核对安全区链路、悬浮条件和底栏锚点，再给出最小修改。
- **自由窗口与多设备适配**
  > 检查当前工程的避让区与自由窗口标题栏实现，确认 `TitleButtonRect` 单位、挖孔四边计算和生命周期注销有没有遗漏。

### 单独运行只读「体检脚本」

不启动 Agent 也能用 Python 3 对任意 HarmonyOS 工程做一次快速静态体检：

```bash
python3 scripts/audit_hds_effects.py /path/to/harmonyos-project
python3 scripts/audit_hds_effects.py /path/to/harmonyos-project --json
```

脚本会扫描 `build-profile.json5` 与 `.ets`/`.ts`/`.json5` 代码，标出版本配置风险、常见材质互斥冲突以及未注销的窗口监听。实际光感视效、系统档位（强/均衡/弱）、小窗表现与功耗仍需在真机或模拟器上实测验收。

---

## 仓库地图

| 文件 | 作用 |
|---|---|
| [`SKILL.md`](SKILL.md) | 技能总入口：接入决策、核心规则与标准工作流 |
| [`references/hds-material.md`](references/hds-material.md) | `hdsMaterial` vs `uiMaterial` 双体系详解、导航/底栏实战、功耗优化与常见问题速查 |
| [`references/immersive-window.md`](references/immersive-window.md) | `.background()` / `.expandSafeArea()` / `.ignoreLayoutSafeArea()` 矩阵、避让区与自由窗口三键区模板 |
| [`references/quality-checklist.md`](references/quality-checklist.md) | 上线前必过清单：生效范围、多设备形态、功耗控制与构建配置 |
| [`references/sources.md`](references/sources.md) | 对应的华为官方指南、API 参考与官方示例索引 |
| [`scripts/audit_hds_effects.py`](scripts/audit_hds_effects.py) | 只读静态审计脚本，快速定位配置与代码隐患 |

---

## 参考文档

- [Claude Code Skills 文档](https://code.claude.com/docs/en/skills)
- [Codex Skills 文档](https://developers.openai.com/codex/skills)
- [OpenCode Skills 文档](https://opencode.ai/docs/skills/)
- [DeepSeek Harness 技能目录文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.zh.md)
- [Gemini CLI Skills 文档](https://geminicli.com/docs/cli/skills/)
- [Vercel Skills CLI 支持列表](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)

## 许可证

仓库中的原创文档和审计脚本采用 [MIT 许可证](LICENSE)。参考的官方文档及第三方示例适用各自的版权和许可。
