# Claude Code Plugins

A collection of Claude Code plugins for Terraform provider development.

## Plugins

### terraform-migration

Skills for migrating any Terraform provider from SDK v2 (`terraform-plugin-sdk/v2`) to the Plugin Framework (`terraform-plugin-framework`).

**Includes:**
- Step-by-step migration workflow for data sources and resources
- Complete code templates for both data sources and resources
- SDK v2 to Plugin Framework schema type mapping
- Lessons learned from real migrations (protocol v5 gotchas, `id` handling, etc.)

## Installation

Add this marketplace to Claude Code (inside an interactive session):

```
/plugin marketplace add burythehammer/claude-code-plugins
```

Install the plugin:

```
/plugin install terraform-migration@burythehammer-claude-code-plugins
```

For local development/testing:

```bash
claude --plugin-dir ./plugins/terraform-migration
```

## Usage

The `migrate-to-plugin-framework` skill triggers automatically when you ask Claude to migrate a data source or resource. Example prompts:

- "Migrate the users data source to the plugin framework"
- "Convert resource_mycloud_database.go to the plugin framework"
- "SDK v2 to plugin framework migration for the regions data source"

## Licence

MIT
