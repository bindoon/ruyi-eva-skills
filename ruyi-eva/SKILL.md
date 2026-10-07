---
name: ruyi-eva
description: Use the Ruyi EVA MCP to create TikTok-style videos for existing personas/units—depth clone, creative replicate, original, or find-viral-then-replicate. Prefer this skill whenever the user wants cloud video generation, storyboards, or downloading finished mp4s via Ruyi MCP tools.
---

# 如奕 EVA 出片

你通过 **如奕 MCP** 出片。工具已经接在当前会话里，直接调用，不要 `npm install`、不要自己写 MCP 客户端。不要猜单元 / 人设 id，不要读项目源码。付费动作前必须先征得用户同意。

## 硬纪律

1. **先查再写**：`list_units` → `get_unit`，确认人设 face 与目标 goal 的生效配方。
2. **分镜整份编辑**：`get_storyboard` 落到本地文件 → 改完 `validate_storyboard` → 通过后再 `save_storyboard`（带正确 `baseVersion`）。冲突时合并最新版再交。
3. **保留 sid / @图片n**：已有镜保留 `sid`；新镜不要带 `sid`。新图先 `attach_subject_image`，不要自己发明未分配过的编号。
4. **生图后自写说明**：上传图片时自己填 `label`（短名）与 `description`（可见特点）；MCP 不识图。
5. **无生图能力**：用户或沙箱 `assets/` 里有图时，必须上传再挂上。`complete_upload` 的 `label`（短名）和 `description`（图里看得见的特点）都不能空。没有用户图时才跳过临时素材，只用单元已有 face / 商品。
6. **付费前询问**：`create_depth_clone`、`confirm_storyboard`、`regenerate_video` 会花钱。先说明将产生费用，等用户明确同意再调。确认若报缺音色样本，说明该 `@音频n` 没有音频文件，从表里去掉该音色主体后再确认，不要空等。
7. **取片下载**：`wait_for_video` → `get_video` → 把 mp4 下载到本地 `ruyi/<contentItemId>/`（建议文件名用返回的 `filename`）。
8. **`regenerate_video` 若返回 reopen**：只是打开了新的分镜草稿，没有入队。必须再 `confirm_storyboard`，不要把上一次的 failed 当成这次结果。
9. **只读查看页**：`create_content_draft`、`save_storyboard` 和 `confirm_storyboard` 返回 `viewUrl` 时，立即发给用户。若响应没有该字段，必须调用 `get_view_link({ contentItemId })` 后再发。不得生成本地 HTML、`present_files` 预览或任何替代分镜网页；取链接失败只报告故障。该页会自动刷新单元、分镜、拆解和成片状态；图片重生、分镜编辑、确认生成仍只通过 MCP 工具完成。

## 四条流程（工具顺序）

详见 [references/workflows.md](references/workflows.md)。分镜字段与冲突合并见 [references/storyboard.md](references/storyboard.md)。

### A. 深度复刻
`list_units` → `get_unit` →（可选上传参考）`create_upload`/`complete_upload` → **征得同意** → `create_depth_clone` → `wait_for_video` → `get_video` → 下载。

### B. 创意复刻
`list_units` → `get_unit` → 上传/选定参考 → `create_content_draft(mode=replicate)` → `analyze_reference_video` → 轮询 `get_generation_job` → `get_content_context` → 写分镜文件 → `validate_storyboard` → `save_storyboard` →（可选挂图）`attach_subject_image` → **征得同意** → `confirm_storyboard` → `wait_for_video` → `get_video` → 下载。

### C. 原创
确认该 goal **有生效配方** → `create_content_draft(mode=original)` → `get_content_context`（读配方与历史）→ 写分镜（套配方，变量写入 `card.variables`）→ 校验 / 保存 / 挂图 → **征得同意** → 确认 → 等待 → 取片 → 下载。

### D. 找爆款后复刻（带货）
`search_products` → 已有带货草稿再 `select_product`（没有草稿就先 `create_content_draft(mode=original, goal=product_sales)`，再把商品写进该条目）。`select_product` 把商品放进商品缓存，不写入单元世界。返回的每张图带 `label`（镜头短名）和 `description`（看得见的特点）。写分镜时按这两项选适合这一条的图，不要把同一商品的几张图无差别塞进一个主体。然后 `get_unit` 看 `commerceProducts`（名称、视频数、每张图的短名），不要从旧的 `assets` 商品图里挑。接着 `search_reference_videos`。同商品结果已按估算收入排序，品牌片会留在列表里。主对标取收入最高的一条；若这一条明显是商家自己的号，改用下一条达人片，不要因为商品名里有品牌就把片整批丢掉。同商品不够再用同类目，换商品图和人设，口播重写。用户已有 mp4 且明确同意才走深度复刻（A）；否则借钩子走原创（C）。公开检索不会自动入库。未征得同意不要 `confirm_storyboard`。

## 分镜要点（摘要）

- 各镜 `durationSeconds` 之和 = brief 时长；允许 0.5 秒步进。
- `shotPrompt` 用中文，人物 / 商品 inline 点名；口播 `voiceover` 用目标语言，并附 `voiceoverZh`。
- 原创跟生效配方；复刻跟拆解，对不上不硬套。
- 派生字段（如口播估时）服务端会重算，提交时不要依赖它们。
