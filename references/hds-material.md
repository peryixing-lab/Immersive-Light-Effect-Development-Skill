# HDS 与 ArkUI 沉浸光感技术手册

## 1. 双体系对比：`hdsMaterial` vs `uiMaterial`

HarmonyOS 目前提供两套互补的沉浸光感（Immersive Light）能力体系，切勿混淆枚举或导入路径：

| 维度 | HDS 组件材质（`hdsMaterial`） | ArkUI 系统材质（`uiMaterial`） |
|---|---|---|
| 起始版本 | HarmonyOS 6.1.0 (`API 23`)+ | `API 26.0.0`+（`targetSdkVersion >= 26.0.0`） |
| 导入模块 | `import { hdsMaterial } from '@kit.UIDesignKit'` | `import { uiMaterial } from '@kit.ArkUI'` |
| 适用范围 | `HdsNavigation` / `HdsNavDestination` 标题栏按钮、`HdsTabs` 悬浮底部页签 | 通用 `Navigation` / `Tabs`、弹窗类组件/接口、`Slider`、`Toggle`、`Select`、`AlphabetIndexer`、`ChipGroup`、`SegmentButton` 等 |
| 模型与卡片 | `getSystemMaterialTypes()` 和相关枚举限定 Stage 模型，支持 ArkTS 卡片（6.1.0(23)+） | 逐接口核对 Stage、卡片及元服务支持范围 |
| 能力探测 | `hdsMaterial.getSystemMaterialTypes()` 返回设备支持的材质类型 | `uiMaterial.isImmersiveMaterialSupported()` 检查支持情况，`getGlobalMaterialLevel()` 读取设备等级，`getMaterialInfo()` 读取应用配置 |
| 材质等级（`MaterialLevel`） | `EXQUISITE`(0 精美) / `GENTLE`(1 轻柔) / `SMOOTH`(2 流畅) / `ADAPTIVE`(10 系统自适应) — **支持主动配置** | `EXQUISITE`(0 高算力) / `GENTLE`(1 中算力) / `SMOOTH`(2 低算力) — **仅只读查询，不支持手动设置，天然自适应** |
| 材质样式（厚度） | 不提供 `ImmersiveStyle`，由 `materialType` + `materialLevel` 与组件差异化实现共同决定 | `ImmersiveStyle`: `ULTRA_THIN`(0)、`THIN`(1)、`REGULAR`(2)、`THICK`(3)、`ULTRA_THICK`(4)（仅高/中算力生效） |
| 空间动效 | 由 HDS 组件内部协同系统实现 | 弹窗/菜单（非线性形变 + 边缘流光）、`Slider`（粒子动画），随算力与用户偏好自适应 |
| 平台约束 | 检查 UI Design Kit 和 `SystemCapability.UIDesign.HDSComponent.Core` | 检查项目 SDK 的导出及设备支持。兼容旧版时先用 `deviceInfo.apiAvailable('26.0.0')` 保护新 API |

> [!IMPORTANT]
> **三档系统偏好与代码编写原则**：用户在系统设置中可选择**强、均衡（默认）、弱**三档沉浸光感。系统底层会自动调节透明度、反色率、折射强度、空间动效和环境交互，**应用无需为三档偏好分别编写三套业务代码**。

---

## 2. HDS 组件空间化与沉浸光感（`@kit.UIDesignKit`，API 23+）

### 2.1 首选：系统自适应策略

`HdsNavigation` / `HdsNavDestination` 通过 `titleBar.style.systemMaterialEffect` 配置标题栏按钮，`HdsTabs` 通过 `HdsTabsFloatingStyle.systemMaterialEffect` 配置悬浮页签。默认用自适应类型和等级。

```ts
import { hdsMaterial } from '@kit.UIDesignKit';

systemMaterialEffect: {
  materialType: hdsMaterial.MaterialType.ADAPTIVE,
  materialLevel: hdsMaterial.MaterialLevel.ADAPTIVE
}
```

> `hdsMaterial.MaterialType` 枚举：`NONE` (0, 无材质)、`ADAPTIVE` (100, 自适应系统材质，默认为沉浸式材质)、`IMMERSIVE` (101, 沉浸式材质)。

### 2.2 自定义强度与能力探测降级

仅在明确视觉需求下偏离 `MaterialLevel.ADAPTIVE`，且必须在 `aboutToAppear()` 等初始化阶段探测一次（**严禁在 `build()` 中反复调用**）：

```ts
import { hdsMaterial } from '@kit.UIDesignKit';
import { BusinessError } from '@kit.BasicServicesKit';

function resolveHdsMaterialLevel(): hdsMaterial.MaterialLevel {
  try {
    const types: Array<hdsMaterial.MaterialType> = hdsMaterial.getSystemMaterialTypes();
    if (types.indexOf(hdsMaterial.MaterialType.IMMERSIVE) >= 0) {
      return hdsMaterial.MaterialLevel.EXQUISITE; // 或 GENTLE
    }
  } catch (err) {
    const error = err as BusinessError;
    console.error(`getSystemMaterialTypes failed, code: ${error.code}, message: ${error.message}`);
  }
  return hdsMaterial.MaterialLevel.SMOOTH;
}
```

- 支持 `IMMERSIVE`：可选 `EXQUISITE` 或 `GENTLE`。
- 不支持 `IMMERSIVE` 时使用 `SMOOTH` 等级。指南示例在两条路径均保留 `MaterialType.ADAPTIVE`，只切换 `materialLevel`。需要兼容旧版时，对起始于 6.1.0(23) 的 HarmonyOS 专用 API 使用 `deviceInfo.apiAvailable('6.1.0')`，并为缺少 HDS 能力的产品保留普通导航组件。

### 2.3 `HdsNavigation` 标题栏渐变模糊与动态显隐

- **渐变模糊对比**（`titleBar.style.scrollEffectOpts`）：
  - `ScrollEffectType.IMMERSIVE_GRADIENT_BLUR`：从**完全透明**渐变到模糊，模糊区域更大、过渡更自然、沉浸感更强。
  - `ScrollEffectType.GRADIENT_BLUR`：从**半透明**渐变到模糊，过渡相对克制，兼顾信息密度。
  - 两者均需配合 `systemMaterialEffect` 与 `.bindToScrollable([this.scroller])` 呈现完整体验。
- **标题栏与状态栏滑动动态显隐**：通过 `dynamicHideTitleBar` 联动 `.bindToScrollable(...)`：
  - `hideTitleArea: true`、`hideStatusBar: true`。
  - `mode` 支持：`HideMode.SCROLL_UP_TO`（上滑到固定位置隐藏、下滑到固定位置显示）、`HideMode.SCROLL_UP`、`HideMode.SCROLL_DOWN`、`HideMode.SCROLL_UP_TO_BLEND_SCROLL_UP`。

同一个页面若同时使用标准 ArkUI 导航与 HDS 导航，留意两个同名的 `ScrollEffectType`。HDS 应导入 UI Design Kit 枚举并配置 `scrollEffectOpts`，标准标题栏使用 `GRADUAL_BLUR` 和 `scrollEffectOptions`。

### 2.4 `HdsTabs` 悬浮底栏、沉浸式 MiniBar 与智感握姿

按空间化示例配置底部悬浮布局和 `.barFloatingStyle(...)`。MiniBar 由容器按可用宽度处理展开与折叠，`adaptToHandedness` 用于支持智感握姿的宽屏设备。按 SDK 核对各字段的起始版本。

```ts
import {
  HdsBarStyle,
  hdsMaterial,
  HdsTabs,
  HdsTabsController,
} from '@kit.UIDesignKit';

// 在 build() 中：
HdsTabs({ controller: this.controller }) {
  // TabContent...
}
.scrollable(false)
.barOverlap(true)
.vertical(false)
.barPosition(BarPosition.End)
.barFloatingStyle({
  barBottomMargin: this.naviIndicatorHeight > 0
    ? this.naviIndicatorHeight
    : $r('sys.float.padding_level8'),
  adaptToHandedness: true, // 智感握姿：宽屏设备上底部悬浮栏自动跟随握持手左右切换
  systemMaterialEffect: {
    materialType: hdsMaterial.MaterialType.ADAPTIVE,
    materialLevel: hdsMaterial.MaterialLevel.ADAPTIVE
  },
  miniBar: {
    miniBarBuilder: () => this.miniBarBuilder(),
    onBarStyleChange: (miniBarStyle: HdsBarStyle) => {
      // 宽屏设备（如平板）默认展开，窄屏设备（如手机）默认折叠
      this.isMiniBar = miniBarStyle === HdsBarStyle.COLLAPSE;
    }
  }
})
```

---

## 3. ArkUI 沉浸光感开启方式与生效范围（`@kit.ArkUI`，API 26.0.0+）

使用 ArkUI 沉浸光感需确保 `targetSdkVersion >= 26.0.0`；若需兼容低版本设备运行，必须配合 `deviceInfo.apiAvailable('26.0.0')` 做运行时保护。

### 3.1 应用级开启（`module.json5`）

仅在 **`entry` 类型的 module** 中配置的 `metadata` 生效：

```json5
{
  "module": {
    "name": "entry",
    "type": "entry",
    "metadata": [
      {
        "name": "ohos.arkui.UIMaterial.state",
        "value": "enable" // 可选: "default" | "enable" | "disable"
      }
    ]
  }
}
```

可通过 `uiMaterial.getMaterialInfo()` 获取 `{ state: MaterialState, type: MaterialType }`：

| `MaterialState` | 对应值 | 行为说明 |
|---|---|---|
| `DEFAULT` (0) | `"default"`（未配置时的默认值） | `Dialog`、`Toast`、`AlphabetIndexer` 在**未主动设置**背景色、模糊和阴影时默认开启沉浸式系统材质；`Text` 设置 `copyOption` 后触发的文本菜单默认开启；其他组件由应用主动设置。 |
| `ENABLE` (1) | `"enable"` | 默认开启组件：`Dialog`、`Toast`、`AlphabetIndexer`、`ChipGroup`/`ChipGroupV2`、`Chip`/`ChipV2`、`Select`、菜单控制、`Toggle`、`SegmentButton`/`SegmentButtonV2`、`Slider`、`SelectionMenu`、`Navigation`、`NavDestination`、`Text`（`copyOption` 菜单），以及生效悬浮样式（`barFloatingStyle`）的 `Tabs` 页签栏。**此模式下材质优先级高于组件自身设置的背景色、模糊、阴影和边框。** |
| `DISABLE` (2) | `"disable"` | 全局禁用沉浸式系统材质，应用级与组件级配置均不生效。 |

### 3.2 组件级开启与关闭

- **三种组件级开启方式**：
  1. 通用属性：`.systemMaterial(new uiMaterial.ImmersiveMaterial({ ... }))`（或传 `undefined` 恢复组件默认材质）。
  2. 弹窗 `options` 参数：`ShowToastOptions`、`CustomDialogControllerOptions`、`AlertDialogParam`、`ActionSheetOptions`、`PopupOptions`、`TipsOptions`、`ContextMenuOptions`、`SheetOptions` 中的 `systemMaterial` 字段。
  3. 组件专属属性：`Select.menuSystemMaterial(...)`、`Navigation`/`NavDestination` `titleBar/title` options 中的 `systemMaterial`、`Tabs` `barFloatingStyle` 中的 `systemMaterial`、`ChipGroup`/`SegmentButton` 的 `backgroundSystemMaterial` 等。
- **优先级**：应用模式允许时，可通过组件的专用入口覆盖和关闭默认效果。`DISABLE` 会阻止 ArkUI 组件级接入。组件没有相应入口时，使用其文档指定的控制方式，例如 `AlphabetIndexer` 的气泡背景属性。
- **正确关闭材质（关键避坑）**：
  - 单独关闭某个默认开启沉浸光感的组件，**必须使用 `uiMaterial.Material.empty`**（例如 `.systemMaterial(uiMaterial.Material.empty)` 或 `.menuSystemMaterial(uiMaterial.Material.empty)`）。
  - **不要传入 `undefined` 企图关闭**：`undefined` 表示“恢复为组件默认的沉浸光感效果”，在 `ENABLE` 模式或默认开启组件上依然会呈现材质。

### 3.3 生效范围硬约束（`Material inactive: out of scope`）

即使在 `API 26.0.0+` 且非 `DISABLE` 模式下，沉浸光感仍受严格区域限制：

1. **全页面任意位置生效**：
   - 指定弹窗类组件：`AlertDialog`、`ActionSheet`、`CustomDialog`、`CalendarPickerDialog`、`DatePickerDialog`、`TimePickerDialog`、`TextPickerDialog`、`SelectionMenu`、`AlphabetIndexer` 提示弹窗、`Text` 设置 `copyOption` 后长按/双击触发的文本菜单。
   - 指定弹窗类接口：`PromptAction`、`ArkUI_NativeDialog`、`@ohos.promptAction`、`Popup` 控制、`Tips` 控制、`Menu` 控制、半模态转场（`bindSheet`）。
   - 全页可用基础控件：`Slider`、`Toggle`（`Switch` / `Button`）、`Select`。
2. **仅限导航标题栏与底部横向页签栏生效**：
   - 其余所有组件（包括 `Button`、`Search`、`ChipGroup`/`ChipGroupV2`、`SegmentButton`/`SegmentButtonV2`、`Column`/`Row` 等容器与普通组件）**仅在 `Navigation`/`NavDestination` 标题栏，或横向 `Tabs`（`vertical: false` 且 `barPosition: BarPosition.End`）的底部 `TabBar` 中生效**。
   - 放置在普通页面内容区中设置 `.systemMaterial()` **不会生效**，且日志会打印：`Material inactive: out of scope. Use component in navigation title bar or Tabbar.`。

---

## 4. `ImmersiveOptions` 核心参数与设计厚度规范

`new uiMaterial.ImmersiveMaterial(options?: ImmersiveOptions)` 支持的参数与默认值：

### 4.1 `style: uiMaterial.ImmersiveStyle`（默认 `REGULAR`）

仅在高算力和中算力设备生效；低算力设备只支持单一降级样式，设置 `style` 不产生差异。

| 枚举值 | 数值 | 视觉特性 | 设计规范与典型适用场景 |
|---|---:|---|---|
| `ULTRA_THIN` | 0 | 超薄，极高透明与折射 | **顶部悬浮组件**（结合渐变模糊延展顶部内容空间）、浮动工具栏、`Navigation` 标题栏、`Select` 按钮、`ChipGroup` |
| `THIN` | 1 | 薄，较强透明与通透感 | **底部悬浮组件**（结合渐变颜色蒙层延展底部内容空间）、搜索框、`Tabs` 悬浮底栏、`SegmentButton` |
| `REGULAR` | 2 | 常规厚度，适度透明与模糊 | 构造器默认样式，用于允许材质且需要中等遮挡的区域 |
| `THICK` | 3 | 厚，模糊效果较强 | **任意位置弹出且非常驻的临时浮层**（保证复杂背景可读性）、`Menu`、`Toast`、`AlphabetIndexer` 提示弹窗 |
| `ULTRA_THICK` | 4 | 超厚，模糊效果很强 | **半模态（`bindSheet`）、较大弹出框（`Dialog`）**（容纳长文本与丰富内容） |

### 4.2 `materialColor: ResourceColor`

- 作用：默认为透明。高/中算力设备将颜色混入材质滤镜，FAQ 说明低算力设备可能将其用作背景色。检查目标组件的低算力回退表现。
- 用途：品牌色调表达，或**降低 `ULTRA_THIN`/`THIN` 边缘折射周围背景色的强度**。
- **必传半透明色**：如 `'#80FFFFFF'`、`'rgba(255, 0, 0, 0.2)'`。传入纯不透明色（如 `Color.Red`、`'#FFFF0000'`）会**完全遮挡材质滤镜效果**。

### 4.3 `colorInvert: boolean`（默认 `false`）

开启后可将组件子树内文字、图标颜色自动反色以保障薄材质下的可读性。**同时满足以下 4 个条件才会生效**：
1. 设备为**高算力或中算力**（低算力不产生效果差异）。
2. `style` 必须为 **`ULTRA_THIN` 或 `THIN`**（`REGULAR`/`THICK`/`ULTRA_THICK` 下不生效）。
3. 达到当前系统强/均衡/弱偏好的反色触发阈值（材质越薄、系统强度越强，越容易触发）。
4. 目标属性必须使用 **26 个特殊系统颜色资源 `$r('sys.color.xxx')`**（硬编码颜色如 `Color.White`、`'#FFFFFF'` 及应用自定义资源 `$r('app.color.xxx')` 均不触发反色）：
   - **常用文字/图标资源**：`sys.color.font_primary`、`font_secondary`、`font_tertiary`、`font_fourth`、`font_on_primary`、`font_emphasize`、`brand`、`brand_font`、`warning`、`icon_primary`、`icon_secondary`、`icon_tertiary`、`icon_fourth`、`icon_emphasize`、`icon_sub_emphasize`
   - **常用容器/交互资源**：`sys.color.comp_background_primary_contrary`、`comp_background_primary_contrary_secondary`、`comp_background_secondary`、`comp_background_tertiary`、`comp_background_emphasize`、`comp_emphasize_secondary`、`comp_emphasize_tertiary`、`comp_divider`、`interactive_hover`、`interactive_focus`、`interactive_pressed`
   - **支持自动反色的属性**：`Text.fontColor`、`Button.fontColor`、`SymbolGlyph.fontColor`、`Image.fillColor`、`Search`（`placeholderColor`/`fontColor`/`searchIcon`/`cancelButton`/`caretStyle`/`searchButton`）、`BottomTabBarStyle`、`Chip`（`prefixIcon.fillColor`/`suffixIcon.fillColor`/`label.fontColor`）、`ChipGroup.itemStyle.fontColor`、`TextArea`/`TextInput`（`fontColor`/`placeholderColor`）、`SegmentButton`（`fontColor`/`selectedFontColor`）、`SegmentButtonV2`（`itemFontColor`/`itemSelectedFontColor`/`itemIconFillColor`/`itemSelectedIconFillColor`/`itemSymbolFontColor`/`itemSelectedSymbolFontColor`）、`Swiper.fontColor`。

### 4.4 `applyShadow: boolean`（默认 `true`）

- 全算力设备生效。
- 为 `true` 时，材质自带阴影**固定生效且优先于通用 `.shadow()`**。
- 如需自定义 `.shadow(...)`，**必须显式传入 `applyShadow: false`**，否则通用 `.shadow()` 不生效且造成重复计算风险。

### 4.5 `interactive: boolean`（默认 `false`）与 `lightEffect: LightEffectOptions | null`（默认 `undefined`）

- `interactive`：全算力设备生效，开启后按压产生弹性形变、松手恢复。
- `lightEffect`：传 `{}` 或 `{ color: Color.White }` 配置交互光感反馈，传 `null` 显式关闭，省略时沿用组件默认行为。具体反馈由组件、设备和系统设置决定。API 26.0.0 SDK 将该参数标注为适用于各算力档。
- 提示：当 `Button` 或 `Select` 启用 `lightEffect` 时，组件默认的点击态与悬浮态视觉反馈不再展示，由材质光感交互反馈替代。

---

## 5. 四大类组件适配速查

### 5.1 导航类组件

| 组件 | `ENABLE` 默认 | 推荐开启方式与关键约束 |
|---|---|---|
| `Navigation` / `NavDestination` | 开启（`ULTRA_THIN`） | 通过 `NavigationTitleOptions.systemMaterial` 配置系统返回键与非自定义菜单。自定义 builder 内的控件通过各自入口设置。需要内容透底时用 `BarStyle.STACK`。 |
| `Tabs`（底部页签） | 仅生效 `barFloatingStyle` 时开启（`THIN`） | 通过 `.barFloatingStyle({ systemMaterial: ... })` 配置，并同时满足 `barOverlap(true)`、`vertical(false)`、`barPosition(BarPosition.End)`。启用材质的分支保持背板透明，主题背景和背景模糊可用于独立回退分支。`TabContent` 不承载 TabBar 背板材质。 |
| `AlphabetIndexer`（索引条） | 开启（提示弹窗 `THICK`） | 用 `.usingPopup(true)` 打开提示气泡。保留默认材质时省略 `popupBackground` 和 `popupBackgroundBlurStyle`，或传 `undefined` 恢复默认。任意一项显式设置都会关闭该气泡的默认材质。高/中算力显示 `THICK`，低算力显示白底。 |

索引条布局按可用高度计算。竖屏有空间时完整展示，横屏或分屏时用 `autoCollapse` 缩略。一般在扣除状态栏、底部工具栏或页签栏后垂直居中。顶部有子页签等组合控件时，从其下边界加适当间距定位。需分别验证索引拖动、列表定位和气泡显示。

### 5.2 弹窗类组件（全页面生效）

| 组件 / 接口 | `ENABLE` 默认 | 推荐开启方式与关键约束 |
|---|---|---|
| `Toast` | 开启（`THICK`） | `ShowToastOptions.systemMaterial`；`DEFAULT` 模式下未设背景/模糊/阴影时默认 `THICK`。 |
| `Popup` / `Tips` | 不默认开启 | 需组件级传入 `PopupOptions.systemMaterial` / `TipsOptions.systemMaterial`。 |
| `Menu` | 开启（`THICK`） | `ContextMenuOptions.systemMaterial` 或 `promptAction.openMenu` 的 `MenuOptions` 中配置；高算力含非线性形变与边缘流光。 |
| `Dialog`（`AlertDialog`、`ActionSheet`、`CustomDialog`、各类 `PickerDialog`） | 开启（`ULTRA_THICK`） | 在 `options.systemMaterial` 配置。处于 `DEFAULT` 时，保留默认背板样式可获得默认材质。独立的 `CalendarPickerDialog` 支持材质，`CalendarPicker` 控件拉起的弹窗由控件内部绘制，通用属性仅作用于触发器。 |
| `bindSheet`（半模态） | 不默认开启 | 需在 `SheetOptions.systemMaterial` 显式设置；设置后 `backgroundColor`、`borderColor`、`borderWidth`、`shadow` 不再生效。 |

**自定义弹窗先核对调用签名。** `PromptAction.openCustomDialog(options: CustomDialogOptions)` 传入 `{ builder, systemMaterial }` 时可给系统背板配置材质。传入 `ComponentContent` 的 `openCustomDialog(dialogContent, options)` 和 `openCustomDialogWithController(dialogContent, controller, options)` 使用开发者自定义背板，即使类型声明允许填写 `systemMaterial`，背板也不会应用该材质。使用 `CustomDialogController` 时，保留系统背板的样式路径（`customStyle` 关闭）。

### 5.3 按钮与选择类组件

| 组件 | `ENABLE` 默认 | 生效区域 | 关键约束与专属接口 |
|---|---|---|---|
| `Button` | 不默认开启 | 仅标题栏/底栏 | 通用 `.systemMaterial()`；未设色时默认按钮主题色材质；启用 `lightEffect` 会替代默认点击/悬浮态。 |
| `Select` | 开启（按钮 `ULTRA_THIN`，菜单 `THICK`） | 全页面 | 按钮用 `.systemMaterial()`，下拉菜单用 `.menuSystemMaterial()`，**两者独立**，单独关闭需传 `uiMaterial.Material.empty`。 |
| `Toggle` | 开启 | 全页面 | `ToggleType.Checkbox` **不支持**；`Switch` 传入参数仅作开关标记（使用内部预设）；`Button` 类型表现同 `Button`。 |
| `Slider` | 开启 | 全页面 | 材质参数用作开关，实际滑块样式由组件预设决定。显式关闭用 `uiMaterial.Material.empty`。适配指南提到传 `undefined` 可恢复原样式，但应用模式仍可能提供默认材质。交互反馈需 `SliderBlockType.DEFAULT` 且样式非 `SliderStyle.NONE`。 |
| `ChipGroup` / `ChipGroupV2` | 开启（`ULTRA_THIN`） | 仅标题栏/底栏 | 使用 `backgroundSystemMaterial`、`selectedBackgroundSystemMaterial`、`iconBackgroundSystemMaterial`；反色需用 `$r('sys.color.xxx')`。 |
| `SegmentButton` / `SegmentButtonV2` | 开启（`THIN`） | 仅标题栏/底栏 | 使用 `options.backgroundSystemMaterial`；**胶囊多选分段按钮（`type: 'capsule'` 且 `multiply: true`）及 `MultiCapsuleSegmentButtonV2` 不支持**；开启后支持选中背景跟手拖拽。 |

### 5.4 其余通用组件与区域对齐

- 布局容器（`Column`/`Row`）、`Search` 等组件通过 `.systemMaterial(...)` 设置，**仅在 `Navigation`/`NavDestination` 标题栏或横向底部 `TabBar` 生效**。
- **材质渲染区域 = 组件布局区域**：`Progress(Capsule)`、`Checkbox`、`Text` 等可视区域可能小于矩形布局区域，须通过 `.width()`、`.height()`、`.borderRadius()` 或 `.clipShape()` 对齐可视边界；`Text` 无法单独对文字笔画本身设置材质。
- **内容层遮盖背板层**：`TextArea` 等自绘制组件如果同时设置了 `.backgroundColor(...)`，背景色绘制在内容层会遮盖背板层的沉浸材质，应移除或设为透明。

---

## 6. 典型场景与跨版本兼容代码模式

### 6.1 搜索框与标题栏联动（`NavDestination` + `BarStyle.STACK`）

```ts
// 关键结构：NavDestination + contentStartOffset 避让 + title BarStyle.STACK + Search 材质
NavDestination() {
  Scroll() {
    Column() {
      // 内容区...
    }
  }
  .contentStartOffset(this.totalTitleHeight)
  .onDidScroll((_xOffset: number, yOffset: number) => {
    this.scrollOffset = Math.max(0, this.scrollOffset + yOffset);
    this.titleOffset = Math.min(this.scrollOffset, this.searchCollapseDistance);
    this.searchOpacity = 1 - this.titleOffset / this.searchCollapseDistance;
  })
}
.title(
  { builder: this.exploreTitleBar, height: this.totalTitleHeight },
  {
    barStyle: BarStyle.STACK,
    scrollEffectOptions: { scrollEffectType: ScrollEffectType.GRADUAL_BLUR }
  }
)
.hideBackButton(true)
```

根据搜索行实际高度设置正数 `searchCollapseDistance`，搜索行随滚动收起，分类行保持可见。用 `contentStartOffset` 给首屏内容留下标题栏空间。若搜索行仅用透明度隐藏，同步处理其触摸和无障碍焦点。保留在标题栏 builder 内的 `Search` 才能使用通用 `.systemMaterial(...)`。底部悬浮页签或内容延伸到避让区时，另行处理底部手势区。

### 6.2 内容区小标题滑入标题栏切换方案（解决内容区不生效限制）

当滚动内容区的分类栏或小标题需要在顶栏呈现沉浸光感时：

1. 把分类控件提取成可复用的组件，两个挂载位置共享选中项及事件。内容区保留普通样式，切入标题栏时用 `Visibility.Hidden` 保留占位。
2. 布局完成后使用 `getUIContext().getComponentUtils().getRectangleById(...)` 读取内容区小标题与顶栏的窗口坐标。在同一坐标系内比较，进入 vp 布局运算前用 `px2vp(...)`。尺寸、安全区或内容布局变化后重新测量。
3. 在滚动回调里判断是否跨过顶栏边界，仅在状态变化时切换到 `title` builder 或还原内容区控件。给顶栏实例配置材质，来回滚动验证位置、选中项和焦点连续。

### 6.3 跨版本兼容与互斥样式

以 `PromptAction.openCustomDialog(options)` 为例，为材质和模糊降级分别构建参数。

```ts
import { promptAction, uiMaterial } from '@kit.ArkUI';
import { deviceInfo } from '@kit.BasicServicesKit';

function dialogOptions(builder: CustomBuilder): promptAction.CustomDialogOptions {
  if (deviceInfo.apiAvailable('26.0.0') && uiMaterial.isImmersiveMaterialSupported()) {
    return {
      builder,
      systemMaterial: new uiMaterial.ImmersiveMaterial({
        style: uiMaterial.ImmersiveStyle.ULTRA_THICK
      })
    };
  }
  return { builder, backgroundBlurStyle: BlurStyle.COMPONENT_THICK };
}
```

在组件内调用 `this.getUIContext().getPromptAction().openCustomDialog(dialogOptions(() => this.dialogBody()))`，处理返回的 Promise。此示例假定项目启用 ArkUI 材质，且兼容下限满足所用的弹窗重载和模糊 API。如果应用提供自己的材质开关，支持设备上显式关闭默认材质时使用 `Material.empty`。

空间化最佳实践的菜单示例同时使用 HDS，并用 `hdsMaterial.getSystemMaterialTypes().length > 0` 作示例条件。独立 ArkUI 接入使用 `uiMaterial.isImmersiveMaterialSupported()`。HDS 自定义等级的判断使用 `IMMERSIVE` 成员检测。兼容旧版时，将构造材质、读取 `Material.empty` 与调用新属性都放在版本保护内。在低于兼容下限或 SDK 缺少对应接口的产品中选择其可用的普通样式。

---

## 7. 功耗优化

沉浸光感叠加滤镜、折射、高光、阴影等多层 GPU 计算，须视为“稀缺视觉资源”：

1. **控制材质面积与位置**：禁止用于全屏背景或大量小元素重复铺设，限定在标题栏、底部悬浮页签和局部需要凸显的浮层。
2. **禁止子树嵌套**：同一子树仅在最外层设置一次 `systemMaterial`，内层节点不再设置，避免重复计算与视觉干扰。
3. **避免同一背板重复模糊**：材质自带滤镜。检查同一背板上的 `backgroundBlurStyle`、`backgroundEffect` 或 `backdropBlur`。版本降级可以单独启用模糊，标题栏的原生滚动渐变可以与局部按钮材质配合。
4. **控制弹窗尺寸**：高算力且光感设为强或均衡时，`Dialog` / `Menu` 默认含形变和流光。尽量缩小材质绘制面积。
5. **避开动态背景**：禁止在播放中的视频、动图或高频动画上方固定悬浮沉浸式系统材质，防止背景逐帧重采样。
6. **缩小 `colorInvert` 作用范围**：仅包裹需要保证可读性的局部文字/图标容器，禁止在包含大量 `ForEach` 列表项的外层容器开启 `colorInvert: true`。
7. **保持参数与子树稳定**：一次性确定 `style`、`materialColor` 等参数，禁止在 `setInterval` 或高频动画回调中反复更改材质参数或增删材质子树节点。
8. **避免阴影重复叠加**：自定义 `.shadow()` 前必须先配置 `applyShadow: false`。

---

## 8. 常见问题速查表

| 现象 | 原因 | 解决措施 |
|---|---|---|
| 设置后无效果，日志报 `Material inactive: out of scope` | 非弹窗/非 `Slider`/`Toggle`/`Select` 组件放在了内容区 | 移入 `Navigation`/`NavDestination` 标题栏或横向 `Tabs` 底部 `TabBar`，或改用滑入标题栏切换方案 / `backgroundColor` |
| 组件只显示纯色/原模糊，看不到材质 | `backgroundColor` 或 `backgroundBlurStyle` 遮挡，或 `.systemMaterial()` 写在样式属性前 | 背景设为 `Color.Transparent` 或移除，删去背景模糊，把 `.systemMaterial()` 放在链式样式最后 |
| `openCustomDialog` / `openCustomDialogWithController` 或 `customStyle: true` 无效 | 调用的是 `ComponentContent` 重载或设置了自定义背板 | 需要系统背板材质时用 `PromptAction.openCustomDialog({ builder, systemMaterial })` |
| 边框出现周围背景颜色 | `ULTRA_THIN`/`THIN` 的正常光学折射表现 | 若需减弱边框折射，可改用 `REGULAR`/`THICK`，或添加半透明 `materialColor`（如 `'#80FFFFFF'`） |
| 传入 `materialColor` 后材质完全消失成纯色 | 传入了纯不透明颜色（如 `Color.Red`） | 改用带透明度的颜色（如 `'#80FF0000'`、`'rgba(255,0,0,0.2)'`） |
| 开启 `colorInvert: true` 文字不变色 | 样式太厚、低算力设备、或未使用特殊 `$r('sys.color.xxx')` | 改用 `THIN`/`ULTRA_THIN` + 26 个系统可反色颜色资源之一 |
| 自定义 `.shadow()` 不生效 | `applyShadow` 默认为 `true`，优先于 `.shadow()` | 在 `ImmersiveOptions` 中显式设置 `applyShadow: false` |
| 传 `undefined` 后材质仍存在 | `undefined` 表示恢复组件默认沉浸光感，而非关闭 | 改传 `uiMaterial.Material.empty`（或在 `module.json5` 设为 `disable`） |
| `AlphabetIndexer` 提示气泡无沉浸光感 | 应用处于 `DISABLE`，气泡背景被显式设置，或设备为低算力 | 确认 `usingPopup` 与应用模式，恢复默认弹窗背景，并核对低算力的预期白底 |
| `Popup`、`Tips` 或 `bindSheet` 在 `ENABLE` 下仍无材质 | 组件需要显式设置 | 分别在 `PopupOptions`、`TipsOptions`、`SheetOptions` 中设置 `systemMaterial` |
| 普通 `Tabs` 设置材质后背板不变 | 悬浮样式没有生效，材质写在 `TabContent`，或背板有其他背景 | 检查横向、底部、重叠三项条件，并将材质放进 `FloatingTabBarStyle` |
| 材质渲染区域比组件形状大（如胶囊变矩形） | 材质按布局区域渲染，未匹配可视区域 | 通过 `.width()` / `.height()` / `.borderRadius()` / `.clipShape()` 对齐可视尺寸 |
