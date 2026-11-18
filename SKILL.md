---
name: immersive-light-effect-development
description: Implements, reviews, debugs, and migrates HarmonyOS Immersive Light (沉浸光感), Spatial UI (空间化), HDS materials, and immersive windows in ArkTS/ArkUI. Use for HdsNavigation, HdsNavDestination, HdsTabs, hdsMaterial, uiMaterial, ImmersiveMaterial, systemMaterial, systemMaterialEffect, MaterialState, ohos.arkui.UIMaterial.state, colorInvert, materialColor, lightEffect, IMMERSIVE_GRADIENT_BLUR, dynamicHideTitleBar, MiniBar, adaptToHandedness (智感握姿), AlphabetIndexer, ChipGroup, SegmentButton, UI Design Kit, 系统材质, 液态玻璃, 背景沉浸, 全屏沉浸, 安全区, 状态栏, 挖孔, 折叠屏, 自由窗口标题栏, ignoreLayoutSafeArea, expandSafeArea, setWindowLayoutFullScreen, setWindowDecorVisible, and getWindowAvoidArea.
license: MIT
---

# 沉浸光感与窗口沉浸

## 选择实现路径

- **HDS 组件材质**适用于 HarmonyOS 6.1.0（API 23）起的 HDS 标题栏按钮和悬浮底部页签。使用 `@kit.UIDesignKit`，在标题栏样式或 `HdsTabs.barFloatingStyle` 中配置 `systemMaterialEffect`。默认选择 `MaterialType.ADAPTIVE` 和 `MaterialLevel.ADAPTIVE`；指定 `EXQUISITE` 或 `GENTLE` 前先检查 `getSystemMaterialTypes()` 是否包含 `IMMERSIVE`，否则使用 `SMOOTH` 等级。
- **ArkUI 系统材质**适用于普通 `Navigation`、`NavDestination`、`Tabs`、弹窗及支持的控件。编译 SDK 须提供相应声明，使用该能力的构建产品须满足 `targetSdkVersion >= 26.0.0`。兼容更低运行时版本时，在构造和使用新 API 前通过 `deviceInfo.apiAvailable('26.0.0')` 保护，再以 `uiMaterial.isImmersiveMaterialSupported()` 判断设备支持情况；不支持时走独立的标准背景或模糊分支。材质视效随设备算力和系统光感档位自动适配。
- **窗口及安全区**适用于背景延伸、内容铺满、系统栏、挖孔和自由窗口。仅延伸背景时优先使用 `.background(...)`，局部沿边绘制使用 `.expandSafeArea(...)`，单页内容覆盖避让区使用 `.ignoreLayoutSafeArea(...)` 并配合 `LayoutPolicy.matchParent` 手动留出交互区域。仅当所有页面都需要全屏布局时使用 `setWindowLayoutFullScreen(true)`。

HDS 与 ArkUI 组件可保留在各自原有的导航结构内。同时实现窗口沉浸和材质时，先确定安全区及可交互区域，再配置有效范围内的组件材质。

## 工作流

1. 检查实际构建产品的 `build-profile.json5`、模块 `module.json5`、`oh-package.json5` 和 SDK 类型声明，记录 `runtimeOS`、`compatibleSdkVersion`、`targetSdkVersion`、设备类型，以及 `entry` 模块中 `ohos.arkui.UIMaterial.state` 的配置。
2. 对现有项目运行 `python3 <skill-dir>/scripts/audit_hds_effects.py <project-root>`（需要机器可读结果时加 `--json`），结合实际组件树、产品配置和互斥分支逐项核实提示。
3. 按 [材质接入与排障](references/hds-material.md) 配置材质、导航栏与底栏结构；修改 `.ets` 前加载项目适用的 ArkTS/ArkUI 开发指引；涉及安全区、浮窗与多设备窗口时按 [窗口沉浸](references/immersive-window.md) 实现。
4. 按 [验收清单](references/quality-checklist.md) 检查生效范围、降级、可读性和功耗，在项目现有工具链构建后，于目标设备或模拟器验证滚动、切页、旋转、小窗、深浅色、减弱动画及离页恢复。

## 生效范围与组件规则

- **生效区域限制**：`Navigation`/`NavDestination` 标题栏和横向底部 `Tabs` 的 `TabBar` 内支持普通控件挂载材质；指定弹窗（`AlertDialog`、`ActionSheet`、`CustomDialog`、各类 `PickerDialog`、`SelectionMenu`、`AlphabetIndexer` 提示气泡、`Text` 的 `copyOption` 菜单）、弹窗接口（`PromptAction`、`ArkUI_NativeDialog`、`@ohos.promptAction`、`Popup`、`Tips`、`Menu`、`bindSheet`）以及 `Slider`、`Toggle`（`Switch`/`Button`）、`Select` 可在全页面生效。其余控件在内容区直接设置会失效并输出 `Material inactive: out of scope`；内容区分类栏需呈现在顶栏材质内时，在滑入标题栏后切换到 `title` builder 中渲染。
- **应用开关与恢复默认**：`ohos.arkui.UIMaterial.state`（`default` / `enable` / `disable`）仅在 `entry` 模块生效。`disable` 会阻止 ArkUI 组件级接入；允许接入时，单独关闭支持该配置的组件须传入 `uiMaterial.Material.empty`，传 `undefined` 表示恢复当前模式下的默认行为。应用内材质开关与设备支持探测共用同一判定条件，开启时背板设 `Color.Transparent`，关闭或不支持时同步恢复主题实体背景。
- **专用入口与类型约束**：标准标题栏 `systemMaterial` 作用于系统返回键和非自定义菜单；标准 `Tabs` 悬浮背板配置在 `FloatingTabBarStyle.systemMaterial` 中，须同时满足 `barOverlap(true)`、`vertical(false)` 和 `barPosition(BarPosition.End)`。`AlphabetIndexer` 保留气泡默认材质时须省略 `popupBackground` 和 `popupBackgroundBlurStyle`（横屏或分屏配合 `autoCollapse`）。自定义弹窗优先核对重载：`PromptAction.openCustomDialog({ builder, systemMaterial })` 作用于系统背板；传入 `ComponentContent` 的重载、`openCustomDialogWithController` 与 `customStyle: true` 使用自定义弹窗背板，不自动应用系统背板材质。
- **属性顺序与互斥规则**：`.systemMaterial(...)` 须放置在宽高、圆角、背景等样式链末尾，保持背板可见并排除不透明 `backgroundColor` 与同背板模糊属性。`materialColor` 须使用带透明度的颜色；需要自定义 `.shadow(...)` 时在 `ImmersiveOptions` 中设置 `applyShadow: false`；`colorInvert: true` 仅在高/中算力设备、`THIN` 或 `ULTRA_THIN` 样式且子组件使用 `$r('sys.color.xxx')` 特殊可反色系统资源时生效。

## 导航、底栏与视觉性能

- **厚度选型与功耗控制**：仅在悬浮重叠的交互层使用材质，设计起点为顶部悬浮 `ULTRA_THIN`、底部悬浮 `THIN`、常规默认 `REGULAR`、临时浮层/菜单/`Toast`/索引条气泡 `THICK`、半模态与较大弹窗 `ULTRA_THICK`。控制材质面积与弹窗尺寸，禁止同一子树嵌套材质、禁止同一背板叠加模糊、避开视频或动图等持续更新背景，局部使用 `colorInvert`；通过 `readonly` 字段或按主题缓存键复用材质实例，避免在 `build()` 或高频回调中反复新建实例。
- **滚动标题栏分层**：采用「导航容器 `BarStyle.STACK` + `ScrollEffectType.GRADUAL_BLUR` 渐进模糊底层 + 可选 `HitTestMode.None` 与 `accessibilityLevel('no')` 渐变衬底 + 返回/操作圆钮及顶栏胶囊 `ULTRA_THIN` 材质」分层结构；自定义浅/深色背景时用 `WithTheme({ theme: { colors: { compBackgroundGray: pageColor } } })` 包裹导航容器消除原生模糊灰底色偏；标题栏外层容器设 `.clip(false)` 避免材质阴影被裁切。根据正文是否可滚入标题栏下（`scrollUnderTitle`）分别配置滚动区 `contentStartOffset` 与主体容器顶部 padding。
- **多页签与悬浮底栏**：窄屏下每个 `TabContent` 包裹独立 `Navigation` 隔离各页滚动模糊状态，宽屏断点可切换为外层共享顶栏、侧栏或独立桌面工作区。悬浮 `Tabs` 须避免设置通用 `.barWidth('100%')`，按 `FloatingTabBarStyle.barWidth` 或原生宽度保持胶囊形态；结合实际布局底边、安全区避让与 `getWindowStatus()` / `windowStatusDidChange`（含 `FLOATING` 小窗）调整底部边距与偏移，并通过 `accessibility` 减弱动画状态同步控制切页与转场动画。
- **HDS 空间动效与来源**：HDS 标题栏渐变模糊（`IMMERSIVE_GRADIENT_BLUR` / `GRADIENT_BLUR`）和 `dynamicHideTitleBar` 须通过 `.bindToScrollable(...)` 绑定实际滚动容器；使用 `MiniBar` 或 `adaptToHandedness`（智感握姿）时验证窄屏折叠、宽屏展开及左右布局。官方来源与 API 核对索引见 [官方来源](references/sources.md)。
