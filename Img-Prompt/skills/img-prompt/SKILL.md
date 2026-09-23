---
name: img-prompt
description: 为生图工具撰写结构化 JSON 提示词，覆盖知识图谱式信息图（系统拆解、原理流程、剖面图鉴）与海报两类。按主题自动判定类型并推导骨架，输出全中文 JSON，不调用任何生图 API。当用户要求"生成图片提示词""写一张图的 prompt""做一张信息图 / 图谱 / 拆解图 / 剖面图 / 图鉴""介绍一下某技术并配图""做一张海报 / poster"时使用。
---

# Img Prompt：生图 JSON 提示词撰写

## 定位

输入一句主题，输出一份结构化 JSON 提示词。用户把这份 JSON 直接粘贴到任意生图工具（Nano Banana / Gemini、Seedream、Qwen-Image、即梦、Midjourney 等）即可出图。

本技能不调用任何生图 API：没有密钥、不下载、不往磁盘写文件。最终交付物就是对话里的一个 JSON 代码块。

如果用户直接说"给我生成一张图"，仍然只产出 JSON，并补一句：这份 JSON 可直接粘贴到常用的生图工具。

## 工作流

1. **判类型**：按下面的路由表确定 `genre`。
2. **推导骨架**：读 `references/infographic-atlas.md` 或 `references/poster.md`，按其中的推导法列出主线环节（信息图）或文字层（海报）。主题越具体，主线就要越具体——写"相干光源、针孔、样品、探测器、相位恢复"，不要写"若干光学元件"。
3. **填 JSON**：严格按 `references/prompt-json-spec.md` 的字段与必填规则写。需要参照密度与语气时，读 `references/examples/` 里的完整示例。
4. **自检**：把 JSON 通过标准输入交给校验脚本，按提示修掉问题再交付：

   ```powershell
   $json | python "<技能目录>\scripts\validate_prompt_json.py" --stdin
   ```

5. **输出**：对话里给 JSON 代码块 + 一句话交付说明（类型、骨架主线、可直接粘贴使用）。默认只给一份；用户要多个方案时再给 2–3 份，共用同一骨架、替换风格与配色。

## 类型路由

| 用户信号 | 类型 | `genre` |
| --- | --- | --- |
| 海报、poster、宣传、展览、旅行、电影感、拼贴、字体海报、收藏海报 | 海报 | `poster` |
| 信息图、图谱、拆解、剖面、图鉴、原理、流程、系统、结构、"介绍一下××并配图" | 信息图 | `infographic` |
| 两类信号都有，或只给了主题 | 默认信息图；交付时补一句"想要海报版我可以再出一份" | `infographic` |

## 不可退让的硬约束

- **全部中文**：图中出现的文字（标题、副标题、面板标题、图例标签、海报文案）一律中文。专有名词可保留原文（CDI、FDTD、某型号），但同一条文字里必须含中文。
- **数量写死**：每个面板都要写清元素类型与数量，例如"1 张剖面示意 + 4 条图例"。
- **底部收束**：信息图必须有 `layout.bottom_row`，作为流程条、因果链或核心总结。
- **负面清单**：信息图 `avoid` ≥ 5 条，海报 `avoid` ≥ 3 条。
- **写实主视觉**：信息图 `centerpiece` 是 1 个超写实三维剖切或爆炸视图，不是拼贴、不是卡通。
- **标注画幅**：海报必须有 `canvas.aspect`（默认 `4:5` 竖版）。
- **不留占位符**：不要出现 `[TITLE]`、`{argument ...}`、`TODO`、`xxx` 之类内容，该填的直接填。

## 参考文件

| 文件 | 用途 |
| --- | --- |
| `references/prompt-json-spec.md` | JSON 字段规范与校验规则，写 JSON 前必读 |
| `references/infographic-atlas.md` | 信息图骨架推导法与写作规律 |
| `references/poster.md` | 海报子类型、文字层与工艺词规律 |
| `references/examples/cdi-infographic.json` | 相干衍射成像 CDI 系统信息图完整示例 |
| `references/examples/poster-example.json` | 旅行海报完整示例 |
| `scripts/validate_prompt_json.py` | 校验 JSON，并可用 `--flatten` 展平成段落提示词 |

插件目录下的 `sample_prompt/` 是提炼这些规律的原始素材，仅供人阅读，不必在生成提示词时引用。
