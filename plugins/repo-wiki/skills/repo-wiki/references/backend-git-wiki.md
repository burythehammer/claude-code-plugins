# Git-wiki backend (GitHub and Forgejo)

Mechanics for a wiki whose backend is `github` or `forgejo`. `SKILL.md` loads this file for those backends. A git wiki is a separate git repository of Markdown files beside the code repository. One mechanism serves both hosts; the host sections below cover what differs. A page is a `.md` file at the clone's top level, and its page name is the file name without `.md`.

## Prerequisites

- `git` is available, and the user can push to the wiki remote (a credential helper or SSH key is already set up). If a push is refused for authentication, stop and tell the user; never embed tokens in URLs.
- The wiki remote URL is known (see Memory fields and the host sections).

## Mechanism

1. **Clone:** shallow-clone the wiki remote into a fresh directory in the scratchpad: `git clone --depth 1 <wiki-remote> <scratchpad>/<repo-name>-wiki`. Do not clone inside the code repository.
2. **Edit in place:** change Markdown files directly in the clone with the file tools.
3. **One commit per command:** at the end of a command, stage everything and make a single commit with a conventional-commit subject describing the command's change (for example `docs: sync wiki with recent commits`). No body, no trailers.
4. **Push rule:**
   - **Public repo:** show the user a diff summary (`git diff --stat` and the changed pages' key hunks) and ask for approval before pushing. Push only after a yes.
   - **Private repo:** push without asking.
   - Visibility comes from the host (see the host sections). If it can't be determined, treat the repo as public.
5. Keep the clone until the push succeeds; if the push is rejected as non-fast-forward, `git pull --rebase`, re-check the diff, and push again.

## Page names

Page names are flat: no folders, no nesting. Name entity pages with Title-Case words joined by hyphens (`Auth-Flow.md`). The home page is `Home.md`. The schema and log pages are `Schema.md` and `Log.md`. Link pages with relative wiki links, `[Auth Flow](Auth-Flow)`. Hierarchy exists only in `## Sub-pages` sections.

## Operations

| Abstract operation | Git action |
|--------------------|------------|
| read | Read `<Page>.md` in the clone |
| list | List `*.md` files at the clone's top level |
| create | Write a new `<Page>.md`, then link it from its parent directory page's `## Sub-pages` section |
| edit | Edit the file in place (Edit tool) |
| append | Add to the end of the file (the log page's new rows go at the end of its table) |
| retire | `git rm <Page>.md`, remove it from its parent directory page; also append a `fixed` row to the log page saying which page was retired and why. The command's single commit names the retired page in its subject (for example `docs: retire Auth-Flow page`). |
| search | Text search over the clone (`grep -rniF "<query>" --include='*.md' <clone>`) |

Search is over the clone, so clone (or `git pull`) fresh at the start of a `search`.

## Public-wiki guard

Before writing to a git wiki on a **public** repo, check what you are about to write. Never write private hostnames, internal URLs, IP addresses, credentials or other secrets, or details copied from private systems, into a public wiki. Replace them with a generic description ("the internal registry") or leave them out. If a page's facts depend on such a detail, describe the behaviour without it. Apply the guard on every command that writes, and again when summarising the diff for approval.

The guard applies to git wikis (GitHub or Forgejo) on public repos. On a private repo's wiki it does not apply, but the push rule above still does.

## GitHub

- **Remote:** derived from `origin` plus `.wiki.git`: `https://github.com/<owner>/<repo>.git` becomes `https://github.com/<owner>/<repo>.wiki.git` (and `git@github.com:<owner>/<repo>.git` becomes `git@github.com:<owner>/<repo>.wiki.git`).
- **Visibility:** `gh repo view --json isPrivate -q .isPrivate` (run for the code repository). `false` means public.
- **First-page stop (`init`):** the wiki remote does not exist until a first page is saved in the web UI. Before `init` does anything else, check `git ls-remote <wiki-remote>`. If it fails because the repository is not found, **stop** and ask the user to open the repo's Wiki tab, save a first page, and then re-run `init`. Do not try to create the remote another way, and do not report the clone error alone. Once the remote exists, `init` lists the files already in the clone rather than assuming it is empty. The placeholder `Home.md` the user saved to create the wiki is the sanctioned exception to `SKILL.md`'s "never repurpose an existing page as the home page": `init` overwrites it as the home page.
- The wiki's default branch is `master` on older wikis and may be `main`; use whatever the clone checks out, and push that branch (`git push origin HEAD`).

## Forgejo

- **Remote:** recorded explicitly in the memory file; ask the user for it during `init` (Forgejo's wiki remote is `<repo-url>.wiki.git`, but self-hosted instances vary, so never derive it).
- **Visibility:** check the repository's visibility in the Forgejo UI or via the Forgejo MCP tools or API if available. If it can't be determined, treat the repo as public.
- **First page:** a Forgejo wiki can be created from the web UI. If the remote is missing, stop and ask the user to save a first page there, as on GitHub.
- The public-wiki guard applies to a public Forgejo repo's wiki in the same way.
- Documented only; this host has no live test.

## Init

There is no location choice: the clone root is the wiki, and pages are flat files there, so present no candidate locations. The remote is derived from `origin` (GitHub) or asked for (Forgejo). Clone it, list the existing files, then create the home, schema, log and entity pages as `SKILL.md` `init` says. Finish under the push rule.

## Resolving the wiki

1. **Memory file:** read the wiki remote URL and the Home, Schema and Log page names.
2. **No memory file:** derive the remote (GitHub) or ask for it (Forgejo), clone it, and identify the home, schema and log pages by file name (`Home.md`, `Schema.md`, `Log.md`). Offer to write the memory file. A lone placeholder `Home.md` from first-page creation means no wiki content yet: run `init`, which overwrites it.
3. A remembered page name with no file in the clone: re-resolve by listing the clone and rewrite the memory file.

## Memory fields

```markdown
- **Backend:** `github`   <!-- or `forgejo` -->
- **Wiki remote:** `<wiki-remote-url>`
- **Home page:** `Home`
- **Schema page:** `Schema`
- **Log page:** `Log`
- **Wiki URL:** <url>
```

On GitHub, the remote is derived from `origin` plus `.wiki.git`; record it anyway so later sessions skip the derivation. On Forgejo it is recorded explicitly and never derived.
