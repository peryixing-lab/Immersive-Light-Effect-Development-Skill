# 官方来源与版本

2026-11-18 阅读用户提供的九篇官方文档。以下日期采用各原文页面显示的更新时间。遇到同名接口或行为差异时，以实际调用的组件 API、重载及对应 SDK 声明为准。能力范围与默认行为查 ArkUI 专项文档，空间化示例用于理解组合方式。

## HDS 组件与能力探测

- 2026-09-09。API 23 HDS 导航与底部页签的两个接入位置，自适应配置，以及自定义等级的 `IMMERSIVE` 成员判断和 `SMOOTH` 回退。 [HDS 组件使用沉浸光感材质](https://developer.huawei.com/consumer/cn/doc/doccenter-capabilities/ui-design-hds-component-material)
- 2026-08-29。`@kit.UIDesignKit` 导入、Stage 模型、系统能力、卡片支持和两组枚举。 [hdsMaterial API 参考](https://developer.huawei.com/consumer/cn/doc/doccenter-references/api/ui-design-hdsmaterial)
- 2026-11-10。首眼标题栏、悬浮底部导航、MiniBar 和智感握姿，以及菜单跨版本示例。 [空间化最佳实践](https://developer.huawei.com/consumer/cn/doc/doccenter-advanced-features/bpta-spatiality-immersive)

## ArkUI 生效范围、适配和排障

- 2026-11-11。搜索随标题栏收缩、`BarStyle.STACK` 下首屏避让、分类栏滑入标题 builder。 [沉浸光感典型场景](https://developer.huawei.com/consumer/cn/doc/doccenter-capabilities/arkts-immersive-light-sample)
- 2026-11-11。区域限制、背板和内容层的样式优先级、自定义弹窗重载、自动反色、几何与阴影排障。 [沉浸光感常见问题](https://developer.huawei.com/consumer/cn/doc/doccenter-capabilities/arkts-immersive-light-sense-faq)
- 2026-09-17。材质使用面积、嵌套、模糊重叠、弹窗大小、动态背景、反色范围、参数稳定性与重复阴影。 [沉浸光感功耗优化](https://developer.huawei.com/consumer/cn/doc/doccenter-capabilities/arkts-immersive-light-sense-constraints)
- 2026-10-26。按组件检查应用级默认值、组件级入口和限制，涵盖导航、弹窗、选择控件以及索引条气泡。 [组件适配沉浸光感](https://developer.huawei.com/consumer/cn/doc/doccenter-capabilities/arkts-immersive-light-sense-component-adaptation)
- 目标 SDK、`entry` 模块开关、`Material.empty` 与默认行为，以及旧版本调用保护。 [开启沉浸光感](https://developer.huawei.com/consumer/cn/doc/doccenter-capabilities/arkts-immersive-light-sense-enable) · [ArkTS API 兼容性保护](https://developer.huawei.com/consumer/cn/doc/harmonyos-releases/arkts-api-compatibility-warning-elim/)
- 材质构造、设备支持探测、可反色资源和属性列表。为标准系统背板配置材质时直接核对接收 `CustomDialogOptions` 的弹窗重载。 [uiMaterial API 参考](https://developer.huawei.com/consumer/cn/doc/doccenter-references/api/arkts-apis-uimaterial) · [openCustomDialog(options) API 参考](https://developer.huawei.com/consumer/cn/doc/doccenter-references/api/arkts-apis-uicontext-promptaction#opencustomdialog12-1)
- 关联能力说明。 [沉浸光感简介](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-immersive-light-sense-overview) · [沉浸式系统材质视效](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-immersive-light-sense-common-capability)

## 设计规范

- 2026-06-12。系统强度偏好、材质厚度选型、与内容重叠的交互元素以及浮层的信息可读性。 [沉浸光感视觉规范](https://developer.huawei.com/consumer/cn/doc/doccenter-ux-design/immersivelight-0000002612101053)
- 2026-06-12。索引条提示浮层、横屏和分屏动态折叠、扣除上下栏后的居中布局。具体气泡材质条件参见《组件适配沉浸光感》。 [索引条视觉规范](https://developer.huawei.com/consumer/cn/doc/doccenter-ux-design/alphabetindexer-0000001956975265#section7681414211)

## 多设备窗口沉浸最佳实践与官方示例

- [窗口沉浸式](https://developer.huawei.com/consumer/cn/doc/best-practices/bpta-multi-device-window-immersive)
  - 依据：`.background()`、`.ignoreLayoutSafeArea()`、`.expandSafeArea()`、`setWindowLayoutFullScreen()` 的层级与限制；避让区分类；挖孔四边计算；自由窗口标题栏三键区适配。
- [HarmonyOS_Samples/Immersive](https://gitcode.com/HarmonyOS_Samples/Immersive)
  - 核对分支/提交：`master` / `5189f3ce966418006c52d581e125c911deae330b`（提交时间 2026-07-20）。
  - 示例基线：HarmonyOS 6.0.0 Release、SDK 6.0.0(20)+。
  - 重点文件：
    - `commons/commons/src/main/ets/utils/WindowUtil.ets`
    - `products/default/src/main/ets/pages/backgroundImmersive/componentBackgroundImmersive/Shopping.ets`
    - `products/default/src/main/ets/pages/backgroundImmersive/componentPageImmersive/ShoppingAvoid.ets`
    - `products/default/src/main/ets/pages/fullScreenImmersive/componentPageImmersive/MiniGame.ets`
    - `products/default/src/main/ets/pages/fullScreenImmersive/freeformWindowImmersive/ShoppingFullScreen.ets`
    - `features/shopping/src/main/ets/view/Header.ets`

示例采用 Apache-2.0 许可证。复用时保留适用的许可证声明；技能默认只提炼模式，不复制整份示例。

## 补充 API 核对

- 标准浮栏宽度、底部锚点、蒙层和 `FloatingTabBarStyle.systemMaterial` 的声明。 [Tabs API 参考](https://developer.huawei.com/consumer/cn/doc/doccenter-references/api/ts-container-tabs/#floatingtabbarstyle)
- 自由窗口标题栏、三键矩形和装饰能力。已核对本机 DevEco Studio 的 HarmonyOS 26.0.0.105 SDK，`@ohos.window.d.ts` 中 `Rect` 使用 px，`TitleButtonRect` 使用 vp。 [自由多窗开发适配](https://developer.huawei.com/consumer/cn/doc/doccenter-capabilities/application-adaptation-freeform-window/) · [窗口沉浸常见问题](https://developer.huawei.com/consumer/cn/doc/harmonyos-faqs/faqs-arkui-1089/)

## 工程实践

实战要点来自四个使用 HarmonyOS API 26.0.0 的应用，涉及独立标题栏、共享顶栏、侧栏和多窗口工作区。案例中的尺寸和偏移是对应项目的参数。相关实现要点见 [项目实战](project-patterns.md)。
