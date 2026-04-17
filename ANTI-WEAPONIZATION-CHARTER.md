# Anti-Weaponization Charter

Huginn & Muninn is built to strengthen democratic discourse. These commitments are non-negotiable. They were written before the features, and they constrain every design decision.

## Commitments

1. **Public narratives, not individuals.** This tool analyzes claims and narratives circulating in public discourse. It does not profile, surveil, or build dossiers on individuals.

2. **No automated censorship.** Verdicts produced by this tool are never suitable for automated content removal. They are analysis aids for human judgment, not machine-actionable takedown signals.

3. **Evidence-first actor analysis.** Any analysis of actors or networks requires documented evidence of coordinated inauthentic behavior. Legitimate dissent, protest, and minority viewpoints must never be flagged as disinformation.

4. **Reconciliation over suppression.** The Common Humanity layer exists to find shared ground between divided groups. It must never manufacture false consensus or push any political agenda.

   *Implementation discipline (v0.8.0):* The Bridge Builder's communication posture (direct correction, inoculation-first, or relational-first) advises the downstream communicator about the FORM of the response. It is never an instrument for suppressing or softening factual content to fit a preferred political register. Posture is mechanically separated from analytical confidence at the schema and runtime levels. No register choice can move a numeric truth-claim.

5. **Transparent uncertainty.** Every output carries confidence scores and explicit unknowns. When the system cannot determine the truth, it says so clearly rather than forcing a verdict.

6. **Autonomy-preserving.** Users are treated as autonomous adults capable of evaluating evidence. The system presents information and asks questions. It never lectures, labels, or condescends.

7. **Anti-bias vigilance.** The system acknowledges its own biases (Western-centric training data, English-language dominance, temporal knowledge gaps) and flags them when relevant. Actor-category symmetry is enforced by automated tests (v0.8.0): structurally equivalent attack signatures must classify identically regardless of whether the described actor is state, commercial, or non-state. Any divergence fails the test suite.

8. **Open methodology.** The analysis methodology, source tiering criteria, and manipulation technique taxonomy are fully transparent and open to public scrutiny.

## What This Tool Will Never Do

- Score or rank individuals on a "radicalization" scale
- Provide outputs usable for automated content filtering or shadow-banning
- Map social networks of legitimate activists, journalists, or whistleblowers
- Present contested political positions as settled facts
- Use manipulative techniques (emotional appeals, urgency, social proof) in its own outputs
- Operate in secret: all analysis methods are documented and open

## What This Tool Rejected (and Why)

Every rejected feature ships with documented falsification criteria. Some rejections are permanent because they would violate a commitment above. Others are conditional, revisitable if the evidence changes.

The full log lives in [REJECTIONS.md](REJECTIONS.md). The charter states what this tool is committed to; REJECTIONS.md records what it considered and refused, and under what conditions each refusal could be revisited.

## Accountability

If you discover this tool being used in ways that violate this charter, please report it. The charter exists because the capability to analyze disinformation is itself a dual-use capability. It must be constrained by values, not just by code.

---

*"Not every disagreement is manufactured. Some are real. But the ones that are manufactured deserve to be seen."*
