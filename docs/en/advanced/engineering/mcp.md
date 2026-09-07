# MCP

## What is MCP

**MCP (Model Context Protocol)** is an open protocol that lets AI coding tools connect to external tools and data sources in a standardized way. If [Skill](./skill) teaches the AI a set of standards for "how to write code", MCP gives the AI "hands and eyes" — querying databases, calling APIs, reading documentation — so the AI can not only generate code, but also actually verify and operate.

### Core Concepts

| Concept | Description |
|------|------|
| **MCP Server** | An independently running service process that exposes specific capabilities to the AI (e.g. querying a database, calling HTTP APIs) |
| **MCP Client** | The protocol implementation on the AI coding tool side, responsible for discovering and calling the tools provided by MCP Servers |
| **Tool** | A concrete capability unit registered by an MCP Server, which the AI can use like a function |
| **Resource** | A data source exposed to the AI by an MCP Server (e.g. database schema, API documentation) |

### Typical Use Cases

| Scenario | Recommended MCP Server |
|------|-------------------|
| Validate generated table structures and data | MySQL / PostgreSQL MCP |
| Validate generated page effects | Playwright MCP (browser automation) |
| Let the AI read API docs to generate frontend code | **Apifox MCP Server** (recommended) |

## Recommended Tool: Apifox MCP Server

### Why Apifox?

In frontend-backend collaboration, backend developers maintain API documentation in Apifox, and frontend developers need to write calling code based on it. **Apifox MCP Server** feeds the Apifox API documentation directly to AI coding tools, so the AI can get real interface information.

![mcp](https://picgocloud.com/m/c792c7fb-765b-49dc-a37f-5070ebcc0d3a.png)

### Key Benefits

- **Lower frontend-backend collaboration cost**: the backend team maintains APIs in Apifox as usual, while frontend AI tools automatically get the latest documentation
- **Multiple data sources**: Apifox project docs, publicly published docs, and local OpenAPI/Swagger files are all supported

## Configuring Apifox MCP

Official link: https://docs.apifox.com/apifox-mcp-server

### Prerequisites

- Node.js >= 18
- An AI coding tool that supports MCP (Qoder / Codex / Trae / Cursor)
- The Apifox tool

### Option 1: Via Apifox Project ID (recommended for team collaboration)

For reading team-internal API documentation; requires an Apifox personal access token.

**Get the project ID and token:**
1. Open the project in Apifox → Project Settings → get the project ID
2. Personal Settings → Personal Access Tokens → generate a new token

**Configure the MCP Server in your AI tool:**

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

### Option 2: Via an OpenAPI/Swagger file (recommended for FastBrace projects)

FastBrace automatically generates OpenAPI documentation based on FastAPI; you can feed the Swagger JSON directly to the Apifox MCP:

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

> After starting the FastBrace API service (`python main.py server api`), visit `/openapi.json` to get the full OpenAPI documentation.

## Configure MCP in AI Tools

### codex

1. Go to Plugins ---> MCP, find the MCP service, and fill in the configuration accordingly

![Screenshot 2026-08-31 18.08.24](https://picgocloud.com/m/4cde1ed2-384a-4a61-a9ed-66f32fc8e37c.png)

### Qoder

1. Open the settings at the top right of the tool, find MCP services, and fill in the following configuration

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

## Other Common MCP Servers

See the community hub: https://modelscope.cn/mcp

## Skill vs MCP

| Dimension | Skill | MCP |
|------|-------|-----|
| What it provides | Project conventions, layering rules, workflows | External capabilities: databases, HTTP, API docs |
| Form | Markdown documents in the repository | Tool protocol in an independent process |
| What it solves | AI-generated code stays **convention-compliant and maintainable long term** | The AI can call external tools to achieve more |

## Next Steps

- Learn how Skill constrains AI code generation: [Skill](./skill)