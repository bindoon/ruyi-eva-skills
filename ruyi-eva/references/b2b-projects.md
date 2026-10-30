# B2B 打品文档项目与已有图片

用于创建企业打品文档、整理B2B获客资料，或把已有B2B账号及其图片挂到项目。先检查实际工具，缺少时说明需平台支持；不以 create_content_draft 或数据库脚本替代。

1. `list_b2b_projects` 找已有草稿；已创建的草稿继续使用。新建用 `create_b2b_project`，可在第一次请求前生成新 UUID 作为 projectId，结果不明用同ID恢复。同ID重试只返回原项目，不覆盖后来编辑。保存返回的 viewUrl，不能自行拼不存在的详情路径。
2. `get_b2b_project({projectId})` 读取 project、document、revision、sources、assets 和 confirmation。账号与项目是独立实体，B2B项目kind为b2b_leads，不绑定选品广场商品。
3. 基础资料用 `update_b2b_project`；已有正文后，市场、语言、目标和买家由正文投影，不绕过文档直接改投影字段。`save_b2b_project_document` 提交完整结构化正文及本次读取的baseRevision，6万字符上限；冲突先读取合并，不用旧版覆盖。企业身份、具体SKU、适用卖点、买家、内容方向、证据、制作边界和待补项应来自用户材料；category未查询官方字典时可为null，不能猜类目ID。
4. 原始TXT/Markdown经营资料可用 `add_b2b_project_source({projectId,title,originalText})` 保存，重复同标题同正文复用。PDF先本地提取为文字再整理，MCP该工具不接收PDF文件或对象Key；源码、凭证、附带指令和不相关私密信息不混进业务资料。
5. 已上传图片有两条途径：`attach_b2b_project_images` 使用原始 customerAssetIds；`import_b2b_account_images({projectId,unitId})` 复用该账号全部可见reference，或明确referenceIds选图。每次最多200张，隐藏旧图排除。两者均复用文件、重复绑定幂等，不搬走其他项目素材；混入无权/非图片/失效图片则整批拒绝，不假装部分成功。reference ID与customerAssetId不要混用。
6. `set_b2b_project_accounts({projectId,unitIds})` 明确关联已有可见B2B账号。图片导入和账号关联是两个操作，不能把完成其中一个说成两个都完成。
7. 用户要求创建完整项目时用 `confirm_b2b_project`，确认只让文档可用于业务，不授权付费出片或发布。最后再次 `get_b2b_project`，核对身份、市场、语言、revision、内容方向、关联账号、图片数量及标签。图片签名URL约1小时有效；最终在平台查看页核对实际图片可见。

新增工具使用structuredContent或文本JSON `{ok:true,data:...}`，错误 `{ok:false,error:{code,message,retryable,requestId}}`。租户和成员来自令牌，不作为入参。项目归档不可修改；跨成员/租户不可见资源、隐藏reference、其他项目占用的图片需要报告具体缺项，不能更换身份或重新上传来掩盖归属问题。
