# MCP

## 什么是 MCP

**MCP（Model Context Protocol）** 是一个开放协议，让 AI 编程工具以标准化方式连接外部工具与数据源。如果说 [Skill](./skill) 告诉AI一套标准「怎么写代码」，MCP 则给 AI 装上「手和眼」——查数据库、调接口、读文档，让 AI 不仅能生成代码，还能实际验证和操作。



### 核心概念

| 概念 | 说明 |
|------|------|
| **MCP Server** | 独立运行的服务进程，向 AI 暴露特定能力（如查询数据库、调用 HTTP 接口） |
| **MCP Client** | AI 编程工具侧的协议实现，负责发现并调用 MCP Server 提供的工具 |
| **Tool** | MCP Server 注册的具体能力单元，AI 可以像调用函数一样使用 |
| **Resource** | MCP Server 向 AI 暴露的数据源（如数据库表结构、API 文档） |

### 典型应用场景

| 场景 | 推荐的 MCP Server |
|------|-------------------|
| 验证生成的表结构与数据 | MySQL / PostgreSQL MCP |
| 验证生成的页面效果 | Playwright MCP（浏览器自动化） |
| 让 AI 读取 API 文档生成前端代码 | **Apifox MCP Server**（推荐） |



## 推荐工具：Apifox MCP Server



### 为什么推荐 Apifox？

在前后端协作中，后端开发者在 Apifox 中维护 API 文档，前端开发者需要根据 API 文档编写调用代码。**Apifox MCP Server** 可以将 Apifox 的接口文档直接提供给 AI 编程工具，让 AI 直接获取真实的接口信息



![mcp](https://picgocloud.com/m/c792c7fb-765b-49dc-a37f-5070ebcc0d3a.png)



### 核心优势

- **降低前后端协同成本**：后端团队在 Apifox 中正常维护 API，前端 AI 工具自动获取最新文档
- **支持多种数据源**：Apifox 项目文档、公开发布的文档、本地 OpenAPI/Swagger 文件均可



## 配置 Apifox MCP



官方链接： https://docs.apifox.com/apifox-mcp-server

### 前置条件

- Node.js >= 18
- 一个支持 MCP 的 AI 编程工具（Qoder / Codex / Trae / Cursor）
- Apifox 工具



### 方式一：通过 Apifox 项目 ID（推荐团队协作）

适用于读取团队内部的 API 文档，需要 Apifox 个人访问令牌。

**获取项目 ID 和令牌：**
1. 在 Apifox 中打开项目 → 项目设置 → 获取项目 ID
2. 个人设置 → 个人访问令牌 → 生成新令牌

**在 AI 工具中配置 MCP Server：**

```json
{
  "mcpServers": {
    "apifox": {
      "command": "npx",
      "args": [
        "-y",
        "apifox-mcp-server",
        "--project-id=你的项目ID",
        "--access-token=你的个人访问令牌"
      ]
    }
  }
}
```



### 方式二：通过 OpenAPI/Swagger 文件（推荐 FastBrace 项目）

FastBrace 基于 FastAPI 自动生成 OpenAPI 文档，可以直接将 Swagger JSON 提供给 Apifox MCP：

```json
{
  "mcpServers": {
    "apifox": {
      "command": "npx",
      "args": [
        "-y",
        "apifox-mcp-server",
        "--openapi-url=http://localhost:8000/openapi.json"
      ]
    }
  }
}
```

> 启动 FastBrace API 服务后（`python main.py server api`），访问 `/openapi.json` 即可获取完整的 OpenAPI 文档。





## 在各 AI 工具中配置 MCP



### codex

1. 进入插件 --->  MCP, 找到mcp服务, 参考配置信息完善

![截屏2026-08-31 18.08.24](https://picgocloud.com/m/4cde1ed2-384a-4a61-a9ed-66f32fc8e37c.png)



### Qoder

1. 找到工具右上角设置  mcp服务，填写以下配置

```
{
  "mcpServers": {
    "FastBrace": {
      "command": "npx",
      "args": [
        "-y",
        "apifox-mcp-server@latest",
        "--project=【写入项目ID】"
      ],
      "env": {
        "APIFOX_ACCESS_TOKEN": "【写入token信息】"
      }
    }
  }
}

```





## 其他常用 MCP Server



参考社区广场： https://modelscope.cn/mcp



## 与 Skill 的分工

| 维度 | Skill | MCP |
|------|-------|-----|
| 提供 | 项目规范、分层约定、工作流程 | 外部能力：数据库、HTTP、API 文档 |
| 形态 | 仓库内的 Markdown 文档 | 独立进程的工具协议 |
| 解决 | AI 写出的代码**规范不跑偏、长期可维护** | AI 能调用外部工具，实现更多功能 |



## 下一步

- 了解 Skill 如何约束 AI 代码生成：[Skill](./skill)
