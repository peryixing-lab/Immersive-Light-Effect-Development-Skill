# HDS 与沉浸光感视效验收

## 视觉与生效范围

- [ ] 材质用于交互层与内容重叠的局部区域（标题栏、悬浮底部页签、局部浮层/弹窗），而不是覆盖整页背景。
- [ ] 普通组件材质仅放在 `Navigation`/`NavDestination` 标题栏或横向 `Tabs`（`vertical: false`、`BarPosition.End`）底部 `TabBar`，日志中无 `Material inactive: out of scope` 警告。
- [ ] 厚度符合交互层的可读性需求。顶部悬浮从 `ULTRA_THIN` 开始，底部悬浮用 `THIN`，临时浮层用 `THICK`，半模态和弹窗用 `ULTRA_THICK`。
- [ ] 开启材质的组件未同时设置非透明 `backgroundColor` 或背景模糊遮挡材质，且 `.systemMaterial(...)` 放置在样式链末尾。
- [ ] `materialColor` 使用带透明度的颜色，未传入纯不透明颜色。
- [ ] 开启 `colorInvert: true` 时材质样式为 `THIN` 或 `ULTRA_THIN`，且文本/图标使用 `$r('sys.color.xxx')` 特殊可反色系统资源。
- [ ] 组件布局区域与可视区域已通过 `width`、`height`、`borderRadius` 或 `clipShape` 对齐。
- [ ] 逐项确认应用模式与组件默认行为。支持显式关闭的组件用 `uiMaterial.Material.empty`，`Select` 的按钮与菜单分别检查。`Popup`、`Tips` 和 `bindSheet` 需要显式配置。
- [ ] 自定义弹窗使用了支持系统背板的重载。若必须使用自定义背板，检查所选回退样式。
- [ ] `AlphabetIndexer` 目标为默认材质时，气泡保留默认背景。核对高/中算力 `THICK` 和低算力白底。使用品牌色气泡时核对对比度，横屏或分屏验证 `autoCollapse` 与索引位置。
- [ ] 自定义标题按钮的排版与阴影完整，装饰性渐变不覆盖控件点击与无障碍焦点。深浅主题下原生滚动模糊无明显色偏。
- [ ] 从已滚动页切到未滚动页，标题栏模糊和收束状态随当前页更新。跨页点击、重选回顶、返回与宽窄布局切换后，选中态和路由保持一致。
- [ ] 明暗模式、复杂图片背景和纯色背景下文字/图标均清晰。
- [ ] 支持系统光感设置的设备上，已检查强、均衡、弱三档的可读性和布局稳定性。
- [ ] 材质关闭或降级为 `SMOOTH` / 低算力样式 / 标准 ArkUI 背景后仍保留层级和交互反馈。
- [ ] 滚动内容穿过浮层时没有突兀分界、重复模糊或闪烁。

## 布局与交互

- [ ] 状态栏、导航指示条、挖孔、侧滑手势和键盘分别避让。底栏按实际布局底边计算间距，导航指示条没有重复扣除，列表末项可滚到浮栏上方并触达。
- [ ] 标准 `Tabs` 浮栏同时满足底部、横向、重叠条件，材质写在 `FloatingTabBarStyle` 中。验证原生胶囊宽度、状态栏延伸和底部锚点。
- [ ] 采用叠层标题栏时，首屏空间只预留一次。分别验证可滚穿顶栏的页面与固定搜索、筛选或编辑器页面。滑入顶栏的分类控件能来回切换，选中项和焦点状态正确。
- [ ] 按目标设备验证旋转方向、宽屏断点、折叠态与展开态。使用 `MiniBar` 或 `adaptToHandedness` 时检查实际宽度与左右布局。
- [ ] 分屏、手机和适用平板的 `WindowStatusType.FLOATING`、自由窗口与缩放下，核对底栏裁切和正文布局。手机全屏、手机小窗和平板小窗分别验证偏移量。
- [ ] 自由窗口三键区使用 `TitleButtonRect` 的 vp 值，窗口避让和尺寸的 px 独立转换。缩放前后标题、搜索与主要操作都避开三键区。
- [ ] 隐藏系统栏的页面离开后会恢复系统栏。
- [ ] 修改窗口装饰后，在退出或中途失败时恢复原始显隐、高度和按钮样式，验证主窗口及独立子窗口。
- [ ] `avoidAreaChange`、`windowTitleButtonRectChange`、`windowSizeChange`、`windowStatusDidChange`、`onAnimationReduceStateChange` 等监听器使用具名回调并在对称生命周期注销。

## 性能与功耗

- [ ] HDS 默认使用自适应类型和等级。显式选择 `EXQUISITE` 或 `GENTLE` 时已查 `IMMERSIVE` 成员，并提供 `SMOOTH` 等级回退。
- [ ] 材质参数稳定，按需复用材质实例。主题、选中态、应用开关和设备不支持的分支分别核对材质及背景，切换后保留可读性和交互。
- [ ] 同一子树仅在最外层设置一次沉浸式系统材质，不存在内外层材质嵌套。
- [ ] 同一背板未重复应用材质和背景模糊，材质与旧版模糊回退处于互斥分支。
- [ ] 如需自定义 `.shadow(...)`，已在 `ImmersiveOptions` 中设置 `applyShadow: false`。
- [ ] `Dialog` / `Menu` 弹窗保持合理尺寸，未接近全屏绘制（避免空间形变与流光动效高开销）。
- [ ] 未将沉浸式系统材质固定悬浮在播放中的视频、动图或持续动画内容上方。
- [ ] `colorInvert: true` 仅包裹局部需要反色的组件，未在包含大量列表项的容器外层整体开启。
- [ ] 材质参数（`style`、`materialColor` 等）及材质子树保持稳定，未在定时器或滚动高频回调中反复重设。
- [ ] 列表滚动、旋转、折叠切换、窗口缩放期间无明显掉帧，在强档与低算力设备上观察温升与能耗；必要时用 DevEco Profiler / SmartPerf 记录帧时间。

## 构建与版本

- [ ] 记录 `runtimeOS`、`compileSdkVersion`、`compatibleSdkVersion`、`targetSdkVersion` 及 `entry` 模块 `ohos.arkui.UIMaterial.state` 配置。
- [ ] HDS API 23 能力按实际接口版本保护。使用 ArkUI 沉浸光感的产品满足 `targetSdkVersion >= 26.0.0`，兼容更早运行时的新 API 调用在 `deviceInfo.apiAvailable('26.0.0')` 内。用于选择视觉降级时已单独检查设备对 `ImmersiveMaterial` 的支持。
- [ ] 各构建产品的 SDK 均提供所用接口，设备覆盖相应系统能力。
- [ ] 以项目现有 DevEco / Hvigor / Node 版本构建，未擅自升级工程。
- [ ] 真机或模拟器覆盖目标设备；Previewer 结果不作为最终结论。

## 交付摘要

完成后用以下顺序汇报：

1. 采用的材质方案（HDS `hdsMaterial` / ArkUI `uiMaterial` / 应用级开关）与窗口沉浸层级。
2. 最低 API、`targetSdkVersion`、运行平台和设备能力假设。
3. 能力探测与低版本/低算力降级路径。
4. 修改文件和关键生命周期恢复点。
5. 构建/审计结果。
6. 尚需真机验证的设备与窗口模式。
