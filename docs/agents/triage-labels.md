# Triage Labels

The skills speak in terms of canonical triage roles. This file maps those roles to the label strings used in this repo's issue tracker (Forgejo).

| Label in mattpocock/skills | Label in our tracker | Meaning                                       |
| -------------------------- | -------------------- | --------------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue       |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information      |
| (none)                     | `needs-spec`         | Triaged, but not yet specced                  |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent       |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation                 |
| `wontfix`                  | `wontfix`            | Will not be actioned                          |

Plus:

- One priority label per triaged issue: `priority:high`, `priority:medium` or `priority:low`.
- `spec` (parent issue owning a branch and PR) and `subtask` (a slice of a spec).

An issue is only `ready-for-agent` / `ready-for-human` once it has been specced. A triaged but unspecced issue gets `needs-spec` instead of `needs-triage`.

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.
