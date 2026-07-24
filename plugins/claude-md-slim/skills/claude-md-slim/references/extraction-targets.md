# Extraction target mechanics

File conventions and exact syntax for each destination the audit can extract
to. Follow these when executing Phase 4.

## `.claude/rules/` files

One topic per file, kebab-case names describing the topic, not the source
section ("testing.md", "api-conventions.md", "git-workflow.md"). Subdirectories
are auto-discovered (`.claude/rules/frontend/react.md` works without
registration).

**Path-scoped** (loads only when Claude reads a file matching a glob):

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/api/**/*.test.ts"
---

# API Development Rules

- All endpoints must include input validation via the shared zod schemas
- Use the standard error envelope from src/api/errors.ts
```

**Unscoped** (no frontmatter — loads every session, like the root file but
organised by topic):

```markdown
# Git Workflow

- Branch names: <ticket>-<slug>, e.g. PROJ-123-fix-login
- Squash-merge only; the main branch history must stay linear
```

Choosing globs: derive them from what the section talks about, and make them
generous — a rule that fails to load is worse than one that loads slightly too
often. Verify each glob matches at least one real file, and **delete any glob
that matches nothing** — a zero-match glob is not "future-proofing", it is an
unverifiable line that suggests the whole frontmatter was never checked. If
the project later grows files in that location, the audit that notices them
can widen the glob then.

```bash
# e.g. for "src/api/**/*.ts"
find src/api -name "*.ts" | head -3
```

Do **not** add an `@import` for these files from the root CLAUDE.md — rules
files load automatically; importing them puts the content in context twice.

## Subdirectory `CLAUDE.md`

For monorepo content relevant only inside one package or app. Place the file
at that package's root (`apps/mobile/CLAUDE.md`); it loads when Claude works
in that subtree. Keep the same discipline there — a subdirectory file over
~100 lines deserves its own mini-audit.

## Convert a procedure to a skill

For EXTRACT → skill verdicts: multi-step procedures Claude executes on
request. Create `.claude/skills/<name>/SKILL.md` in the project:

```markdown
---
name: release
description: >-
  Cut a release of this project. Use when the user asks to release, publish,
  tag a version, or deploy to production.
---

# Release process

1. ...steps moved verbatim from CLAUDE.md...
```

Write the `description` to trigger on the phrases a user would actually say —
it is the only part loaded until the skill fires. Leave a one-line breadcrumb
in the root file only if discoverability matters ("releases: ask Claude to
'cut a release'").

## Recommend a hook (never write one unprompted)

For RECOMMEND → hook verdicts. Hooks in `.claude/settings.json` execute
arbitrary commands at lifecycle events, so the audit only *recommends* them in
the report — e.g. "the rule 'never push to main' could become a PreToolUse
hook blocking `git push origin main`". If the user asks you to implement one,
do it as a separate follow-up task with its own review. Until a hook exists,
the prose rule stays wherever it currently loads — do not delete a guard-rail
on the promise of future enforcement.

## `CLAUDE.local.md` (personal preferences)

For MOVE verdicts: preferences of one developer (editor choice, personal
aliases, "I prefer pnpm") found in the shared file. Move them to
`CLAUDE.local.md` next to the root CLAUDE.md and make sure it is gitignored
(`grep -q CLAUDE.local.md .gitignore || echo "CLAUDE.local.md" >> .gitignore`).
It still loads every session for that developer — the saving is for everyone
else on the team.

## `@import` from the root file

Only for content that genuinely must load every session but the user wants
factored out of the root file. Syntax — a bare `@path` on the line, path
relative to the importing file:

```markdown
# Commands
@docs/claude/commands.md
```

- Maximum import depth: 4 hops.
- Backticks make a path inert: `` `@docs/foo.md` `` is a mention, not an
  import. Use backticks whenever you *refer* to a file in prose.
- Do not point imports at `.claude/rules/` (double-loading) or at large
  generated files like `package.json` unless the user already does.

## On-demand docs (plain pointer)

For reference material Claude should read only when relevant, write a normal
file under `docs/` and mention it in the root with backticks and a cue for
when to read it:

```markdown
- Release process: see `docs/releasing.md` before cutting a release
```

## Knowledgebase offload (Outline)

Use only when Outline MCP tools (`mcp__outline__*`) are connected — never
invent document IDs or fake an upload. Applies to OFFLOAD verdicts: long-form
narrative (architecture history, runbooks, onboarding) that informs
occasionally but should never sit in context.

1. **Find the right home.** Search for an existing collection for this repo:
   `list_documents(query="<repo-name>")`. If the repo already has a wiki
   collection (e.g. one maintained by a repo-wiki skill), nest the document
   there. Otherwise ask the user which collection to use — creating
   collections unprompted litters the workspace.
2. **Create the document** with `create_document(title=..., text=...,
   parentDocumentId=... | collectionId=...)`. The title is a separate field —
   do not start the body with an H1; begin with prose or an H2.
3. **Link it from the root CLAUDE.md** as a plain markdown link with a cue:

   ```markdown
   - Architecture decision history: [Outline](https://outline.example.com/doc/…)
     — search Outline via MCP when historical context is needed
   ```

   Never use `@import` for external content.
4. **Report the URL** in the Phase 4 summary so the user can verify the upload
   before the original text is removed from CLAUDE.md.

If the upload fails or Outline is not connected, fall back to a `docs/` file
and say so — content must land somewhere durable before it leaves CLAUDE.md.
