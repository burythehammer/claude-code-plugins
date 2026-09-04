---
name: repo-wiki
description: Use when the user invokes /repo-wiki, or asks to bootstrap, sync, lint, enrich, or search a project's Outline wiki — or proactively, when wiki facts may be stale, pages orphaned, coverage sparse, or docs have drifted from the code.
---

# Repo Wiki

Structured wikis in Outline — one per code project. Compile knowledge into persistent pages rather than re-deriving it from code each session.

## Structure

Within the wiki, every parent document is a **directory**: it opens with links to all its direct children — no wiki page is left blank. (If you nest the wiki under a pre-existing doc, that external doc is out of scope — the skill never edits it.)

- **Root doc** (named after the repo) — the wiki home: a one-line description, then entity links grouped by category, plus links to the schema and log docs. This *is* the index; there is no separate index page.
- **Entity docs** — describe one component each; an entity that has sub-pages opens with a `## Sub-pages` directory linking them.

## Prerequisites

Every command drives the **Outline MCP server** (`mcp__outline__*` tools). Before any wiki work, confirm those tools are available. If they are not, stop and tell the user the Outline MCP server isn't connected — wiki commands can't run until it is. Do **not** fall back to writing wiki content into local files or inventing document IDs.

## Quick Reference

| Situation — user asks to… | Command |
|---------------------------|---------|
| No wiki yet — *bootstrap, set up, initialise* | `/repo-wiki init` |
| Behind recent commits — *update, sync, catch up* | `/repo-wiki sync` |
| Facts may be stale/wrong, pages orphaned or isolated — *audit, fact-check, verify, lint* | `/repo-wiki lint` |
| Accurate but sparse — *enrich, deepen, expand* | `/repo-wiki enrich` |
| Looking something up — *search, find, "where is…"* | `/repo-wiki search <query>` |

**Invoked with no mode?** Resolve IDs (below). No wiki found → offer `init`. Wiki found → say what exists and ask which mode fits; default to `sync` if the user only wants it current.

### Resolve IDs for the current repo (first step of every command)

1. **Local memory (fast path):** Read `~/.claude/projects/<encoded-cwd>/memory/repo-wiki.md`, where `<encoded-cwd>` is the absolute CWD with every `/` replaced by `-` (e.g. `/home/alice/workspace/myapp` → `-home-alice-workspace-myapp`). If found, extract the Collection ID, Root doc ID, and the Schema / Log doc IDs.
2. **Outline search (fallback):** `list_documents(query="<repo-name>")` to find the wiki root, note its `collectionId`, then `list_collection_documents(collectionId=...)` and identify the schema and log docs by title. Offer to write the memory file so the next session skips this search.
3. **Neither found:** offer to run `/repo-wiki init`.

Always re-resolve at the start of a command — never trust IDs remembered from earlier in the conversation. If a cached ID resolves to an archived or missing document, re-resolve via search and rewrite the memory file.

## Outline tool reference

| Task | Tool |
|------|------|
| Search documents (full-text) | `list_documents(query=...)` |
| Read a document | `fetch(resource="document", id=...)` |
| List all docs in a collection (full tree) | `list_collection_documents(collectionId=...)` |
| Create a new document | `create_document(title=..., text=..., parentDocumentId=...)` |
| Surgical edit (preferred) | `update_document(id=..., editMode="patch", findText=..., text=...)` |
| Append / prepend | `update_document(id=..., editMode="append"\|"prepend", text=...)` |
| Full replace (last resort) | `update_document(id=..., editMode="replace", text=...)` |
| Archive an orphaned document | `delete_document(id=..., archive=true)` |

- Document content must not start with an H1 — the title is a separate field; begin the body with H2 or prose.
- Create documents **published** (the `create_document` default). Drafts and archived docs are excluded from `list_collection_documents` and full-text search, so `lint` and `search` can't see them.
- `editMode="patch"` needs `findText` copied **verbatim** from the current markdown; it replaces only the first match and preserves the rest of the document's rich formatting. `replace` overwrites the whole document and discards formatting markdown can't represent — use it only as a last resort.

---

## /repo-wiki init

Bootstrap a wiki for a repo that has none. If local memory or Outline already has an entry for this repo, run `sync` instead.

1. **Agree on location** — ask where the wiki should live. Use `list_collections` + `list_collection_documents` to present candidates; the user picks a collection (and optionally an existing doc to nest under). Never repurpose an existing doc as the wiki — always create your own root. Note the chosen **collection's ID**; it goes in the memory file (step 8).
2. Gather: `CLAUDE.md`/`README.md`, primary config file, `git log --oneline -40`, any existing Outline docs.
3. Create the **root** document, named after the repo, at the chosen location — the wiki home and top-level directory. Fill its body last (step 7).
4. Create a **schema** document under the root (`parentDocumentId=<root id>`, as for every child below) — file-structure table, entity-page template, log format, source-of-truth hierarchy.
5. Create a **log** document under the root — backfill from git history; format `| YYYY-MM-DD | TYPE | Summary |`; types: `added · changed · fixed · removed · learned`. Write each summary as *why*, not *what*: "Fixed auth loop — root cause: token refresh misread a 401" beats "Fixed auth".
6. Create **entity** documents under the root — one per significant component, following the schema template; skip trivial pass-throughs. If an entity needs sub-pages, nest them under it and give that entity a `## Sub-pages` directory.
7. **Build the root directory** — now that every child exists, patch the root body (see Structure): a one-line repo description, then entity links grouped by category, plus links to the schema and log docs. No blank parents.
8. **Write project memory** — create `~/.claude/projects/<encoded-cwd>/memory/repo-wiki.md` from the template below, recording the Collection ID from step 1 plus the Root / Schema / Log doc IDs that `create_document` returned in steps 3–5; add a pointer line to `MEMORY.md` in the same directory. This is the fast-path lookup for every future session.

### Memory file template

```markdown
---
name: repo-wiki
description: Outline wiki location for this repo — IDs used by the repo-wiki skill
metadata:
  type: reference
---

- **Collection ID:** `<collection-id>`
- **Root doc ID:** `<id>`   <!-- wiki home / directory -->
- **Schema doc ID:** `<id>`
- **Log doc ID:** `<id>`
- **Wiki URL:** <url>
```

Add to `MEMORY.md`:
```
- [repo-wiki](repo-wiki.md) — Outline IDs (collection, root, schema, log) for the repo-wiki skill
```

---

## /repo-wiki sync

Bring the wiki up to date with recent changes. Incremental — only touches what changed.

1. Resolve IDs (above).
2. `git log --after="<last-log-date>"` (the date of the log doc's newest entry) + any uncommitted session changes.
3. Map commits → affected entity documents; for each: `fetch` the doc, compare to current code, update stale facts, add new gotchas; `create_document` from the schema template if it doesn't exist yet, and add a link to it in its parent directory (the root, or the entity it nests under).
4. Append to the log document (`update_document` with `editMode="append"`) — never edit past entries; correct an error with a new row instead of rewriting history.
5. Report in two sentences.

---

## /repo-wiki lint

Verify wiki accuracy against current code — fix stale facts, archive orphaned pages, reconnect isolated ones.

**State-driven, not event-driven.** Compares wiki claims to actual code state regardless of git history. Use after refactors, renames, or long gaps between syncs.

1. Resolve IDs (above); `list_collection_documents(collectionId=...)` to enumerate every document in the wiki.
2. **Orphans** — excluding the root, schema, and log docs (their IDs are in memory), confirm each remaining entity document's subject still exists (module, file, service, CLI command). If gone: `delete_document(id, archive=true)` — never silently delete.
3. **Isolated pages** — walk the collection tree against the directories: every doc must be linked from its parent directory (the root body, or its parent entity's `## Sub-pages` section), and no directory may point at an archived/removed doc. Patch directories to add missing links and drop dead ones — no parent left blank.
4. **Verifiable claims** — extract from surviving docs: file paths, symbol names, CLI flags, env vars, config keys, data flows. Skip narrative (decisions, history, gotchas).
5. **Verify** — use available code search tools + filesystem; classify: **Stale** (was true, no longer) · **Wrong** (never accurate) · **Incomplete** (true but missing caveats).
6. Fix in-place — `update_document` with `editMode="patch"`; surgical edits only, never rewrite entire documents.
7. Append to the log document — type `fixed`; note any documents archived or relinked.

---

## /repo-wiki enrich

Deepen wiki coverage with information in the code but not yet documented.

Goes beyond `init`/`sync`, which capture high-level structure. Run `lint` first.

1. Resolve IDs (above); `list_collection_documents` then `fetch` existing docs — map what's documented to avoid duplication.
2. Choose targets where code complexity exceeds wiki coverage: complex algorithms, silent error handling (swallowed exceptions, fallbacks, retries), code comments (`NOTE:` `HACK:` `FIXME:` `WARNING:`), test edge-case setups, config with non-obvious ordering.
3. Investigate with available code search — look for: preconditions, failure modes, perf limits, external-state dependencies, upstream-bug workarounds.
4. Write enrichments — `update_document` with `editMode="patch"` on existing documents, or `create_document` for new ones (link them into their parent directory).
5. Append to the log document — type `changed`; note the category added (e.g. "documented failure modes").
6. Report: what was enriched + the single most valuable finding — two sentences max.

---

## /repo-wiki search

1. Resolve IDs (above) — if not found, offer `init`.
2. `list_documents(query="<user's query>", collectionId=...)`.
3. `fetch(resource="document", id=...)` on the 1–3 most relevant results — summaries are rarely enough.
4. Answer with citations; don't fall back on general knowledge if the wiki doesn't have it.
5. Surface gaps — if the answer required reading code rather than the wiki, say so and offer to update the document.
