---
name: immersive-light-effect-development
description: Implements, reviews, debugs, and migrates HarmonyOS Immersive Light (沉浸光感), Spatial UI (空间化), HDS materials, and immersive windows in ArkTS/ArkUI. Use for HdsNavigation, HdsNavDestination, HdsTabs, hdsMaterial, uiMaterial, ImmersiveMaterial, systemMaterial, systemMaterialEffect, MaterialState, ohos.arkui.UIMaterial.state, colorInvert, materialColor, lightEffect, IMMERSIVE_GRADIENT_BLUR, dynamicHideTitleBar, MiniBar, adaptToHandedness (智感握姿), AlphabetIndexer, ChipGroup, SegmentButton, UI Design Kit, 系统材质, 液态玻璃, 背景沉浸, 全屏沉浸, 安全区, 状态栏, 挖孔, 折叠屏, 自由窗口标题栏, ignoreLayoutSafeArea, expandSafeArea, setWindowLayoutFullScreen, setWindowDecorVisible, and getWindowAvoidArea.
license: GPL-3.0-only
---

# 沉浸光感与窗口沉浸

## 选择实现路径

- **HDS 组件材质**适用于 HarmonyOS 6.1.0（API 23）起的 HDS 标题栏按钮和悬浮底部页签。使用 `@kit.UIDesignKit`，在标题栏样式或 `HdsTabs.barFloatingStyle` 中配置 `systemMaterialEffect`。默认选 `MaterialType.ADAPTIVE` 和 `MaterialLevel.ADAPTIVE`。需要指定 `EXQUISITE` 或 `GENTLE` 时，先检查 `getSystemMaterialTypes()` 是否包含 `IMMERSIVE`，否则使用 `SMOOTH` 等级。
- **ArkUI 系统材质**适用于普通 `Navigation`、`NavDestination`、`Tabs`、弹窗及支持的控件。编译 SDK 须提供相应声明，`targetSdkVersion` 须达到 `26.0.0`。兼容更低版本时，在访问新 API 前使用 `deviceInfo.apiAvailable('26.0.0')`。再用 `uiMaterial.isImmersiveMaterialSupported()` 判断设备支持情况。旧系统或不支持的设备可走单独的标准背景或模糊分支。系统自动处理支持设备的算力等级和用户光感强度。
- **窗口及安全区**适用于背景延伸、内容铺满、系统栏、挖孔和自由窗口。仅延伸背景时优先检查 `.background(...)`，局部沿边绘制用 `.expandSafeArea(...)`，单页内容覆盖避让区用 `.ignoreLayoutSafeArea(...)` 并为交互内容留出可用区域。只有需求涉及窗口所有页面时才使用 `setWindowLayoutFullScreen(true)`。

HDS 和 ArkUI 组件可保留在各自原有的导航结构内。需要同时实现窗口沉浸和材质时，先确定安全区及可交互区域，再选择材质所在的组件。

## 工作流

1. 检查实际构建产品的 `build-profile.json5`、模块 `module.json5`、`oh-package.json5` 和 SDK 类型声明，记录运行平台、SDK 兼容下限和目标版本。定位组件的真实挂载点及状态来源，检查 `entry` 模块中的 `ohos.arkui.UIMaterial.state`。
2. 对现有项目可运行 `python3 <skill-dir>/scripts/audit_hds_effects.py <project-root>`，使用 `--json` 获取结构化结果。结合实际组件树、产品配置和互斥分支确认每条提示。
3. 按 [材质接入与排障](references/hds-material.md) 选择专用接口、可见层、样式与降级。复用现有标准 ArkUI 导航、悬浮底栏或桌面工作区时，按 [四项目实战](references/project-patterns.md) 选结构。修改 `.ets` 前加载项目适用的 ArkTS/ArkUI 开发指引。涉及安全区和多设备窗口时读取 [窗口沉浸](references/immersive-window.md)。
4. 按 [验收清单](references/quality-checklist.md) 检查生效范围、降级、可读性和功耗。在项目现有工具链里构建，按目标设备验证滚动、切页、旋转及窗口状态。涉及全屏或系统栏配置时检查离页恢复。交付时记录实际通过的检查和待验证的设备场景。

## 生效范围与常见故障

- 普通控件的材质生效位置是 `Navigation` / `NavDestination` 标题栏或横向 `Tabs` 的底部 `TabBar`。指定弹窗、`Slider`、`Toggle`（`Switch` / `Button`）和 `Select` 可在全页面生效。出现 `Material inactive: out of scope` 时，优先检查组件挂载点。滚动中的分类栏可在进入标题区时切换至标题栏 builder。
- 标准标题栏的 `systemMaterial` 作用于系统返回键和非自定义菜单。自定义标题栏控件按各自接口配置。标准 `Tabs` 的悬浮背板通过 `barFloatingStyle.systemMaterial` 设置，须同时满足 `barOverlap(true)`、`vertical(false)`、`barPosition(BarPosition.End)`。
- 应用级材质配置只在 `entry` 生效。`default` 和 `enable` 各有默认开启的组件及条件，`disable` 会关闭 ArkUI 组件级接入。支持组件级配置的组件用 `uiMaterial.Material.empty` 单独关闭，用 `undefined` 恢复该组件当前模式下的默认行为。
- `AlphabetIndexer` 的材质作用在 `usingPopup` 打开的提示气泡。保留默认材质时省略 `popupBackground` 和 `popupBackgroundBlurStyle`。检查高/中算力的 `THICK` 与低算力的白底表现。横屏或分屏使用 `autoCollapse`，按扣除系统栏和底部工具栏后的可用区域布置索引条。
- 自定义弹窗优先核对重载。系统背板材质用 `PromptAction.openCustomDialog({ builder, systemMaterial })`。传入 `ComponentContent` 的重载、`openCustomDialogWithController` 和 `customStyle: true` 的背板由开发者负责。
- 样式设置后再调用通用 `.systemMaterial(...)`。保持背板可见，排除不透明背景、叠加模糊和自绘内容层遮挡。使用自定义阴影时设 `applyShadow: false`。自动反色须使用 `THIN` / `ULTRA_THIN`、支持反色的系统资源和属性，并在高/中算力设备核对实际触发效果。

## 视觉与性能

- 为与滚动内容重叠的交互层使用材质。设计起点为顶部悬浮 `ULTRA_THIN`、底部悬浮 `THIN`、临时浮层 `THICK`、半模态和弹窗 `ULTRA_THICK`。通用构造默认 `REGULAR`。先确认该位置支持材质，再根据背景复杂度和文字对比度选厚度。
- 将材质和自动反色限制在需要的区域。同一子树用一层材质，弹窗尺寸适中，避开视频、动图等持续更新的背景。保持材质实例、参数和子树稳定。标题栏滚动渐变可与局部按钮材质配合，按钮背板避免额外的背景模糊。
- 滚动标题栏由对应导航容器持有模糊，局部交互控件配置材质。正文可滚到栏下时用 `contentStartOffset` 和 `contentEndOffset` 留出首尾空间。固定搜索、筛选或编辑器按栏高避让。悬浮底栏按实际布局底边和窗口状态计算边距。
- HDS 的渐变模糊与动态显隐按所用组件绑定实际滚动容器。使用 MiniBar 或智感握姿时验证窄屏折叠、宽屏展开和支持设备的左右布局。
- 官方指南、API 参考和示例出处见 [官方来源](references/sources.md)。字段、重载和起始版本以项目 SDK 与对应 API 文档为准。
