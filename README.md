# 如奕 EVA Agent Skill

面向如奕出片 MCP 的通用 Agent Skill。支持已接入 `npx skills` 的 Agent 客户端。

分工：外部 Agent 负责定方向、写分镜和准备主体图（可以用客户端自带的生图能力，例如 Codex），如奕负责提供人设 / 素材 / 配方等事实、校验分镜、编译成片提示词并出片。Skill 里带了与平台内创作 Agent 同一套的创作规范（钩子、节奏、片型、分镜字段、主体图、口播合规），见 `ruyi-eva/references/`。

不支持：B2B 获客与打品项目建稿、知识库检索、修改人设 / 单元 / 配方、发布。这些请在如奕平台内完成。

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
