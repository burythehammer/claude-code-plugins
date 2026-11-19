# Outline backend

Mechanics for a wiki whose backend is Outline. `SKILL.md` loads this file when the memory file says `backend: outline` or has no `backend` field. Page IDs here are Outline document IDs.

## Prerequisites

Every operation drives the **Outline MCP server** (`mcp__outline__*` tools). Before any wiki work, confirm those tools are available. If they are not, stop and tell the user the Outline MCP server isn't connected; wiki commands can't run until it is. Do **not** fall back to writing wiki content into local files or inventing document IDs.

## Operations

| Abstract operation | Outline call |
|--------------------|--------------|
| Search pages (full-text) | `list_documents(query=..., collectionId=...)` |
| Read a page | `fetch(resource="document", id=...)` |
| List every page in the wiki (full tree) | `list_collection_documents(collectionId=...)` |
| Create a page under a parent | `create_document(title=..., text=..., parentDocumentId=...)` |
| Edit a page (surgical, preferred) | `update_document(id=..., editMode="patch", findText=..., text=...)` |
| Append to a page | `update_document(id=..., editMode="append", text=...)` |
| Prepend to a page | `update_document(id=..., editMode="prepend", text=...)` |
| Replace a page (last resort) | `update_document(id=..., editMode="replace", text=...)` |
| Retire a page | `delete_document(id=..., archive=true)` |
| List candidate locations (`init`) | `list_collections` + `list_collection_documents` |

## Gotchas

- Page content must not start with an H1. The title is a separate field; begin the body with H2 or prose.
- Create pages **published** (the `create_document` default). Drafts and archived pages are excluded from `list_collection_documents` and full-text search, so `lint` and `search` can't see them.
- `editMode="patch"` needs `findText` copied **verbatim** from the current markdown; it replaces only the first match and preserves the rest of the page's rich formatting. `replace` overwrites the whole page and discards formatting markdown can't represent; use it only as a last resort.
- Retire means archive, never delete outright.

## Resolving the wiki

1. **Memory file:** read the Collection ID, Home page ID, and the Schema and Log page IDs.
2. **Search fallback:** `list_documents(query="<repo-name>")` to find the home page, note its `collectionId`, then `list_collection_documents(collectionId=...)` and identify the schema and log pages by title. Offer to write the memory file so the next session skips this search.
3. A remembered ID that resolves to an archived or missing page: re-resolve by search and rewrite the memory file.

## `init` mechanics

- **Location:** ask where the wiki should live. List collections and their pages; the user picks a collection (and optionally an existing page to nest under). Never repurpose an existing page as the home page; always create your own. Note the chosen **collection's ID**.
- **Nesting:** every child is created with `parentDocumentId=<parent page id>`. The home page is created at the chosen location (under the existing page, if any).
- **Pre-existing parent:** if you nest the wiki under an existing page, that page is out of scope; never edit it.

## Memory fields

Beyond `backend: outline` (which may be omitted in older files), the memory file records:

```markdown
- **Collection ID:** `<collection-id>`
- **Home page ID:** `<id>`
- **Schema page ID:** `<id>`
- **Log page ID:** `<id>`
- **Wiki URL:** <url>
```

Older memory files label the home page "Root doc ID" and the others "doc ID"; read those labels as the same fields.
