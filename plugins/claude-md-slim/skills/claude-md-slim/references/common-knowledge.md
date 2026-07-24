# Identifying common-knowledge rules

A rule earns its place in context only if Claude would behave differently
without it. Common-knowledge rules fail that test: the model already follows
them by default, so they cost tokens every session and change nothing. This
file gives the deletion criteria and worked examples for the
DELETE — common knowledge verdict.

## The test

Ask of each rule: **"Would a fresh Claude session, given no instructions,
already do this?"** If yes, delete. If it encodes a *choice between defensible
alternatives* or a *lesson this project learned the hard way*, keep or extract.

Three sub-tests that catch most cases:

1. **Framework documentation restated.** If the rule paraphrases the official
   docs of React, Django, Go, Terraform, pytest, etc., the model already knows
   it more thoroughly than the summary.
2. **Generic best practice.** "Write tests", "handle errors", "use meaningful
   names", "keep functions small" — universally endorsed advice adds no signal.
3. **Tool mechanics.** How git works, what `npm install` does, how to write a
   Dockerfile. The model knows; the repo's *specific* invocations (`make
   test-fast`, the deploy alias) it cannot know.

## Worked examples

### Delete — the model already does this

```markdown
- Use functional components with hooks instead of class components
- Always use const/let, never var
- Follow PEP 8 style guidelines
- Use async/await instead of raw promises where possible
- Write descriptive commit messages
- useEffect cleanup functions should cancel subscriptions
- Don't mutate state directly in React; use setState
- Prefer composition over inheritance
- Use prepared statements to avoid SQL injection
```

Each of these is default model behaviour. The SQL-injection one *looks* like
security content, but it prescribes universal practice rather than a project
policy — contrast with the keeper security examples below.

### Keep or extract — project signal the model cannot derive

```markdown
- We use class components in the legacy/ tree — do NOT convert them; the
  migration is tracked in JIRA-1234 and must go through the platform team
- Run `make test-fast`, never `npm test` (npm test hits the real staging DB)
- Our ESLint config bans default exports — named exports only
- The `User.email` column is nullable for historical reasons; always guard
- API responses use snake_case even though the codebase is camelCase, because
  the mobile client predates the style guide
```

Each encodes a choice, an exception, or a scar. A fresh session would get
these wrong.

### The disguised keeper

Beware rules that look generic but carry a project-specific tail:

```markdown
- Write unit tests for new code, placing them in test/unit/ (NOT alongside
  the source — our CI globs only test/)
```

"Write unit tests" is deletable filler; "`test/unit/` because CI globs only
`test/`" is a keeper. Split such rules: delete the filler clause, keep the
project clause.

## Never delete, regardless of the test

- **Security and permissions content**: secret-handling rules, lists of files
  never to read, deny policies, credential locations. Even when phrased as
  generic advice, the user put it there as a guard-rail; removing it widens
  the blast radius of a future mistake. Downgrade at most to an unscoped
  `.claude/rules/` file.
- **Rules with emphatic formatting** (ALL CAPS, "CRITICAL", repeated warnings).
  Emphasis is evidence of a past incident. Flag in the report's Questions
  section instead of deleting.
- **Anything you cannot confidently classify.** The report's Questions section
  exists precisely for these; a wrongly deleted rule fails silently weeks
  later, which is far costlier than one extra line of context.
