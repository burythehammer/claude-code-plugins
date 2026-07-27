# Claude Code Plugins

A [Claude Code](https://claude.com/claude-code) plugin marketplace with skills for Terraform provider development, project wiki maintenance, and CLAUDE.md housekeeping.

Each plugin is a set of Markdown skills that Claude Code loads at runtime — there is no build step or compiled code. Plugins also ship manifests for Codex, Cursor, and Gemini CLI, so the same skills can be used across tools.

## Plugins

| Plugin | Description |
| ------ | ----------- |
| [terraform-migration](#terraform-migration) | Migrate Terraform providers from SDK v2 to the Plugin Framework |
| [repo-wiki](#repo-wiki) | Maintain structured per-project wikis in Outline |
| [claude-md-slim](#claude-md-slim) | Audit and slim down bloated CLAUDE.md files with progressive disclosure |

### terraform-migration

Migrates Terraform provider data sources and resources from [`terraform-plugin-sdk/v2`](https://github.com/hashicorp/terraform-plugin-sdk) to the [`terraform-plugin-framework`](https://github.com/hashicorp/terraform-plugin-framework), following patterns already established in the target codebase.

- Discovery-first workflow: inspects the provider's existing framework code before writing any
- Complete code templates for data sources and resources
- SDK v2 to Plugin Framework schema type mapping
- Gotchas learned from real migrations (protocol v5 block constraint, `id` handling, muxed servers)

The skill triggers automatically on prompts like:

- "Migrate the users data source to the plugin framework"
- "Convert resource_mycloud_database.go to the plugin framework"
- "SDK v2 to plugin framework migration for the regions data source"

### repo-wiki

Maintains a structured wiki per code project in [Outline](https://www.getoutline.com/), compiling knowledge into persistent pages so future sessions don't re-derive it from code.

| Command | Purpose |
| ------- | ------- |
| `/repo-wiki init` | Bootstrap a wiki for a repo that has none |
| `/repo-wiki sync` | Update the wiki after recent commits |
| `/repo-wiki lint` | Fix stale facts and archive orphaned pages |
| `/repo-wiki enrich` | Deepen coverage with non-obvious details from code |
| `/repo-wiki search <query>` | Look something up in the wiki |

> [!IMPORTANT]
> Requires an Outline MCP server configured in your Claude Code setup. Without it, wiki commands will refuse to run rather than fall back to local files.

### claude-md-slim

Audits bloated `CLAUDE.md` files and restructures them with progressive disclosure, so instructions load only when they're actually needed.

- Deletes common-knowledge rules the model already follows
- Extracts sections into path-scoped `.claude/rules/` files and subdirectory `CLAUDE.md` files
- Injects `@imports` for readability where splitting helps maintainability
- Offloads long-form docs to Outline when an MCP server is configured

The workflow is **audit → confirm → apply**: it always shows a report of proposed changes before touching the file. Triggers on prompts like "my CLAUDE.md is too long", "slim down the project instructions", or "audit CLAUDE.md for context bloat".

## Installation

Add the marketplace inside an interactive Claude Code session:

```text
/plugin marketplace add burythehammer/claude-code-plugins
```

Then install the plugins you want:

```text
/plugin install terraform-migration@burythehammer-claude-code-plugins
/plugin install repo-wiki@burythehammer-claude-code-plugins
/plugin install claude-md-slim@burythehammer-claude-code-plugins
```

## Local development

Test a plugin without publishing by loading it directly from disk:

```bash
claude --plugin-dir ./plugins/terraform-migration
```

Once inside the session, the plugin's skills are available and trigger on their description keywords.

## Repository structure

```text
.claude-plugin/marketplace.json          # Marketplace index — lists all plugins
plugins/<name>/
  .claude-plugin/plugin.json             # Plugin metadata (name, version, author)
  .codex-plugin/plugin.json              # Cross-tool manifest for Codex
  .cursor-plugin/plugin.json             # Cross-tool manifest for Cursor
  gemini-extension.json                  # Cross-tool manifest for Gemini CLI
  skills/<skill-name>/
    SKILL.md                             # The skill itself — loaded by Claude at runtime
    references/                          # Supporting reference docs cited from SKILL.md
```

See [CLAUDE.md](CLAUDE.md) for details on adding a new plugin and the `SKILL.md` file format.
