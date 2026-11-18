# HDS 与 ArkUI 沉浸光感技术手册

## 1. 双体系对比：`hdsMaterial` vs `uiMaterial`

HarmonyOS 提供两套互补的沉浸光感（Immersive Light）能力体系，切勿混淆枚举或导入路径：

| 维度 | HDS 组件材质（`hdsMaterial`） | ArkUI 系统材质（`uiMaterial`） |
|---|---|---|
| 起始版本 | HarmonyOS 6.1.0 (`API 23`)+ | `API 26.0.0`+（`targetSdkVersion >= 26.0.0`） |
| 导入模块 | `import { hdsMaterial } from '@kit.UIDesignKit'` | `import { uiMaterial } from '@kit.ArkUI'` |
| 适用范围 | `HdsNavigation` / `HdsNavDestination` 标题栏按钮、`HdsTabs` 悬浮底部页签 | 通用 `Navigation` / `Tabs`、弹窗类组件/接口、`Slider`、`Toggle`、`Select`、`AlphabetIndexer`、`ChipGroup`、`SegmentButton` 等 |
| 模型与卡片 | `getSystemMaterialTypes()` 和相关枚举限定 Stage 模型，支持 ArkTS 卡片（6.1.0(23)+） | 逐接口核对 Stage、卡片及元服务支持范围 |
| 能力探测 | `hdsMaterial.getSystemMaterialTypes()` 返回设备支持的材质类型 | `uiMaterial.isImmersiveMaterialSupported()` 检查支持情况，`getGlobalMaterialLevel()` 读取设备等级，`getMaterialInfo()` 读取应用配置 |
| 材质等级（`MaterialLevel`） | `EXQUISITE`(0 精美) / `GENTLE`(1 轻柔) / `SMOOTH`(2 流畅) / `ADAPTIVE`(10 系统自适应) — **支持主动配置** | `EXQUISITE`(0 高算力) / `GENTLE`(1 中算力) / `SMOOTH`(2 低算力) — **仅只读查询，不支持手动设置，天然自适应** |
| 材质样式（厚度） | 不提供 `ImmersiveStyle`，由 `materialType` + `materialLevel` 与组件差异化实现共同决定 | `ImmersiveStyle`: `ULTRA_THIN`(0)、`THIN`(1)、`REGULAR`(2)、`THICK`(3)、`ULTRA_THICK`(4)（仅高/中算力生效） |
| 空间动效 | 由 HDS 组件内部协同系统实现 | 弹窗/菜单（非线性形变 + 边缘流光）、`Slider`（粒子动画），随设备算力和系统光感档位自适应 |
| 平台约束 | 检查 UI Design Kit 和 `SystemCapability.UIDesign.HDSComponent.Core` | 检查项目 SDK 的导出及设备支持。兼容旧版时先用 `deviceInfo.apiAvailable('26.0.0')` 保护新 API |

> [!IMPORTANT]
> 系统光感提供强、均衡（默认）、弱三档。透明度、反色率、折射、动效和环境交互由系统按档位调节，应用共用同一套材质配置。

---

## 2. HDS 组件空间化与沉浸光感（`@kit.UIDesignKit`，API 23+）

### 2.1 首选：系统自适应策略

`HdsNavigation` / `HdsNavDestination` 通过 `titleBar.style.systemMaterialEffect` 配置标题栏按钮，`HdsTabs` 通过 `HdsTabsFloatingStyle.systemMaterialEffect` 配置悬浮页签。默认使用自适应类型和等级：

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

- 支持 `IMMERSIVE` 时可选 `EXQUISITE` 或 `GENTLE`，不支持时使用 `SMOOTH` 等级。
- 探测与降级分支均可保持 `MaterialType.ADAPTIVE`，仅切换 `materialLevel`。兼容更低系统版本时，对起始于 6.1.0(23) 的 API 使用 `deviceInfo.apiAvailable('6.1.0')` 保护，并为缺少 HDS 能力的产品保留普通导航组件。

### 2.3 `HdsNavigation` 标题栏渐变模糊与动态显隐

- **渐变模糊对比**（`titleBar.style.scrollEffectOpts`）：
  - `ScrollEffectType.IMMERSIVE_GRADIENT_BLUR`：从**完全透明**渐变到模糊，模糊区域更大、过渡更自然、沉浸感更强。
  - `ScrollEffectType.GRADIENT_BLUR`：从**半透明**渐变到模糊，过渡相对克制，兼顾信息密度。
  - 两者均需配合 `systemMaterialEffect` 与 `.bindToScrollable([this.scroller])` 呈现完整效果。
- **标题栏与状态栏滑动动态显隐**：通过 `dynamicHideTitleBar` 联动 `.bindToScrollable(...)`：
  - `hideTitleArea: true`、`hideStatusBar: true`。
  - `mode` 支持：`HideMode.SCROLL_UP_TO`（上滑到固定位置隐藏、下滑到固定位置显示）、`HideMode.SCROLL_UP`、`HideMode.SCROLL_DOWN`、`HideMode.SCROLL_UP_TO_BLEND_SCROLL_UP`。

同一个页面若同时使用标准 ArkUI 导航与 HDS 导航，需区分两个同名的 `ScrollEffectType`：HDS 从 `@kit.UIDesignKit` 导入枚举并配置 `scrollEffectOpts`，标准标题栏使用 `ScrollEffectType.GRADUAL_BLUR` 与 `scrollEffectOptions`。

### 2.4 `HdsTabs` 悬浮底栏、沉浸式 MiniBar 与智感握姿

底部悬浮页签须同时满足 `barOverlap(true)`、`vertical(false)`、`barPosition(BarPosition.End)`，并在 `.barFloatingStyle(...)` 中配置材质与动态行为。`MiniBar` 由容器按可用宽度处理展开与折叠，`adaptToHandedness` 用于支持智感握姿的宽屏设备，各字段起始版本以目标 SDK 声明为准：

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

使用 ArkUI 沉浸光感须确保目标产品 `targetSdkVersion >= 26.0.0`；兼容更低运行时版本时，必须配合 `deviceInfo.apiAvailable('26.0.0')` 做运行时保护。

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
- **优先级**：应用模式允许时，可通过组件的专用入口覆盖和关闭默认效果。`DISABLE` 会阻止 ArkUI 组件级接入。组件没有相应入口时，使用其文档指定的控制方式（例如 `AlphabetIndexer` 的气泡背景属性）。
- **正确关闭材质与恢复默认**：
  - 单独关闭某个默认开启沉浸光感的组件，**必须使用 `uiMaterial.Material.empty`**（例如 `.systemMaterial(uiMaterial.Material.empty)` 或 `.menuSystemMaterial(uiMaterial.Material.empty)`）。
  - **不要传入 `undefined` 企图关闭**：`undefined` 表示“恢复为组件默认的沉浸光感效果”，在 `ENABLE` 模式或默认开启组件上依然会呈现材质。
- **应用内材质开关与主题背景联动**：
  - 使用应用开关、API 版本与 `uiMaterial.isImmersiveMaterialSupported()` 统一推导 `useMaterial`，同时决定材质与背板背景色：开启且设备支持时保持背板 `Color.Transparent`，通过带透明度的 `materialColor` 混入品牌色；关闭或设备不支持时恢复主题实体背景色，避免在应用开关开启但设备不支持的分支出现空材质配透明背板。
  - **检查专用字段的类型定义**：API 26 SDK 将 `FloatingTabBarStyle.systemMaterial` 声明为 `ImmersiveMaterial`。在该字段传入 `uiMaterial.Material.empty` 前须使用目标 SDK 构建并验证关闭材质后的画面；若目标 SDK 或设备上无法通过 `Material.empty` 可靠关闭，应切换为显式普通底栏样式并保留操作可达性。

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

## 4. `ImmersiveOptions` 核心参数、厚度规范与实例复用

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

- 默认为透明。高/中算力设备将颜色混入材质滤镜，低算力设备将其作为背景色处理，须按目标组件核查低算力下的表现。
- 用于表达品牌色调，或**降低 `ULTRA_THIN`/`THIN` 边缘折射周围背景色的强度**。
- **必传半透明色**：如 `'#80FFFFFF'`、`'rgba(255, 0, 0, 0.2)'`。传入纯不透明色（如 `Color.Red`、`'#FFFF0000'`）会**完全遮挡材质滤镜效果**。

### 4.3 `colorInvert: boolean`（默认 `false`）

开启后可将组件子树内文字、图标颜色自动反色以保障薄材质下的可读性。**同时满足以下 4 个条件才会生效**：
1. 设备为**高算力或中算力**（低算力不产生效果差异）。
2. `style` 必须为 **`ULTRA_THIN` 或 `THIN`**（`REGULAR`/`THICK`/`ULTRA_THICK` 下不生效）。
3. 达到当前系统强/均衡/弱档位的反色触发阈值（材质越薄、系统强度越强，越容易触发）。
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
- `lightEffect`：传 `{}` 或 `{ color: Color.White }` 配置交互光感反馈，传 `null` 显式关闭，省略时沿用组件默认行为。具体反馈由组件、设备和系统设置决定，API 26.0.0 SDK 将该参数标注为适用于各算力档。
- 当 `Button` 或 `Select` 启用 `lightEffect` 时，组件默认的点击态与悬浮态视觉反馈不再展示，由材质光感交互反馈替代。
- **区分选中态与交互反馈**：顶栏或分段导航的选中项可配置半透明主题 `materialColor` 与阴影（`applyShadow: true`），未选中项可仅保留 `lightEffect` 并设 `applyShadow: false`，或仅对选中项显式设置材质。采用 `lightEffect` 后须验证按压与悬停反馈及对比度；使用可反色系统资源 `$r('sys.color.xxx')` 时再开启 `colorInvert` 并核查自动反色效果。

### 4.6 材质实例复用与主题动态缓存

- **固定配置复用**：固定样式的材质通过组件 `readonly` 字段或模块常量复用，避免在 `build()` 每次重绘时创建新实例；`uiMaterial.isImmersiveMaterialSupported()` 探测结果同样在初始化阶段缓存。
- **主题动态赋色缓存**：按影响构造的样式、半透明 `materialColor`、光效色与 `applyShadow` 等参数组合缓存键复用实例，仅在主题或选中样式变化时新建或切换；颜色来源有限时复用静态 `Map`，支持任意自定义颜色时仅保留当前主题的少量实例。
- 拼接透明度前缀（如 `'#CC' + rgb.substring(1)`）前须确认输入色值为 `#RRGGBB` 格式：

```ts
import { LengthMetrics, uiMaterial } from '@kit.ArkUI';

export interface PaletteLike {
  isDark: boolean;
  primary: string;
  card: string;
  page: string;
}

export class ImmersiveTitleStyle {
  private static supported: boolean | undefined = undefined;
  private static materials: Map<string, uiMaterial.ImmersiveMaterial> =
    new Map<string, uiMaterial.ImmersiveMaterial>();

  static isSupported(): boolean {
    if (ImmersiveTitleStyle.supported === undefined) {
      try {
        ImmersiveTitleStyle.supported = uiMaterial.isImmersiveMaterialSupported();
      } catch (_error) {
        ImmersiveTitleStyle.supported = false;
      }
    }
    return ImmersiveTitleStyle.supported;
  }

  static background(palette: PaletteLike, enabled: boolean, active: boolean = false): ResourceColor {
    if (enabled && ImmersiveTitleStyle.isSupported()) {
      return Color.Transparent;
    }
    return active ? palette.primary : palette.card;
  }

  static material(palette: PaletteLike, enabled: boolean, active: boolean = false): uiMaterial.Material {
    if (!enabled || !ImmersiveTitleStyle.isSupported()) {
      return uiMaterial.Material.empty;
    }
    const baseHex: string = active ? palette.primary : palette.card;
    const tint: string = (palette.isDark ? '#CC' : '#38') + baseHex.substring(1);
    const cacheKey: string = `${tint}_${palette.primary}`;
    const cached: uiMaterial.ImmersiveMaterial | undefined = ImmersiveTitleStyle.materials.get(cacheKey);
    if (cached !== undefined) {
      return cached;
    }
    const material: uiMaterial.ImmersiveMaterial = new uiMaterial.ImmersiveMaterial({
      style: uiMaterial.ImmersiveStyle.ULTRA_THIN,
      materialColor: tint,
      interactive: true,
      applyShadow: true,
      lightEffect: { color: palette.primary }
    });
    ImmersiveTitleStyle.materials.set(cacheKey, material);
    return material;
  }

  static titleTheme(palette: PaletteLike): CustomTheme {
    return { colors: { compBackgroundGray: palette.page } };
  }

  static titleBarOptions(immersiveEnabled: boolean, scrollUnderTitle: boolean): NavigationTitleOptions {
    const useScrollEffect: boolean = immersiveEnabled && scrollUnderTitle;
    return {
      barStyle: BarStyle.STACK,
      backgroundColor: Color.Transparent,
      scrollEffectOptions: useScrollEffect
        ? {
            scrollEffectType: ScrollEffectType.GRADUAL_BLUR,
            blurEffectiveStartOffset: LengthMetrics.vp(8),
            blurEffectiveEndOffset: LengthMetrics.vp(32)
          }
        : undefined,
      systemMaterial: useScrollEffect ? undefined : uiMaterial.Material.empty
    };
  }
}
```

---

## 5. 四大类组件适配速查

### 5.1 导航类组件

| 组件 | `ENABLE` 默认 | 推荐开启方式与关键约束 |
|---|---|---|
| `Navigation` / `NavDestination` | 开启（`ULTRA_THIN`） | 通过 `NavigationTitleOptions.systemMaterial` 配置系统返回键与非自定义菜单。自定义 builder 内的控件通过各自入口设置。需要内容透底时用 `BarStyle.STACK`。 |
| `Tabs`（底部页签） | 仅生效 `barFloatingStyle` 时开启（`THIN`） | 通过 `.barFloatingStyle({ systemMaterial: ... })` 配置，并同时满足 `barOverlap(true)`、`vertical(false)`、`barPosition(BarPosition.End)`。启用材质的分支保持背板透明，主题背景和背景模糊可用于独立降级分支。`TabContent` 不承载 TabBar 背板材质。 |
| `AlphabetIndexer`（索引条） | 开启（提示弹窗 `THICK`） | 用 `.usingPopup(true)` 打开提示气泡。保留默认材质时省略 `popupBackground` 和 `popupBackgroundBlurStyle`，或传 `undefined` 恢复默认。任意一项显式设置都会关闭该气泡的默认材质。高/中算力显示 `THICK`，低算力显示白底。 |

- **`Tabs` 浮栏胶囊宽度与遮罩控制**：保持原生胶囊宽度，或通过 `FloatingTabBarStyle.barWidth`（`smallBarWidth` / `mediumBarWidth` / `largeBarWidth`）与 `barSideMargin` 定制宽度。**切勿**对开启 `barFloatingStyle` 的 `Tabs` 设置通用 `.barWidth('100%')`，否则会覆盖胶囊宽度规则将底栏拉满屏幕两侧。仅需关闭浮栏下方的默认渐变蒙层时，在 `barFloatingStyle` 中传入 `maskColor: Color.Transparent` 与 `maskHeight: 0`。
- **`AlphabetIndexer` 布局与长列表首项联动**：
  - 索引条布局按扣除状态栏与底部工具栏/页签后的可用高度垂直居中；顶部存在子页签等组合控件时，从其下边界加适当间距定位；横屏或分屏高度不足时使用 `autoCollapse(true)` 动态折叠，并分别验证拖动索引、列表定位与气泡显示。如需品牌色实体气泡而非默认沉浸气泡，可显式设置主题 `popupBackground` 并核对对比度。
  - 搜索、统计、导出等列表头工具条可作为 `List` 的首个 `ListItem` 随列表滚动（数据行由 `LazyForEach` 承载），消除固定栏下方的硬裁切线。固定列表头占索引 0 时，字母跳转定位数据行使用 `rowIndex + 1`，滚动同步反向扣除 1；过滤或列数变化后重建字母到行索引的映射并校验选中项，覆盖空结果、首尾及跨列调整。

### 5.2 弹窗类组件（全页面生效）

| 组件 / 接口 | `ENABLE` 默认 | 推荐开启方式与关键约束 |
|---|---|---|
| `Toast` | 开启（`THICK`） | `ShowToastOptions.systemMaterial`；`DEFAULT` 模式下未设背景/模糊/阴影时默认 `THICK`。 |
| `Popup` / `Tips` | 不默认开启 | 需组件级传入 `PopupOptions.systemMaterial` / `TipsOptions.systemMaterial`。 |
| `Menu` | 开启（`THICK`） | `ContextMenuOptions.systemMaterial` 或 `promptAction.openMenu` 的 `MenuOptions` 中配置；高算力含非线性形变与边缘流光。 |
| `Dialog`（`AlertDialog`、`ActionSheet`、`CustomDialog`、各类 `PickerDialog`） | 开启（`ULTRA_THICK`） | 在 `options.systemMaterial` 配置。处于 `DEFAULT` 时，保留默认背板样式可获得默认材质。独立的 `CalendarPickerDialog` 支持材质，`CalendarPicker` 控件拉起的弹窗由控件内部绘制，通用属性仅作用于触发器。 |
| `bindSheet`（半模态） | 不默认开启 | 需在 `SheetOptions.systemMaterial` 显式设置；设置后 `backgroundColor`、`borderColor`、`borderWidth`、`shadow` 不再生效。 |

**自定义弹窗先核对调用签名。** `PromptAction.openCustomDialog(options: CustomDialogOptions)` 传入 `{ builder, systemMaterial }` 时可给系统背板配置材质。传入 `ComponentContent` 的 `openCustomDialog(dialogContent, options)` 和 `openCustomDialogWithController(dialogContent, controller, options)` 使用自定义弹窗背板，即使类型声明允许填写 `systemMaterial`，背板也不会应用该材质。使用 `CustomDialogController` 时，保留系统背板的样式路径（`customStyle` 关闭）。

### 5.3 按钮与选择类组件

| 组件 | `ENABLE` 默认 | 生效区域 | 关键约束与专属接口 |
|---|---|---|---|
| `Button` | 不默认开启 | 仅标题栏/底栏 | 通用 `.systemMaterial()`；未设色时默认按钮主题色材质；启用 `lightEffect` 会替代默认点击/悬浮态。标题栏圆形图标按钮使用 `Button({ type: ButtonType.Circle, buttonStyle: ButtonStyleMode.TEXTUAL }).width(40).height(40).padding(0)` 避免默认强调底色与图标偏移。 |
| `Select` | 开启（按钮 `ULTRA_THIN`，菜单 `THICK`） | 全页面 | 按钮用 `.systemMaterial()`，下拉菜单用 `.menuSystemMaterial()`，**两者独立**，单独关闭需传 `uiMaterial.Material.empty`。 |
| `Toggle` | 开启 | 全页面 | `ToggleType.Checkbox` **不支持**；`Switch` 传入参数仅作开关标记（使用内部预设）；`Button` 类型表现同 `Button`。 |
| `Slider` | 开启 | 全页面 | 材质参数用作开关，实际滑块样式由组件预设决定。显式关闭传 `uiMaterial.Material.empty`，传 `undefined` 恢复组件默认行为。交互反馈需 `SliderBlockType.DEFAULT` 且样式非 `SliderStyle.NONE`。 |
| `ChipGroup` / `ChipGroupV2` | 开启（`ULTRA_THIN`） | 仅标题栏/底栏 | 使用 `backgroundSystemMaterial`、`selectedBackgroundSystemMaterial`、`iconBackgroundSystemMaterial`；反色需用 `$r('sys.color.xxx')`。 |
| `SegmentButton` / `SegmentButtonV2` | 开启（`THIN`） | 仅标题栏/底栏 | 使用 `options.backgroundSystemMaterial`；**胶囊多选分段按钮（`type: 'capsule'` 且 `multiply: true`）及 `MultiCapsuleSegmentButtonV2` 不支持**；开启后支持选中背景跟手拖拽。 |

### 5.4 其余通用组件与区域对齐

- 布局容器（`Column`/`Row`）、`Search` 等组件通过 `.systemMaterial(...)` 设置，**仅在 `Navigation`/`NavDestination` 标题栏或横向底部 `TabBar` 生效**。
- **材质渲染区域 = 组件布局区域**：`Progress(Capsule)`、`Checkbox`、`Text` 等可视区域可能小于矩形布局区域，须通过 `.width()`、`.height()`、`.borderRadius()` 或 `.clipShape()` 对齐可视边界；`Text` 无法单独对文字笔画本身设置材质。
- **内容层遮盖背板层**：`TextArea` 等自绘制组件如果同时设置了 `.backgroundColor(...)`，背景色绘制在内容层会遮盖背板层的沉浸材质，应移除或设为透明。

---

## 6. 导航布局与典型场景模式

### 6.1 宽窄屏导航结构与页签切换

根据页面与多设备断点选择结构，并确保主导航、路由栈和滚动状态一致：

- **窄屏底栏 + 宽屏共享顶栏**：窄屏每个 `TabContent` 包裹独立 `Navigation`（避免切页时未滚动的新页签残留上一页签的标题栏模糊状态）；达到宽屏断点（如 `>= 840vp`）后，隐藏底栏并由外层 `Navigation` 持有共享顶栏，各 `TabContent` 移除内层导航直接放置 `Scroll` 驱动外层顶栏模糊。
- **窄屏底栏 + 宽屏侧栏导航轨**：保留 `Tabs` 承载内容，宽屏隐藏底栏并显示独立导航轨；窄屏二级页按路由决定是否通过 `barHeight(0)`、`barOverlap(false)` 并移除 `barFloatingStyle` 隐藏底栏，需跨模块流转的编辑流程按需保留主导航。
- **窄屏独立标题 + 宽屏独立桌面工作区**：窄屏使用各页独立滚动标题，宽屏切入桌面工作区组件，按页面映射选中状态并协同编辑器及自由窗口原生三键按钮；两种布局共享业务路由与选中状态，各自维护滚动容器。
- **内容区侧栏**：位于普通内容区的侧栏不在标题栏或底部 `TabBar` 材质生效范围内，应使用常规主题背景、圆角与选中态维持可读性，并为触摸、鼠标和键盘提供一致的导航激活行为。
- **统一控制器与减弱动画联动**：顶栏、侧栏、底栏驱动同一原生 `Tabs` 时复用同一个 `TabsController`（自定义入口调用 `changeIndex` 请求切换，`Tabs.onChange` 提交选中态，`onTabBarClick` 处理重选回顶，避免双向索引绑定与控制器冲突）。切页动画可使用 `AnimationMode.CONTENT_FIRST_WITH_JUMP` 与 `curves.springMotion`，并从 `accessibility.isAnimationReduceEnabledSync()` 初始化，通过具名回调订阅/注销 `onAnimationReduceStateChange` / `offAnimationReduceStateChange`，开启减弱动画时同步降级主 Tab、二级路由与自定义选中态动效。

### 6.2 原生滚动标题栏分层与 `scrollUnderTitle` 双模

1. **三层解耦结构**：
   - **导航容器层**：在 `Navigation` / `NavDestination` 的 `.title({ builder, height }, options)` 配置 `barStyle: BarStyle.STACK`、`backgroundColor: Color.Transparent` 及 `scrollEffectOptions: { scrollEffectType: ScrollEffectType.GRADUAL_BLUR }`。宽屏共享标题栏时，让当前页的滚动容器直接驱动外层导航，避免嵌套独立标题栏。
   - **可选渐变可读性衬底层**：将渐进色遮罩置于标题内容下方，必须设置 `.hitTestBehavior(HitTestMode.None)` 与 `.accessibilityLevel('no')` 保留按钮点击与读屏顺序。
   - **局部控件材质层**：仅在返回圆钮、右侧操作圆钮/胶囊与顶栏导航胶囊上挂载 `ULTRA_THIN` 材质；标题栏外层容器设 `.clip(false)` 避免 `applyShadow: true` 阴影被裁切，长标题限制行数并省略。
2. **首屏空间预留与自定义主题去色偏**：
   - 滚动容器通过 `contentStartOffset` 留出标题区域高度：可使用固定栏高（如 `56vp`）配合顶部 `.expandSafeArea(...)` 让系统安全区定位控件，也可显式将顶部 `titleTopInset` 计入栏高、`contentStartOffset` 与标题内部顶部 padding（系统已保留顶部时省去手工 inset）。
   - 原生 `BarStyle.STACK` + `ScrollEffectType.GRADUAL_BLUR` 会混入系统主题 Token `compBackgroundGray`，在自定义浅色或深色背景下可用 `WithTheme({ theme: { colors: { compBackgroundGray: pageColor } } })` 包裹 `Navigation`/`NavDestination` 消除灰底色偏，并分别验证深浅模式。
3. **`scrollUnderTitle` 双模切换**：
   - 内容可滚到标题栏下（`scrollUnderTitle = true`）：主体容器顶部 padding 为 `0`，由实际滚动容器提供 `contentStartOffset` 并开启 `GRADUAL_BLUR`。
   - 顶部固定搜索、筛选或编辑器不可滚入标题栏下（`scrollUnderTitle = false`）：主体容器提供栏高顶部 padding，关闭标题栏 `scrollEffectOptions` 并传 `systemMaterial: uiMaterial.Material.empty`，仅保留标题栏按钮自身的材质：

```ts
import { uiMaterial } from '@kit.ArkUI';

function titleOptions(immersiveEnabled: boolean, scrollUnderTitle: boolean): NavigationTitleOptions {
  const useScrollEffect: boolean = immersiveEnabled && scrollUnderTitle;
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

### 6.3 搜索框折叠与大标题收束联动（`NavDestination` + `BarStyle.STACK`）

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

- 根据搜索行实际高度设置正数 `searchCollapseDistance`，搜索行随滚动收起，分类行保持可见。用 `contentStartOffset` 为首屏内容留出标题栏空间；若搜索行仅用透明度隐藏，同步处理触摸拦截与无障碍焦点。保留在标题栏 builder 内的 `Search` 可直接设置 `.systemMaterial(...)`；底部悬浮页签或内容延伸到避让区时另行处理底部手势区。
- **页面大标题收束判定**：为各页大标题与顶栏绑定 id，在滚动时通过 `getUIContext().getComponentUtils().getRectangleById(...)` 直接比较两者的 `windowOffset.y + size.height`（均为窗口 px，可直接比较，避免 px/vp 混算）。节点未完成布局时用滚动偏移作临时判定，布局、窗口或内容变化后重测；每页独立记录收束布尔值且仅在状态改变时更新，切换或重选页签时按产品需求保持滚动位置或回到顶部。

### 6.4 内容区分类栏滑入标题栏切换方案（解决内容区不生效限制）

当滚动内容区的分类栏或小标题需要在顶栏呈现沉浸光感时：

1. 将分类控件提取为可复用组件，内容区与标题栏两个挂载位置共享选中项与事件；内容区保留常规样式，切入标题栏时用 `Visibility.Hidden` 保留占位。
2. 布局完成后使用 `getUIContext().getComponentUtils().getRectangleById(...)` 读取内容区控件与顶栏的窗口坐标，在统一坐标系内比较（进入 vp 布局运算前用 `px2vp(...)` 转换）；尺寸、安全区或内容布局变化后重新测量。
3. 在滚动回调中判断是否跨过顶栏边界，仅在状态变化时切换到 `title` builder 或还原内容区控件；为顶栏实例配置材质，来回滚动验证位置、选中项与焦点连续性。

### 6.5 跨版本兼容与互斥降级

以 `PromptAction.openCustomDialog(options)` 为例，为材质与模糊降级分别构建参数：

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

- 在组件内调用 `this.getUIContext().getPromptAction().openCustomDialog(dialogOptions(() => this.dialogBody()))` 并处理返回的 Promise。应用提供独立材质开关时，在支持设备上显式关闭默认材质须使用 `uiMaterial.Material.empty`。
- 兼容 API 26.0.0 以下运行时，将构造 `ImmersiveMaterial`、读取 `Material.empty` 与设置新属性均放在 `deviceInfo.apiAvailable('26.0.0')` 保护内，再通过 `uiMaterial.isImmersiveMaterialSupported()` 探测设备支持。同时使用 HDS 组件（API 23+）时，单独按 `deviceInfo.apiAvailable('6.1.0')` 与 `hdsMaterial.getSystemMaterialTypes()` 判断能力；在低于兼容下限或 SDK 缺少对应接口的产品中使用普通样式或标准模糊降级。

---

## 7. 功耗优化

沉浸光感叠加滤镜、折射、高光、阴影等多层 GPU 计算，须视为“稀缺视觉资源”：

1. **控制材质面积与位置**：禁止用于全屏背景或大量小元素重复铺设，限定在标题栏、底部悬浮页签和局部需要凸显的浮层。
2. **禁止子树嵌套**：同一子树仅在最外层设置一次 `systemMaterial`，内层节点不再设置，避免重复计算与视觉干扰。
3. **避免同一背板重复模糊**：材质自带滤镜，须排除同一背板上的 `backgroundBlurStyle`、`backgroundEffect` 或 `backdropBlur`。低版本降级分支可单独启用模糊，标题栏原生滚动渐变可与局部按钮材质配合。
4. **控制弹窗尺寸**：高算力且系统光感设为强或均衡时，`Dialog` / `Menu` 默认含非线性形变与边缘流光，应尽量缩小材质绘制面积。
5. **避开动态背景**：禁止在播放中的视频、动图或高频动画上方固定悬浮沉浸式系统材质，防止背景逐帧重采样。
6. **缩小 `colorInvert` 作用范围**：仅包裹需要保证可读性的局部文字/图标容器，禁止在包含大量 `ForEach` / `LazyForEach` 列表项的外层容器开启 `colorInvert: true`。
7. **保持参数与子树稳定**：一次性确定 `style`、`materialColor` 等参数并复用材质实例，禁止在 `setInterval` 或高频滚动/动画回调中反复更改参数或增删材质子树节点。
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
| `AlphabetIndexer` 提示气泡无沉浸光感 | 应用处于 `DISABLE`，气泡背景被显式设置，或设备为低算力 | 确认 `usingPopup` 与应用模式，省略或置空 `popupBackground`/`popupBackgroundBlurStyle`，并核对低算力白底表现 |
| `Popup`、`Tips` 或 `bindSheet` 在 `ENABLE` 下仍无材质 | 组件需要显式设置 | 分别在 `PopupOptions`、`TipsOptions`、`SheetOptions` 中设置 `systemMaterial` |
| 普通 `Tabs` 设置材质后背板不变 | 悬浮样式未生效，材质写在 `TabContent`，或存在其他背景/`.barWidth('100%')` 干扰 | 检查横向、底部、重叠三项条件，将材质放进 `FloatingTabBarStyle`，并移除 `.barWidth('100%')` |
| 材质渲染区域比组件形状大（如胶囊变矩形） | 材质按布局区域渲染，未匹配可视区域 | 通过 `.width()` / `.height()` / `.borderRadius()` / `.clipShape()` 对齐可视尺寸 |
