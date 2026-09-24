<div align="center">

# 🖼️ Img Prompt

**一句话主题 → 一份可以直接粘贴进生图工具的中文 JSON 提示词**

*把「介绍一下相干衍射成像」「做一张城市黄昏的海报」这类需求，变成成品级的结构化提示词。*

[![Version](https://img.shields.io/badge/version-0.4.0-2f6feb?style=flat-square)](./.codex-plugin/plugin.json)
[![License](https://img.shields.io/badge/license-MIT-3fb950?style=flat-square)](../LICENSE)
[![Codex CLI](https://img.shields.io/badge/Codex_CLI-plugin-0b7285?style=flat-square)](https://github.com/Lex669/AutoSim)
[![Form](https://img.shields.io/badge/形态-Markdown_技能包-d97757?style=flat-square)](./skills/img-prompt/SKILL.md)
[![No API](https://img.shields.io/badge/生图_API-无需调用-e8590c?style=flat-square)](#-它是怎么工作的)
[![Python](https://img.shields.io/badge/Python-仅标准库-3776ab?style=flat-square&logo=python&logoColor=white)](./skills/img-prompt/scripts/validate_prompt_json.py)

</div>

Img Prompt 是 [AutoSim](https://github.com/Lex669/AutoSim) 插件市场中的一个技能插件。它不画图、不联网、不需要任何 API Key：**它只写提示词**——把一句主题推导成信息图或海报的结构化描述，逐字写死标题、模块、部件数量、参数与画幅，最后落成项目里的一个 JSON 文件。

> *In English: Img Prompt turns a one-line theme into an all-Chinese JSON prompt for image generators — infographics (atlas pages, cutaways, process chains, dashboards…) and posters. It decides the genre, fixes the canvas aspect, derives the skeleton from the subject, then writes the prompt as a validated project file. It never calls an image API.*

> [!TIP]
> 信息图最常见的翻车点不是「不够好看」，而是**没先定画幅**：79 个优秀案例里只有 23% 写了画幅，而画幅一错，模块必然挤成一团或空成一片。所以画幅、子类型、模块数量在这个插件里都是必填项。

---

## ✨ 它能做什么

| 能力 | 说明 |
| --- | --- |
| 🧭 **自动判类型** | 按用户说法在「信息图」与「海报」之间路由；只有主题时默认信息图，并提示可再出一版海报 |
| 🗂️ **落到子类型** | 信息图细分科普图鉴 / 结构拆解 / 系统手册页 / 因果链 / 流程步骤 / 数据宫格 / 地图导览 / 分析报告 / 人物档案 |
| 📐 **先定画幅** | 按用途写死 `9:16` / `3:4` / `A4` / `1:1` / `16:9`，海报默认 `4:5`——版式不再靠模型猜 |
| 🧱 **推导骨架** | 主题越具体主线越具体：CDI 会写成「相干光源 → 针孔整形 → 样品 → 远场采集 → 相位恢复 → 重建评估」 |
| 🔢 **数量与文字写死** | 每个面板写明「1 张剖面示意 + 4 条图例」，标题与图例标签逐字给出，参数连单位写死 |
| 🚫 **负面清单防退化** | `avoid` 必须覆盖「海报广告感」与「乱码 / 错字」两类问题，信息图 ≥5 条、海报 ≥3 条 |
| 🎨 **三套视觉系统** | 纸感文博系 / 现代白底系 / 暗色科技系，选一套并落到具体材质词（手工和纸、拉丝钛金属、冷凝水……） |
| ✅ **校验后落盘** | 提示词经校验脚本检查通过才写入 `prompts/`，项目里不会留下带占位符的半成品 |
| 🔌 **离线可复现** | 校验脚本只用 Python 标准库，不装依赖、不连网络 |

---

## 🧭 它是怎么工作的

```text
一句主题
   │
   ├─▶ ① 判类型 ────── 信息图 / 海报
   │
   ├─▶ ② 定子类型 + 画幅 ── 9 类子类型 × 5 种画幅，写进 subtype / canvas.aspect
   │
   ├─▶ ③ 推导骨架 ──── 列出主线环节（信息图）或文字层（海报）
   │
   ├─▶ ④ 填 JSON ───── 按 prompt-json-spec.md 的字段与必填规则展开
   │
   ├─▶ ⑤ 校验 ──────── validate_prompt_json.py 通过才继续
   │
   └─▶ ⑥ 交付 ──────── prompts/{genre}-{主题}.json（可直接粘贴进任意生图工具）
```

以「相干衍射成像 CDI」为例，主线会同时驱动三处，三者一一对应：

| 位置 | 内容 |
| --- | --- |
| `centerpiece` 主视觉 | 三维剖切的实验腔，光路自左向右贯穿，发光青色束线连接各环节 |
| 编号面板 | `01` 相干光源 · `02` 光束整形 · `03` 样品与过采样 · `04` 远场采集 · `05` 相位恢复 · `06` 重建评估 |
| `layout.bottom_row` | 相干照明 → 过采样衍射 → 强度采集 → 相位恢复 → 重建成像 |

---

## 🗂️ 覆盖的类型

**类型路由**（判错了后面全错，所以这一步写死在技能里）：

| 用户信号 | 类型 | `genre` |
| --- | --- | --- |
| 海报、poster、宣传、展览、旅行、电影感、拼贴、字体海报 | 海报 | `poster` |
| 信息图、图谱、拆解、剖面、图鉴、原理、流程、系统、结构、「介绍一下××并配图」 | 信息图 | `infographic` |
| 两类信号都有，或只给了主题 | 默认信息图 | `infographic` |

**信息图子类型**与它的主线推导：

| 子类型 | 识别信号 | 主线推导 |
| --- | --- | --- |
| 科普图鉴 / 百科卡 | 「介绍一下××」「图鉴」「科普」 | 主视觉 → 外观特征 → 结构组成 → 材质工艺 → 使用或生长条件 → 速记评分卡 |
| 结构拆解 / 剖面 / 爆炸图 | 器物、建筑、产品、生物、装置 | 拆成几层或几个部件（数量写死）→ 每个部件标注名称 + 一句功能 |
| 系统 / 工程手册页 | 装置、设备、工艺、链路、生产、运维 | 抽 4–8 个有序环节，构成输入到输出的链路 |
| 因果链 | 「××是怎么产生的」「一张××的由来」 | 一条两端明确的链，编号统一两位数，每步一句说明 |
| 流程 / 步骤 / 食谱 | 做法、步骤、教程 | 每步「图形 + 说明 + 秘技」+ 一条动线（Z 字形、蛇形、顺时针） |
| 数据 / 宫格卡片 | 「×条」「×个」「清单」「指南」 | N 列 × M 行宫格，每格标题 + 正文 + 配图元素，方便切图 |
| 地图 / 导览绘本 | 地点、路线、城市、儿童科普 | 大场景 + 导览路线 + 出现 2–3 次的导览 IP + 3–6 个知识站点 |
| 分析报告 / 画像 | 人像、美妆、穿搭、健康、测评 | 输入区 → 分析结论 → 对比矩阵（核心）→ 底部建议 |
| 人物 / 文化档案 | 神话、历史人物、文化专题 | 身份 → 源流 → 特征 → 器物 → 典故 → 象征 → 影响 |

**海报子类型**：字体肖像 · 编辑艺术 · 旅行 · 拼贴 · 极简几何。

**画幅对照**（信息图按用途选，海报默认 `4:5`）：

| 用途 | `aspect` | 版式特征 |
| --- | --- | --- |
| 长图科普卡（小红书 / 公众号） | `9:16` | 上标题、中主视觉、下模块，阅读动线自上而下 |
| 图鉴卡 / 打印页 | `A4` 或 `3:4` | 中轴对称，左右分栏，底部总结横幅 |
| 工程 / 系统信息页 | `1:1` | 中央主视觉 + 四周信息卡 |
| 流程 / 时间轴 / 对比 | `16:9` | 横向串联，箭头贯穿 |

---

## 📐 输出长什么样

提示词是「画面指令清单」而不是形容词堆砌。下面是节选（为便于阅读省略了 `style`、`avoid` 与其余面板，完整版见 [`cdi-infographic.json`](./skills/img-prompt/references/examples/cdi-infographic.json)）：

```json
{
  "genre": "infographic",
  "subtype": "系统手册页",
  "type": "复杂系统图谱式信息图",
  "theme": "相干衍射成像（CDI）：从相干光源到相位重建的完整链路",
  "canvas": { "aspect": "1:1", "orientation": "方形" },
  "header": {
    "title": "相干衍射成像 CDI 系统图谱",
    "subtitle": "从相干光源到相位重建，一张图看清无透镜成像的完整链路"
  },
  "layout": {
    "top_right": {
      "id": "参数",
      "title": "关键参数",
      "elements": "1 张 6 行参数表",
      "count": 6,
      "labels": ["波长", "样品到探测器距离", "像素尺寸", "采样率", "迭代次数", "重建分辨率"]
    }
  }
}
```

需要一段连贯的文字版时，用 `--flatten` 把同一份 JSON 展平成中文段落，直接喂给不支持 JSON 的生图工具。

---

## 🚀 安装

```bash
# 1. 注册 AutoSim 插件市场
codex plugin marketplace add Lex669/AutoSim

# 2. 安装本插件（autosim 为清单注册名）
codex plugin add img-prompt@autosim
```

> [!NOTE]
> 本插件在 AutoSim 的 Codex 市场清单里以**本地源**（`./Img-Prompt`）注册，所以只对克隆了 AutoSim 仓库的本地用户可用——远程市场消费者无法安装它。

插件本身只是一组 Markdown 规范加一个 Python 脚本，因此也可以直接把 `skills/img-prompt/` 放进你惯用的技能目录（如 `~/.codex/skills/`）。目前它尚未登记到仓库的 Claude Code 市场清单（`.claude-plugin/marketplace.json`）中。

---

## 💬 这样用它

装好之后直接用自然语言描述需求，技能会自己路由：

| 你说 | 得到 |
| --- | --- |
| 为相干衍射成像 CDI 写一份信息图 JSON 提示词 | 系统手册页式信息图，方形画幅，6 个编号面板 |
| 把「透射电镜」拆解成图鉴式信息图提示词 | 纸感文博系科普图鉴，含材质工艺区与速记评分卡 |
| 做一张城市黄昏主题的海报 JSON 提示词 | 编辑式竖版海报，文字层逐条写死，含印刷工艺词 |
| 介绍一下青花瓷的工艺，配一张图 | 默认走信息图，交付时附一句「想要海报版可以再出一份」 |

交付物只有一个东西：项目 `prompts/` 目录下的 `{genre}-{主题}.json`（UTF-8、2 空格缩进、中文不转义，同名自动加 `-2`、`-3`）。对话里只汇报类型、骨架主线与保存路径，不会把整份 JSON 贴屏；需要看内容时说一句「贴出来看看」即可。

---

## 🧪 校验与落盘

`skills/img-prompt/scripts/validate_prompt_json.py` 是唯一的检查入口，规则与 [`prompt-json-spec.md`](./skills/img-prompt/references/prompt-json-spec.md) 一一对应：

```powershell
# 校验单个文件
python skills\img-prompt\scripts\validate_prompt_json.py prompt.json

# 校验标准输入（日常自检，不落盘）
$json | python skills\img-prompt\scripts\validate_prompt_json.py --stdin

# 校验通过后写入项目 prompts/ 目录
$json | python skills\img-prompt\scripts\validate_prompt_json.py --stdin --out prompts

# 展平成中文段落提示词 / 输出机器可读报告
python skills\img-prompt\scripts\validate_prompt_json.py prompt.json --flatten
python skills\img-prompt\scripts\validate_prompt_json.py prompt.json --json
```

| 退出码 | 含义 |
| --- | --- |
| `0` | 通过（可能含不影响交付的警告） |
| `1` | 存在校验错误，未写文件 |
| `2` | 用法、读取或写入失败 |

脚本会检查：必填字段与分支字段是否齐全（含 `subtype`、`canvas.aspect`）、面板是否写了元素与数量、`avoid` 条数、文字是否含中文、是否残留 `TODO` / `[TITLE]` / `xxx` 之类占位符或空字符串。

---

## 📊 规律从哪来

参考文件里的每一条硬约束都来自实测统计，不是感觉：

| 指标 | 实测结果 |
| --- | --- |
| 统计样本 | 541 例中筛出 **79 个信息图 / 科普图案例**，逐条读过原文 |
| 提示词长度 | 中位数 **1696 字符**（全库中位 1044），45 例超过 1500 字符 |
| 写明画幅的比例 | 仅 **23%** —— 而这正是常见的翻车点 |
| 版式信息 | 24.1% 写明模块数量，60.8% 给出模块方位 |
| 底部收束 | 54.4% 含数据 / 评分 / 对比元素 |
| 海报样本 | `sample_prompt/poster/` 的四份样本（字体肖像、编辑艺术、水彩旅行、拼贴电影感） |

`sample_prompt/` 是提炼规律的原始素材，**只供人阅读**，生成提示词时不会被引用。

---

## 📁 目录结构

```text
Img-Prompt/
├─ .codex-plugin/plugin.json          # 插件清单：版本、描述、默认提示
├─ skills/img-prompt/
│  ├─ SKILL.md                        # 技能入口：工作流 + 路由表 + 硬约束
│  ├─ references/
│  │  ├─ prompt-json-spec.md          # JSON 字段规范（校验规则的唯一依据）
│  │  ├─ infographic-atlas.md         # 信息图子类型 / 画幅 / 骨架推导法
│  │  ├─ poster.md                    # 海报子类型 / 文字层 / 工艺词库
│  │  └─ examples/                    # 三份完整示例，均通过校验
│  │     ├─ cdi-infographic.json      # 深色科技系 · 系统手册页
│  │     ├─ heritage-infographic.json # 纸感文博系 · 科普图鉴
│  │     └─ poster-example.json       # 编辑式旅行海报
│  └─ scripts/validate_prompt_json.py # 校验 / 落盘 / 展平
├─ sample_prompt/                     # 规律来源素材（只读）
├─ AGENTS.md                          # 贡献指南
└─ README.md
```

---

## ❓ 常见问题

**它会帮我出图吗？**
不会。插件只产出提示词 JSON，出图交给你常用的工具（Nano Banana / Gemini、Seedream、Qwen-Image、即梦、Midjourney 等）。

**为什么保存成文件，而不是直接贴出来？**
提示词往往上百行，落盘后可以版本化、复用、批量迭代；改稿时直接改原文件，不会散落一堆游离副本。项目已有约定目录（如 `assets/prompts/`）时以项目约定为准。

**能出多套方案吗？**
默认一份。要多个方案时说一声，会共用同一骨架、替换风格与配色，再存 2–3 份。

**图文内容会编造吗？**
不会刻意编。不确定的细节写「相关记载较少」，而不是编一个看起来很像的数字。

---

## 🗓️ 更新日志

### v0.4.0 · 2026-09-24 — 落盘契约与 79 例信息图规律

- 交付方式改变：提示词不再留在对话里，校验通过后写入项目 `prompts/{genre}-{主题}.json`（同名自动 `-2`、`-3`），对话只汇报路径与要点。
- 采纳 79 例信息图统计规律：`subtype` 与 `canvas.aspect` 变为必填，信息图 `avoid` ≥5 条、海报 ≥3 条，`layout.bottom_row` 必填。
- 新增 `references/infographic-atlas.md` 的子类型表与「用途 → 画幅」对照表；新增示例 `heritage-infographic.json`（青花瓷工艺图鉴，纸感文博系）。
- 校验器升级：新增 `--out <目录>`（校验通过才落盘）、`--json`（机器可读报告），并增加占位符、中文文字与数量一致性检查。
- 新增 `AGENTS.md` 贡献指南，以及 `sample_prompt/信息图与科普图提示词规律.md` 统计文档与本 README。

### v0.2.0 · 2026-09-23 — Img-Gen 重构为 Img-Prompt

- 不再调用 DashScope 生图 API：删除 `generate_image.py`、密钥配置与相关依赖，交付物改为结构化 JSON 提示词。
- 从优秀样本提炼出 `references/prompt-json-spec.md`、`infographic-atlas.md`、`poster.md` 三份规范。
- 新增 `scripts/validate_prompt_json.py` 与两份示例 `cdi-infographic.json`、`poster-example.json`。
- 插件目录与市场条目更名为 `Img-Prompt` / `img-prompt`（本地源 `./Img-Prompt`）；删除旧的学术配图与 PPT 插图模板。

### 2026-09-07 — 前身 Img-Gen 上线

- 作为 AutoSim 插件市场插件引入，用 DashScope `qwen-image-3.0-pro` 生成学术配图与答辩 PPT 插图。
- 注册到 `.agents/plugins/marketplace.json`，随 Codex CLI 支持一同上线（`codex plugin add` 可安装）。

---

<div align="center">

**Img Prompt** · MIT License · [AutoSim 插件市场](https://github.com/Lex669/AutoSim)

*输入一个主题，输出一张图的完整说明书。*

</div>
