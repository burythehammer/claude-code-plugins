---
name: repo-wiki
description: Use when the user invokes /repo-wiki, asks to update, audit, search, or deepen a project's Outline wiki, or when a wiki may have stale facts, orphaned pages, or sparse documentation.
---

# Repo Wiki

Structured wikis in Outline — one per code project. Compile knowledge into persistent pages rather than re-deriving it from code each session.

## Quick Reference

| Situation | Command |
|-----------|---------|
| No wiki yet | `/repo-wiki init` |
| Behind recent commits | `/repo-wiki sync` |
| May have stale/wrong facts or orphaned pages | `/repo-wiki lint` |
| Accurate but sparse | `/repo-wiki enrich` |
| Looking something up | `/repo-wiki search <query>` |

**Universal first step — resolve IDs for the current repo:**
1. **Local memory (fast path):** Read `~/.claude/projects/<encoded-cwd>/memory/repo-wiki.md` where `<encoded-cwd>` is the CWD with every `/` replaced by `-` (e.g. `/home/alice/workspace/myapp` → `-home-alice-workspace-myapp`). If found, extract **Parent doc ID** and **Collection ID** and proceed.
2. **Outline search (fallback):** Search Outline with `list_documents(query="<repo-name>")` to find a matching wiki root document.
3. **Neither found:** offer to run `/repo-wiki init`.

Never rely on a remembered version.

**Command ordering:** Run `lint` before `enrich` — enriching stale content embeds errors deeper.

## Outline tool reference

| Task | Tool |
|------|------|
| Search for a document | `list_documents(query=...)` |
| Read a document | `fetch(resource="document", id=...)` |
| List all docs in a collection (full tree) | `list_collection_documents(collectionId=...)` |
| Create a new document | `create_document(title=..., text=..., parentDocumentId=...)` |
| Surgical edit (preferred) | `update_document(id=..., editMode="patch", findText=..., text=...)` |
| Full replace | `update_document(id=..., editMode="replace", text=...)` |
| Append to a document | `update_document(id=..., editMode="append", text=...)` |
| Archive an orphaned document | `delete_document(id=..., archive=true)` |

Document content must not start with an H1 — the title is a separate field.

---

## /repo-wiki init

Bootstrap a wiki for a repo that has none. If local memory or Outline already has an entry for this repo, run `sync` instead.

1. **Agree on Outline location** — ask the user where to create the wiki. Use `list_collections` + `list_collection_documents` to present candidate locations and let them choose a parent doc.
2. Gather: `CLAUDE.md`/`README.md`, primary config file, `git log --oneline -40`, any existing Outline docs.
3. Create a `schema` document under the parent — file structure table, entity page template, log format, source-of-truth hierarchy.
4. Create a `log` document under the parent — backfill from git history; format: `| YYYY-MM-DD | TYPE | Summary |`; types: `added · changed · fixed · removed · learned`.
5. Create entity documents — one per significant component following the schema template; skip trivial pass-throughs.
6. Create an index document — all entity docs linked by title, organised by category.
7. **Write project memory** — create `~/.claude/projects/<encoded-cwd>/memory/repo-wiki.md` using the template below; add a pointer line to `MEMORY.md` in the same directory. This is the fast-path lookup for all future sessions.

### Memory file template

```markdown
---
name: repo-wiki
description: Outline wiki location for this repo — IDs used by the repo-wiki skill
metadata:
  type: reference
---

- **Parent doc ID:** `<id>`
- **Collection ID:** `<collection-id>`
- **Wiki URL:** <url>
```

Add to `MEMORY.md`:
```
- [repo-wiki](repo-wiki.md) — Outline parent doc ID and collection ID for the repo-wiki skill
```

---

## /repo-wiki sync

Bring the wiki up to date with recent changes. Incremental — only touches what changed.

1. Resolve IDs (universal first step above); `fetch` the schema doc and `list_documents` to find the log doc.
2. `git log --after="<last-log-date>"` + any uncommitted session changes.
3. Map commits → affected entity documents; for each: `fetch` the doc, compare to current code, update stale facts and add new gotchas; `create_document` from template if it doesn't exist yet.
4. Append to the log document (`update_document` with `editMode="append"`) — never edit past entries.
5. Report in two sentences.

---

## /repo-wiki lint

Verify wiki accuracy against current code — fix stale facts and archive orphaned pages.

**State-driven, not event-driven.** Compares wiki claims to actual code state regardless of git history. Use after refactors, renames, or long gaps between syncs.

1. Resolve IDs (universal first step above); use `list_collection_documents(collectionId=...)` to enumerate all documents in the wiki.
2. **Orphans** — confirm each entity document's subject still exists (module, file, service, CLI command). If gone: `delete_document(id, archive=true)` — never silently delete.
3. **Verifiable claims** — extract from surviving docs: file paths, symbol names, CLI flags, env vars, config keys, data flows. Skip narrative (decisions, history, gotchas).
4. **Verify** — use available code search tools + filesystem; classify: **Stale** (was true, no longer) · **Wrong** (never accurate) · **Incomplete** (true but missing caveats).
5. Fix in-place — `update_document` with `editMode="patch"`; surgical edits only, never rewrite entire documents.
6. Append to the log document — type `fixed`; note any documents archived.

---

## /repo-wiki enrich

Deepen wiki coverage with information in the code but not yet documented.

Goes beyond `init`/`sync` which capture high-level structure. Run `lint` first.

1. `fetch` all existing documents — map what's documented to avoid duplication.
2. Choose targets where code complexity exceeds wiki coverage: complex algorithms, silent error handling (swallowed exceptions, fallbacks, retries), code comments (`NOTE:` `HACK:` `FIXME:` `WARNING:`), test edge-case setups, config with non-obvious ordering.
3. Investigate with available code search — look for: preconditions, failure modes, perf limits, external-state dependencies, upstream-bug workarounds.
4. Write enrichments — `update_document` with `editMode="patch"` on existing documents, or `create_document` for new ones.
5. Append to the log document — type `changed`; note what category was added (e.g. "documented failure modes").
6. Report: what was enriched + the single most valuable finding — two sentences max.

---

## /repo-wiki search

1. Resolve IDs (universal first step above) — if not found, offer `init`.
2. `list_documents(query="<user's query>", collectionId=...)`.
3. `fetch(resource="document", id=...)` on the 1–3 most relevant results — summaries are rarely enough.
4. Answer with citations; don't fall back on general knowledge if the wiki doesn't have it.
5. Surface gaps — if the answer required reading code rather than the wiki, note it and offer to update the document.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Re-reading the full wiki on every sync | Use the log doc's last entry date as `--after` cursor — only read what changed |
| Editing past log entries | Append only; add a correction row if needed |
| Log entries describing *what* not *why* | "Fixed auth loop — root cause: token refresh misinterpreted 401" beats "Fixed auth" |
| Creating documents for trivial components | Only document entities with non-obvious behaviour, gotchas, or decisions worth preserving |
| Search returns nothing → falling back on memory | Say the wiki doesn't have it; offer to add it |
| Running `enrich` before `lint` | Enriching inaccurate pages embeds wrong information deeper |
| Using `sync` after a major refactor/rename | Use `lint` — `sync` only sees git history; `lint` sees current code state |
| Deleting orphaned documents | Archive with `delete_document(archive=true)`; historical context has value |
| `lint` rewriting whole documents for one wrong fact | Surgical `update_document(editMode="patch")` only; preserve non-verifiable narrative content |
| Starting document content with H1 | Outline stores the title separately — start body text with H2 or plain prose |
