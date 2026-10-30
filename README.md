# 如奕 EVA Agent Skill

面向如奕出片 MCP 的通用 Agent Skill。支持已接入 `npx skills` 的 Agent 客户端。

分工：外部 Agent 负责定方向、写分镜和准备主体图（可以用客户端自带的生图能力，例如 Codex），如奕负责提供人设 / 素材 / 配方等事实、校验分镜、编译成片提示词并出片。MCP 还支持广场爆款导入与创意复刻、人设和绑定账号资源查询、如奕发布记录查询，营销账号领取与效果查询，以及用户明确确认后的普通视频 / TikTok Shop 挂车发布。Skill 里带了与平台内创作 Agent 同一套的创作规范（钩子、节奏、片型、分镜字段、主体图、口播合规），见 `ruyi-eva/references/`。

支持 B2B 经营账号创建、经营资料更新、PDF 目录资料与图片提取、六类真实参考图片绑定、独立账号头像和自动获客复刻，具体见 `ruyi-eva/references/b2b.md` 与 `b2b-catalog.md`。PDF 提取脚本需要本地 Python 的 pypdf、pypdfium2、Pillow；视频与账号接口仍以实际 MCP 工具为准。

支持 B2B 打品文档项目创建与恢复、结构化正文保存、正文来源、已有账号图片导入及项目确认，见 `ruyi-eva/references/b2b-projects.md`。需服务端实际提供对应工具；项目资料维护不启动视频或模型。

不支持：B2B 原创视频建稿、通用知识库写入、B2C 人物身份 / 世界 / 配方修改及 TK 账号授权。挂车沿用美国 / 新加坡通道，实际可用性取决于配置、授权与平台预检；模拟测试不代表真实发布已验收。缺 MCP 连接时先完成本地资料，不能当作服务端缺工具；新接口需对应服务端版本，使用前检查实际可用工具。

## 安装与更新

```bash
npx skills add bindoon/ruyi-eva-skills --skill ruyi-eva -g
npx skills update
```

`npx skills add` 会引导选择当前 CLI 支持的客户端。只安装到一个客户端时，可加 `--agent codex`、`--agent cursor` 或其他 [受支持的 Agent](https://skills.sh/) 标识。项目级安装可省略 `--global`。

之前手动安装的 `ruyi-cuber` 请先从客户端移除，再运行以上命令安装 `ruyi-eva`。之后用 `npx skills update` 获取该仓库最新版本。

## 配置如奕 MCP

MCP endpoint：`https://eva.ruyifuture.com/api/mcp`。生成 API 令牌后，在 Agent 客户端配置名为 `ruyi` 的 HTTP MCP server，设置 `Authorization: Bearer <RUYI_API_TOKEN>`。令牌请保存在客户端的安全配置或环境变量中。

Codex `~/.codex/config.toml`：

```toml
[mcp_servers.ruyi]
url = "https://eva.ruyifuture.com/api/mcp"
bearer_token_env_var = "RUYI_API_TOKEN"
```

Cursor `~/.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "ruyi": {
      "url": "https://eva.ruyifuture.com/api/mcp",
      "headers": {
        "Authorization": "Bearer ${RUYI_API_TOKEN}"
      }
    }
  }
}
```

WorkBuddy 使用 HTTP MCP，并加上 `"type": "http"`。其他客户端请参照其 MCP 配置格式。
