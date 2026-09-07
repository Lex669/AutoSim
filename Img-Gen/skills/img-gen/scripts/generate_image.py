#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""img-gen: DashScope Qwen-Image 文生图脚本。

调用阿里云 DashScope 的 qwen-image-3.0-pro 模型（MultiModalConversation 接口）
生成图片，自动下载到本地，并在 stdout 输出单行 JSON：

    {"files": ["<绝对路径>", ...], "request_id": "...", "size": "...", "model": "..."}

用法示例：
    python generate_image.py --prompt "一段详细的中文画面描述" --size 2048*1152 --name cover
    python generate_image.py --prompt-file prompt.txt --size 2048*2048

环境变量：
    DASHSCOPE_API_KEY  DashScope API 密钥（必需）
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

DEFAULT_MODEL = "qwen-image-3.0-pro"
DEFAULT_SIZE = "2048*2048"
DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
DEFAULT_NEGATIVE_PROMPT = (
    "Low resolution, low quality, distorted limbs, malformed fingers, "
    "oversaturated colors, wax-figure appearance, lack of facial detail, "
    "excessive smoothness, AI-looking artifacts, chaotic composition, "
    "blurry or warped text."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate images with DashScope Qwen-Image (qwen-image-3.0-pro)."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--prompt", help="提示词文本")
    source.add_argument("--prompt-file", help="UTF-8 提示词文件路径")
    parser.add_argument(
        "--size",
        default=DEFAULT_SIZE,
        help="输出尺寸，格式 宽*高（默认 %(default)s；预设：2048*1152 / 2048*1536 / 1536*2048 / 1152*2048）",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="DashScope 模型名（默认 %(default)s）")
    parser.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE_PROMPT, help="负向提示词")
    parser.add_argument(
        "--no-prompt-extend",
        action="store_true",
        help="关闭模型端提示词自动扩写（默认开启）",
    )
    parser.add_argument("--watermark", action="store_true", help="添加水印（默认无水印）")
    parser.add_argument("--out-dir", default="./generated_images", help="图片保存目录（默认 %(default)s）")
    parser.add_argument("--name", default="", help="文件名后缀，便于区分版本")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="DashScope base HTTP API URL")
    return parser.parse_args()


def resolve_prompt(args: argparse.Namespace) -> str:
    if args.prompt is not None:
        return args.prompt.strip()
    prompt_path = Path(args.prompt_file)
    if not prompt_path.is_file():
        print(f"错误: 提示词文件不存在: {prompt_path}", file=sys.stderr)
        raise SystemExit(2)
    return prompt_path.read_text(encoding="utf-8").strip()


def extract_image_urls(value):
    """递归提取响应 JSON 中所有 image URL。"""
    urls = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "image" and isinstance(item, str) and item.startswith("http"):
                urls.append(item)
            else:
                urls.extend(extract_image_urls(item))
    elif isinstance(value, list):
        for item in value:
            urls.extend(extract_image_urls(item))
    return urls


def slugify(name: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff\-]+", "-", name, flags=re.UNICODE).strip("-")
    return slug[:40]


def download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "img-gen-plugin/0.1"})
    with urllib.request.urlopen(request, timeout=180) as response:
        dest.write_bytes(response.read())


def main() -> int:
    args = parse_args()
    prompt = resolve_prompt(args)
    if not prompt:
        print("错误: 提示词为空。", file=sys.stderr)
        return 2

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print(
            "错误: 未设置 DASHSCOPE_API_KEY。\n"
            "请先配置 DashScope API 密钥：\n"
            '  临时（当前 PowerShell 会话）: $env:DASHSCOPE_API_KEY="sk-..."\n'
            '  永久（新开终端生效）        : setx DASHSCOPE_API_KEY "sk-..."\n'
            "密钥获取: https://dashscope.console.aliyun.com/",
            file=sys.stderr,
        )
        return 2

    try:
        import dashscope
        from dashscope import MultiModalConversation
    except ImportError:
        print(
            "错误: 未安装 dashscope SDK。请运行: python -m pip install --upgrade dashscope",
            file=sys.stderr,
        )
        return 2

    dashscope.base_http_api_url = args.base_url

    response = MultiModalConversation.call(
        api_key=api_key,
        model=args.model,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        result_format="message",
        stream=False,
        watermark=args.watermark,
        prompt_extend=not args.no_prompt_extend,
        negative_prompt=args.negative_prompt,
        size=args.size,
    )

    status = getattr(response, "status_code", None)
    if status != 200:
        print(f"HTTP 状态码: {status}", file=sys.stderr)
        print(f"错误码: {getattr(response, 'code', '')}", file=sys.stderr)
        print(f"错误信息: {getattr(response, 'message', '')}", file=sys.stderr)
        return 1

    try:
        payload = json.loads(json.dumps(response, ensure_ascii=False))
    except (TypeError, ValueError):
        payload = response
    urls = extract_image_urls(payload)
    if not urls:
        print("错误: 响应中未找到图片 URL。完整响应:", file=sys.stderr)
        try:
            print(json.dumps(response, ensure_ascii=False, default=str), file=sys.stderr)
        except Exception:
            print(str(response), file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = f"-{slugify(args.name)}" if args.name.strip() else ""
    files = []
    for index, url in enumerate(urls):
        index_suffix = f"-{index + 1}" if len(urls) > 1 else ""
        dest = out_dir / f"{timestamp}{suffix}{index_suffix}.png"
        download(url, dest)
        files.append(str(dest.resolve()))

    result = {
        "files": files,
        "request_id": getattr(response, "request_id", "") or "",
        "size": args.size,
        "model": args.model,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
