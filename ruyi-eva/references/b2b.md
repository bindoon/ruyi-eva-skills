# B2B 账号与自动获客复刻

本流程仅在服务端 tools/list 含新增工具时可用。令牌属于当前用户和企业；客户端不能使用应用管理 Secret 或取得小九后台代持的 SK。外部客户端用户授权需要单独配置，工具存在不代表已经授权。

## 资料与素材

1. `list_units` → `get_unit` 读取真实资料；B2B 单元 `businessMode=b2b` 可无 persona，不要求国籍、出生日期、视觉锤或配方。不得虚构工厂资质、客户、产能。
2. 用户明确要新账号时用 `create_b2b_account`；修改用 `update_b2b_account`，缺项先补资料，再 `confirm_b2b_account`。不为 B2C 账号改模式，不混用 B2C 人物写入。
3. 六类图片 portrait/product/factory/logistics/customer_cooperation/company_document 均选填；有图才上传。`create_upload` → PUT 返回 URL → `complete_upload`（label、description 必填），再 `bind_account_references`。原件 customerAssetId 与账号 reference ID 不同，后续生成 assetIds 只用账号 reference ID。
4. `update_account_reference` 维护标签、描述、分类、顺序、隐藏；`set_b2b_account_avatar` 设独立账号头像，不改人物 face。用户图片缺失时告知，不在此流程自行生图补齐。

## 选片、报价与授权

5. `list_viral_videos` / `get_viral_video` 选平台已拆解公共模板；不是 `search_reference_videos` 的商品广场检索。已拆解模板不再 analyze，不产生重复拆解费用。
6. `quote_content({operation:"b2b_replicate",request:{unitId,viralVideoId,model,resolution,durationSeconds,...}})`，模型和分辨率按用户/已确认设置，不自行为了便宜降低规格。
7. 明确展示对外固定视频金额、Agent 创作区间、总区间和单位；`rangeIsCap=false` 不是硬封顶，报价未开通/未知必须说明，不编价格，也不透露内部成本。取得本次明确生成授权后才提交；询价、持有 SK、用户要脚本均不等于同意付费视频。
8. `create_b2b_replicate` 带相同业务参数、quoteId、稳定 idempotencyKey、authorizeAutoGeneration=true。报价过期或参数/素材变了要重新询价；结果不明只用原键原参数恢复，不能换键重复付费。

## 平台自动执行与轮询

9. 平台 Agent 写完整分镜、校验及生成。客户端不再 draft/save/confirm 一遍，不启动第二个创作 Agent，不生图，不改人脸，不走 B2C 配方。
10. 按返回 contentItemId 用 `get_content_task` 轮询，遵循 retryAfterSeconds。`runId` 不是视频终态标识；stage 成功但 billing pending 可先取片并说明费用未核定，不能把 null/零当免费。
11. 最终对外收费以 billing.state=settled 与 chargedAmount 为准；用 `get_video` 刷新签名链接取片。用户取消用 `cancel_content_task`，仍查询最终费用；already_submitted 不承诺立即停止/免费。
12. 生成授权不包含发布，发布仍按原独立明确确认流程，真实发布可用性以平台预检为准。

新增工具返回 structuredContent 或文本 JSON `{ok:true,data:...}`，错误 isError=true 且 `{ok:false,error:{code,message,retryable,requestId}}`。旧 list_units/get_unit/upload/get_video 保持原格式，不能强制所有工具都有 data。新工具缺失或协议错误时明确说明，不用源码、临时脚本或其它用户凭证绕过。
