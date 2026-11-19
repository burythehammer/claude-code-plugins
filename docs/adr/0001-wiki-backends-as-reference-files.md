# Wiki backends as reference files in one skill

`repo-wiki` stays one skill. `SKILL.md` describes its commands over an abstract
set of page operations: read, list, create, edit, append, retire and search.
Each backend's mechanics live in one reference file, and the skill loads only
the file for the repo's backend. GitHub and Forgejo wikis are both git
repositories of Markdown pages, so they share one reference file, with a short
section for each host.

## Considered options

- **One skill per backend** (`repo-wiki-outline`, `repo-wiki-github`, …): this
  copies the command logic, which then drifts, and it splits the skill's
  trigger keywords across several skills.
- **Backend branches inline in `SKILL.md`**: every run would load every
  backend's mechanics, and the command steps would fill up with per-backend
  conditions.

## Consequences

- Hierarchy is link-based only (directory pages list their children), because
  git wikis have flat page names and no parent field.
- The memory file records the backend. A memory file without one means
  Outline, so existing installs keep working without being migrated.
