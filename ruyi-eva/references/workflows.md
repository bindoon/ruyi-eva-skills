# 出片流程

出片流程共用同一套「读事实 → 定方向 → 写表 → 主体图 → 校验保存 → 付费确认 → 取片」。工作目录统一用 `ruyi/<contentItemId>/`：`storyboard.json`、`refs/`（下载的参考图）、`images/`（你生成的图）、成片 mp4 都放这里。

用户只要脚本时，完成到「主体图 → 校验保存 → get_storyboard 复读」即结束；不要确认入队。指定隔离工作目录时，上述相对路径放在本轮的新目录内。

## 选哪条

| 用户说 | 流程 |
| --- | --- |
| 「照这条视频原样换成我的人 / 货」，且给了 mp4、同意花钱 | A 深度复刻 |
| 「参考这条视频的结构给我做一条」，有 mp4 | B 创意复刻 |
| 「给某单元做一条养号 / 带货视频」，没有参考片 | C 原创 |
| 「找个爆款带这个货」 | D 推荐爆款后创意复刻 |
| B2B 自动获客复刻视频 | [B2B 自动流程](b2b.md)，不走下方 B2C 外部写表流程 |
| B2B 打品文档项目、挂已有账号图片 | [项目资料流程](b2b-projects.md)，不启动出片 |

## 共用前置

```
list_units                      # 找到单元；名字对不上就列给用户选，不要猜
get_unit(unitId)
```

用户给商品链接时，先 `get_product(productId, region)` 读确切商品；不要把数字 ID 当关键词传给 `search_products`，关键词检索失败不代表商品不存在。用户让你自行找单元时，先读目标商品与市场，再筛选 `list_units` 里该 goal 有生效配方的候选，逐个 `get_unit` 核对配方适用性及人设 face；确定后才建稿。别把穿搭配方硬套成护肤，也别借 `persona_ip` 配方建带货。缺配方是平台准备项，MCP 不能写配方；报告前先排查其他适用候选。

原创和创意复刻写分镜前单独检索红线，修改商品/市场/主题/宣传表述后再查。平台与本租户规则共同参考，同时遵守账号 redlines；按适用范围判断，block 遵守、warn 提醒，零命中可继续，故障须告知。

从 `get_unit` 读并记下：

- `unit.language` / `targetMarket`：口播语言和市场（US 账号写英文）。
- `unit.redlines`：本账号红线，写口播时避开。
- `unit.contentStrategy`：内容支柱（`card.pillar` 只能用这里的原名）。
- `unit.world.scenes` / `cameraGrammar`：常驻场景（带 `assetId`）和画面语法。
- `personas[]`：`role=lead|cast`，`soul`（外貌 appearance、口头禅 catchphrases、语气 toneRules 等），`faceAssetId` + `faceUrl`，`voiceAssetId`。
- `assets[]`：单元素材库（face / scene / prop / voice …），每张带 `label`、`description`、`url`。
- `commerceProducts[]`：带过的货，每张图带 `label`、`description`、`url`。
- `playbooks[goal].approved`：生效配方。

`url` 是约 1 小时有效的临时链接，过期就重新调 `get_unit` / `get_content_context`，不要把链接写进分镜或长期保存。

## A. 深度复刻（不写分镜）

```
create_upload(kind=reference_video, unitId, contentType=video/mp4)
PUT 文件到 putUrl（带返回的 headers）       # PUT 成功后再 complete，不要并行
complete_upload(uploadId, kind=reference_video, durationMs, title?)
→ 说明费用，等用户同意
create_depth_clone(unitId, referenceVideoId, personaIds, productAssetIds?, durationSeconds, note?)
wait_for_video → get_video → 下载
```

`note` 只写用户亲口给的补充说明，不要把人设性格拼进去。

## B. 创意复刻

```
上传参考视频（同 A 前三步），或用单元已有的 referenceVideoId
create_content_draft(mode=replicate, unitId, goal, referenceVideoId, personaIds,
                     productAssetIds?, durationSeconds, language?, note?)
analyze_reference_video(contentItemId) → 轮询 get_generation_job 到 succeeded / reused
get_content_context                       # referenceBreakdown + mentions + 素材
search_knowledge(query="行业 + 市场 + 主题", categories=["redline"], unitId=unitId)
get_storyboard → 按 replication.md 写表 → validate → save
按 subject-images.md 补图 → attach_subject_image → get_storyboard 刷新
→ 说明费用，等用户同意
confirm_storyboard → wait_for_video → get_video → 下载
```

- 参考片不超过 30 秒；输出时长 4–15 秒，且不长于参考片。用户要 15 秒但参考片更短，按参考片时长写。
- `productAssetIds` 填 `commerceProducts[].images[].id`；`backgroundAssetId` 只接受 `kind=background` 的素材，常驻场景图不要填这里，写进分镜主体即可。
- 拆解失败：告诉用户换一条参考视频，到此为止。拆解为空或用户要求重拆才 `force=true`。

## C. 原创

```
get_unit 确认 playbooks[goal].approved 存在；没有就停，请用户去平台补配方
create_content_draft(mode=original, unitId, goal, personaIds, productAssetIds?, durationSeconds, language?, note?)
get_content_context                       # playbook + recentEpisodes + mentions
search_knowledge(query="行业 + 市场 + 主题", categories=["redline"], unitId=unitId)
按 creative.md 定方向：盘点近作 → 2–3 个角度 → 等用户选
get_storyboard → 写表（套配方，变量写进 card.variables）→ validate → save
按 subject-images.md 补图 → attach → 刷新
→ 说明费用，等用户同意
confirm_storyboard → wait_for_video → get_video → 下载
```

- `note` 写选定角度的一句话说明（例如「在便利店被店员认出：口头禅接反转」）；不写就用配方默认说明。
- 原创总时长最长 60 秒，超过单段上限时服务端在镜头边界自动切段再拼接；单镜不能超过 15 秒。默认 15 秒。

## D. 推荐爆款后创意复刻（带货）

只使用广场商品。此流程是复刻，不要求生效配方，不先建原创稿。

```
get_product(productId, region)            # 有确切链接 / ID 时；未知商品才 search_products
list_units → get_unit                    # 用户选人设，核对其所属单元、语言、市场、face、绑定账号
search_reference_videos(unitId, personaId, productId, region, limit=5)
→ 展示 3–5 条参考片：标题、播放、估算收入、链接、适配依据；等用户选片
import_reference_video(unitId, videoId, region, productId)
→ pending：按 retryAfterSeconds 重调同参数；ready：取得 referenceVideoId；failed：告知原因、换片
create_content_draft(mode=replicate, goal=product_sales, unitId, personaIds,
                     referenceVideoId, durationSeconds, language?)
select_product(contentItemId, productId, region)
get_content_context → get_unit           # 取当前 mentions 与 commerceProducts 商品真图
analyze_reference_video(contentItemId) → get_generation_job 等拆解成功
search_knowledge(query="行业 + 市场 + 主题", categories=["redline"], unitId)
按 B 和 replication.md 写表、准备素材、校验保存
→ 用户确认付费生成 → confirm_storyboard → wait_for_video → get_video
```

同商品候选已按估算收入排序，优先向用户推荐收入较高且适合人设演示方式的片；指标是第三方估算。商品市场必须与单元市场匹配。只有网页链接但不可导入的来源不能假装已经复刻；导入失败不自动切原创。参考片 / 输出时长服从 B 的现有约束。

`select_product` 后重新读 context。保留建稿时分配的人设编号；将当前商品图库真实图片加入 product 主体并至少进一镜，不把商品图生成人设身份图。

## 资源列表与确认发布

领取营销账号、普通视频发布及账号统计见 [managed-accounts.md](managed-accounts.md)；下文发布示例保留原有挂车模式。

```
list_units / get_unit                    # personas 含 ID / role，tiktokAccount 区分 registered / authorized
list_content_items(unitId?, tiktokAccountId?, page?, pageSize?)
list_published_videos(unitId?, personaId?, tiktokAccountId?, page?, pageSize?)
```

账号属于经营单元，配角不能独立绑号。`authorized` 表示存在可用授权，能否挂车还要看 `canPublishShop`、具体商品及发布预检。已发布列表只含经如奕真实通道确认成功的记录，可见性另看 `visibilityStatus`；videoUrl 为空就说明平台尚未提供链接，不能拼接猜测；playbackUrl 可播放实际发布版本，临时链接过期后重新查询。

```
get_publish_preview(contentItemId, tiktokAccountId)
→ 展示 videoUrl / viewUrl、contentAssetId 与版本、账号、商品、标题及发布设置
→ blockers 中授权 / 市场等缺项须先处理；用户确认看过并认可成片，且明确同意发布
approve_content_item(contentItemId, contentAssetId, explicitConfirm=true)
publish_video(contentItemId, tiktokAccountId, contentAssetId, productId, region,
              title, tags, privacyLevel, commercialDisclosure, explicitConfirm=true)
get_publish_job(publishJobId, tiktokAccountId) → 查询到成功 / 失败 / 结果待核对
```

一期挂车选公开发布；预览返回默认设置。成片或商品变化则重新预览与确认。`queued`、`running` 只是作业进度，不是已发布；`reconciliationRequired=true` 表示官方提交结果待核对，不重复提交。失败报告原因。审核和生成成功都不能代替真实挂车发布验收。

## 上传图片的固定动作

```
create_upload(kind=image, unitId, contentType=image/png)   # 返回 uploadId / putUrl / headers / assetId
curl -X PUT -H "Content-Type: image/png" --data-binary @ruyi/<id>/images/xxx.png "<putUrl>"
complete_upload(uploadId, kind=image, label=<短名>, description=<看得见的特点>)
attach_subject_image(contentItemId, unitId, assetId, subjectLabel=@图片n, subjectKind?, label?)
get_storyboard                                              # 挂图不出新版本，必须刷新本地文件
```

单张图不超过 20 MB。`label` 是镜头里用的短名（「白色棉T」），`description` 写图里看得见的特点（「纯白短袖圆领棉T，平铺，无图案」），两项都不能空，MCP 不识图。

## 确认与出片

- 确认前最后一次 `validate_storyboard`：`errors` 和 `mustFix` 都为空；所有进镜的主体都有图；带货有商品图。
- 保存后调用一次 `review_storyboard`。建议不阻止生成。只按原文证据修一次并再查一次，剩余建议交给用户。检查失败或返回未检查时，不要说已经通过。
- 确认报「缺音色样本」：该 `@音频n` 没有音频文件，从表里删掉这个音色主体（以及 `card.narrator.voiceLabel`）再确认，不要空等。
- `wait_for_video` 最多等约 50 秒，`timedOut=true` 就再调，直到 `succeeded` / `failed`。失败把 `lastError` 原样告诉用户，问要不要改表重出。
- 成片不满意要再出一版：说明费用 → `regenerate_video`。返回 reopen 时按修订规则改表，再 `confirm_storyboard`。
