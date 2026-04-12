# LinkedIn Post Draft: Huginn & Muninn v0.7.0 to v0.9.0

**Target length**: under 1500 characters
**Tone**: professional, mission-driven, honest about limitations
**No emojis. No em dashes.**

---

## Draft

Fact-checking is losing. Not because it is inaccurate, but because modern disinformation does not always depend on false claims. It operates by flooding the hypothesis space until people cannot decide which interpretation the evidence supports.

That is the problem Huginn & Muninn was built to address.

H&M is an open-source, local-first AI framework for disinformation analysis. The mission: de-polarize, not just debunk. Help people find each other as human beings. Then make the tool unnecessary.

Three recent milestones:

v0.7.0 added cognitive warfare detection: three new DISARM techniques for hypothesis flooding, source suppression before narratives are seeded, and synchronized narratives disguised as expert consensus. These attacks work even when every individual claim is technically true.

v0.8.0 grounded the Bridge Builder in 27 peer-reviewed citations. It now advises not just what is true, but how to communicate it to someone who currently believes otherwise. Every rejected feature ships with documented falsification criteria so the decision can be revisited if the evidence changes.

v0.9.0 hardened every external boundary. A regulated envelope now wraps all 10 serialization surfaces. Operators can suppress sensitive fields. The API documents its own GDPR and EU AI Act limitations. A scope scrubber converts prompt-level policy into a mechanical implementation guarantee: a model swap cannot accidentally emit defamatory content.

511 tests. Adversarial multi-faction review on every PR.

The Three Questions framework at the core is designed to be transferable: learn the pattern, then stop needing the tool.

If you work in media literacy, counter-disinformation, or responsible AI: the repo is public and the charter is non-negotiable.

github.com/Jochen-s/huginn-muninn

---

**Character count (post body only)**: ~1,430 characters

---

## Notes for revision

- The GitHub URL is a placeholder; replace with the actual repo URL before publishing.
- "Three Questions" is referenced but not spelled out; LinkedIn is not the place to list them in full. The repo README has them.
- The v0.10.0 framing was omitted intentionally: announcing "soon" features on LinkedIn before they ship can read as vaporware. Recommend a separate post once v0.10.0 is tagged.
- If Jochen wants a harder hook (e.g., naming a specific real-world event), that is a Station 1 editorial call best left to him.
