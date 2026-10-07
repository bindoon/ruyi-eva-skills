# 分镜文件式编辑

## 流程

1. `get_storyboard`：记下 `version` 与完整 `storyboard`。
2. 把 `storyboard` 写成本地 JSON（例如 `storyboard.json`）。
3. 整份编辑。保留已有镜的 `sid` 与主体的 `@图片n`。
4. `validate_storyboard`（同一文档）。有错误按路径改，直到 `ok`。
5. `save_storyboard`：`baseVersion` = 刚才读到的 `version`（首版为 `0`）。
6. 若返回冲突：用返回的最新版覆盖本地文件，合并你的改动后重交。

## 编号规则

- **已有镜**：必须保留 `sid`（如 `s1`）。
- **新镜**：不要带 `sid`，服务端分配大于历史最大值的新 sid。
- **主体**：只用已分配的 `@图片n` / `@音频n`。新图先 `attach_subject_image`，再把返回的 label 写进分镜。
- 不要发明从未出现过的 `s99` 或 `@图片99`。

## 冲突合并

保存返回 `conflict: true` 时：

1. 以服务端 `latest` 为底稿。
2. 把你未入库的改动手工合并进去（尤其是你新加的镜与口播）。
3. 用新的 `baseVersion`（冲突里的 `latestVersion`）再 `validate` → `save`。

## 字段要点

| 字段 | 要求 |
| --- | --- |
| `scenes[].durationSeconds` | 0.5 步进；总和 = brief 时长 |
| `scenes[].shotPrompt` | 中文；点名人物 / 商品 |
| `scenes[].voiceover` | 目标语言；可空 |
| `scenes[].voiceoverZh` | 非中文口播时的译文 |
| `card.variables` | 原创时填配方变量 |
| `subjects[].description` | 商品只抄 brief + 资产说明，不自补材质色泽 |
| 锁定镜 | 已 `locked` 的镜不要改结构，否则保存被拒 |

## 口播估时

- `validate_storyboard` 估算每镜口播时长，估时大于画面时长就是 mustFix。警告级时校验仍可能通过，保存后仍会列出 mustFix，修完再存。
- 估时按词数，大约 0.39 秒/词。写口播时按「画面秒数 × 2.6 词」留上限（3 秒镜不超过 7 个词，5 秒镜不超过 13 个词）。
- 数字和缩写读出来更长（`33-degree` 会读成 thirty-three degrees），再留余量。
- 商品主体 `source` 用 `unit_library`（选品入库之后）。`card` 不要加自定义字段；对标信息写进 `angleRationale`。
- `card.pillar` 必须用单元里已有支柱的原名。
