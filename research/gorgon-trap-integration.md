# Gorgon Trap Integration Research Note

**Date**: 2026-04-10
**Version integrated**: 0.7.0
**Source paper**: Briggs, G., Danyk, Y., & Weiss, S. (2026). *The Gorgon Trap: Entropy, Cognitive Paralysis, and the Mechanics of Cognitive Warfare.* Zenodo. DOI [10.5281/zenodo.19326432](https://zenodo.org/records/19326432)

## Summary

The Gorgon Trap paper proposes a taxonomy of contemporary information-warfare techniques that extends classical disinformation analysis in two directions: it describes attacks that target the sense-making phase of decision-making rather than the belief-formation phase, and it names a class of attacks (Pattern Injection) that operate by *adding* structurally coherent false signal rather than by drowning true signal in noise. The paper also proposes a counter-doctrine and a mathematical formalism that, after analysis, we do not adopt.

This note documents what we integrated from the paper, what we deliberately did not, and why. It exists so that future contributors can understand the provenance of the new `GT-*` DISARM entries, the `hypothesis_crowding` / `frame_capture_risk` fields, and the `_compute_hypothesis_expansion_score` helper.

## What we integrated

### 1. Three new DISARM techniques (`data/disarm_techniques.json`)

| ID | Name | Tactic | Attack class |
|----|------|--------|--------------|
| GT-001 | White Noise | Execute | Flood the information space with high-volume, low-signal content to crowd the hypothesis space and make verification computationally expensive. |
| GT-002 | Black Noise | Prepare | Systematically suppress or exclude contradicting sources from the information ecosystem *before* primary narratives are seeded, shaping the evidentiary baseline so counter-evidence is absent rather than rebutted. |
| GT-003 | Pattern Injection | Prepare | Seed synchronized narratives that mimic the structural markers of expert consensus (fabricated sourcing, credential laundering, mimicry of investigative journalism) so audiences accept engineered conclusions as independently verified findings. |

The three entries are deliberately written in actor-neutral language: they do not name state actors, political ideologies, or regions. The same pattern may be executed by a state intelligence service, a commercial public-relations firm, a grassroots campaign, or a single influencer; the classifier should recognise the structural signature regardless of the operator.

Each entry carries a provenance note in its description referring back to the Briggs et al. taxonomy. The entries are marked as heuristics and remain pending community empirical validation — contributions with labelled examples are welcome.

### 2. `hypothesis_crowding` field on `DecomposerOutput`

A qualitative three-valued signal (`low` / `medium` / `high`) capturing how many plausible competing interpretations the input framing admits. It is not an entropy calculation. The paper gestures at a density-matrix / von Neumann formalism for this concept; after review we judged that formalism to be decorative rather than predictive in the absence of a concrete Hilbert space and a measurement protocol, and opted for a qualitative scale grounded in the Decomposer's existing reasoning. The scale is:

- `low` — a single dominant interpretive framing
- `medium` — two competing framings visible in the input
- `high` — three or more competing framings, or the input appears designed to invite multiple incompatible readings

The Decomposer prompt explicitly prohibits inflating sub-claim count to justify a higher `hypothesis_crowding` rating. The field defaults to `low` when the framing is unambiguous.

Two companion fields ride along: `manipulation_vector_density` (a qualitative 0.0-1.0 estimate of the ratio of sub-claims that open a manipulation surface) and `complexity_explosion_flag` (a boolean derived from explicit thresholds on sub-claim count and causal-claim ratio).

### 3. `notable_omissions` on `TracerOutput` and `relay_type` on `NarrativeMutation`

`notable_omissions` is a capped list (maximum three entries) of source *types* that would be expected to exist for a given claim's topic and era but are missing from the available context. The Tracer prompt requires that entries be phrased as "missing from context", not as "suppressed" or "censored"; intent attribution is explicitly prohibited, and source names must not be invented. The field defaults to an empty list. It captures the Black Noise signal without requiring the infrastructure needed for a full omission-detection search system, and without encouraging the LLM to speculate about suppression where no evidence of suppression exists.

`relay_type` on the existing `NarrativeMutation` contract classifies each amplification step as `knowing`, `unknowing`, or `ambiguous`, defaulting to `ambiguous` when the relay's awareness of the underlying operation is not explicit.

### 4. `frame_capture_risk` on `AuditorOutput`

A three-valued audit signal (`none` / `possible` / `high`) capturing whether the pipeline's own analysis has adopted the input claim's framing, labels, or implied causality without independently restating the question. A short `frame_capture_evidence` string carries the specific imported frame element.

The term **frame capture** is deliberately chosen over the paper's "verification trap" wording. The paper's strong claim is that fact-checking itself validates an adversary's frame; we judged this claim to be undergrounded and, more importantly, dangerous as an operational directive. A pipeline instructed to treat verification as an adversary tool would degrade into exactly the kind of fatalism that disinformation research is meant to counter. The frame-capture framing preserves the genuine insight (that framing adoption is a real risk) without compromising the pipeline's commitment to verification as a first-class activity. The Auditor prompt explicitly states that frame capture is *distinct from fact-checking* and that a claim can be rigorously fact-checked and have frame-capture issues simultaneously.

The assessment is gated: the Auditor is instructed to consider `frame_capture_risk` only when at least one upstream signal is present (`hypothesis_crowding="high"`, a non-empty `notable_omissions` list, or a matched TTP with a `GT-` prefix). Otherwise the default is `"none"`. This prevents the check from degrading into speculative flagging.

Cognitive-warfare findings are routed through the existing `AuditFinding.category` values (`manipulation` / `quality`) with description prefixes `[cognitive_warfare]` / `[frame_capture]`. We did not expand the category enum in this release; that change will land in a later PR after the downstream report renderers (`cli.py`, `api.py`, `db.py`) have been audited for category-based grouping logic.

### 5. Deterministic hypothesis-expansion helper

`_compute_hypothesis_expansion_score` in `orchestrator.py` is a pure Python helper that derives a bounded 0.0-1.0 score from the Decomposer's existing output (sub-claim count, causal-claim ratio, declared complexity). It is deterministic, adds zero LLM tokens, and feeds the Auditor's context as part of a `gorgon_signals` dictionary so that frame-capture gating can rely on a reproducible signal rather than on LLM re-inference of the Decomposer's work.

## What we did not integrate, and why

### The counter-doctrine ("Weaponized Absurdity")

The paper recommends "Narrative Interruption via Weaponized Absurdity" as a counter-tactic: deliberate reductio ad absurdum directed at an adversary narrative. We do not implement this, not as a detection label and not as a Bridge Builder technique, for four reasons:

1. **The cited doctrinal support is a Wonkette op-ed.** The paper's citation for this recommendation is a satirical blog post, not peer-reviewed research or operational doctrine. The recommendation has no controlled-study evidence base.

2. **It is structurally opposed to the Bridge Builder.** The Bridge Builder is designed to lower users' defensive posture toward opposing views so common ground can become visible. Weaponized absurdity requires users to *raise* their defensive posture. Running both in the same pipeline produces internally contradictory outputs.

3. **It violates the Anti-Weaponization Charter.** Specifically, Commitment 4 ("reconciliation, not suppression") and Commitment 6 ("autonomy-preserving"). Applying satirical reductio at the people holding a manipulated belief — as opposed to at the manipulation architecture — registers as mockery and forecloses relationship.

4. **It is inconsistent with the best current evidence on belief change.** Costello, Pennycook, and Rand (2024, *Science*) found that personalized Socratic dialogue in a non-confrontational register reduced conspiracy belief by approximately 20% with durable effects at two months. The mechanism was dignity-preserving engagement, not tempo-breaking.

### The literal quantum formalism

The paper uses density matrices and von Neumann entropy `S(ρ) = -tr(ρ ln ρ)` to represent "epistemic coherence". We do not implement this as a computation. The formalism specifies no concrete Hilbert space, no measurement protocol, no falsifiable experimental prediction, and no predictive advantage over classical information-theoretic tools already available (Shannon entropy applied to belief distributions). Implementing it literally would introduce false precision — users would see a number like `entropy: 0.73` and trust it as a rigorous measurement when it is an LLM-estimated heuristic dressed in quantum notation. The qualitative `hypothesis_crowding` field captures the useful residue of the concept without the false precision.

### The "victim of cognitive warfare" framing

The paper consistently refers to audiences of disinformation as "victims of cognitive warfare". This framing removes agency, creates a rescuer-victim dynamic, and is inconsistent with the deep-canvassing and motivational-interviewing evidence base that underpins the Bridge Builder. People who hold conspiratorial beliefs often have legitimate underlying grievances and real experiences of institutional failure; positioning them as victims flattens that complexity and makes genuine engagement harder.

We use "people navigating information environments designed to exploit trust" where the paper would use "victims". This preserves the adversarial-context recognition while keeping the reader's agency intact.

### Population-level claims

The paper's mechanism descriptions operate at the level of "decision-making bodies", "public discourse ecosystems", and "national cognitive infrastructure". Huginn & Muninn operates at the level of a single claim submitted by a single user. We deliberately do not extrapolate the paper's population-level mechanisms into individual-level diagnostics. Any signals inspired by the paper and shipped here are framed as individual-level heuristics, not as systemic indicators.

### Public citation of the paper

The paper is a Zenodo preprint as of this integration and carries a specific policy-advocacy valence in its framing of adversary selection. We cite it in this research note and in code comments for provenance, but we do not position it as a foundational reference in user-facing documentation. Where an independent foundational reference exists — Boyd's OODA loop, Paul and Matthews' RAND "Firehose of Falsehood", Lakoff on frame engagement, or the Pomerantsev ethnographic work on Russian information operations — we prefer those.

## Revisit triggers

This integration should be revisited when any of the following conditions change:

1. The paper progresses from Zenodo preprint to peer-reviewed publication.
2. A community empirical validation corpus for the `GT-*` entries reaches roughly N=50 labelled examples per technique. At that point the `heuristic` status in the technique descriptions can be reviewed for removal.
3. A symmetric actor-extension plan is published documenting how the `GT-*` signatures apply to actors the paper does not name (Western state actors, commercial marketing, corporate communications). This is a precondition for any user-facing surfacing of the signals.
4. The `AuditFinding.category` enum is ready to expand with `cognitive_warfare` and `frame_capture` literals. Requires a renderer audit first.
5. A peer-reviewed randomized trial of weaponized absurdity as a counter-tactic is published. This is the falsification criterion for our rejection of the paper's counter-doctrine.
6. A paper specifies a concrete Hilbert-space construction for cognitive-warfare dynamics with measurable interference effects. This is the falsification criterion for our rejection of the density-matrix formalism.

## Related reading

- The Anti-Weaponization Charter (`ANTI-WEAPONIZATION-CHARTER.md`) — the governing commitments that shaped every rejection decision above.
- `research/engagement-research/band-1-inoculation.md` — the inoculation theory that underpins the prebunking infrastructure the Bridge Builder shares with this work.
- Paul, C. & Matthews, M. (2016). *The Russian "Firehose of Falsehood" Propaganda Model*. RAND. The foundational description of the White Noise attack class, independent of the Gorgon Trap paper.
- Costello, T. H., Pennycook, G., & Rand, D. G. (2024). Durably reducing conspiracy beliefs through dialogues with AI. *Science*.
- Lakoff, G. (2004). *Don't Think of an Elephant*. The cognitive-linguistic grounding of the frame-engagement effect underlying `frame_capture_risk`.
