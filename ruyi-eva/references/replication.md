# 创意复刻：拆解怎么落到新分镜

复刻 = 借参考片的**结构**，换成本单元的人和货，口播与 `shotPrompt` 全部重写。确认后如奕按你的表编译提示词出片，不是把参考片丢给复刻接口。

## 读拆解

`get_content_context.referenceBreakdown`：

- `summary`：剧情概述。
- `shots[]`：每镜时间轴、描述、运镜、音效、台词。
- `subjects[]`：原片主体（人物、商品、场景）。
- `forbidden[]`：原片的禁止项（面部漂移、商品形变、凭空字幕），系统默认继承，不用写进 `shotPrompt`。

拆解为空就先 `analyze_reference_video` 并轮询作业；已有 `shots` 就直接写表，不要反复读空转。角度来自拆解，不问用户，也不检索公开对标片。

## 跟拆解走的

- 镜数、每镜时长比例、节奏、运镜、情绪弧沿用原片；`sourceShotIndex` 写对应镜号。
- 总时长按 brief 缩放：先按比例缩每镜，再砍口播字数，镜数不变。
- 台词节奏保留（一镜一句 / 反问开场 / 结尾 CTA）。

## 替换规则

| 原片 | 换成 | 没有时 |
| --- | --- | --- |
| 人物 | `mentions` 里 `role=person` 的图（人设 face） | 多人但只给了一张人像：全片都用这一张，不要编第二个人 |
| 商品 | `role=product` 的图 | `goal=product_sales` 必须补商品图：表照写，回复第一句「确认前必须补商品图」，给「上传 / 从商品库选」两个选项。不得改成生活方式，不得让模型凭文字画商品 |
| 场景 | `role=background` 的图，或单元 `world.scenes` / `assets` 里的场景图 | 用 `shotPrompt` 文字锁场景，主体写 `source=reference_only`，回复里说明；需要补图按 subject-images.md 生一张场景图 |
| 道具 / 非人设主体 | 单元库同类图 | 按 subject-images.md 补 |

`sourceSubjectName` 写对应拆解 `subjects[].name`。

## 口播

- 按当前商品卖点和用户补充说明（`brief.description`）重写；没有的卖点不编。
- 不照抄原片台词里的竞品名、价格、活动。
- 语言用 brief / 单元语言（US 账号英文），非中文时 `voiceoverZh` 给译文。
- 过一遍 compliance.md。

## 配方只兜底

本单元该 goal 有生效配方时，只在拆解对得上的地方借固定结尾、口头禅、音色。对不上的 `structure` / `variables` 丢掉，不要为了套配方改镜数或节奏，也不必填齐 `card.variables`。没有配方不追问。

## 写完之后

告诉用户查看页里能看到拆解脚本、分镜表和编译后的成片提示词，请先看这三份再决定是否确认生成。
