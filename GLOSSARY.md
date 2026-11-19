# Claude Code plugins

A marketplace of Claude Code plugins. The vocabulary below is the `repo-wiki`
plugin's: the per-project wikis it builds and keeps current.

## Language

### Wikis and where they live

**Wiki**:
The set of pages that records one code project's knowledge, kept current by
`repo-wiki`. One wiki per repo.
_Avoid_: Docs, knowledge base, collection

**Backend**:
The service a wiki is stored in: Outline, a GitHub wiki or a Forgejo wiki. A
wiki has exactly one backend.
_Avoid_: Provider, host, store

**Git wiki**:
A backend whose pages are Markdown files in a git repository beside the code
repository (GitHub and Forgejo wikis).
_Avoid_: Repo wiki, Gollum wiki

### Pages

**Page**:
One document in a wiki.
_Avoid_: Document, doc, article

**Home page**:
The wiki's entry page: a one-line description of the repo, then links to every
entity page, the schema page and the log page. It is the wiki's index.
_Avoid_: Root doc, index page

**Schema page**:
The page that sets the wiki's own conventions: its layout, the entity page
template, the log format and the order sources are trusted in.
_Avoid_: Conventions page, template page

**Log page**:
The page holding the wiki's append-only change history, one row per change.
_Avoid_: Changelog, history

**Entity page**:
A page describing one significant component of the repo.
_Avoid_: Component doc, topic page

**Directory page**:
A page that has child pages and lists them under `## Sub-pages`. The home page
is the top directory page.
_Avoid_: Parent doc, folder, index

**Retire**:
To take a page out of a wiki because its subject no longer exists, while
keeping a record that it did.
_Avoid_: Delete, archive, remove
