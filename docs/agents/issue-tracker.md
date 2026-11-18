# Issue tracker: Forgejo (code and PRs on GitHub)

Issues and specs live in Forgejo issues at `forgejo.burythehammer.com/burythehammer/claude-code-plugins` (account `burythehammer`). Use the `forgejo` MCP server (tools are `mcp__forgejo__*`, with `owner: "burythehammer"`, `repo: "claude-code-plugins"`) for issues, labels and the wiki. Tool schemas are deferred: load them with `ToolSearch` (`select:mcp__forgejo__<name>`) before calling. Confirm names with `list_repo_labels` rather than from memory.

**The code host is GitHub** (`burythehammer/claude-code-plugins`, remote `origin`). Branches and PRs live there and use `gh`. The Forgejo repo's code is a mirror only; Forgejo's own PR feature is not used.

## Mirror policy

`main` is pushed to the `forgejo` remote by hand when it needs updating (`git push forgejo main`, a fast-forward). There is no automation. Never commit to the Forgejo copy first.

## Conventions

- **Create an issue**: `create_issue` with `title`, `body` and `labels` in the same call. The body states the reasoning, not just the title.
- **Read an issue**: `get_issue_by_index`, plus `list_issue_comments` for the discussion.
- **List issues**: `list_repo_issues` (filter with `labels`, `state`); `search_issues` across the owner.
- **Comment**: `create_issue_comment`
- **Apply / remove labels**: `add_issue_labels` / `remove_issue_labels` (by name)
- **Assign**: `update_issue` (`assignees`)
- **Close**: `create_issue_comment` with a closing note, then `issue_state_change` with `state: "closed"`
- **Create a label**: `create_repo_label`. Read `list_repo_labels` first so it does not duplicate.

## Linking issues to GitHub PRs

GitHub cannot auto-close a Forgejo issue, so:

- The PR body links the issue by full URL (`https://forgejo.burythehammer.com/burythehammer/claude-code-plugins/issues/<n>`), never a bare `#<n>`: on GitHub that would point at an unrelated GitHub issue or PR.
- Commit messages say `Refs forgejo#<n>`.
- After the PR merges, close the Forgejo issue by hand with a comment linking the merged PR.
- Set the issue's branch field (`ref`) to the GitHub branch name via `update_issue` where the MCP build supports it.

## Specs and subtasks

One spec = one worktree = one GitHub PR.

- **Spec** (label `spec`): parent issue; owns the branch, the worktree and the single PR.
- **Subtask** (labels `subtask`, `ready-for-agent`): a slice that lands as commits on the spec's branch, never its own PR. Body has `## Parent` and `## Blocked by`, plus native dependency links (`add_issue_dependency`).
- The spec gets a comment (not a body edit) listing its subtasks.
- The PR body lists the spec and each subtask by full URL, one per line. After merge, close each by hand.

## Pull requests

**PRs as a request surface: no.** PRs are on GitHub:

- **Open**: `gh pr create`; write the body from the `/pr` template and assign it to yourself.
- **Merge**: `gh pr merge`, only after the user's go-ahead.

## When a skill says "publish to the issue tracker"

Create a Forgejo issue with `create_issue`.

## When a skill says "fetch the relevant ticket"

Run `get_issue_by_index` (and `list_issue_comments`) on the Forgejo repo.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: an issue labelled `wayfinder:map` (Notes / Decisions-so-far / Fog body). Create the label on first use.
- **Child ticket**: an issue with `Part of #<map>` at the top of its body; labels `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, assign to the driving dev.
- **Blocking**: Forgejo native dependencies (`add_issue_dependency`), plus a `Blocked by: #<n>` line at the top of the body. A ticket is unblocked when every blocker is closed.
- **Frontier query**: list the map's open children, drop any with an open blocker or an assignee; first in map order wins.
- **Claim**: assign the issue to yourself as the session's first write.
- **Resolve**: comment the answer, close the issue, then append a pointer to the map's Decisions-so-far.

## Wiki

The repo wiki is the Forgejo wiki, not Outline (the Outline copy is frozen and only points here). Use `get_wiki_page`, `update_wiki_page` and `create_wiki_page`, and append to the `log` page after any significant change; never edit past entries. The `repo-wiki` skill is Outline-only, so do not use it for this repo.
