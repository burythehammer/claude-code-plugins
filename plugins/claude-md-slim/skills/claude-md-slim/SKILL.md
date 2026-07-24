---
name: claude-md-slim
description: >-
  Audit and slim down bloated CLAUDE.md files — and other overlong project
  markdown like READMEs — by applying progressive disclosure. Use whenever
  the user asks to audit, trim, shrink, slim, refactor, declutter,
  restructure, or optimise a CLAUDE.md (or AGENTS.md / project memory) file,
  says their CLAUDE.md or README is too long or bloated, mentions context
  bloat or token waste from project instructions, wants rules moved into
  .claude/rules/ or subdirectory CLAUDE.md files, wants long docs split into
  linked pages, or asks about @imports or progressive disclosure — even if
  they don't name the file explicitly (e.g. "my project instructions are
  getting out of hand").
---

# CLAUDE.md Slim

Every line of a root CLAUDE.md is loaded into context in **every session** in
that project. Past roughly 200 lines, context usage climbs and instruction
adherence measurably drops — the important rules drown in the noise. The fix
is not to delete knowledge but to move each piece to the place where it loads
only when actually needed. This skill audits a CLAUDE.md, classifies every
section, then restructures the file with the user's approval.

The workflow is **audit → confirm → apply**. Restructuring deletes and moves
content, so never apply changes without showing the report first — unless the
user has explicitly told you to proceed without confirmation ("just do it",
"apply without asking"), in which case run all phases in one pass and show the
summary at the end.

## The loading model (why each destination exists)

Every extraction decision follows from *when* each location is loaded:

| Location | Loaded | Use for |
|---|---|---|
| Root `CLAUDE.md` | Every session, always | Short, universal, project-specific rules and pitfalls |
| `@path/to/file.md` import | Every session, eagerly at launch | Organisation only — splits the file but saves **zero** tokens |
| `.claude/rules/*.md` (no `paths:`) | Every session, automatically | Universal rules grouped by topic |
| `.claude/rules/*.md` (with `paths:` globs) | Only when Claude reads a matching file | Rules for one file type or area — the real progressive disclosure |
| Subdirectory `CLAUDE.md` | Only when working in that subtree | Monorepo package/app-specific instructions |
| Skill (`.claude/skills/<name>/SKILL.md`) | Only when invoked | Multi-step procedures Claude executes: releases, migrations, scaffolding recipes |
| Hook (`.claude/settings.json`) | Never loaded as prose — enforced at lifecycle events | Hard must/never rules; enforcement beats reminders |
| `CLAUDE.local.md` / auto-memory | Every session, but personal and gitignored | Individual preferences that don't belong in the shared file |
| Plain doc + backticked mention | Only when Claude chooses to read it | Reference material needed occasionally |
| Knowledgebase (Outline) | On demand via MCP search | Long-form background: architecture history, onboarding narrative |

Two consequences worth internalising:

- **@imports are for maintainability, not token savings.** Imported files are
  expanded at launch. Use them when the user wants the root file readable and
  modular; use `paths:`-scoped rules or subdirectory files when the goal is a
  smaller context footprint.
- **Deletion is the only zero-cost win.** Rules that restate what the model
  already knows (framework conventions, generic best practice) cost context
  every session and add nothing. Delete them outright rather than relocating
  the bloat.

## Phase 1 — Scan

1. Locate the target. Default to `./CLAUDE.md` in the project root; also
   discover subdirectory `CLAUDE.md` files and existing `.claude/rules/`
   content so the audit sees the whole memory surface:
   ```bash
   find . -name "CLAUDE.md" -not -path "*/node_modules/*" -not -path "*/.git/*"
   ls .claude/rules/ 2>/dev/null
   ```
2. Run the bundled inventory script to get a per-section line count:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/claude-md-slim/scripts/scan.py" CLAUDE.md
   ```
   It prints each heading with its line count, flags sections over 30 lines,
   and reports the total.
3. Apply the threshold: a file **over 200 lines** gets the full audit. A file
   under 200 lines is healthy — say so, point out any obviously deletable
   common-knowledge rules if present, and stop unless the user asks for more.

## Phase 2 — Classify every section

Read the file and assign each section (and any oversized paragraph within a
section) exactly one verdict. Consult
`references/common-knowledge.md` for the deletion criteria and worked examples,
and `references/extraction-targets.md` for the mechanics of each destination.

Route each surviving section by asking, in order: *Is it a must/never rule
that could be mechanically enforced?* (→ hook) *Is it a multi-step procedure
Claude executes on request?* (→ skill) *Does it apply only to certain files?*
(→ path-scoped rule) *Is it one person's preference?* (→ `CLAUDE.local.md`)
*Only relevant in one subtree?* (→ subdirectory `CLAUDE.md`) Only what falls
through every question stays in the root file.

| Verdict | Criteria |
|---|---|
| **KEEP** | Project-specific, non-derivable, needed in most sessions, short. Pitfalls, invariants, house conventions, "never do X" rules. |
| **DELETE — common knowledge** | Restates what any competent model already knows: framework idioms, generic best practice, standard tool usage. |
| **DELETE — derivable** | Restates what Claude can read from the repo itself: directory listings, dependency lists mirroring `package.json`, boilerplate descriptions. |
| **EXTRACT → `.claude/rules/<topic>.md` with `paths:`** | Applies only to certain files or directories (test rules, API rules, frontend rules). |
| **EXTRACT → `.claude/rules/<topic>.md` no `paths:`** | Universal but a distinct topic that deserves its own file (git conventions, security policy). |
| **EXTRACT → subdirectory `CLAUDE.md`** | Only relevant when working inside one package/app of a monorepo. |
| **EXTRACT → skill** | A multi-step procedure or runbook Claude executes on request (release process, adding an endpoint, data migration). Becomes `.claude/skills/<name>/SKILL.md`, costing nothing until invoked. |
| **RECOMMEND → hook** | A must/never rule that tooling could enforce (block pushes to main, run formatter after writes). Do not write hooks yourself — list the recommendation in the report; hooks execute code and the user must own them. Keep the rule in place until a hook exists. |
| **MOVE → `CLAUDE.local.md`** | Personal preference or machine-local detail sitting in the shared file. |
| **EXTRACT → doc + `@import`** | Must load every session but the user wants the root file modular (e.g. shared command reference). Use sparingly — no token saving. |
| **OFFLOAD → knowledgebase** | Long-form narrative that informs occasionally but is never *executed*: architecture decision history, onboarding guides, incident post-mortems. (Executable runbooks are skills, not knowledgebase docs.) |

Safety overrides, regardless of classification:

- **Never delete security or permissions content** (secret-handling rules,
  files-never-to-read lists, deny policies), even when it reads like common
  knowledge. Downgrade at most to EXTRACT without `paths:` so it still loads
  every session.
- When genuinely unsure whether a rule is common knowledge or a hard-won
  project lesson, prefer KEEP or EXTRACT over DELETE and flag it as a
  question for the user in the report. The user wrote these lines for a
  reason you may not see.

## Phase 3 — Report and confirm

Present the audit with this exact structure:

```markdown
# CLAUDE.md Audit: <path>

**Current size:** N lines (~T tokens every session) → **projected root size:** ~M lines

## Verdicts
| Section | Lines | Verdict | Destination / reason |
|---|---|---|---|

## Content to be deleted
<quote each deleted rule in full — the user must see exactly what disappears>

## Proposed new layout
<file tree of the files to be created, with one-line descriptions>

## Questions
<sections you were unsure about, with your lean>
```

Then wait. Apply the user's per-section overrides — they may rescue a rule you
marked for deletion or push a KEEP out to a rules file. Do not proceed to
Phase 4 until they approve.

## Phase 4 — Apply

Work from the approved report only. Before touching anything, note
`git status` for the affected files so everything is revertible; if the
working tree has unrelated uncommitted changes to CLAUDE.md, warn first.

1. **Create the extracted files.** Move content **verbatim** — resist the urge
   to rewrite while relocating; the user's phrasing and emphasis carry intent.
   Only adjust heading levels and add the `paths:` frontmatter where the
   verdict calls for it. Follow the file conventions in
   `references/extraction-targets.md`.
2. **Offload to the knowledgebase, if configured.** Check whether Outline MCP
   tools (`mcp__outline__*`) are available. If yes, follow the Outline section
   of `references/extraction-targets.md`; leave a plain link in the root file.
   If no knowledgebase is connected, fall back to `docs/` files with backticked
   mentions and tell the user why.
3. **Rewrite the root CLAUDE.md.** Keep the KEEP sections, inject `@path`
   imports only for EXTRACT→import verdicts, and add a short pointer list for
   on-demand material. Do **not** add `@imports` for `.claude/rules/` files —
   they load automatically, and importing them loads the content twice.
4. **Verify** before reporting done:
   - Re-run `scan.py` on the new root file and confirm the projected size.
   - Every line of the original is accounted for: either present in the new
     root, present in an extracted file, or listed under "Content to be
     deleted" in the approved report. Nothing may vanish silently.
   - Every `@import` path and every `paths:` glob resolves to something that
     exists (`ls` each referenced path; test one representative file against
     each glob). Remove any glob that matches zero files — do not leave
     speculative patterns for files the project doesn't have.
5. Show a summary: old size → new size, files created, rules deleted, and the
   command to revert (`git checkout -- <files>` / `git clean` for new files —
   or if the tree was dirty, where the backup copy went).

## Generic long documents (README, docs pages)

The same audit → confirm → apply method works for other overlong markdown —
README.md, CONTRIBUTING.md, handbook pages — with one fundamental difference:
those files never load into Claude's context, so the loading-model table and
the token arithmetic do not apply. The goal shifts from context footprint to
reader navigation:

- Scan and classify the same way (`scan.py` works on any markdown file).
- The root document keeps what a first-time reader needs: what this is, how
  to get started, and pointers. Long reference sections move to their own
  pages under `docs/` with ordinary markdown links; add a table of contents
  if the trimmed file is still long.
- Delete verdicts still apply — stale sections and content duplicated from
  elsewhere — but "common knowledge" is judged for the human reader, not for
  the model.
- Never use `@imports` or `.claude/rules/` here; those are memory-file
  mechanisms. Plain links are the right tool.
- The safety rules hold unchanged: report first, quote every deletion,
  nothing vanishes silently.

## Gotchas

- `@import` paths resolve **relative to the file containing the import**, not
  the CWD. Imports nest at most 4 hops deep.
- To *mention* a path without importing it, wrap it in backticks:
  `` `@docs/foo.md` `` is inert; a bare `@docs/foo.md` imports.
- Rules in subdirectories of `.claude/rules/` are discovered automatically —
  `.claude/rules/frontend/react.md` needs no registration.
- `paths:` globs match when Claude **reads** a matching file. Rules that must
  hold before any file is read (e.g. "never run X") belong in the root file or
  an unscoped rules file.
- A user-level `~/.claude/CLAUDE.md` may duplicate project rules; if you spot
  overlap, mention it in the report but never edit user-level files without
  being asked.
