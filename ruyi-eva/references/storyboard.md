# 分镜表

一张表 = 脚本卡 `card` + 主体 `subjects` + 逐镜 `scenes`，外加 `hookScript` / `cta` / `language` / `title` / `caption` / `hashtags`。完整 JSON Schema 在 MCP 资源 `ruyi://schema/storyboard`，与服务端校验一致。

你只写表。确认时如奕把表**编译**成成片提示词送生视频，你不写整段时间轴、不写 model / prompt / engine。

## 文件式编辑

1. `get_storyboard`：记下 `version`（无草稿时是 `0`，返回的是骨架）和 `storyboard`，写进 `ruyi/<contentItemId>/storyboard.json`。
2. 整份编辑本地文件。
3. `validate_storyboard`（同一份文档）。按返回改，直到 `ok=true` 且 `mustFix` 为空。
4. `save_storyboard(contentItemId, baseVersion=刚读到的 version, storyboard, changeNote?)`。成功后版本 +1，`changedBy=mcp`。保存结果里仍有 `mustFix` 就接着修。
5. **冲突**（返回 `conflict: true`）：用户可能在查看页 / 平台面板改过。以返回的 `latest` 为底稿，把你没入库的改动合并进去，用 `latestVersion` 作新的 `baseVersion` 再 validate → save。不要用旧文件覆盖用户的改动。
6. `attach_subject_image` 会原地改最新草稿但**不出新版本号**：挂完图一定先 `get_storyboard` 刷新本地文件，再继续改表，否则会把刚钉上的图覆盖掉。

已确认（`status` 不是 `draft`）的表不能再存；要改先 `regenerate_video` 打开新草稿。

## 编号

- **镜 `sid`**：已有镜必须保留（`s1`、`s2`…）。新镜不带 `sid`，服务端分配。删镜不复用编号，不要发明 `s99`。用户说「第 3 镜」先对到 sid。
- **主体 `@图片n` / `@音频n`**：两套独立编号。第 1 版可以自由续编号；有版本之后，**新编号只能通过 `attach_subject_image` 产生**，表里直接写一个从没出现过的编号会被拒。所以第 1 版就把计划要用的主体行都写上（没图的先 `source=reference_only`、`referenceAssetIds=[]`）。
- `get_content_context.mentions` 是建稿时已经分配好的编号，原样保留。

## 脚本卡 card

| 字段 | 填什么 |
| --- | --- |
| `creativeAngle` | 选定角度，一句话（必填） |
| `angleRationale` | 为什么这个角度对这个账号 / 这个品成立；对标信息写这里 |
| `purchaseBarrier` / `coreTrigger` | 带货必填：观众不买的理由 / 打穿它的心理触发。养号不填 |
| `emotionalArc` | 三段式（必填） |
| `hookType` | 只选一种（必填），见 creative.md 十种钩子 |
| `visualStyle` / `visualAnchor` | 全局风格一句 / 全片反复出现的画面锚点 |
| `shootingMode` | `single_take` 一镜到底，或 `edited` 多镜剪辑。新脚本必须选。一镜到底的时间段是同一镜头里的动作节拍，不是切镜 |
| `continuityNotes` | 进出场方向、空间位置、动作和道具状态承接，最多 6 条，会写进成片 prompt。一镜到底至少 1 条 |
| `narrator` | `{ language, toneInstruction, voiceLabel }`；有口播时 `language` 必须有 |
| `shootingNotes` | 2–4 条 |
| `negativeDirectives` | 全片禁项，最多 6 条 |
| `pillar` | 单元内容支柱原名 |
| `variables` | 原创：配方每个变量的取值 `{ 变量名: 取值 }` |

`card` 不接受自定义字段。

## 主体 subjects

| 字段 | 规则 |
| --- | --- |
| `label` | `@图片n` 或 `@音频n` |
| `kind` | `person` 人设/角色 · `product` 商品 · `scene` 场景 · `voice` 音色 · `style` 穿搭 / 造型参考（不是第二个人，脸仍用人设） |
| `name` | 短名（「Coco」「多效抗衰润肤棒」「客厅」）；mentions 里的照抄 `subject` |
| `role` | 这个主体在片里干什么 |
| `description` | person：人设外貌（从 `soul.appearance` 抄）；穿搭只改衣服词，不要换成参考图里另一个人。product：只抄商品名 + 卖点 + 该图 `description`，**禁止自补颜色 / 材质 / 五金 / Logo** |
| `usage` | 用户用途原样保留；未填时按图写参考属性，见下方字段分工 |
| `source` | `persona_pointer` 人设 face · `unit_library` 单元库 / 商品库 · `session_upload` 用户这次给的图 · `generated` 你生成的图 · `reference_only` 原片有、我们还没图 |
| `referenceAssetIds` | 素材 id，`[0]` 是成片用的那张，最多 4 个。人设主体只填该角色 `faceAssetId` |
| `personaId` | 来自人设的 person 必填；修订时不要删、不要改 |
| `sourceSubjectName` | 复刻：对应拆解 `subjects[].name` |

常见写法：

```json
{ "label": "@图片1", "kind": "person", "name": "Coco", "role": "主角",
  "description": "<soul.appearance 压成一句>", "source": "persona_pointer",
  "referenceAssetIds": ["<faceAssetId>"], "personaId": "<personaId>" }
{ "label": "@图片2", "kind": "product", "name": "<商品名>", "role": "被测试的商品",
  "description": "<商品名>；<卖点>；<该图 description>", "source": "unit_library",
  "referenceAssetIds": ["<commerceProducts[].images[].id>"] }
{ "label": "@图片3", "kind": "scene", "name": "客厅", "description": "<该图 description>",
  "source": "unit_library", "referenceAssetIds": ["<world.scenes[].assetId>"] }
{ "label": "@音频1", "kind": "voice", "name": "主角音色", "description": "主角音色",
  "source": "persona_pointer", "referenceAssetIds": ["<voiceAssetId>"] }
```

- 每个非音色主体都必须至少进一镜 `subjectLabels`，否则 `mustFix`。
- 音色至多一个，用 `@音频n`，不要占 `@图片n`；相关镜 `subjectLabels` 带上它，`card.narrator.voiceLabel` 指向它。
- 带货（`product_sales`）必须有 `kind=product` 主体，确认时必须有图。

## 逐镜 scenes

| 字段 | 规则 |
| --- | --- |
| `sid` | 已有镜保留；新镜省略 |
| `beat` | 带货：钩子 / 痛点 / 功效 / 卖点 / CTA；剧情：钩子 / 冲突 / 互动 / 高潮 / 结尾 |
| `durationSeconds` | 0.5 秒步进；单镜不超过 15 秒；**各镜之和 = brief 时长** |
| `suggestedDurationSeconds` | 压时长前你觉得合适的值（可选） |
| `emotion` / `camera` / `location` | 情绪（落在情感弧里）/ 运镜机位 / 场景名 |
| `visual` | 中文一两句剧情，给运营看，**不是**成片正文 |
| `shotPrompt` | **成片正文，中文写**（人名、地名、品牌名可留原文）。见下 |
| `voiceover` | 目标语言口播；无口播留空 |
| `voiceoverZh` | 目标语言不是中文时的译文 |
| `audio` | 环境声、动作音效、音乐取舍；台词只放 voiceover |
| `onScreenText` | 字幕，目标语言，复述口播不另起说法 |
| `subjectLabels` | 这一镜**真出现**的 `@图片n` / `@音频n`，最多 8 个 |
| `locked` | 锁住的镜修订时不能改也不能删 |
| `sourceShotIndex` | 复刻：对应拆解镜号 |

不要传 `index`、`estimatedSpeechSeconds`，服务端会算。

## 字段分工

- `subjects.usage`：素材参考哪些属性。用户已填用途原样保留；未填时按实际图补一句，易串角色才补不采用的内容。例：场景「只参考空间和光线，不引入图中人物」；换装「只参考服装，身份仍是主角」。外貌由图定义，不把 description 抄进逐镜。
- `shotPrompt`：中文动作正文，专名可留原文。从动作起笔，人物 / 商品 / style 在做事处 inline `@图片n`，且与本镜 `subjectLabels` 对齐；场景只进 labels。开头连续 2+ 标签会被剥掉，单个开头标签保留。`visual` 是运营摘要。
- `camera`：景别、机位、运动与焦点对象。少见术语补可见变化，如「移焦：手中杯子逐渐虚化，后方人物面部变清晰」。转场写触发物、方向和到达构图；一镜到底只能连续运动，不能跳到独立特写。
- `audio`：按需写环境声、动作音效、音乐的取舍。无人声时 voiceover 留空；不要为凑字段增加声音。台词只放 `voiceover`，译文只放 `voiceoverZh`；语言和口音 / 语气用 `language`、`card.narrator`，不在 audio 或 shotPrompt 重抄台词。
- `card.visualStyle` / `negativeDirectives`：全局风格 / 禁项，逐镜不重复。准确字幕、Logo、价格、CTA 字样不交给成片模型；字幕填 onScreenText。不要宣称平台已经自动完成后期。

## 动作与状态

每段一个主要变化，必要时写「动作 → 结束时可见状态」：谁仍在画面哪侧、道具由谁持有、放在哪里、数量是否改变。下一段从该状态承接；简单镜头一句即可，不强制长模板。按用户给定的物理 / 材质 / 禁项写清，不概括掉。

`continuityNotes` 只写跨镜不变量：身份与数量、服装、道具归属、空间方向、光线或运动趋势，最多 6 条，一镜到底至少 1 条。区分人物自身左右与画面左右。情绪保留 emotion / emotionalArc，正文用触发事件加 2–4 个关键外在反应，不堆抽象强度词或无关细节。

时长保留 0.5 秒步进，系统生成连续时间轴；时间是节奏指引，不保证帧级落点。动作过密就删非必要动作或与用户调整时长，不塞频次指令。一镜到底的总时长与参考图必须落在当前单段上限内，单段最多 30 图；以 get_content_context 返回的 constraints 为准，不因指南写 30 秒就放宽。

## 三个局部改写例

以下只展示变化字段，完整表仍按 schema 填。

1. **单人商品演示**：原 shotPrompt「@图片1 展示 @图片2，惊喜。」→「@图片1 把 @图片2 放到桌面中央，松手后看向它，眉头舒展并轻轻点头；结束时商品留在桌上，手已移开。」camera「固定中景，人物和商品均在画面内」；audio「保留放置声与室内底噪，无背景音乐」；voiceover「It fits right here.」，voiceoverZh「它正好放这里。」；narrator `{language: "en", toneInstruction: "自然美式英语，轻声"}`。商品 usage「只参考实际商品外观，不改变结构」；不用虚构功效证明。
2. **双角色道具交接**：原 shotPrompt「@图片1 和 @图片2 交换 @图片3。」→「@图片1 从画面左侧把 @图片3 递给右侧的 @图片2；@图片2 双手接稳后，@图片1 松手；结束时道具只由 @图片2 持有。」continuityNotes「两人站位不交换，道具始终只有一个」；camera「固定双人中景，交接手部可见」。三者都进 subjectLabels，voiceover 留空。
3. **一镜到底推进**：原 camera「全景切特写再切背面。」→ card.shootingMode「single_take」；第一段 shotPrompt「@图片1 拿起 @图片2，结束时商品在右手、人物仍站桌后」；第二段「@图片1 将右手的 @图片2 举到胸前，结束时停稳面向镜头」；camera 分别「固定中景」「从同一机位缓慢推近，持续保留手与商品」；continuityNotes「商品始终在右手，人物不离开桌后，镜头连续推近不跳切」。


### 编译出来长这样（只用来理解，不要自己写）

```
风格：<card.visualStyle>
拍摄方式：全片一镜到底。以下时间段是同一个连续镜头内的动作节拍，不代表切镜……
连续性要求：<continuityNotes>
参考素材：@图片1 = Coco（角色外观参考）；@图片3 = 厨房（场景空间参考，不是待插入的静帧）
动作时间轴（时间为节奏指引）：
[0-2.5s] @图片1 <shotPrompt>。镜头：<camera>。声音：<audio>。口播（en）："…"
禁止：<negativeDirectives>
不得生成字幕、Logo、价格、CTA 文案或购买按钮；这些由后期合成。
```

口播和声音由视频模型按提示词一起生成，没有独立 TTS。

## 口播时长

- 口播按需：先决定这条有没有人声，无人声 `voiceover` 留空，不要为了凑而硬写。
- 系统按语言估算每镜口播秒数；**估时超过画面时长 + 0.5 秒进 `mustFix`**，确认前必须改完。
- 上限：英文不超过 `2.6 × (镜时长 + 0.5)` 个词，中文不超过 `4.2 × (镜时长 + 0.5)` 个字。3 秒镜约 9 个英文词，4 秒镜约 11 个。数字和缩写读出来更长（`33-degree` → thirty-three degrees），再留余量。
- 一镜一句、一口气说完；在名词或数字上断句。最后一镜落在 CTA 或固定结尾，不加告别。
- 超时只砍那几镜的口播：去形容词、一镜一句，每次都比上一版短；砍完仍超才缩画面，镜数不变。

## 修订

用户改的是槽位，不是故事。没点名的镜逐字保留，只改被点名的部分：

| 用户说 | 只改 | 不动 |
| --- | --- | --- |
| 压到 15 秒 | 相关镜 `durationSeconds`，砍口播 | 镜数、画面 |
| 换场景 | `location`、`shotPrompt` 环境词；缺场景主体就加一行并写进相关镜 `subjectLabels`（有版本后新编号要走 attach） | 人物动作、口播 |
| 改第 n 镜口播 | 该镜 `voiceover` / `voiceoverZh` | 其它镜 |
| 换 / 重生某主体图 | 出图后 attach 到原编号 | 表的文字 |
| 挪镜 | 调整数组顺序，保留 sid | 不要删了再新建 |

- 复刻时长缩放：按比例缩每镜、砍口播字数，镜数不变（20 秒 5 镜压到 15 秒是每镜缩 25%，不是砍掉一镜）。
- 出图黑、手坏、脸漂是生图缺陷，重生图即可，不改表。
- `changeNote` 写一句为什么改（用户要求 / 口播超时 / 合规改词 / 口味 / 试另一种钩子）。
- 最新一版是 `draft` 时，哪怕更早有一版已确认、已经出过片，也按这一版继续改；不要告诉用户「已确认没法改」。

## 保存前写作自查

检查素材对应与职责、动作容量、必要结束状态、人物数量与道具归属、机位和拍摄方式、声音取舍及语言。此处是创作自查，不新增服务端硬门。validate → save → get_storyboard 复读；表与图就绪后沿用 review_storyboard：只按原文证据修一次再查一次，剩余建议交给用户。改表或换图后旧检查作废，故障不得说通过。

## 系统会拦的

| 级别 | 情形 |
| --- | --- |
| 拒绝保存 | 各镜时长之和 ≠ brief 时长；时长不是 0.5 倍数；单镜超 15 秒；一镜到底总时长或参考图超过单段上限；`subjectLabels` 指向不存在的主体；`shotPrompt` 写了不在 `subjectLabels` 里的编号；`shotPrompt` 写字幕 / Logo / 价格 / 购物车；主体编号重复或非法；音色多于 1 个；建稿 mentions 丢失或没进镜；单段参考图超 30 张；改了锁定镜；新编号未经 attach |
| `mustFix`（存得进去，确认前必须清） | 口播超时；`shotPrompt` 缺失或没点名本镜人物 / 商品；主体没进任何镜；带货没有商品主体；有口播没语言；与近作角度 + 钩子重复或变量取值完全相同 |
| 连续性检查（不阻止生成） | `review_storyboard` 看最终编译 prompt。只修有原文证据的问题一次，再查一次。改表或换图后旧结果作废。检查失败不得说通过 |
| `warnings`（转成选项给用户） | 支柱连用 3 条、变量池外新值等 |
| 确认时额外拦 | 进镜主体没有图；带货商品主体没有图 |

## 创作红线自查

写原创/创意复刻分镜前，单独调用 `search_knowledge`，`categories: ["redline"]`，query 带行业、市场、主题；修改商品/市场/主题/宣传表述后再查。按行业、市场、平台判断平台和当前租户规则的适用范围，空数组不限。block 必须遵守，warn 提醒，rewriteHint 用于改写。零命中可继续，故障要明确告知。检查口播、屏幕字、钩子与 CTA，不能照抄参考片的违规宣称。

写作方法参考：[火山 Seedance 2.5 指南](https://docs.volcengine.com/docs/ark/seedance-2-5-prompt-guide?lang=zh)、[飞书撰写指南](https://bytedance.larkoffice.com/docx/OsiUdR1OxoDqvnxsK8LczYx7nPd)。这里只吸收现有分镜字段可执行的写法，不代表如奕新增视频编辑、延长或关键帧接口。提示词不保证特定画质、完全一致或帧级剪辑。
