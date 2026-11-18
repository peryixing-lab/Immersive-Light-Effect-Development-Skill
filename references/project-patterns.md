# 四个 HarmonyOS 项目的沉浸光感实战

四个项目均以 HarmonyOS API 26.0.0 为目标和兼容下限，`entry` 模块均配置 `ohos.arkui.UIMaterial.state = enable`。这里的标题栏和底栏使用标准 ArkUI `Navigation`、`NavDestination`、`Tabs` 与 `uiMaterial`。项目中的 38/40vp、56/64vp、840vp 和窗口偏移是各自的设计参数。兼容早期系统的项目应在构造和使用新材质前检查 API 版本。

## 按现有页面结构选方案

- **同一组页签在窄屏用底栏，宽屏移到顶部**。带共享顶栏的工具应用 窄屏每个 `TabContent` 有自己的 `Navigation`，宽屏由外层 `Navigation` 持有共享顶栏，各页直接提供 `Scroll`。词库应用 在达到 840vp 的平板和 2in1 使用该结构，其他达到断点的设备可使用侧栏并保留各页的标题栏。
- **同一组页签在宽屏移到侧栏，模块还要控制二级页是否显示底栏**。带侧栏的工具应用 保留 `Tabs` 的内容承载，宽屏显示独立导航轨。窄屏的二级页按路由决定是否通过 `barHeight(0)`、`barOverlap(false)` 和移除悬浮配置隐藏底栏。仍需跨模块导航的编辑流程可保留主导航。
- **宽屏成为独立桌面工作区**。多窗口笔记应用 窄屏使用各页独立的滚动标题，宽屏切入 桌面工作区组件，按页面映射选择状态并处理编辑器及原生窗口按钮。复用此模式时，让两种界面共享业务路由与选中状态，维护各自的布局和滚动容器。
- **侧栏直接位于内容区**。用普通主题背景、圆角和选中态维持可读性，给触摸、鼠标和键盘提供相同的导航动作。词库应用 的侧栏已有键盘激活处理，其内容区 `.systemMaterial(...)` 调用需要按官方材质生效区域判断，普通内容区侧栏以主题背板作为可用方案。

## 原生滚动标题栏

1. **由导航容器绘制滚动模糊**。使用 `BarStyle.STACK` 与 `scrollEffectOptions.scrollEffectType: ScrollEffectType.GRADUAL_BLUR`。将驱动模糊的 `Scroll` 或 `List` 放进对应导航分支。在宽屏共享标题栏时，让当前页的滚动容器直接驱动外层导航，避免再嵌套独立标题栏。
2. **由滚动容器留出首屏空间**。`contentStartOffset` 等于首屏应避让的标题区域高度。可沿 带共享顶栏的工具应用 使用固定栏高和顶部 `.expandSafeArea(...)`，交互控件由系统安全区定位。也可沿 带侧栏的工具应用 或 多窗口笔记应用 显式管理顶部 inset，栏高与首屏滚动偏移均计入 inset，标题内容仅应用一次对应顶部 padding。系统已经保留顶部时，省去手工 inset。
3. **局部控件使用材质**。返回与操作圆钮可用 `ButtonType.Circle`、`ButtonStyleMode.TEXTUAL` 和 `padding(0)`。标题文字与主要操作保持清晰，长标题限制行数并省略。局部壳层设 `.clip(false)` 保留材质阴影，必要时继续排查父层裁切。
4. **可读性衬底作为独立绘制层**。带侧栏的工具应用 和 多窗口笔记应用 的渐变衬底位于标题内容下方，用 `HitTestMode.None` 和 `.accessibilityLevel('no')` 保留按钮事件及读屏顺序。如果原生渐进模糊混入默认灰底，在持有导航标题样式的主题作用域检查 `WithTheme({ theme: { colors: { compBackgroundGray: pageColor } } })` 并分别验证浅色和深色。
5. **按内容是否可滚到标题下选择布局**。带侧栏的工具应用 的 `scrollUnderTitle` 为真时，主体容器顶部 padding 为零，由实际滚动容器提供 `contentStartOffset` 并启用原生滚动模糊。固定搜索、筛选或编辑器无法滚到栏下时，由主体容器提供栏高 padding，关闭标题栏滚动效果。自定义标题按钮仍按自己的材质开关更新。

以下 API 26 标题配置复用 带侧栏的工具应用 的选项逻辑。标题的 `height` 与首屏避让由布局调用方提供。

```ts
import { uiMaterial } from '@kit.ArkUI';

function titleOptions(immersiveEnabled: boolean, scrollUnderTitle: boolean): NavigationTitleOptions {
  const useScrollEffect = immersiveEnabled && scrollUnderTitle;
  return {
    barStyle: BarStyle.STACK,
    backgroundColor: Color.Transparent,
    scrollEffectOptions: useScrollEffect
      ? { scrollEffectType: ScrollEffectType.GRADUAL_BLUR }
      : undefined,
    systemMaterial: useScrollEffect ? undefined : uiMaterial.Material.empty
  };
}
```

### 标题收束和页签切换

带共享顶栏的工具应用 和 词库应用 为各页大标题与顶栏挂 id，在滚动时比较两者的 `windowOffset.y + size.height`。两组坐标均使用窗口 px，可以直接比较。节点未完成布局时使用滚动偏移作为暂时判定，布局、窗口或内容改变后重新检查。每页独立存储收束状态，仅在布尔值变化时更新，并在切换或重选时按产品需求保留滚动位置或回到顶部。

顶栏、侧栏、底栏若驱动同一套原生 `Tabs`，复用同一个 `TabsController`。自定义入口用 `changeIndex` 请求切换，`Tabs.onChange` 提交实际选中态。带共享顶栏的工具应用 用 `onTabBarClick` 处理重选回顶，避免索引绑定和控制器同时发起切换。跨过宽屏断点时检查选择映射、回退栈和界面焦点。

## 材质、应用开关和主题

- **明确区分关闭和恢复默认**。对支持该用法的字段，应用开关主动关闭时使用 `uiMaterial.Material.empty`，并提供同一套判断得出的实体背景。组件传 `undefined` 会交回该应用模式下的原生默认行为。词库应用 和 带共享顶栏的工具应用 用这一语义处理设备探测未通过的分支。
- **检查专用字段的类型**。本机 API 26 SDK 将 `FloatingTabBarStyle.systemMaterial` 声明为 `ImmersiveMaterial`。带侧栏的工具应用 在该字段显式传 `Material.empty`，复用前需用目标 SDK 构建并验证关掉材质后的画面。若目标 SDK、组件或设备上无法可靠关闭，切换到显式普通底栏样式并保留操作可达性。
- **材质和背景共用一个生效条件**。用应用开关、API 版本及设备探测推导 `useMaterial`，同时决定材质和背板背景。启用时让背板透明，品牌色用带 alpha 的 `materialColor`。关闭或不支持时恢复主题实体底。这样可以覆盖 带侧栏的工具应用 底栏中「用户开启、设备不支持」分支，避免空材质配透明背板。
- **按主题复用实例**。固定配置可用 带共享顶栏的工具应用 或 词库应用 的 `readonly` 实例。主题动态赋色参考 带侧栏的工具应用 按 tint 和光色缓存。缓存键覆盖影响构造的样式、阴影、交互反馈等数据，颜色来源有限时可复用映射，任意自定义颜色可保留当前主题的少量实例。多窗口笔记应用 的主题材质工厂会在 builder 调用时新建对象，可将重建时机收敛到主题或选中样式变化。诸如 `'#CC' + rgb.substring(1)` 的写法只适用于已确认的 `#RRGGBB`。
- **区分选中态与反馈**。多窗口笔记应用 顶栏的选中项带半透明主题色和阴影，未选中项可保留光效并关闭阴影。带共享顶栏的工具应用 只对选中项显式设置材质。保持可辨认的选中态，并在采用 `lightEffect` 后验证按压与悬停反馈。使用项目自有颜色资源时直接验证对比度，使用可反色系统资源时再启用并核查自动反色。

## 悬浮底栏锚点及小窗

- 标准 `Tabs` 的横向底部浮栏需要 `barPosition: BarPosition.End`、`vertical(false)`、`barOverlap(true)`。让原生控件管理胶囊形状。词库应用 保留原生宽度，带侧栏的工具应用 通过 `FloatingTabBarStyle.barWidth` 的三个宽度字段和 `barSideMargin` 定制宽度。普通 `.barWidth('100%')` 在 词库应用 的复现中拉满了胶囊。
- 从实际 `Tabs` 的布局底边出发计算 `barBottomMargin`，先确认容器 padding 是否已扣除手势区。若已扣除，只增加视觉间距。若延伸至窗口底边，把必要避让计入同一条路径。将正文的尾部留白放进 `contentEndOffset`，以便最后一个条目滚动到浮栏上方，同时保持视口可延伸到手势区。仅需关闭浮栏下方的渐变时，使用 `maskColor: Color.Transparent` 和 `maskHeight: 0`。
- 需要让 `Tabs` 的布局进入安全区时，参考 词库应用 和 带共享顶栏的工具应用 的 `LayoutPolicy.matchParent` 与 `ignoreLayoutSafeArea`，再按需从外层容器到 `Tabs`、`TabContent`、导航根、滚动容器与标题 builder 补齐 `expandSafeArea` 绘制路径。各分支按自身避让策略配置边缘。多窗口笔记应用 的窄屏 `Tabs` 只扩展底部，带侧栏的工具应用 使用自己的顶边 inset 和普通高度布局。复现底栏上移时先核对布局盒，再检查扩展绘制和边距。
- 绑定实际窗口状态。词库应用 在窗口控制器启动时读取 `getWindowStatus()`，再监听 `windowStatusDidChange`。手机全屏的 8vp 下移量在手机小窗归零，平板小窗使用独立的 24vp 偏移。将 `barModifier` 与 `barBottomMargin` 作为一组按目标设备实测。使用 `CommonModifier().offset(...)` 时仅移动栏，正文避让依据实际可见区域单独计算。
- 切页动画参考 词库应用 和 带共享顶栏的工具应用 的 `AnimationMode.CONTENT_FIRST_WITH_JUMP` 与 `curves.springMotion`。从 `accessibility.isAnimationReduceEnabledSync()` 初始化，通过同一具名回调订阅和注销变化。开启减弱动画时同步降级主 Tab、二级路由和自定义选中态动画，保留切页和返回操作。

## 长列表、索引条与窗口装饰

- 词库应用 让搜索、统计、导出等工具随 `List` 首个 `ListItem` 滚动，使用 `LazyForEach` 承载数据行。固定存在的列表头占索引 0 时，字母跳转对数据行使用 `rowIndex + 1`，滚动同步时反向扣除 1。过滤或改变列数后重建字母到行的映射并检查选中项，覆盖空结果、首尾和跨列调整。
- 词库应用 当前索引条显式使用主题 `popupBackground`，提示气泡走实体背景。若目标是恢复气泡的默认沉浸材质，保留 `usingPopup(true)` 与 `autoCollapse(true)`，去掉显式背景及背景模糊，再看高/中算力材质与低算力白底。已存在的品牌色气泡只有在需求涉及该效果时才需要改动。
- 窗口控制器从当前 `Window` 读取系统避让、挖孔和导航指示条，向组件发布 vp。API 26 的 `window.Rect` 使用 px，`window.TitleButtonRect` 已是 vp。计算右侧三键区用其 `width` 与 `right`，无需二次转换。带侧栏的工具应用 的窗口尺寸计算和 多窗口笔记应用 的装饰备份/恢复可按需组合，具体流程见 Skill 入口列出的窗口沉浸参考。

## 已有证据与复测

- 词库应用的模拟器回归中，调整后恢复约 328vp 的原生胶囊宽度，并在当时的手机窗口中保留约 8vp 的底部间距。复测时记录窗口尺寸、滚动位置和主题，对照顶部模糊、底栏锚点与末项可达性。
- 交付前按目标场景验证应用材质开关、减弱动画、返回、主题切换和断点往返。历史截图和当前源码用于定位实现，折叠、分屏、小窗、PC 缩放与低算力效果需在相应环境观察。
