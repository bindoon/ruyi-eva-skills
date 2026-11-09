# 脚本与分镜

以 `tools/list` 的输入 schema 为准。支持 `text` 的 `save_storyboard` 用文本脚本。维护旧服务或结构化历史稿时，按下文的结构化分镜流程处理。

## 文本脚本

1. 先用 `get_storyboard` 读最新版本，初稿 `baseVersion=0`。已有文本稿以返回的 `scenes[].shotPrompt`、时长、附件和 `card.shootingMode` 为底，只改用户点名的部分。
2. `save_storyboard` 传 `contentItemId`、`baseVersion` 和 `text`。一段稿用 `text.prompt`，继承当前时长和素材。需要分次生成且允许剪辑时用 `text.segments`，各段给 `prompt` 与 `durationSeconds`，总和等于当前设置。未在本段正文引用但确实要随段发送的素材用 `attachments`。修改多段稿时保留未改段的正文、时长和附件。
3. 服务端保存时校验文本稿。`validate_storyboard` 接收结构化 `storyboard`。查看保存结果的 `saved` 和 `mustFix`，保存成功后用 `get_storyboard` 核对版本、正文与素材。版本冲突时重读合并。确认生成前处理所有阻塞项，普通 `warnings` 按需取舍。

素材使用 `get_content_context.mentions` 和已挂图的稳定 `@图片n`、`@音频n`。新素材按 [主体图](subject-images.md) 准备。挂图后重读草稿，核对版本和绑定，再改正文。新增或更换的素材若尚未写入稿件，用 `text.materials` 提交 `label`、`kind`、`name`、`assetId`，以及适用的 `personaId` 和 `usage`。上传后使用绑定工具返回的 `boundAssetId`，角色 face 和商品真图沿用本次选择。

## 正文写法

- 写生成模型可执行的动作、镜头与声音。画面用中文，专名可保留原文，台词用目标语言。人物、商品和音色在实际使用处直接写稳定的 @ 编号，说明各图负责的身份、衣着、外观或空间。背景中的路人不进入角色设定。
- 开场交代地点、站位、姿态、持物和可见范围。每拍写主要动作与结束状态，下一拍接续。写出交接、拾放和进出场，区分人物自身左右和画面左右。全片保持人物数量、衣着、道具归属和运动方向一致。
- 景别、机位、焦点和运动服务于动作与揭晓。用触发事件和可见反应表现情绪。写实风格给出现场光源、曝光、肤色和材质，用户指定风格优先。全片共用的约束写一次。
- 时间轴从 0 秒连续排到本次结尾。压时长先精简台词与次要动作，保留因果和交接。有人声才写台词，给呼吸、动作和停顿留余量。英文约每秒 2–2.6 词，中文约每秒 3–4 字作粗估。环境声、音效和音乐按需写。口播、字幕和宣称按 [合规指引](compliance.md) 检查。

## 一镜到底

明确「全片一镜到底，连续拍摄」。文本稿设 `text.shootingMode=single_take`，用一份 `prompt` 写全片。结构化稿用 `card.shootingMode=single_take`，时间段只标记同一个连续镜头的动作节拍。

- 写清摄影机起点、主体站位、道具位置和初始可见范围。每拍说明主体动作、镜头如何跟随、结束时人和物在哪里。
- 通过连续推近、后退、跟随或摇移改变景别和焦点。跨区域要拍出移动过程，避免跳切、反打、插入特写或瞬间换景。
- 遮挡揭晓先定遮挡物和相机位置，再写移开或绕行后的首次可见时刻。遮挡前后保持人物、道具、声音和动作进程连续。

例如 10 秒稿可写「0–2 秒，中景固定，人物在桌左侧右手持杯，纸盒遮住桌右侧。2–6 秒，人物将杯放在桌上，相机向右平移，逐渐露出纸盒后的小狗。6–10 秒，相机停住，小狗探头，人物转头，杯子留在原位」。

一镜到底的总时长与所用素材必须落在当前模型单次生成上限内。超限先保留稿件并说明阻塞，缩短时长、减少素材或经用户同意改为多镜剪辑。多个生成段拼接不能交付为一镜到底。

## 结构化分镜

完整字段见 `ruyi://schema/storyboard`。用 `get_storyboard` 读取 `version` 和 `storyboard`，保存本地 `ruyi/<contentItemId>/storyboard.json`，修改后用 `validate_storyboard` 校验，再带 `baseVersion` 和 `storyboard` 调 `save_storyboard`。挂图可能直接更新最新稿且不增加版本号，挂完先复读再保存。冲突时用最新稿合并，已确认稿需要重新开草稿才能编辑。

- `title` 写短标题，`card.synopsis` 用 1–3 句交代剧情，改剧情时同步。`card` 保留选定的角度、钩子、情绪弧、支柱和配方变量，带货填写购买顾虑和触发点。`visualStyle`、`continuityNotes`、`negativeDirectives` 分别写风格、跨镜承接和禁项。`shootingNotes` 供后期查看，生成要求写进实际编译字段。
- `subjects` 保留建稿 mentions 的编号、`referenceAssetIds` 与适用的 `personaId`。用 `usage` 区分素材职责。`@图片n` 和 `@音频n` 独立编号，音色至多一个。固定人物只用该角色 face。已有稿的新编号先挂图取得。每个非音色主体至少进一镜，带货须有 `kind=product` 商品主体与真图。
- `scenes` 保留已有 `sid`，新镜省略，锁定镜保持原样。镜时长支持小数，各镜之和等于总时长。`shotPrompt` 写中文画面，人物、商品和穿搭在动作处直接点名，场景进 `subjectLabels`。每镜只挂所用主体。`camera` 写运镜，`audio` 写非台词声音，`voiceover` 写目标语言台词，`voiceoverZh` 写译文。后期画面文字用 `onScreenText`。
- `validate_storyboard` 的 `errors` 处理后才能提交，`mustFix` 在生成前清零。保存后重读，核对素材可解析和时长。单段时长、参考图和口播超限按返回修正。

交付前检查素材、动作容量、必要结束状态、声音与语言。连续长镜沿时间轴确认摄影机能走完、主体与道具没有瞬移、揭晓前没有穿帮。按保存和校验结果处理具体问题，直接交付查看页。
