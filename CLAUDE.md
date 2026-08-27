# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A Claude Code plugin marketplace. There is no build system, compiled code, or test suite — the "artifacts" are Markdown files that Claude Code loads as skills at runtime. See `README.md` for the current list of plugins.

## Testing Locally

To test a plugin without publishing:

```bash
claude --plugin-dir ./plugins/<name>
```

This loads the plugin directly from disk. Once inside the session, the skills are available and trigger on their description keywords.

## Repository Structure

```
.claude-plugin/marketplace.json          # Marketplace index — lists all plugins
plugins/<name>/
  .claude-plugin/plugin.json             # Plugin metadata (name, version, author)
  skills/<skill-name>/
    SKILL.md                             # The skill itself — loaded by Claude at runtime
    references/                          # Supporting reference docs cited from SKILL.md
```

## Adding a New Plugin

1. Create `plugins/<name>/.claude-plugin/plugin.json` with name, version, author, repository, license.
2. Add the plugin entry to `.claude-plugin/marketplace.json` under `plugins[]`, referencing `"source": "./plugins/<name>"`.
3. Create at least one skill under `plugins/<name>/skills/<skill-name>/SKILL.md`.

## Skill File Format (`SKILL.md`)

Skills begin with YAML frontmatter:

```yaml
---
name: skill-name-in-kebab-case
description: >-
  Trigger phrases and description of when to invoke this skill.
  Include the key keywords Claude should pattern-match on.
---
```

The body is freeform Markdown. It is given verbatim to Claude when the skill activates, so write it as instructions to the LLM — imperative, specific, with concrete code patterns and examples.

## Reference Files

Files under `references/` are supporting material cited by `SKILL.md` (e.g., code templates, mapping tables, gotchas). They are not automatically loaded — `SKILL.md` must explicitly point Claude to them. Keep each reference file focused on a single topic so `SKILL.md` can direct Claude with precision ("consult `references/gotchas.md` #3").

## Publishing

Install into a Claude Code session from the marketplace:

```
/plugin marketplace add burythehammer/claude-code-plugins
/plugin install <name>@burythehammer-claude-code-plugins
```

See `README.md` for the current plugin names.

## Agent skills

### Issue tracker

Issues live as GitHub issues on `burythehammer/claude-code-plugins` (via the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five canonical labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` + `docs/adr/` at the repo root, created lazily by `/domain-modeling` when needed. See `docs/agents/domain.md`.
