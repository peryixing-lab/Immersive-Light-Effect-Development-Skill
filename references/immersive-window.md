# 页面与窗口沉浸

## 方案矩阵

| 方案 | 层级 | 背景延伸 | 内容延伸 | 自动避让 | 适用场景 |
|---|---|---:|---:|---:|---|
| `.background(...)` | 组件 | 是 | 否 | 是 | 背景融入状态栏/导航条，内容留在安全区 |
| `.ignoreLayoutSafeArea()` + `LayoutPolicy.matchParent` | 组件/页面 | 是 | 是 | 否 | 单页全屏内容、可滚动内容需覆盖避让区 |
| `.expandSafeArea(...)` | 组件 | 是 | 否 | 子组件留在安全区 | 指定方向的局部绘制延伸 |
| `setWindowLayoutFullScreen(true)` | 窗口 | 是 | 是 | 否 | 所有页面统一全屏 |

优先按页面组合组件级策略。全局窗口沉浸会影响所有页面，除非产品所有页面都需要全屏，否则不要使用。

## 背景沉浸

当内容应留在安全区时使用：

```ts
Column() {
  PageContent()
}
.background($r('app.color.page_background'))
```

官方实践区分 `.background(...)` 与 `.backgroundColor(...)`：前者可把绘制延伸到避让区，后者的颜色限定在安全区。先在目标 SDK 验证该行为，不要机械替换项目已有复杂背景。

限制：滚动区域本身不会因此延伸到状态栏和导航条。

## 页面沉浸与手动避让

```ts
Column() {
  PageContent()
}
.ignoreLayoutSafeArea()
.height(LayoutPolicy.matchParent)
.padding({
  top: `${topAvoidPx}px`,
  bottom: `${bottomAvoidPx}px`
})
```

- 背景和布局都覆盖避让区。
- 使用 `getWindowAvoidArea()` 获取初始值，使用 `on('avoidAreaChange', callback)` 监听变化。
- 对 ArkUI 数值布局优先用 `UIContext.px2vp()` 转换；字符串 `px` 只在项目已有相同模式且类型允许时使用。
- 在页面销毁或窗口销毁时用同一个具名回调注销监听。

## 安全区域拓展

`.expandSafeArea(...)` 适合只扩展绘制区域、让子组件仍在安全区内布局的局部场景。使用前确认：

- 组件与目标安全区边界重合。
- 组件没有固定的非百分比宽高。
- 父容器不是滚动容器；滚动父容器下该属性无效。
- 明确指定 `SafeAreaType` 与 `SafeAreaEdge`，不要无差别扩展所有方向。

## 沉浸光感组件与安全区协同

开启标题栏或悬浮底栏沉浸光感时，需要让底层可滚动内容延伸到浮层下方以体现通透折射，同时保证初始内容与交互区不被遮挡：

1. **标题栏沉浸光感协同**：
   - `HdsNavigation`：配合 `.ignoreLayoutSafeArea([LayoutSafeAreaType.SYSTEM], [LayoutSafeAreaEdge.TOP, LayoutSafeAreaEdge.BOTTOM])`，内部滚动容器使用 `.clipContent(ContentClipMode.SAFE_AREA)` 或设置合理内边距；通过 `.bindToScrollable([scroller])` 驱动标题栏 `IMMERSIVE_GRADIENT_BLUR` / `GRADIENT_BLUR` 及 `dynamicHideTitleBar`。
   - ArkUI `Navigation` / `NavDestination`（两种 `topInset` 高度协同范式）：
     - **显式管理顶部避让**。页面自身负责顶边时，将 `titleTopInset` 计入标题高度和滚动区 `contentStartOffset`，标题内容设置对应的顶部 padding。使用系统装饰或系统已保留安全区的窗口按照实际可用顶部空间计算。
     - **保持安全区内布局**。标题栏高度与 `contentStartOffset` 使用同一基础值，带共享顶栏的工具应用 示例为 56vp。对需要延伸的导航、滚动容器及标题栏 builder 补齐顶部 `expandSafeArea`，让模糊绘制延伸而标题控件保留在安全区。
2. **悬浮底部页签与索引条协同**：
   - `HdsTabs` / `Tabs` 悬浮底栏核查底部、横向、重叠三项布局条件。`Tabs` 需要扩展布局盒进入底部时，给 `ignoreLayoutSafeArea` 配对 `LayoutPolicy.matchParent`，并检查父容器边界。
   - `barBottomMargin` 从实际布局盒底边计起。导航指示条已由父容器或 Tabs padding 避让时，margin 只保留设计间距。滚动尾部的 `contentEndOffset` 按浮栏覆盖范围和末项所需间距计算。
   - `AlphabetIndexer`：通常扣除顶部信号栏与底部工具栏/页签高度后居中展示；横屏或分屏高度不足时开启 `autoCollapse` 折叠展示。

## 避让区模型

分别保存并响应：

- `TYPE_SYSTEM`：状态栏等系统区域。
- `TYPE_NAVIGATION_INDICATOR`：底部导航指示条。
- `TYPE_CUTOUT`：挖孔区域。
- `TYPE_SYSTEM_GESTURE`：侧滑返回等手势区域。
- `TYPE_KEYBOARD`：固定软键盘区域。

挖孔位置随旋转、折叠和窗口模式改变。确认矩形坐标与当前窗口在同一坐标系后，按非空的避让矩形计算四边 padding。以下公式使用窗口内坐标和当前窗口尺寸。

- 顶部：`topRect.top + topRect.height`
- 左侧：`leftRect.left + leftRect.width`
- 右侧：`windowWidth - rightRect.left`
- 底部：`windowHeight - bottomRect.top`

用当前窗口的 `UIContext.px2vp()` 转换 `window.Rect` 的像素结果，再写入响应式状态。多个避让类型从同一边覆盖时取所需最大范围。未占用该边的空矩形按零处理。已由 `KeyboardAvoidMode.RESIZE` 负责的键盘变化可独立处理，避免覆盖持久的系统栏 inset。

## 系统栏

仅在游戏、视频或明确的无干扰场景隐藏系统栏：

```ts
mainWindow.setWindowSystemBarEnable([]);
```

页面离开时恢复：

```ts
mainWindow.setWindowSystemBarEnable(['status', 'navigation']);
```

隐藏系统栏不代表挖孔消失。仍需监听 `TYPE_CUTOUT`，并验证四种旋转方向。

## 自由窗口标题栏

设备及窗口形态支持标题栏装饰能力时，可按 多窗口笔记应用 的主窗口路径集成系统三键区。

1. 等 `loadContent` 完成，读取并保存当前窗口的装饰显隐、装饰高度和按钮样式。仅当该场景需要自绘标题栏时再修改。
2. 设置 `setWindowDecorHeight(...)` 和 `setWindowDecorVisible(false)`，在支持该组合的形态上保留原生三键与拖动热区。按需用 `setDecorButtonStyle(...)` 配置按钮尺寸，并在 `onConfigurationUpdate` 更新明暗色。
3. 用 `getTitleButtonRect()` 初始化右侧避让，监听 `windowTitleButtonRectChange` 更新。**`TitleButtonRect.width` 和 `right` 已是 vp**，按实际热区使用 `Math.max(0, rect.width + rect.right)`。若产品已掌控三键尺寸和间距，可按 多窗口笔记应用 的实测剔除热区前导留白，并验证缩放、最大化及按钮点击。
4. 部分安装步骤失败时，回滚已修改的窗口状态，回退到系统装饰。结束时用同一回调注销，并对仍有效的窗口恢复捕获的原值。主窗和文档子窗分别管理各自状态。

多窗口笔记应用 的 文档窗口 Ability 在独立窗口创建时启用自绘装饰，随窗口销毁释放引用。若将同样的装饰用于仍会存续的窗口中的暂时场景，需要在离开场景时恢复该窗口的原始装饰。

### 实战工程精炼要点（2in1 / PC 与自由小窗）

- **浮窗初始状态与后续变化**。词库应用 先读 `getWindowStatus()` 再监听 `windowStatusDidChange`。手机进入 `FLOATING` 后可去掉全屏专用下移量，平板小窗使用独立规则。通过实际窗口尺寸和系统栏矩形检查底栏位置。
- **系统栏样式去重与恢复**。带侧栏的工具应用 通过 `themeKey` 去重调用 `setWindowSystemBarProperties`，更新失败时允许重试，控制器退出时恢复读取到的原始样式。多窗口实现将缓存及异步更新归属到具体窗口。

## 生命周期模板

- 在 `onWindowStageCreate` 获取主窗口并建立窗口控制器。
- 内容加载完成后获取 `UIContext`、初始避让区和标题按钮矩形，再注册监听。
- 在 `NavDestination.onShown`/`onHidden` 或对称页面生命周期中开启/恢复场景状态。
- 在 `onWindowStageDestroy` 注销仍存活的 `avoidAreaChange`、`windowTitleButtonRectChange`、`windowSizeChange` 和窗口状态监听。
- 使用具名回调；不要注册匿名函数后再尝试注销。

## 多设备最低验证集

- 直板机：竖屏、横屏、反向方向、挖孔设备。
- 折叠屏：折叠/展开、方向切换。
- 平板/2in1/PC：全屏、分屏、悬浮/自由窗口。
- 每种模式检查：状态栏、导航指示条、系统手势、键盘、三键区、滚动边缘和返回操作。
