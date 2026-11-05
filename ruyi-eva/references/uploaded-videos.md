# 自有视频上传与发布

用户已经有成片，只借如奕通道发布时使用。先 tools/list 检查 create_simple_unit、confirm_simple_unit、complete_uploaded_video 以及既有上传/发布工具。连接使用当前企业自己的成员 SK，不使用小九代持 SK 或应用管理 Secret；凭证仅留服务端/内存。工具存在不代表独立 OAuth 已交付。

1. list_units / get_unit 找已有经营单元。简版和完整版都可用。没有时用 create_simple_unit 创建简版草稿：调用方生成稳定 unitId UUID，重试同 ID 不另建。补齐名称、市场、语言、经营描述等实际确认缺项，可用 update_simple_unit 修改，再 confirm_simple_unit；不虚构人物、配方或业务资料。
2. 账号领取、授权、绑定与解绑请用户前往返回的 platformUrl 操作，本流程不代办；没有账号可先上传保存。账号归经营单元，不要求创建人物。
3. create_upload({kind:"publish_video",unitId,contentType:"video/mp4",filename}) → 对 putUrl 使用返回 headers PUT 二进制，不向 OSS 发送 SK → complete_uploaded_video({uploadId,idempotencyKey,title,caption,tags,aiSource})。
4. 文件最大200MB，MP4、H.264视频、可选AAC音频、3–600秒、宽高360–4096。实际时长由服务器读取，不沿用生成模型或参考拆解的60秒上限。aiSource true/false/null分别表示包含AI/非AI/未声明，不从“上传”推断非AI。同请求键和参数重试找回原内容，改参数用新键。新工具 structuredContent 为 ok/data 或 ok/error，既有工具保留原格式。
5. 新视频是 ready / pending，上传不等于审核或发布；不写分镜、不拆解、不生图或生视频、不收生成费用。get_publish_preview({contentItemId,publishMode:"ordinary"}) 可省略账号ID，读取当前绑定账号；缺账号返回平台操作链接。展示实际成片、目标账号、发布文案/标签与设置。
6. 用户认可具体版本且明确同意发布后，approve_content_item({contentItemId,contentAssetId,explicitConfirm:true}) → publish_video({contentItemId,tiktokAccountId,contentAssetId,publishMode:"ordinary",title,tags,privacyLevel,commercialDisclosure,explicitConfirm:true})。普通视频不传productId/region；设置以预览和用户确认事实为准。绑定变化、版本变化或通道阻塞先解决，不能自动换号、换通道或去掉声明。
7. 保存publishJobId，按get_publish_job查询原任务。queued/running/结果待核对不重发；执行成功、作品已关联、统计已同步分开报告。videoUrl或统计为空不猜补。其它查询复用list_publish_jobs/list_published_videos/list_account_works。

上传来源与AI属性独立；通道不能满足所需AI标记或商业披露时明确说明阻塞，不冒充已设置。两种账号通道分别验收，不把本地模拟或上传成功称为真实TikTok发布验收。
