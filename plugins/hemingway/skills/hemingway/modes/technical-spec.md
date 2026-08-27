Apply these layers in addition to the core Analysis Framework.

**Precision audit:**
- Flag ambiguous quantifiers: "fast", "lightweight", "scalable", "efficient" → demand numbers
- Flag undefined terms on first use. Every acronym gets expanded once
- Flag "should" vs "must" vs "may" inconsistency — pick one convention (RFC 2119) and enforce it

**Completeness check:**
- Are inputs, outputs, and error states defined for every operation?
- Are edge cases addressed or explicitly marked as out of scope?
- Are constraints and limitations stated, not just capabilities?

**Structure enforcement:**
- Does every section answer: What? Why? How? What if it fails?
- Are requirements traceable — can each be verified independently?
- Flag narrative paragraphs that should be tables, lists, or diagrams

**Passive voice exception:** In specs, passive voice is acceptable when the actor is the system and emphasis belongs on the action or object. "The request is validated against the schema" is fine. "Mistakes were made" is not.
