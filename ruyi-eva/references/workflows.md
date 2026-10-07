# 出片流程

四条流程共用同一套「读事实 → 定方向 → 写表 → 主体图 → 校验保存 → 付费确认 → 取片」。工作目录统一用 `ruyi/<contentItemId>/`：`storyboard.json`、`refs/`（下载的参考图）、`images/`（你生成的图）、成片 mp4 都放这里。

## 选哪条

| 用户说 | 流程 |
| --- | --- |
| 「照这条视频原样换成我的人 / 货」，且给了 mp4、同意花钱 | A 深度复刻 |
| 「参考这条视频的结构给我做一条」，有 mp4 | B 创意复刻 |
| 「给某单元做一条养号 / 带货视频」，没有参考片 | C 原创 |
| 「找个爆款带这个货」 | D 找爆款后原创 |
| B2B 获客、打品项目 | 不支持，请用户回平台「创建视频」 |

## 共用前置

```
list_units                      # 找到单元；名字对不上就列给用户选，不要猜
get_unit(unitId)
```

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
create_content_draft(mode=original, unitId, goal, personaIds, durationSeconds, language?, note?)
get_content_context                       # playbook + recentEpisodes + mentions
按 creative.md 定方向：盘点近作 → 2–3 个角度 → 等用户选
get_storyboard → 写表（套配方，变量写进 card.variables）→ validate → save
按 subject-images.md 补图 → attach → 刷新
→ 说明费用，等用户同意
confirm_storyboard → wait_for_video → get_video → 下载
```

- `note` 写选定角度的一句话说明（例如「在便利店被店员认出：口头禅接反转」）；不写就用配方默认说明。
- 原创总时长最长 60 秒，超过单段上限时服务端在镜头边界自动切段再拼接；单镜不能超过 15 秒。默认 15 秒。

## D. 找爆款后原创（带货）

需要该单元 `product_sales` 有生效配方（同 C）。

```
search_products(query, region?)           # 选品广场
create_content_draft(mode=original, goal=product_sales, ...)   # 先有条目
select_product(contentItemId, productId, region?)   # 写入 brief.product；商品图进商品缓存
get_unit → commerceProducts 里找到这件货和它每张图的 label / description / url
search_reference_videos(contentItemId, limit=5)
```

挑对标：

- 同商品结果已按估算收入从高到低排，**主对标取收入最高的一条**，不要改选播放更高、收入更低的片。
- 最高一条明显是商家自己的号 → 改用下一条达人片。不要因为商品名里有品牌就把同名片整批丢掉。
- 同商品不够时会补同类目片：借前三秒、演示方式和价格出现方式，换成本单元的人设和商品图，口播重写。
- 给用户列 3–5 条（标题、播放、估算收入、链接），写明主对标是哪一条、借它什么。
- 结果只有网页链接，**不能复刻文件**。用户另外给了 mp4 且同意花钱才走 A / B；否则就是借钩子写原创（C 的后半段）。

之后按 C 写表。商品主体只挂适合这一条的图（读每张 `label` / `description`），不要把同一商品的几张图无差别塞进一个主体。

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
- 确认报「缺音色样本」：该 `@音频n` 没有音频文件，从表里删掉这个音色主体（以及 `card.narrator.voiceLabel`）再确认，不要空等。
- `wait_for_video` 最多等约 50 秒，`timedOut=true` 就再调，直到 `succeeded` / `failed`。失败把 `lastError` 原样告诉用户，问要不要改表重出。
- 成片不满意要再出一版：说明费用 → `regenerate_video`。返回 reopen 时按修订规则改表，再 `confirm_storyboard`。
