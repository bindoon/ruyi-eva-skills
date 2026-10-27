# 营销账号领取、普通发布与效果

先通过 tools/list 确认工具存在。此流程仅管理已有经营单元的营销账号，不创建人设或 B2B 项目，不接收或返回账号密码。

## 领取营销账号

用户要求为现有单元领取账号时：

1. `get_unit` 确认 unitId、目标市场及当前账号。
2. `request_tiktok_account(unitId, country, idempotencyKey)`；country 使用单元市场，同一业务重试沿用原幂等键。
3. 返回申请 ID 后，用 `get_tiktok_account_allocation(allocationId)` 查询。waiting_inventory / verifying 只代表准备中，不代表已绑定成功，不重新申请。
4. succeeded 后重新 `get_unit` 获取账号和业务能力。已有真实账号时直接返回当前账号，不消耗第二份库存。

账号归经营单元，配角不能另领。等待库存或需要处理时向用户说明当前状态，不编造账号、不承诺准备时间。账号可发布与数据可同步是独立事实，以 canPublish / canReadMetrics 为准。

## 读取账号信息

`get_unit.tiktokAccount`、`list_units.units[].tiktokAccount` 和 `get_publish_preview.account` 中，托管账号提供 `profile = {handle, displayName, country, status, followers, likes, worksCount}`。顶层 handle/displayName 同样使用最新同步的账号资料；syncedAt 是 EVA 最近同步账号信息的时间，不是 TikTok 数据更新时间。计数 null 表示未知，0 是实际零值；账号获赞数和作品数不能当作某条视频的指标。信息约每五分钟由后台同步，重复查询不会加快源数据采集。非托管账号没有 profile，账号对象为空或没有真实 handle 时不能宣称已绑定。工具名、入参与原 JSON 包装不变，不返回供应商账号 ID、云机编号或凭证。

## 普通视频发布

明确普通视频与挂车的选择。用户要求挂车时不能自动降级；省略 publishMode 的旧调用仍是挂车。

```text
get_publish_preview(contentItemId, tiktokAccountId, publishMode="ordinary")
→ 展示成片、版本、账号、文案、设置及 blockers
→ 用户认可成片并明确同意本次发布
approve_content_item(contentItemId, contentAssetId, explicitConfirm=true)
publish_video(contentItemId, tiktokAccountId, contentAssetId,
              publishMode="ordinary", title, tags,
              privacyLevel="PUBLIC_TO_EVERYONE", commercialDisclosure=false,
              explicitConfirm=true)
get_publish_job(publishJobId, tiktokAccountId)
```

ordinary 不传 productId 或 region。任何 blockers 都先处理，不能为了通过发布擅自改掉用户要求的设置。当前部分普通发布通道不能设置平台 AI 标记或商业披露；以预览为准，不宣称标记已设置，不将商业披露当作 AI 标记。

queued / running / reconciliationRequired 不能描述成已发布；结果待核对时继续查询原作业，不重复发片。任务成功而作品待关联时说明“发布执行完成，作品待关联”，不能猜作品 ID 或链接。

## 查询作品效果

`list_account_works(tiktokAccountId, page?, pageSize?)` 返回账号作品及播放、点赞、评论数、分享数。此列表可以包含其他入口发布、尚未关联如奕成片的作品；不能把候选作品的效果自动归给本条成片。

`list_published_videos` / `get_publish_job` 只在已确认关联时提供该如奕成片的效果。dataUpdatedAt 是数据源更新时间，syncedAt 是平台读取时间；授权失效或同步异常时说明可能停更。0 是有效数值，空值或空列表不能解释为没有播放。评论正文和回复不在本流程内。

## 找回发布任务与同步状态

`list_publish_jobs(contentItemId)` 返回最近 100 条任务（含处理中/失败），按账号和成片版本匹配。预检的 existingPublishJob 表示同版已有任务；排队、执行中或成功时不再次提交。publish_video 返回后按 retryAfterSeconds 查询 get_publish_job，不等待发布完成才响应用户。

任务与已发布列表返回 metricsStatus / metricsLastError / metricsSyncedAt（syncedAt 同义）。available 只是缓存可读；authorization_required / sync_error 时旧数据仍可用但可能停更；awaiting_association 不能自动猜测关联，not_supported 不能显示为零。Worker 最近 24 小时发过片的账号约每 5 分钟同步，其余约每 30 分钟；供应商数据更新时间可能更早，频繁查询不会加速采集。终态查询建议 300 秒，处理中建议 5 秒。只能展示评论数量，不读取正文或自动回复。
