---
name: repo-wiki
description: Use when the user invokes /repo-wiki, or asks to bootstrap, sync, lint, enrich, or search a project's wiki (Outline, GitHub or Forgejo) — or proactively, when wiki facts may be stale, pages orphaned, coverage sparse, or docs have drifted from the code.
---

# Repo Wiki

Structured wikis, one per code project. Compile knowledge into persistent pages rather than re-deriving it from code each session. Vocabulary follows `GLOSSARY.md` (wiki, backend, page, home page, schema page, log page, entity page, directory page, retire).

## Structure

Every page that has children is a **directory page**: it lists all its direct children under a `## Sub-pages` heading, so no page is left blank and every page is reachable by links. Hierarchy is link-based only; page names stay flat. (If the wiki is nested under a pre-existing page, that external page is out of scope; the skill never edits it.)

- **Home page** (named after the repo, unless the backend reference file fixes the name): a one-line description, then entity links grouped by category, plus links to the schema and log pages. It is the top directory page and the wiki's index; there is no separate index page. It also lists its children under `## Sub-pages`.
- **Schema page**: the wiki's conventions (see `init`).
- **Log page**: append-only change history.
- **Entity pages**: one component each. An entity with sub-pages is a directory page and lists them under `## Sub-pages`.

## Backends and operations

A wiki's **backend** is where its pages are stored. Commands never call a backend directly; they use these abstract operations, and the backend reference file maps each to its mechanics:

| Operation | Meaning |
|-----------|---------|
| read | Get one page's content |
| list | Enumerate every page in the wiki |
| create | Add a page under a parent (directory) page |
| edit | Change part of a page in place, surgically |
| append | Add to the end of a page |
| retire | Take a page out of the wiki, keeping a record that it existed |
| search | Find pages matching a text query |

**Load only the reference file for the repo's backend**, once the backend is known (see Resolve the wiki):

| `backend` | Reference file |
|-----------|----------------|
| `outline` (or field missing) | `references/backend-outline.md` |
| `github`, `forgejo` | `references/backend-git-wiki.md` |

Follow that file's prerequisites before any wiki work. If a prerequisite is unmet, stop and tell the user; never fall back to writing wiki content into local files or inventing page IDs.

## Quick Reference

| Situation — user asks to… | Command |
|---------------------------|---------|
| No wiki yet — *bootstrap, set up, initialise* | `/repo-wiki init` |
| Behind recent commits — *update, sync, catch up* | `/repo-wiki sync` |
| Facts may be stale/wrong, pages orphaned or isolated — *audit, fact-check, verify, lint* | `/repo-wiki lint` |
| Accurate but sparse — *enrich, deepen, expand* | `/repo-wiki enrich` |
| Looking something up — *search, find, "where is…"* | `/repo-wiki search <query>` |

**Invoked with no mode?** Resolve the wiki (below). None found → offer `init`. Wiki found → say what exists and ask which mode fits; default to `sync` if the user only wants it current.

### Resolve the wiki for the current repo (first step of every command)

1. **Local memory (fast path):** Read `~/.claude/projects/<encoded-cwd>/memory/repo-wiki.md`, where `<encoded-cwd>` is the absolute CWD with every `/` replaced by `-` (e.g. `/home/alice/workspace/myapp` → `-home-alice-workspace-myapp`). If found, read its `backend` field: **a memory file with no `backend` field means `outline`**. Load that backend's reference file, then extract the page identifiers it names (home, schema and log pages, plus any backend location fields).
2. **Backend lookup (fallback):** with no memory file, ask the user which backend the wiki uses (default `outline`), load its reference file, and follow its "Resolving the wiki" section to find the home page and identify the schema and log pages by title. Offer to write the memory file so the next session skips this search.
3. **Neither found:** offer to run `/repo-wiki init`.

Always re-resolve at the start of a command; never trust identifiers remembered from earlier in the conversation. If a remembered page resolves to a retired or missing page, re-resolve via search and rewrite the memory file.

---

## /repo-wiki init

Bootstrap a wiki for a repo that has none. If local memory or the backend already has a wiki for this repo, run `sync` instead.

1. **Agree on backend and location** — ask which backend the wiki uses and where it should live; the backend reference file says how to present candidates. Load that reference file. Never repurpose an existing page as the home page; always create your own.
2. Gather: `CLAUDE.md`/`README.md`, primary config file, `git log --oneline -40`, any existing wiki pages.
3. Create the **home page**, named after the repo unless the backend reference file fixes the name, at the chosen location: the top directory page. Fill its body last (step 7).
4. Create a **schema page** under the home page (as for every child below): file-structure table, entity-page template, log format, source-of-truth hierarchy. A backend reference file may give the schema page a fuller template; follow it where it does, and write no Outline-specific content (page IDs, parent documents) into a git wiki's schema.
5. Create a **log page** under the home page. Backfill from git history; format `| YYYY-MM-DD | TYPE | Summary |`; types: `added · changed · fixed · removed · learned`. Write each summary as *why*, not *what*: "Fixed auth loop — root cause: token refresh misread a 401" beats "Fixed auth".
6. Create **entity pages** under the home page: one per significant component, following the schema template; skip trivial pass-throughs. If an entity needs sub-pages, create them under it and give that entity a `## Sub-pages` section.
7. **Build the home page's directory** — now that every child exists, edit its body (see Structure): a one-line repo description, then entity links grouped by category, plus links to the schema and log pages, and a `## Sub-pages` section listing every direct child. No blank directory pages.
8. **Write project memory** — create `~/.claude/projects/<encoded-cwd>/memory/repo-wiki.md` from the template below, recording the backend and the identifiers the backend reference file lists, using the values returned when the pages were created; add a pointer line to `MEMORY.md` in the same directory. This is the fast-path lookup for every future session.
9. Finish by applying the backend reference file's commit and push rule (a no-op on Outline).

### Memory file template

```markdown
---
name: repo-wiki
description: Wiki location for this repo — backend and page identifiers used by the repo-wiki skill
metadata:
  type: reference
---

- **Backend:** `outline`   <!-- outline | github | forgejo; a missing field means outline -->
- (backend fields: see the backend reference file's "Memory fields"; git backends record the wiki remote URL)
```

Add to `MEMORY.md`:
```
- [repo-wiki](repo-wiki.md) — wiki backend and page identifiers for the repo-wiki skill
```

---

## /repo-wiki sync

Bring the wiki up to date with recent changes. Incremental — only touches what changed.

1. Resolve the wiki (above).
2. Find what changed since the log's newest entry. Where a log row names a commit (for example `(b550f77)`), use `git log <sha>..HEAD`. Otherwise use `git log --after="<last-log-date>"`, and for commits on the log's own date, read the log rows to see which the log already covers, since a date has no time of day. Add any uncommitted session changes. If nothing is newer than the log, change nothing, say so and stop. When you log a change, name the newest commit it covers in the row.
3. Map commits → affected entity pages; for each: read the page, compare to current code, update stale facts, add new gotchas; create it from the schema template if it doesn't exist yet, and add a link to it in its parent directory page (the home page, or the entity it nests under).
4. Append to the log page. Never edit past entries; correct an error with a new row instead of rewriting history.
5. Finish by applying the backend reference file's commit and push rule (a no-op on Outline).
6. Report in two sentences.

---

## /repo-wiki lint

Verify wiki accuracy against current code — fix stale facts, retire orphaned pages, reconnect isolated ones.

**State-driven, not event-driven.** Compares wiki claims to actual code state regardless of git history. Use after refactors, renames, or long gaps between syncs.

1. Resolve the wiki (above); list every page in the wiki.
2. **Orphans** — excluding the home, schema and log pages, confirm each remaining entity page's subject still exists (module, file, service, CLI command). If gone: retire the page; never silently delete.
3. **Isolated pages** — check the links, not the page names. Ignore link syntax inside code spans and fenced blocks (a schema page's `[Auth Flow](Auth-Flow)` example is not a link). Build the set of pages reachable by following links from the home page's `## Sub-pages` section and from each directory page's `## Sub-pages` section. Every page other than the home page must be linked from a directory page, and no directory page may link to a retired or missing page. Edit directory pages to add missing links and drop dead ones; no directory page left blank.
4. **Verifiable claims** — extract from surviving pages: file paths, symbol names, CLI flags, env vars, config keys, data flows. Skip narrative (decisions, history, gotchas).
5. **Verify** — use available code search tools + filesystem; classify: **Stale** (was true, no longer) · **Wrong** (never accurate) · **Incomplete** (true but missing caveats).
6. Fix in place — surgical edits only, never rewrite entire pages.
7. Append to the log page — type `fixed`; note any pages retired or relinked.
8. Finish by applying the backend reference file's commit and push rule (a no-op on Outline).

---

## /repo-wiki enrich

Deepen wiki coverage with information in the code but not yet documented.

Goes beyond `init`/`sync`, which capture high-level structure. Run `lint` first.

1. Resolve the wiki (above); list the pages, then read the existing ones — map what's documented to avoid duplication.
2. Choose targets where code complexity exceeds wiki coverage: complex algorithms, silent error handling (swallowed exceptions, fallbacks, retries), code comments (`NOTE:` `HACK:` `FIXME:` `WARNING:`), test edge-case setups, config with non-obvious ordering.
3. Investigate with available code search — look for: preconditions, failure modes, perf limits, external-state dependencies, upstream-bug workarounds.
4. Write enrichments — edit existing pages, or create new ones (and link them into their parent directory page).
5. Append to the log page — type `changed`; note the category added (e.g. "documented failure modes").
6. Finish by applying the backend reference file's commit and push rule (a no-op on Outline).
7. Report: what was enriched + the single most valuable finding — two sentences max.

---

## /repo-wiki search

1. Resolve the wiki (above) — if not found, offer `init`.
2. Search the wiki for the user's query.
3. Read the 1–3 most relevant results — summaries are rarely enough.
4. Answer with citations; don't fall back on general knowledge if the wiki doesn't have it.
5. Surface gaps — if the answer required reading code rather than the wiki, say so and offer to update the page.
