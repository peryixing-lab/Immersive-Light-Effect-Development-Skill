#!/usr/bin/env python3
"""Read-only audit for HarmonyOS HDS and immersive-window implementation."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple


SKIP_DIRS = {
    ".git",
    ".hvigor",
    ".idea",
    "build",
    "node_modules",
    "oh_modules",
}
TEXT_SUFFIXES = {".ets", ".ts", ".json", ".json5"}
MAX_FILE_BYTES = 2 * 1024 * 1024

SIGNALS: Sequence[Tuple[str, str]] = (
    ("hds_material", r"\bhdsMaterial\b"),
    ("ui_material", r"\buiMaterial\b"),
    ("system_material_effect", r"\bsystemMaterialEffect\b"),
    ("system_material_attr", r"\.systemMaterial\s*\("),
    ("immersive_material", r"\bImmersiveMaterial\b"),
    ("material_empty", r"\bMaterial\.empty\b"),
    ("module_material_state", r"ohos\.arkui\.UIMaterial\.state"),
    ("material_probe", r"\bgetSystemMaterialTypes\s*\("),
    ("ui_material_probe", r"\bisImmersiveMaterialSupported\s*\("),
    ("api_available_guard", r"\bapiAvailable\s*\("),
    ("ui_material_version_guard", r"""\bapiAvailable\s*\(\s*['"]26\.\d+\.\d+['"]\s*\)"""),
    ("adaptive_material", r"\bMaterialLevel\.ADAPTIVE\b"),
    ("custom_material", r"\bhdsMaterial\.MaterialLevel\.(?:EXQUISITE|GENTLE)\b"),
    ("smooth_fallback", r"\bhdsMaterial\.MaterialLevel\.SMOOTH\b"),
    (
        "hds_scroll_blur",
        r"\bScrollEffectType\.(?:IMMERSIVE_GRADIENT_BLUR|GRADIENT_BLUR|GRADUAL_BLUR)\b",
    ),
    ("dynamic_hide_title", r"\bdynamicHideTitleBar\s*\("),
    ("mini_bar", r"\bminiBar\s*:"),
    ("adapt_handedness", r"\badaptToHandedness\s*:"),
    ("background_immersive", r"\.background\s*\("),
    ("background_color", r"\.backgroundColor\s*\("),
    ("ignore_safe_area", r"\.ignoreLayoutSafeArea\s*\("),
    ("match_parent", r"\bLayoutPolicy\.matchParent\b"),
    ("expand_safe_area", r"\.expandSafeArea\s*\("),
    ("window_fullscreen", r"\bsetWindowLayoutFullScreen\s*\("),
    ("hide_system_bars", r"\bsetWindowSystemBarEnable\s*\(\s*\[\s*\]\s*\)"),
    (
        "restore_system_bars",
        r"\bsetWindowSystemBarEnable\s*\(\s*\[\s*['\"]status['\"]\s*,\s*['\"]navigation['\"]\s*\]",
    ),
    ("avoid_area_get", r"\bgetWindowAvoidArea\s*\("),
    ("avoid_area_on", r"\.on\s*\(\s*['\"]avoidAreaChange['\"]"),
    ("avoid_area_off", r"\.off\s*\(\s*['\"]avoidAreaChange['\"]"),
    ("hide_decor", r"\bsetWindowDecorVisible\s*\(\s*false\s*\)"),
    ("restore_decor", r"\bsetWindowDecorVisible\s*\(\s*true\s*\)"),
    ("title_rect_get", r"\bgetTitleButtonRect\s*\("),
    (
        "title_rect_on",
        r"\.on\s*\(\s*['\"]windowTitleButtonRectChange['\"]",
    ),
    (
        "title_rect_off",
        r"\.off\s*\(\s*['\"]windowTitleButtonRectChange['\"]",
    ),
    ("window_size_on", r"\.on\s*\(\s*['\"]windowSizeChange['\"]"),
    ("window_size_off", r"\.off\s*\(\s*['\"]windowSizeChange['\"]"),
)

VERSION_PATTERN = re.compile(
    r'["\']?(compileSdkVersion|compatibleSdkVersion|targetSdkVersion)["\']?'
    r"\s*:\s*(?:([\"'])([^\"']+)\2|(\d+))"
)
RE_BLUR_OVERLAP = re.compile(r"\.(?:backgroundBlurStyle|backgroundEffect|backdropBlur)\s*\(")
RE_OPAQUE_MATERIAL_COLOR = re.compile(
    r"materialColor\s*:\s*(?:Color\.(?!Transparent\b)[A-Za-z]+|['\"]#(?:[Ff]{2}[0-9A-Fa-f]{6}|[0-9A-Fa-f]{6})['\"])"
)
RE_INDEXER_POPUP_BG = re.compile(
    r"\.popupBackground(?:BlurStyle)?\s*\(\s*(?!undefined\b)[^\s)]"
)
RE_BAR_WIDTH_FULL = re.compile(r"\.barWidth\s*\(\s*['\"]100%['\"]\s*\)")


def _parse_sdk_api_level(entry: str) -> Optional[int]:
    raw_value = entry.rsplit(" (", 1)[0].strip()
    paren = re.search(r"\((\d+)\)", raw_value)
    if paren:
        return int(paren.group(1))
    leading = re.match(r"(\d+)", raw_value)
    return int(leading.group(1)) if leading else None


def _all_versions_at_least(entries: Sequence[str], min_api: int) -> bool:
    levels = [_parse_sdk_api_level(entry) for entry in entries]
    return bool(levels) and all(level is not None and level >= min_api for level in levels)


def iter_project_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size <= MAX_FILE_BYTES:
                yield path
        except OSError:
            continue


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def find_locations(
    root: Path, file_texts: Sequence[Tuple[Path, str]], pattern: str
) -> List[str]:
    compiled = re.compile(pattern)
    locations: List[str] = []
    for path, text in file_texts:
        rel = path.relative_to(root)
        for line_number, line in enumerate(text.splitlines(), start=1):
            if compiled.search(line):
                locations.append(f"{rel}:{line_number}")
    return locations


def detect_versions(
    root: Path, file_texts: Sequence[Tuple[Path, str]]
) -> Dict[str, List[str]]:
    versions: Dict[str, List[str]] = {}
    for path, text in file_texts:
        if path.name != "build-profile.json5":
            continue
        rel = path.relative_to(root)
        for match in VERSION_PATTERN.finditer(text):
            key = match.group(1)
            value = match.group(3) if match.group(3) is not None else match.group(4)
            entry = f"{value} ({rel})"
            versions.setdefault(key, [])
            if entry not in versions[key]:
                versions[key].append(entry)
    return versions


def _first_match_loc(rel: Path, text: str, pattern: re.Pattern[str]) -> str:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            return f"{rel}:{line_number}"
    return str(rel)


def _scan_code_file_warnings(
    rel: Path, text: str, add: Callable[[str, str, str], None]
) -> None:
    if re.search(r"\.ignoreLayoutSafeArea\s*\(", text) and not re.search(
        r"\bLayoutPolicy\.matchParent\b", text
    ):
        add(
            "WIN001",
            "ignoreLayoutSafeArea() 所在文件未发现 LayoutPolicy.matchParent；检查页面是否真正覆盖父容器。",
            str(rel),
        )
    if re.search(r"\.systemMaterial\s*\(", text) and RE_BLUR_OVERLAP.search(text):
        add(
            "MAT001",
            "同一文件有 .systemMaterial() 与背景模糊属性；检查是否同时作用于同一背板。不同控件或互斥回退分支可分别使用。",
            _first_match_loc(rel, text, RE_BLUR_OVERLAP),
        )
    if (
        re.search(r"\bImmersiveMaterial\b", text)
        and re.search(r"\.shadow\s*\(", text)
        and not re.search(r"applyShadow\s*:\s*false", text)
    ):
        add(
            "MAT002",
            "同一文件有 ImmersiveMaterial 与 .shadow()；如果给同一背板设置自定义阴影，需先设 applyShadow: false。",
            str(rel),
        )
    if re.search(r"colorInvert\s*:\s*true", text) and re.search(
        r"\bImmersiveStyle\.(?:REGULAR|THICK|ULTRA_THICK)\b", text
    ):
        add(
            "MAT003",
            "同一文件有 colorInvert: true 与较厚的材质；检查开启反色的实例是否使用 THIN 或 ULTRA_THIN。",
            str(rel),
        )
    if RE_OPAQUE_MATERIAL_COLOR.search(text):
        add(
            "MAT004",
            "materialColor 疑似传入纯不透明颜色；需使用带透明度的颜色，否则会完全遮挡材质滤镜效果。",
            _first_match_loc(rel, text, RE_OPAQUE_MATERIAL_COLOR),
        )
    if re.search(r"\bAlphabetIndexer\b", text) and RE_INDEXER_POPUP_BG.search(text):
        add(
            "MAT005",
            "AlphabetIndexer 主动设置了 popupBackground/popupBackgroundBlurStyle，会与提示弹窗默认沉浸光感互斥失效。",
            _first_match_loc(rel, text, RE_INDEXER_POPUP_BG),
        )
    if re.search(r"\.barFloatingStyle\s*\(", text) and RE_BAR_WIDTH_FULL.search(text):
        add(
            "WIN008",
            "同一文件同时存在 .barFloatingStyle() 与 .barWidth('100%')；后者会覆盖悬浮胶囊宽度规则并将底栏拉满屏幕两侧。",
            _first_match_loc(rel, text, RE_BAR_WIDTH_FULL),
        )


def build_warnings(
    root: Path,
    file_texts: Sequence[Tuple[Path, str]],
    locations: Dict[str, List[str]],
    versions: Dict[str, List[str]],
) -> List[Dict[str, str]]:
    warnings: List[Dict[str, str]] = []

    def add(code: str, message: str, location: str = "") -> None:
        warnings.append({"code": code, "message": message, "location": location})

    if locations["custom_material"] and not locations["material_probe"]:
        add(
            "HDS001",
            "发现 EXQUISITE/GENTLE 自定义材质，但未发现 getSystemMaterialTypes() 能力探测。",
            locations["custom_material"][0],
        )
    if (
        locations["custom_material"]
        and locations["material_probe"]
        and not locations["smooth_fallback"]
    ):
        add(
            "HDS002",
            "发现 HDS 自定义材质等级；检查不支持 IMMERSIVE 时是否使用 SMOOTH 降级。",
            locations["custom_material"][0],
        )

    for path, text in file_texts:
        if path.suffix.lower() in {".ets", ".ts"}:
            _scan_code_file_warnings(path.relative_to(root), text, add)

    if locations["hide_system_bars"] and not locations["restore_system_bars"]:
        add(
            "WIN002",
            "隐藏系统栏后未发现 status/navigation 恢复逻辑。",
            locations["hide_system_bars"][0],
        )
    if locations["avoid_area_on"] and not locations["avoid_area_off"]:
        add(
            "WIN003",
            "注册 avoidAreaChange 后未发现对应 off；检查窗口销毁和页面生命周期。",
            locations["avoid_area_on"][0],
        )
    if locations["hide_decor"] and not locations["restore_decor"]:
        add(
            "WIN004",
            "隐藏自由窗口标题栏后未发现 setWindowDecorVisible(true) 恢复逻辑。",
            locations["hide_decor"][0],
        )
    if locations["title_rect_on"] and not locations["title_rect_off"]:
        add(
            "WIN005",
            "注册 windowTitleButtonRectChange 后未发现对应 off。",
            locations["title_rect_on"][0],
        )
    if locations["window_size_on"] and not locations["window_size_off"]:
        add(
            "WIN007",
            "注册 windowSizeChange 后未发现对应 off。",
            locations["window_size_on"][0],
        )
    if locations["window_fullscreen"]:
        add(
            "WIN006",
            "setWindowLayoutFullScreen() 是窗口级全局沉浸；确认所有页面都处理了避让。",
            locations["window_fullscreen"][0],
        )
    if locations["hds_material"] and not versions.get("compatibleSdkVersion"):
        add(
            "CFG001",
            "发现 hdsMaterial，但未在 build-profile.json5 中识别 compatibleSdkVersion；手动确认最低 API 23。",
            locations["hds_material"][0],
        )
    ui_mat_locs = (
        locations["ui_material"]
        or locations["immersive_material"]
        or locations["module_material_state"]
    )
    if ui_mat_locs and not _all_versions_at_least(versions.get("targetSdkVersion", []), 26):
        add(
            "CFG002",
            "发现 ArkUI 沉浸光感配置；请确认使用该能力的构建产品 targetSdkVersion >= 26.0.0。",
            ui_mat_locs[0],
        )
    uses_ui_material_api = locations["ui_material"] or locations["immersive_material"]
    if (
        uses_ui_material_api
        and not _all_versions_at_least(versions.get("compatibleSdkVersion", []), 26)
        and not locations["ui_material_version_guard"]
    ):
        add(
            "CFG003",
            "项目可能兼容 API 26.0.0 以下；请确认实际的新 API 调用均有 deviceInfo.apiAvailable('26.0.0') 版本保护。",
            ui_mat_locs[0],
        )
    return warnings


def audit(root: Path) -> Dict[str, object]:
    file_texts: List[Tuple[Path, str]] = [
        (path, read_text(path)) for path in iter_project_files(root)
    ]
    locations = {
        name: find_locations(root, file_texts, pattern) for name, pattern in SIGNALS
    }
    versions = detect_versions(root, file_texts)
    warnings = build_warnings(root, file_texts, locations, versions)
    return {
        "root": str(root),
        "files_scanned": len(file_texts),
        "versions": versions,
        "signals": {
            name: {"count": len(items), "locations": items[:20]}
            for name, items in locations.items()
            if items
        },
        "warnings": warnings,
    }


def render_markdown(report: Dict[str, object]) -> str:
    lines = [
        "# HarmonyOS HDS / 沉浸式审计",
        "",
        f"- 项目：`{report['root']}`",
        f"- 扫描文件：{report['files_scanned']}",
        "",
        "## SDK",
        "",
    ]
    versions = report["versions"]
    if isinstance(versions, dict) and versions:
        for key, values in versions.items():
            lines.append(f"- {key}: {', '.join(f'`{value}`' for value in values)}")
    else:
        lines.append("- 未识别到 SDK 版本；请检查根目录与模块级 build-profile.json5。")

    lines.extend(["", "## 信号", ""])
    signals = report["signals"]
    if isinstance(signals, dict) and signals:
        for name, info in signals.items():
            count = info["count"]
            sample = ", ".join(f"`{item}`" for item in info["locations"][:3])
            lines.append(f"- {name}: {count}（{sample}）")
    else:
        lines.append("- 未发现 HDS 或沉浸式相关 API。")

    lines.extend(["", "## 警告", ""])
    warnings = report["warnings"]
    if isinstance(warnings, list) and warnings:
        for warning in warnings:
            location = f" — `{warning['location']}`" if warning["location"] else ""
            lines.append(
                f"- [{warning['code']}] {warning['message']}{location}"
            )
    else:
        lines.append("- 未发现脚本可识别的高风险模式。")

    lines.extend(
        [
            "",
            "## 下一步",
            "",
            "- 人工确认目标设备、窗口模式、明暗主题、生效范围和系统沉浸光感档位。",
            "- 结合安装 SDK 类型声明验证 API、枚举与 `targetSdkVersion`（HDS 23+ / uiMaterial 26.0.0+）。",
            "- 构建后在真机或模拟器检查旋转、折叠、分屏、自由窗口、功耗和生命周期恢复。",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit HarmonyOS HDS materials and immersive-window code."
    )
    parser.add_argument("project_root", help="HarmonyOS project root")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of Markdown",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: project root is not a directory: {root}", file=sys.stderr)
        return 2
    report = audit(root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
