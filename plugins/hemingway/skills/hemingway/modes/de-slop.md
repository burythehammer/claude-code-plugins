AI-generated text has distinctive failure patterns. This mode targets them specifically, in addition to the core Analysis Framework.

**Slop markers — flag and kill every instance:**

| Pattern | Example | Fix |
|---------|---------|-----|
| Enthusiasm padding | "Great question!", "Absolutely!", "That's a fantastic point!" | Delete entirely |
| Filler transitions | "Now, let's dive into...", "Let's explore...", "Let's take a closer look at..." | Cut or replace with direct statement |
| Sycophantic hedging | "This is a really great start, but...", "You've done an excellent job, however..." | State the issue directly |
| False certainty | "This will definitely...", "This ensures that..." | Qualify appropriately or cite evidence |
| Meaning-free intensifiers | "truly", "incredibly", "remarkably", "significantly" | Delete or replace with specific measure |
| Cliche metaphors | "game-changer", "deep dive", "level up", "at the end of the day" | Rewrite with concrete language |
| Summary repetition | Restating what was just said in slightly different words | Delete the repetition |
| Emoji seasoning | Random emoji that add no meaning | Delete |
| List-itis | Converting everything to bullet points when prose flows better | Rewrite as prose where appropriate |
| Fake structure | "In this article, we will..." / "In conclusion..." | Delete throat-clearing; if the conclusion adds nothing, cut it |
| Hollow acknowledgment | "That's an interesting approach" | Delete or engage with the specifics |
| Thesaurus syndrome | Using 3 synonyms where 1 word works ("efficient, effective, and streamlined") | Pick the best one |
| Corporate passive | "It should be noted that...", "It is important to..." | Say who notes it and why, or delete |

**Tone normalization:**
- AI text tends toward relentless positivity. Flag sentences that are positive without justification
- AI text avoids strong opinions. If the content *should* take a stance, flag wishy-washy both-sidesing
- AI text over-qualifies. "In many cases, this can potentially help to..." → "This helps..."

**Structure de-slop:**
- Flag unnecessary introductions that restate the title
- Flag conclusions that only summarize without adding insight
- Flag sections that exist for "completeness" but add no value to the reader
- Flag bullet-point lists that would read better as 2-3 sentences

**Voice consistency:**
- Compare the text's voice against the surrounding content (if available)
- Flag tonal shifts that suggest AI-written sections were inserted into human-written text
- If the user has a style guide or prior writing samples, match to that voice
