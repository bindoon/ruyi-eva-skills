# 四条出片流程

## 共用前置

```
list_units
get_unit(unitId)   # 确认 face、配方、素材库；带货商品在 commerceProducts（label / description / videoCount），不在 world
```

付费工具（先问再调）：`create_depth_clone`、`confirm_storyboard`、`regenerate_video`。

## 1. 深度复刻

```
create_upload(kind=reference_video) → PUT putUrl → complete_upload(durationMs)
# PUT 返回成功后再 complete_upload，不要和 PUT 并行
# 或单元已有参考视频
征得同意
create_depth_clone(...)
wait_for_video(contentItemId)
get_video → 下载到 ruyi/<contentItemId>/
```

## 2. 创意复刻

```
create_content_draft(mode=replicate, referenceVideoId, ...)
# 输出时长不能长于参考片。用户要 15 秒但参考片更短时，按参考片时长写分镜，不要先按口中的秒数确认。
analyze_reference_video(contentItemId)
# 轮询 get_generation_job 直到 succeeded / reused
get_content_context
get_storyboard → 本地编辑 → validate_storyboard → save_storyboard
# 用户或 assets/ 里有图：create_upload(image) → PUT → complete_upload(label, description) → attach_subject_image
# label、description 都不能空；description 写可见特点。没有用户图才跳过。
征得同意
confirm_storyboard
wait_for_video → get_video → 下载
```

## 3. 原创

```
# get_unit 确认该 goal 有生效配方；没有则停，请用户先在平台确认配方
create_content_draft(mode=original, goal, note?, ...)
# note 写入 brief 说明；不写则服务端用一句配方说明，并在建稿时确认 brief
get_content_context   # 读配方 + 最近历史
写分镜（套配方 structure / variables）
validate → save →（可选挂图）
征得同意 → confirm → wait → get → 下载
```

## 4. 找爆款后复刻

```
# 先 search_products。没有带货草稿时先 create_content_draft(mode=original, goal=product_sales)，再 select_product。
# select_product 写入商品缓存，不进单元世界。每张图有 label（镜头短名）和 description。
# 分镜只挂适合这一条的图。get_unit.commerceProducts 能看到这个单元带过的货和视频数。
# 同商品结果已按估算收入从高到低排，品牌片会留在列表里。
# 主对标 = 收入最高的一条。不要改选播放更高、收入更低的片。
# 若这一条明显是商家自己的号，改用下一条达人片。不要因为商品名里有品牌就把片整批丢掉。
# 同商品不够时，clips 里会补同类目片：借前三秒、演示和价格出现方式，换商品图和人设脸，口播重写。
# 结果只有网页链接，不是视频文件。不要 brew / pip / npm 安装下载器。
# 用户已经给了 mp4，且明确同意花钱，才走深度复刻（A）。否则借钩子走原创（C），reference 记在回复里。
# 不要为了复刻去硬下载，也不要复用已有 original 条目改成 replicate。
```

## 无生图能力时

跳过自己生图。用户或 `assets/` 给了图就 `create_upload` → PUT 成功后再 `complete_upload`（`label` 与 `description` 都必填）→ `attach_subject_image`。没有用户图才只用单元已有 face / 商品图。
