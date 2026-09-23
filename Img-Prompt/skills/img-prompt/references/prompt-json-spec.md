# JSON 提示词规范

本文件是 `scripts/validate_prompt_json.py` 校验规则的唯一依据：文档写什么，脚本就查什么。写 JSON 前后都对照一遍。

## 总原则

- 顶层键沿用优秀样本的命名：`type` / `theme` / `style` / `header` / `centerpiece` / `layout`，再按类型分支扩展 `genre` / `canvas` / `avoid`。
- 所有值都要是**可直接执行的画面指令**，不是评论。"配色高级"要写成"主色深靛蓝，点缀暖金，背景近黑"。
- 图中文字一律中文；专有名词可保留原文，但同一条文字里必须含中文（`相干衍射成像 CDI` 合格，`CDI` 单独出现不合格）。
- 不留占位符：不写 `[TITLE]`、`{argument name=...}`、`TODO`、`xxx`。

## 顶层字段

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `genre` | string | 是 | `infographic`（信息图）或 `poster`（海报） |
| `type` | string | 是 | 类型短语，例：`复杂系统图谱式信息图`、`编辑式旅行海报` |
| `theme` | string | 是 | 主题一句话，写清对象与视角 |
| `style` | string | 是 | 风格段落：风格锚点 + 背景 + 配色 + 材质/工艺 + 排版气质 |
| `header` | object | 是 | 文字层，字段随类型分支（见下） |
| `centerpiece` | object | 是 | 主视觉，字段随类型分支（见下） |
| `layout` | object | 是 | 版式分区，字段随类型分支（见下） |
| `canvas` | object | 海报必填 | `{"aspect": "4:5", "orientation": "竖版"}`；信息图可选（如 `1:1`） |
| `avoid` | string[] | 是 | 负面清单：信息图 ≥5 条，海报 ≥3 条 |

## 样式为 `infographic` 时的分支字段

### header

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `title` | 是 | 中文主标题，建议 ≤16 字 |
| `subtitle` | 是 | 一句话副标题或导语 |
| `overview_label` | 否 | 角标小字标题，如 `系统总览` |

### centerpiece

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `description` | 是 | 超写实三维剖切 / 爆炸视图描述：材质、结构、光线、束线走向 |
| `elements` | 是 | 可见部件清单，≥3 条，每条是部件名 |

### layout

必须是对象，键取自下列分区名，值是**面板对象**或**面板对象数组**：

`top_left`、`top_right`、`side_panels`、`left_column`、`center_overlay`、`right_column`、`bottom_row`、`footer`

- 面板总数 ≥3，建议 5–12。
- `bottom_row` 必填，承担底部收束（流程条 / 因果链 / 核心总结）。
- 每个面板对象必填四项：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `id` | 是 | 编号或短标识，如 `01`、`参数表` |
| `title` | 是 | 中文面板标题 |
| `elements` | 是 | 元素说明，必须含数量，如 `1 张剖面示意 + 4 条图例` |
| `count` | 是 | 整数 ≥1，与 `elements` 里的数量一致 |
| `labels` | 否 | 中文图例标签数组 |
| `steps` | 否 | 流程类面板的步数 |

## 样式为 `poster` 时的分支字段

### header（承载全部文字层）

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `headline` | 是 | 主标题，中文，建议 ≤16 字 |
| `subheadline` | 否 | 副标题 |
| `signature` | 否 | 落款 / 展览名 / 日期 |
| `text_blocks` | 是 | ≥2 条文字区块，每条含 `text`、`position`、`level` |

`text_blocks` 里的 `position` 用版面方位描述（`左上`、`底部信息条`、`右下竖排`），`level` 用层级描述（`主标题`、`副标题`、`小字信息`、`装饰性小字`）。

### centerpiece

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `subject` | 是 | 主视觉主体：谁 / 什么，在哪，周围有什么 |
| `composition` | 是 | 构图：主体位置、地平线高度、视线方向、留白安排 |

### layout

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `sections` | 是 | ≥3 条版面分区，按从上到下顺序写 |
| `decorations` | 是 | ≥3 条装饰与工艺元素，如 `半透明几何色块`、`细颗粒纸纹` |

## 校验脚本

```powershell
# 校验文件
python "<技能目录>\scripts\validate_prompt_json.py" prompt.json

# 校验标准输入（不落盘，日常自检用这个）
$json | python "<技能目录>\scripts\validate_prompt_json.py" --stdin

# 校验通过后，额外把 JSON 展平成中文段落提示词
python "<技能目录>\scripts\validate_prompt_json.py" prompt.json --flatten
```

退出码：`0` 通过（可能有警告）、`1` 存在错误、`2` 用法或读取失败。警告不阻塞交付，但建议按提示修掉。

脚本会检查：必填字段与分支字段是否齐全、面板是否写了元素与数量、`avoid` 条数、画幅比例、文字是否含中文、是否残留占位符或空字符串，并对标题过长、面板数量异常、海报缺少工艺词给出警告。

## 最小骨架

信息图：

```json
{
  "genre": "infographic",
  "type": "复杂系统图谱式信息图",
  "theme": "……",
  "canvas": { "aspect": "1:1", "orientation": "方形" },
  "style": "……背景……主色……点缀……材质……排版……",
  "header": { "title": "……", "subtitle": "……" },
  "centerpiece": { "description": "超写实三维剖切渲染……", "elements": ["……", "……", "……"] },
  "layout": {
    "top_left": { "id": "00", "title": "……", "elements": "1 张总览小图 + 4 条图例", "count": 4 },
    "left_column": [ { "id": "01", "title": "……", "elements": "1 张剖面示意 + 4 条图例", "count": 4 } ],
    "right_column": [ { "id": "02", "title": "……", "elements": "1 张剖面示意 + 4 条图例", "count": 4 } ],
    "bottom_row": { "id": "03", "title": "核心结论……", "elements": "1 条五步流程条 + 1 张总结卡", "count": 5 }
  },
  "avoid": ["……", "……", "……", "……", "……"]
}
```

海报把 `header`、`centerpiece`、`layout` 换成海报分支字段，并补上 `canvas` 即可。
