# Skill

## What is a Skill

A **Skill** is a **reusable instruction set** for AI coding tools, stored as Markdown files. It tells the AI "how to write code in a specific project" — including project conventions, layering rules, naming standards, workflows, and acceptance criteria.

When you develop with AI coding tools such as **Codex, ClaudeCode, WorkBuddy, Qoder, Trae**, the AI automatically loads the constraints defined in the Skill, so the generated code naturally conforms to the project's architecture style and engineering standards — no need to describe the project context manually every time.

### Core Idea

```
Traditional way: every conversation repeats project structure, naming rules, layering conventions...
Skill way:       write once → all AI tools follow automatically
```

The essence of a Skill is **standardized accumulation of project knowledge**:
- **Task-oriented**: each Skill solves one specific category of problems (the current FastBrace focuses on engineering-oriented backend module development)
- **Standardized process**: a Skill defines clear execution steps and acceptance criteria
- **Reusable**: defined once, reused across sessions and tools — not limited to any single AI coding tool
- **Loaded on demand**: business details live in the `references/` subdirectory; the AI loads them progressively as tasks require, avoiding context overflow and reducing token consumption

## FastBrace Skill Directory

FastBrace ships a complete Skill file system in the project root:

```
skills/
├── SKILL.md                          # Skill entry document (read by the AI first)
└── references/                       # Reference material loaded on demand
    ├── project.md                    # Tech stack, DDD layering, directory conventions, naming rules
    ├── code-style.md                 # Code style, thinking principles, logging conventions
    ├── modules.md                    # Business module implementation order and layer responsibilities
    ├── file-resource.md              # File/resource handling conventions
    ├── permission.md                 # Permission system conventions
    ├── scripts.md                    # Maintenance script conventions
    └── version-iter-template.md      # Version iteration note template
```

**`SKILL.md`** is the core entry file. It tells the AI how to write code that conforms to the project conventions, and how to validate and deliver the result.

The **`references/`** directory holds business detail documents that the AI loads progressively as tasks require:

| Document | Responsibility |
|------|------|
| `project.md` | Tech stack, layering, directories, naming, file headers, and SQL conventions |
| `code-style.md` | Thinking, simplification, precise-change and logging principles (inspired by: https://github.com/multica-ai/andrej-karpathy-skills) |
| `modules.md` | Business module implementation order and layer responsibilities |
| `file-resource.md` | File and resource handling |
| `permission.md` | Permission system |
| `scripts.md` | Maintenance scripts |
| `version-iter-template.md` | Version iteration note template |

## Integrate into AI Coding Tools

### Codex

**How to configure:**

1. Codex has a built-in skill-creation capability. After downloading FastBrace and opening the project, reference the skill in the project directory, then enter the prompt below (as shown in the screenshot)

   ```
   Please fully reference the contents under skills to generate the FastBrace skill, and display the image above as the logo
   ```

   ![Screenshot 2026-08-31 17.48.40](https://picgocloud.com/m/fcc0d7b2-aa3e-42d8-8813-b002e3110903.png)

2. After the skill is created, you can find the plugin in the left sidebar, then locate the created skill in the skills section
3. You can then reference the skill in any specific project

⚠️: Since Codex supports displaying a skill logo, the prompt above includes the logo image. Normally, a skill can be generated without uploading a logo image.

### Qoder

Qoder natively supports project-level Skill discovery. Place the Skill files under `.agent/skills/` in the project root and they will be detected automatically. If they are not detected, upload the skills folder to the project.

### Trae

Trae natively supports project-level Skill discovery. Place the Skill files under `.agent/skills/` in the project root and they will be detected automatically.

## Next Steps

- Learn how MCP extends AI tool capabilities: [MCP](./mcp)