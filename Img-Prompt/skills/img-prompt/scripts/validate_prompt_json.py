#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""img-prompt: 生图 JSON 提示词校验器。

校验规则与 references/prompt-json-spec.md 一一对应。

用法：
    python validate_prompt_json.py prompt.json
    python validate_prompt_json.py --stdin < prompt.json
    python validate_prompt_json.py prompt.json --flatten
    python validate_prompt_json.py prompt.json --json

退出码：0 通过（可含警告）、1 校验错误、2 用法或读取失败。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

FORBIDDEN_TOKENS = ("todo", "[todo", "placeholder", "占位", "待填", "xxx")

PANEL_CONTAINERS = (
    "top_left",
    "top_right",
    "side_panels",
    "left_column",
    "center_overlay",
    "right_column",
    "bottom_row",
    "footer",
)

CONTAINER_LABELS = {
    "top_left": "左上",
    "top_right": "右上",
    "side_panels": "侧栏",
    "left_column": "左栏",
    "center_overlay": "中部叠加",
    "right_column": "右栏",
    "bottom_row": "底部收束",
    "footer": "页脚",
}

CRAFT_KEYWORDS = (
    "纸纹",
    "纸张",
    "纤维",
    "颗粒",
    "网点",
    "印",
    "油墨",
    "拼贴",
    "水彩",
    "丝网",
    "手绘",
    "纹理",
    "材质",
    "版画",
    "晕染",
    "撕纸",
    "错位",
)

AVOID_MINIMUM = {"infographic": 5, "poster": 3}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="校验 img-prompt 生图 JSON 提示词（信息图 / 海报）。"
    )
    parser.add_argument("path", nargs="?", help="JSON 提示词文件路径")
    parser.add_argument("--stdin", action="store_true", help="从标准输入读取 JSON")
    parser.add_argument(
        "--flatten",
        action="store_true",
        help="校验通过后，额外输出展平后的中文段落提示词",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="以 JSON 输出校验结果（机器可读）",
    )
    return parser.parse_args()


def load_payload(args: argparse.Namespace) -> Any:
    if args.stdin:
        raw = sys.stdin.buffer.read().decode("utf-8-sig")
        source = "<stdin>"
    else:
        if not args.path:
            raise ValueError("需要提供 JSON 文件路径，或使用 --stdin")
        path = Path(args.path)
        if not path.is_file():
            raise ValueError(f"文件不存在: {path}")
        raw = path.read_text(encoding="utf-8-sig")
        source = str(path)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"{source} 不是合法 JSON: {error}") from error


def walk_strings(value: Any, path: str = "$") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, str):
        found.append((path, value))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(walk_strings(item, f"{path}[{index}]"))
    elif isinstance(value, dict):
        for key, item in value.items():
            found.extend(walk_strings(item, f"{path}.{key}"))
    return found


def require_object(payload: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any] | None:
    value = payload.get(key)
    if value is None:
        errors.append(f"缺少必填字段 `{key}`")
        return None
    if not isinstance(value, dict):
        errors.append(f"`{key}` 必须是对象")
        return None
    return value


def require_string(obj: dict[str, Any], key: str, field: str, errors: list[str]) -> str | None:
    value = obj.get(key)
    if value is None:
        errors.append(f"缺少必填字段 `{field}`")
        return None
    if not isinstance(value, str) or not value.strip():
        errors.append(f"`{field}` 必须是非空字符串")
        return None
    return value


def require_string_list(
    obj: dict[str, Any],
    key: str,
    field: str,
    errors: list[str],
    *,
    minimum: int,
) -> list[str]:
    value = obj.get(key)
    if value is None:
        errors.append(f"缺少必填字段 `{field}`")
        return []
    if not isinstance(value, list):
        errors.append(f"`{field}` 必须是字符串数组")
        return []
    items = [item for item in value if isinstance(item, str) and item.strip()]
    if len(items) < minimum:
        errors.append(f"`{field}` 至少 {minimum} 条（当前 {len(items)} 条）")
    return items


def check_cjk(text: str | None, field: str, errors: list[str]) -> None:
    if text and not CJK_RE.search(text):
        errors.append(f"`{field}` 必须含中文（专有名词可保留原文，但不能整条都是外文）")


def check_length(text: str | None, field: str, warnings: list[str], limit: int = 16) -> None:
    if text and len(text) > limit:
        warnings.append(f"`{field}` 有 {len(text)} 字，标题类建议 ≤{limit} 字")


def collect_panels(layout: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    panels: list[tuple[str, dict[str, Any]]] = []
    for key, value in layout.items():
        if key not in PANEL_CONTAINERS:
            continue
        if isinstance(value, dict):
            panels.append((key, value))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict):
                    panels.append((f"{key}[{index}]", item))
    return panels


def check_panel(field: str, panel: dict[str, Any], errors: list[str]) -> None:
    require_string(panel, "id", f"{field}.id", errors)
    title = require_string(panel, "title", f"{field}.title", errors)
    require_string(panel, "elements", f"{field}.elements", errors)
    check_cjk(title, f"{field}.title", errors)

    count = panel.get("count")
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        errors.append(f"`{field}.count` 必须是 ≥1 的整数")

    labels = panel.get("labels")
    if labels is None:
        return
    if not isinstance(labels, list):
        errors.append(f"`{field}.labels` 必须是字符串数组")
        return
    for index, label in enumerate(labels):
        label_field = f"{field}.labels[{index}]"
        if not isinstance(label, str) or not label.strip():
            errors.append(f"`{label_field}` 必须是非空字符串")
            continue
        check_cjk(label, label_field, errors)


def validate_infographic(
    payload: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    header = require_object(payload, "header", errors)
    if header is not None:
        title = require_string(header, "title", "header.title", errors)
        subtitle = require_string(header, "subtitle", "header.subtitle", errors)
        check_cjk(title, "header.title", errors)
        check_cjk(subtitle, "header.subtitle", errors)
        check_length(title, "header.title", warnings)

    centerpiece = require_object(payload, "centerpiece", errors)
    if centerpiece is not None:
        require_string(centerpiece, "description", "centerpiece.description", errors)
        require_string_list(
            centerpiece, "elements", "centerpiece.elements", errors, minimum=3
        )

    layout = require_object(payload, "layout", errors)
    if layout is None:
        return

    for key in layout:
        if key not in PANEL_CONTAINERS:
            warnings.append(f"`layout.{key}` 不是规范的版式分区名，模型可能忽略它")

    panels = collect_panels(layout)
    if len(panels) < 3:
        errors.append(f"信息图至少需要 3 个面板（当前 {len(panels)} 个）")
    if not 4 <= len(panels) <= 12:
        warnings.append(f"面板数量为 {len(panels)}，建议控制在 4–12 个")

    for field, panel in panels:
        check_panel(f"layout.{field}", panel, errors)

    if "bottom_row" not in layout:
        errors.append("信息图必须包含 `layout.bottom_row`，作为底部收束")
    elif not any(field == "bottom_row" or field.startswith("bottom_row[") for field, _ in panels):
        errors.append("`layout.bottom_row` 里至少要有一个面板对象")


def validate_poster(
    payload: dict[str, Any],
    errors: list[str],
    warnings: list[str],
) -> None:
    canvas = require_object(payload, "canvas", errors)
    if canvas is not None:
        require_string(canvas, "aspect", "canvas.aspect", errors)

    header = require_object(payload, "header", errors)
    if header is not None:
        headline = require_string(header, "headline", "header.headline", errors)
        check_cjk(headline, "header.headline", errors)
        check_length(headline, "header.headline", warnings)
        blocks = header.get("text_blocks")
        if not isinstance(blocks, list) or not blocks:
            errors.append("`header.text_blocks` 必须是至少含 2 条文字区块的数组")
        else:
            if len(blocks) < 2:
                errors.append(f"`header.text_blocks` 至少 2 条（当前 {len(blocks)} 条）")
            for index, block in enumerate(blocks):
                field = f"header.text_blocks[{index}]"
                if not isinstance(block, dict):
                    errors.append(f"`{field}` 必须是对象")
                    continue
                text = require_string(block, "text", f"{field}.text", errors)
                require_string(block, "position", f"{field}.position", errors)
                require_string(block, "level", f"{field}.level", errors)
                check_cjk(text, f"{field}.text", errors)

    centerpiece = require_object(payload, "centerpiece", errors)
    if centerpiece is not None:
        require_string(centerpiece, "subject", "centerpiece.subject", errors)
        require_string(centerpiece, "composition", "centerpiece.composition", errors)

    layout = require_object(payload, "layout", errors)
    if layout is not None:
        require_string_list(layout, "sections", "layout.sections", errors, minimum=3)
        require_string_list(
            layout, "decorations", "layout.decorations", errors, minimum=3
        )

    style = payload.get("style")
    if isinstance(style, str) and not any(word in style for word in CRAFT_KEYWORDS):
        warnings.append(
            "`style` 里看不出纸纹、颗粒、印、拼贴一类的工艺词，海报质感容易变平"
        )


def validate(payload: Any) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(payload, dict):
        return ["提示词必须是一个 JSON 对象"], warnings

    for path, text in walk_strings(payload):
        if not text.strip():
            errors.append(f"`{path}` 是空字符串")
        lowered = text.lower()
        for token in FORBIDDEN_TOKENS:
            if token in lowered:
                errors.append(f"`{path}` 含禁止的占位词 `{token}`")
                break

    genre = payload.get("genre")
    if genre not in AVOID_MINIMUM:
        errors.append("`genre` 必须是 `infographic` 或 `poster`")
        return errors, warnings

    require_string(payload, "type", "type", errors)
    require_string(payload, "theme", "theme", errors)
    style = payload.get("style")
    if not isinstance(style, str) or not style.strip():
        errors.append("`style` 必须是非空字符串")

    require_string_list(
        payload, "avoid", "avoid", errors, minimum=AVOID_MINIMUM[genre]
    )

    if genre == "infographic":
        validate_infographic(payload, errors, warnings)
    else:
        validate_poster(payload, errors, warnings)

    return errors, warnings


def flatten(payload: dict[str, Any]) -> str:
    genre = payload.get("genre")
    lines: list[str] = []
    lines.append(f"【类型】{payload.get('type', '')}")
    lines.append(f"【主题】{payload.get('theme', '')}")

    canvas = payload.get("canvas")
    if isinstance(canvas, dict):
        aspect = canvas.get("aspect", "")
        orientation = canvas.get("orientation", "")
        lines.append(f"【画幅】{aspect}{('（' + orientation + '）') if orientation else ''}")

    centerpiece = payload.get("centerpiece")
    if isinstance(centerpiece, dict):
        if genre == "infographic":
            lines.append(f"【主视觉】{centerpiece.get('description', '')}")
            elements = centerpiece.get("elements")
            if isinstance(elements, list) and elements:
                lines.append(f"【可见部件】{'、'.join(str(item) for item in elements)}")
        else:
            lines.append(f"【主视觉】{centerpiece.get('subject', '')}")
            lines.append(f"【构图】{centerpiece.get('composition', '')}")

    if genre == "infographic":
        header = payload.get("header")
        if isinstance(header, dict):
            lines.append(
                f"【标题】{header.get('title', '')} —— {header.get('subtitle', '')}"
            )
        layout = payload.get("layout")
        if isinstance(layout, dict):
            lines.append("【版式】")
            for key, value in layout.items():
                if key not in PANEL_CONTAINERS:
                    continue
                label = CONTAINER_LABELS[key]
                panels = value if isinstance(value, list) else [value]
                for panel in panels:
                    if not isinstance(panel, dict):
                        continue
                    lines.append(
                        f"- {label}（{panel.get('id', '')}）{panel.get('title', '')}："
                        f"{panel.get('elements', '')}，共 {panel.get('count', '')} 项"
                    )
                    labels = panel.get("labels")
                    if isinstance(labels, list) and labels:
                        lines.append(f"  图例：{' / '.join(str(item) for item in labels)}")
    else:
        header = payload.get("header")
        if isinstance(header, dict):
            lines.append(f"【主标题】{header.get('headline', '')}")
            if header.get("subheadline"):
                lines.append(f"【副标题】{header.get('subheadline')}")
            blocks = header.get("text_blocks")
            if isinstance(blocks, list):
                lines.append("【文字层】")
                for block in blocks:
                    if not isinstance(block, dict):
                        continue
                    lines.append(
                        f"- {block.get('position', '')}（{block.get('level', '')}）："
                        f"“{block.get('text', '')}”"
                    )
        layout = payload.get("layout")
        if isinstance(layout, dict):
            sections = layout.get("sections")
            if isinstance(sections, list) and sections:
                lines.append(f"【版面分区】{' → '.join(str(item) for item in sections)}")
            decorations = layout.get("decorations")
            if isinstance(decorations, list) and decorations:
                lines.append(f"【装饰与工艺】{'、'.join(str(item) for item in decorations)}")

    style = payload.get("style")
    if isinstance(style, str) and style.strip():
        lines.append(f"【风格】{style.strip()}")

    avoid = payload.get("avoid")
    if isinstance(avoid, list) and avoid:
        lines.append(f"【不要出现】{'；'.join(str(item) for item in avoid)}")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        payload = load_payload(args)
    except ValueError as error:
        print(f"用法错误: {error}", file=sys.stderr)
        return 2

    errors, warnings = validate(payload)
    ok = not errors

    if args.json_output:
        print(
            json.dumps(
                {"ok": ok, "errors": errors, "warnings": warnings},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0 if ok else 1

    for warning in warnings:
        print(f"警告: {warning}")
    if errors:
        print("校验未通过：")
        for error in errors:
            print(f"- {error}")
        return 1

    print("校验通过。")
    if args.flatten:
        print()
        print(flatten(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
