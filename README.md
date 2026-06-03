# Claude Code Plugins

A collection of Claude Code plugins for development workflows.

## Plugins

### terraform-migration

Skills for migrating any Terraform provider from SDK v2 (`terraform-plugin-sdk/v2`) to the Plugin Framework (`terraform-plugin-framework`).

**Includes:**
- Step-by-step migration workflow for data sources and resources
- Complete code templates for both data sources and resources
- SDK v2 to Plugin Framework schema type mapping
- Lessons learned from real migrations (protocol v5 gotchas, `id` handling, etc.)

### repo-wiki

Skills for maintaining structured per-project wikis in [Outline](https://www.getoutline.com/). Compiles knowledge into persistent pages so future sessions don't re-derive it from code.

**Requires:** Outline MCP server configured in your Claude Code setup.

**Commands:**
- `/repo-wiki init` — bootstrap a wiki for a repo that has none
- `/repo-wiki sync` — update the wiki after recent commits
- `/repo-wiki lint` — fix stale facts and archive orphaned pages
- `/repo-wiki enrich` — deepen coverage with non-obvious details from code
- `/repo-wiki search <query>` — look something up in the wiki

## Installation

Add this marketplace to Claude Code (inside an interactive session):

```
/plugin marketplace add burythehammer/claude-code-plugins
```

Install a plugin:

```
/plugin install terraform-migration@burythehammer-claude-code-plugins
/plugin install repo-wiki@burythehammer-claude-code-plugins
```

For local development/testing:

```bash
claude --plugin-dir ./plugins/terraform-migration
claude --plugin-dir ./plugins/repo-wiki
```

## Usage

**terraform-migration:** The `migrate-to-plugin-framework` skill triggers automatically when you ask Claude to migrate a data source or resource. Example prompts:

- "Migrate the users data source to the plugin framework"
- "Convert resource_mycloud_database.go to the plugin framework"
- "SDK v2 to plugin framework migration for the regions data source"

**repo-wiki:** Use `/repo-wiki <command>` explicitly, or ask Claude to update/audit/search the project wiki.

## Licence

MIT
