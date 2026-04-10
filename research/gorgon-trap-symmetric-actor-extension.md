# Symmetric Actor Extension Plan for the Gorgon Trap Taxonomy

**Status**: Charter Commitment 7 precondition for any user-facing surfacing of the `GT-*` TTP entries.
**Version**: 1.0
**Date**: 2026-04-10
**Parent note**: `research/gorgon-trap-integration.md`

## 1. Why This Plan Exists

The Gorgon Trap taxonomy shipped in v0.7.0 (GT-001 White Noise, GT-002 Black Noise, GT-003 Pattern Injection) was derived from a paper that names specific state actors. Huginn & Muninn's Anti-Weaponization Charter Commitment 7 requires that the pipeline apply every detection signature symmetrically: the same structural pattern must trigger the same classification regardless of which actor category executes it.

This document is the formal record that the `GT-*` detection signatures are not coded to any single actor category, and it names the categories the signatures are expected to cover. It exists so that a future contributor adding a new scenario, a new TTP, or a new evaluation fixture can check their work against a principle rather than a feeling.

## 2. The Symmetry Principle

A narrative-attack signature is symmetric if and only if the classification outcome is invariant under substitution of the actor identity, holding the structural inputs constant. Formally: for any scenario `S = (pattern, actor, context)`, if we replace `actor` with any other actor drawn from the recognised categories without changing `pattern` or `context`, the expected TTP set and severity counts must not change.

This is a testable property. The fixture at `tests/fixtures/gorgon_symmetry_cases.json` and the test at `tests/test_gorgon_symmetry.py` encode the property as adversarial pairs that differ only in the actor-category slot. Any GT-family classifier or downstream consumer that produces different outputs across a pair is in violation of Charter Commitment 7.

The principle has a negative-space expression as well: a signature that only triggers on a single actor category, or that triggers with higher severity for one category than for another, is not a detection signature — it is an editorial position. Editorial positions are not disallowed by the charter, but they must not be presented to users as classifier outputs.

## 3. Actor Categories

The following categories are enumerated at the level of structural role, not at the level of current operations. The plan deliberately does not name specific campaigns, individuals, or named operations; those belong in evidence-grade research notes, not in a taxonomy precondition.

### 3.1 State and state-adjacent categories

The following category descriptions exist for symmetry-testing coverage only. They are structural labels for test-corpus purposes, not current-operational attributions. No paragraph in this section names a sub-organisation, campaign, or operation; see Section 5 for what this plan explicitly does not do.

**Five Eyes intelligence community**. Includes the US, UK, Canada, Australia, and New Zealand intelligence and strategic-communications apparatus as a structural category for symmetry testing. Historical literature describes signatures such as foreign-language outlet seeding, coordination with sympathetic journalism outlets, and timed release of partial evidence into news cycles. This category is included so those signatures are not treated differently when associated with Western state actors.

**Russian Federation**. Includes state and state-adjacent information operations as a structural category for symmetry testing. The RAND "Firehose of Falsehood" model (Paul & Matthews 2016) describes high-volume, multi-channel saturation patterns that map to White Noise without requiring the Gorgon Trap paper's adversary framing. This category is included so those signatures are tested as structural patterns rather than as Russia-specific labels.

**PLA and United Front Work Department**. Includes PRC state and state-adjacent narrative coordination as a structural category for symmetry testing. Public literature describes diaspora-engagement pressure, channel coordination, and consensus-mimicry patterns that can instantiate Black Noise and Pattern Injection at structural grain. This category is included to test whether those signatures are applied symmetrically rather than reserved for a single geopolitical bloc.

**Gulf-state-aligned operations**. Includes state-aligned narrative operations coordinated through or on behalf of Gulf governments as a structural category for symmetry testing. Historical reporting describes astroturf-style coordination, think-tank laundering, and saturation tactics that map to the GT-family at structural grain. This category is included so those patterns are tested without making current-operational attribution claims.

**Iranian state apparatus**. Includes Iranian state and state-adjacent narrative operations as a structural category for symmetry testing. Public literature describes persona amplification, diaspora-channel mutation, and consensus-mimicry patterns that can instantiate Pattern Injection-style signatures. This category is included to test symmetry at the signature level, not to attribute current operations.

**Israeli state and state-adjacent strategic communications**. Includes Israeli state and state-adjacent strategic-communications activity as a structural category for symmetry testing. Public literature describes coordinated talking-point distribution, takedown pressure, and high-volume amplification patterns that can instantiate GT-family signatures at structural grain. This category is included to ensure the same signatures are applied symmetrically without making current-operational attribution claims.

### 3.2 Non-state categories

**Commercial public-relations firms**. Includes crisis-comms agencies, reputation-management firms, and boutique influence shops that execute on behalf of corporate clients. Documented signatures are structurally identical to the state categories above: Pattern Injection via bought expert testimony and fake grassroots studies, Black Noise via SLAPP suits and coordinated search-result suppression, White Noise via press-release floods.

**Influencer networks**. Includes coordinated clusters of creators who amplify synchronised narratives for commercial or political reasons, whether paid directly or motivated by shared commercial incentives. Signatures include Pattern Injection via credential-adjacent personas and White Noise via coordinated posting schedules.

**Engineered grassroots coordination**. Includes coordinated activity that mimics grassroots origin while being directed or funded by a concealed sponsor. This category is deliberately named to avoid conflating engineered coordination with legitimate grassroots movements, which Charter Commitment 3 protects as legitimate dissent. Structural signatures include Pattern Injection via fabricated citizen testimonials and Black Noise via coordinated pressure campaigns against genuine grassroots critics.

**Non-state media operations**. Includes partisan media organisations, conspiracy-entrepreneurial outlets, and ideologically-aligned networks that execute the same structural attacks without state direction. Signatures are the full GT-family, often executed with lower resource constraints but higher tempo flexibility.

## 4. Falsification Cases

The following falsification cases are templates describing the shape of a category-breaking scenario. They are not themselves historical attributions; verified example citations per category will be added in a follow-up research note once the review corpus is assembled and vetted.

For each category, a falsification case is a template for the kind of documented scenario in which the category executes a signature that the corpus would otherwise associate with a different category. If the pipeline fails to trigger the signature on the falsification case, the signature is category-coded rather than structural, and the charter commitment is violated.

**Five Eyes falsification**. Any case template in which a Five Eyes-associated outlet seeds narratives through sympathetic journalism channels such that the same ecosystem would trigger White Noise or Pattern Injection classification if executed by a different category. Falsifying outcome: the pipeline classifies the template case identically to the paired case.

**Russian Federation falsification**. Any case template in which Russian-Federation-associated activity uses Black Noise (ecosystem suppression) signatures, as opposed to the White Noise signatures most commonly associated with the category. Falsifying outcome: Black Noise triggers even when the acting category is the one most associated with White Noise.

**PLA/UFWD falsification**. Any case template in which PRC-associated narrative coordination is executed through Western academic channels. Falsifying outcome: the signature triggers despite the channel being a Western institution.

**Gulf-state-aligned falsification**. Any case template in which Gulf-state-aligned activity uses Pattern Injection through apparently independent think-tanks headquartered in Western capitals. Falsifying outcome: the signature triggers despite the apparent independence of the forwarding institution.

**Iranian falsification**. Any case template in which Iranian-associated activity uses personas that mimic commercial-influencer aesthetics. Falsifying outcome: the signature triggers regardless of the persona's visual style.

**Israeli strategic-communications falsification**. Any case template in which Israeli state and state-adjacent strategic-communications activity uses White Noise volume floods during a non-operational window. Falsifying outcome: the signature triggers on volume, not on temporal proximity.

**Commercial PR falsification**. Any case template in which a commercial PR firm executes Black Noise via coordinated legal threats against journalists, in a pattern that would trigger the signature if executed by a state actor. Falsifying outcome: the pipeline classifies the commercial case identically to the state-actor paired case.

**Influencer-network falsification**. Any case template in which an influencer network executes Pattern Injection via credential-adjacent aesthetics (lab-coats-in-kitchens, fake citation graphics). Falsifying outcome: the signature triggers on structural credential mimicry, not on the speaker's day job.

**Engineered-grassroots-coordination falsification**. Any case template in which an engineered grassroots campaign uses Pattern Injection via fabricated citizen testimonials that mimic investigative-journalism framing. Falsifying outcome: the signature triggers on structural mimicry, not on stated identity. This template deliberately excludes legitimate grassroots movements, which Charter Commitment 3 protects as legitimate dissent.

**Non-state-media falsification**. Any case template in which a partisan media network executes the full GT-family (White + Black + Pattern) in a single coordinated campaign, with the same structural signature that state-actor cases receive. Falsifying outcome: the signature set triggers identically.

## 5. What This Plan Does Not Do

This plan does not attribute specific current operations to specific actors. Attribution is evidentially demanding and legally exposed, and the pipeline is not an attribution tool. The plan enumerates structural categories so that the detection signatures can be tested for symmetry; it does not claim that any category is currently executing any specific campaign.

This plan also does not prescribe the pipeline's response to detections. Detection is distinct from response; the Bridge Builder's approach to a detected signature is governed by the Anti-Weaponization Charter and the Three Questions framework, not by this document.

## 6. Enforcement

Charter Commitment 7 is enforced at three layers:

1. **Fixture layer**. `tests/fixtures/gorgon_symmetry_cases.json` contains adversarial pairs that differ only in actor category. The pairs are the test corpus.
2. **Test layer**. `tests/test_gorgon_symmetry.py` asserts bit-equivalent TTP sets and severity counts within each pair, and asserts the corpus contains multiple state and multiple non-state categories.
3. **Documentation layer**. This note plus `research/gorgon-trap-integration.md` record the decisions so that future contributors can find them.

A change that adds a new GT-family TTP, a new evaluation scenario, or a new Bridge Builder routing signature must update all three layers. Updates that only touch one layer are a Charter Commitment 7 risk and should be rejected in code review.

## 7. Revisit Triggers

- A new GT-family TTP is proposed. Requires new adversarial pair at fixture layer.
- A new actor category emerges that the current enumeration does not cover. Requires updating `REQUIRED_ACTOR_CATEGORIES` in the test file and adding at least one pair.
- Evidence emerges that a specific detection signature in the pipeline has asymmetric behaviour across categories. This is the falsification case trigger for the specific signature and invalidates its charter compliance until fixed.
- The Gorgon Trap paper progresses to peer review or a peer-reviewed RCT shows that any category's signatures have measurably different structural properties than another's. This would be grounds to revisit the symmetry claim itself.

## 8. Related Documents

- `ANTI-WEAPONIZATION-CHARTER.md` -- the governing commitments (Commitment 7 is enforced here).
- `research/gorgon-trap-integration.md` -- the parent record of the Gorgon Trap taxonomy decision, including rejections and revisit triggers.
- `tests/fixtures/gorgon_symmetry_cases.json` -- the test corpus.
- `tests/test_gorgon_symmetry.py` -- the deterministic invariance tests.
- Paul, C. & Matthews, M. (2016). *The Russian "Firehose of Falsehood" Propaganda Model*. RAND. Independent description of White Noise.
- Lakoff, G. (2004). *Don't Think of an Elephant*. The frame-engagement grounding that makes Pattern Injection recognisable.
