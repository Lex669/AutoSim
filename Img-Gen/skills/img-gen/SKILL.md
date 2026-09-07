---
name: img-gen
description: 使用阿里云 DashScope qwen-image-3.0-pro 文生图。适用于学术配图（论文插图、图形摘要 graphical abstract、TOC 图、方法/装置示意图、机理概念图、期刊封面）与 PPT 汇报/答辩图片（封面、目录页、章节过渡页、内容配图、概念背景图、致谢页），以及一般文生图需求。当用户要求生成图片、画一张图、做汇报/答辩配图、海报背景时使用。
---

# Img Gen：学术与 PPT 生图

通过本技能目录下的 `scripts/generate_image.py` 调用阿里云 DashScope `qwen-image-3.0-pro` 文生图模型（技能目录 = 本 SKILL.md 所在目录）。

## 环境检查（每个会话首次使用前）

1. 依赖：运行 `python -c "import dashscope"`；失败则先 `python -m pip install --upgrade dashscope`（需要网络）。
2. 密钥：脚本从环境变量 `DASHSCOPE_API_KEY` 读取密钥；缺失时脚本 exit 2 并给出指引，此时提示用户：
   - 临时（当前 PowerShell 会话）：先执行设置环境变量的命令再运行脚本
   - 永久：`setx DASHSCOPE_API_KEY "sk-..."`（仅对新开终端生效）
   - 密钥获取：https://dashscope.console.aliyun.com/

## 工作流

1. **澄清需求**：用途（学术配图 or PPT 图）、画幅比例、风格基调、主题色、图中需要的文字。能从上下文推断的不要反复追问。
2. **撰写提示词**：写成一段详细的中文描述（参考用户习惯的长描述风格）：先总述画面类型与整体氛围，再按空间顺序描述主体、布局、配色、光线、质感与风格。图中文字务必少而短（≤12 字）并用引号给出原文；不重要的文字干脆不要。
   - 学术场景模板：`references/academic-figures.md`
   - PPT 场景模板：`references/ppt-figures.md`
3. **选择尺寸**（`--size`，格式 `宽*高`）：
   - `2048*2048` 1:1 默认：图形摘要、方形示意图、方版封面
   - `2048*1152` 16:9：PPT 宽屏页面
   - `2048*1536` 4:3：传统 PPT
   - `1536*2048` 3:4：竖版海报/期刊封面
   - `1152*2048` 9:16：竖屏展示
   - API 若报尺寸相关错误，回退 `2048*2048` 并在交付时说明。
4. **生成**：长提示词先写入临时 txt 文件（UTF-8），再用 `--prompt-file` 传入以避免 shell 转义问题：

   ```powershell
   python "<技能目录>\scripts\generate_image.py" --prompt-file "<提示词文件>" --size 2048*1152 --name cover
   ```

5. **展示与迭代**：脚本成功时 stdout 输出单行 JSON：`{"files": [绝对路径...], "request_id": ...}`。取 `files` 中的绝对路径，用 `![图片描述](绝对路径)` 展示给用户；按用户反馈修改提示词后重新生成。每次调用生成 1 张图，需要多方案就多次调用（可微调提示词）。

## 脚本参数速查

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--prompt` / `--prompt-file` | 必填（二选一） | 提示词文本 / 提示词文件路径 |
| `--size` | `2048*2048` | 输出尺寸 `宽*高` |
| `--model` | `qwen-image-3.0-pro` | DashScope 模型名 |
| `--negative-prompt` | 内置英文负向词 | 不希望出现的内容 |
| `--no-prompt-extend` | 默认开启模型扩写 | 关闭提示词自动扩写（需要严格遵循提示词时使用） |
| `--watermark` | 默认无水印 | 添加水印 |
| `--out-dir` | `./generated_images` | 图片保存目录（相对当前工作目录） |
| `--name` | 无 | 文件名后缀，便于区分版本 |

## 注意事项

- 模型渲染文字不可靠：标题、姓名、编号等关键文字建议后期叠加；必须入图的引号文字保持简短。
- 学术图避免直接复刻受版权保护的期刊 Logo、出版社标志。
- 生成失败时先看脚本 stderr 的错误码/错误信息：限流（Throttling）稍后重试；密钥错误（InvalidApiKey）引导用户核对密钥。
