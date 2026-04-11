# Bridge Scoped Diagnostics — Scientific Grounding

**Status**: Companion note for Sprint 2 PR 3 (`communication_posture`, `pattern_density_warning`, `vacuum_filled_by`, `prebunking_note`, Inferential Gap Map as reparative Pattern-Injection response).
**Version**: 1.0
**Date**: 2026-04-11
**Parent notes**: `research/gorgon-trap-integration.md`, `research/gorgon-trap-symmetric-actor-extension.md`

## 1. Purpose of This Note

Sprint 2 PR 3 adds four diagnostic fields to the Bridge Builder agent and labels one existing field. Each addition is grounded in peer-reviewed literature rather than product intuition. This note is the permanent record of that grounding so that a future contributor adding a fifth diagnostic, revising the prompt, or auditing the pipeline can trace each field back to the science that motivates it.

The note deliberately stops at citation level. Citations are pinned to the state of the literature at April 2026. If a cited finding fails replication, the corresponding field is a revisit trigger (see Section 7).

## 2. Inferential Gap Map as the Reparative Pattern-Injection Response

### 2.1 What Pattern Injection is

Gorgon Trap GT-003 (Briggs, Danyk, Weiss 2026 — see `research/gorgon-trap-integration.md` for the canonical citation form with author initials, unified across all H&M research notes to the Sprint 1 v0.7.0 reference) names Pattern Injection as the structural technique of inserting a fabricated pattern — a fake consensus, a manufactured expert cluster, a synchronised citation graph — into an information environment so that the pattern then serves as evidence for a downstream claim. The injected pattern is the payload; the downstream claim is what the payload is designed to carry.

Classical refutation fails against Pattern Injection for a reason that the replication literature has re-demonstrated many times (see Lewandowsky et al. 2012 on the continued-influence effect; Walter & Tukachinsky 2020 meta-analysis of correction effectiveness). A refutation that addresses the downstream claim without addressing the injected pattern leaves the pattern intact. The reader then reasons forward from the pattern to the next claim the pattern supports. The refutation has removed a leaf, not the branch.

### 2.2 Why the kernel-and-leap structure repairs it

Method 2's Bridge Builder has always produced a Layer 4 "Inferential Gap Map": the specific separation of the kernel of truth from the unsupported leap. The PR 3 relabeling recognises what this layer has always been doing. The kernel-and-leap structure is the reparative Pattern-Injection response because:

1. The kernel is named and kept. The reader does not have to surrender the observation that led them to the claim; that observation is often real. Surrendering it is the identity cost that classical refutation demands and that triggers backfire in identity-threat conditions (Nyhan & Reifler 2010; Wood & Porter 2019 replication).
2. The leap is named and separated. The structural transition from "X is documented fact" to "therefore Y" is the injected pattern's load-bearing move. Naming the leap in concrete terms is what lets the reader see the pattern as an inference-step they can independently evaluate, not as a holistic narrative they must accept or reject wholesale.
3. The name-the-gap move is technique-recognition, not identity confrontation. The reader is being taught a structural move they can apply to other claims. This is the trainable cognitive-filter dimension that maps onto Common Humanity perspective-taking findings (Perry et al. Common Humanity scale; see Section 4).

### 2.3 The PR 3 labeling discipline

The load-bearing lines in `bridge.py` — the Layer 4 "kernel of truth" / "inferential leap" / "X is documented fact; the leap to Y is unsupported because Z" block — are not changed by PR 3. PR 3 adds a label above them ("REPARATIVE PATTERN-INJECTION RESPONSE — load-bearing") so that a future edit cannot silently collapse the kernel+leap separation into a generic refutation. The test `TestBridgePromptPreservation` enforces this at the assertion level: if the kernel and leap vocabulary disappears, PR 3's primary repair channel is broken and the test fails loudly.

## 3. Communication Posture as Epistemic/Communicative Separation

### 3.1 The three postures

`communication_posture` is a `Literal["direct_correction","inoculation_first","relational_first"] = "direct_correction"` field on `BridgeOutput`. It selects the communicative register of the analysis. It is orthogonal to `overall_confidence`. The two are enforced-separate by a runtime invariance test (`test_communication_posture_does_not_co_vary_with_overall_confidence`) and a grep-style architectural lock (`test_communication_posture_not_referenced_in_confidence_computation`).

### 3.2 direct_correction — classical refutation

Appropriate when the reader is already open to correction and the analytical frame is shared. This is the default because it is the lowest-overhead posture and, in readers who are not currently in a manipulation frame, it is the most honest. The literature is consistent that classical refutation works when identity defence is not triggered: Walter & Tukachinsky 2020 (meta-analysis, k=32) found corrections have substantive effects in low-identity-threat conditions. The failure mode of this posture is that it also gets deployed in high-identity-threat conditions, which is what motivates the other two postures.

### 3.3 inoculation_first — technique-naming prebunk

Appropriate when the reader is still inside the manipulation frame and a direct correction would trigger identity defence. The posture leads with naming the technique ("this is how X-style argument works") before introducing counter-evidence. Grounding literature:

- **McGuire 1964** introduced inoculation theory: exposing readers to a weakened form of a persuasive attack builds cognitive resistance in the same way a vaccine builds immunological resistance. The analogy is load-bearing: the reader is not told the conclusion; they are shown the mechanism. McGuire 1964 is the theoretical origin, not a contemporary misinformation-correction effect-size source.
- **van der Linden 2020** (*Nature Human Behaviour*, "Conspiracy theories and the injection of doubt") is a theoretical synthesis / review piece, not an original experiment. It frames inoculation as the strategy of choice for conspiracy-belief resistance and is cited here for the framing, not for primary empirical evidence.
- **van der Linden, Leiserowitz, Rosenthal, Maibach 2017** extended inoculation to climate-misinformation and showed that inoculation-plus-correction outperforms correction alone by a substantial margin in pre-registered designs.
- **Roozenbeek & van der Linden 2019, 2022** demonstrated that gamified technique-naming (the "Bad News" and "Go Viral!" interventions) produces measurable resistance to misinformation techniques and generalises across topics. **Primary empirical durability evidence** for PR 3 lives in Roozenbeek, van der Linden, Goldberg, Rathje, Lewandowsky 2022 (*Science Advances*). The critical finding: the effect is in technique-recognition, not in topic-specific correction.
- **Traberg, Roozenbeek, van der Linden 2022** showed that active prebunking produces larger effects than passive warning labels, which matters for the Bridge Builder: the posture must name the technique concretely, not generically gesture at "manipulation".

**Effect-size and durability caveat** (Sprint 2 PR 3 fleet-review convergence, Holodeck P-roles): the "durable resistance" characterisation above must not be read as indefinite durability. Contemporary meta-analyses (Stasielowicz 2026; Wang, Lewandowsky, et al. 2025 on ecological conditions) report average effect sizes in the Cohen's d ≈ 0.16-0.30 range under ecological conditions, with decay on the order of 1-4 weeks in most studies absent reinforcement. The Roozenbeek et al. 2022 finding is that the effect exists and generalises; it is not that the effect lasts a year without booster exposure. `inoculation_first` is literature-grounded, not claimed to be a durable one-shot intervention, and the revisit-trigger section (§7) specifies the conditions under which this grounding would need revision.

`inoculation_first` should be selected when the upstream TTP Classifier has flagged GT-family techniques, when manipulation-vector density is high, or when the reader profile suggests the frame has already taken hold.

### 3.4 relational_first — Common Humanity / acknowledgment-first

Appropriate when identity stakes dominate the claim and any correction will be read as attack unless the kernel of truth is acknowledged first. The posture starts from the human concern behind the claim, names it explicitly as legitimate, and only then introduces structural analysis.

**Evidence-level note (Codex PR 3 adversarial-review correction):** unlike `direct_correction` and `inoculation_first`, the `relational_first` posture is not yet a validated member of a tested misinformation-correction posture taxonomy. It is a *design-informed synthesis* drawing on adjacent literatures that each speak to a piece of the mechanism, not a single replicated empirical finding naming "relational_first" as a posture with measured effects against a control. The posture is retained as a first-class schema field because the synthesis is plausible, the prompt-level fallback discipline is safe (direct_correction is the default), and the Bridge Builder's register choice is downstream of truth-claim analysis and cannot move `overall_confidence`. The grounding literatures are:

- **Common Humanity psychology** (Oveis, Horberg, Keltner 2010 for the construct's initial operationalisation as compassion-through-shared-experience; Tiwari & Elmufti 2024 [manuscript status: *in press*; citation must be updated on publication] on Common Humanity scale psychometric development) treats the perception of shared human experience as a trainable cognitive filter. Sprint 2 PR 3 fleet-review correction (Holodeck P-roles P2): this note does NOT attribute a five-month durability finding to Common Humanity. The construct literature reports mixed cross-cultural psychometric properties and a range of intervention durabilities across different paradigms; PR 3 does not claim it predicts misinformation-correction success at any specific time horizon.
- **Costello protocol** (Costello, Pennycook, Rand 2024, *Science*) reports durable reductions in conspiracy belief after GPT-4 dialogues that combine perspective-getting, counter-evidence presented as questions, and shared-ground framing. The paper does *not* disaggregate which component of the three-round structure is load-bearing; attributing the "acknowledge the kernel of truth" move specifically to Round 1 is our reading, not a finding of the paper. The `relational_first` posture is inspired by this design, not validated by it as an isolated intervention.
- **Kappes, Harvey, Lohrenz, Montague, Sharot 2020** (*Nature Neuroscience*, "Confirmation bias in the utilization of others' opinion strength") investigates how participants weight others' opinions asymmetrically based on prior agreement. Sprint 2 PR 3 fleet-review correction (Holodeck P-roles P3): this paper is cited as a **mechanistic building block** consistent with the design intuition that prior agreement modulates receptive updating. It does NOT directly measure shared-reality perception as a misinformation-correction precondition. The inference from Kappes 2020 to the `relational_first` posture is a theoretical extension, not a direct empirical finding.

`relational_first` should be selected when perception_gap is high, when moral_foundations diverge sharply across the actors involved, or when the upstream pipeline signals identity-targeting dynamics. If the Costello 2024 result fails independent replication, or if follow-up work disaggregates the dialogue components and finds acknowledgment-first is not the load-bearing move, the posture must be re-scoped or deprecated (see §7 revisit triggers).

### 3.5 Why posture must be orthogonal to confidence

Confidence is the Auditor's question: how certain is the analysis? Posture is the Bridge Builder's question: how should the analysis land? Conflating the two is Codex's Sprint 1 Risk #6 ("confidence-posture conflation") — the failure mode where a message that needs to be delivered relationally gets its confidence dragged down because the message's form is soft. PR 3 makes the separation mechanical. The runtime test asserts that varying posture across all three literals does not move `overall_confidence` for otherwise-identical inputs. The grep test asserts that `communication_posture` is not referenced inside the confidence-computation block at `orchestrator.py`. Both tests together enforce BG-042 (Confidence-Posture Separation) at the Sprint 2 PR 3 level.

## 4. Pattern Density Warning — Content-Describing, Not Reader-Diagnosing

`pattern_density_warning: bool = False` replaces the original proposal of `apophenia_bait_flag`. The rename is deliberate: "apophenia" is a clinical term describing the human tendency to perceive meaningful patterns in random data (Brugger 2001; for contemporary review see Fyfe, Williams, Mason, Pickup 2008). Using "apophenia_bait_flag" in a user-facing schema would pathologise the reader. PR 3 rejects that framing.

The field is content-describing. True iff the claim exhibits structural features that predispose readers to over-connect:

- Repeated numeric coincidences (e.g., "on 9/11, United 93, 93 minutes, 93 passengers" — the rhythmic number repetition is the bait).
- Rhythmic lexical choices that create mnemonic bonding across unrelated claims.
- Escalating concept chains that string together a sequence of individually-plausible steps into an implausible conclusion.
- Dense cross-reference to a constellation of related claims that form a self-reinforcing web.

The literature on why pattern density matters: **Whittlesea & Williams 2001** on fluency attribution, **Alter & Oppenheimer 2009** on processing-fluency effects, and **Schwarz 1998** on how processing fluency is read as truth. Claims that are pattern-dense feel true even when their content is weakly supported. Flagging this at the Bridge Builder level gives the downstream communicator a concrete cue about the claim's structural persuasive pull, separate from its factual accuracy.

The flag never diagnoses the reader as pathological. The Holodeck feedback in Sprint 2 planning was explicit: readers are not apophenia patients. Readers are ordinary humans operating with ordinary cognitive biases under claims that are engineered to exploit those biases. The field names the engineering, not the reader.

## 5. Vacuum Filled By — Narrative Pattern Only

`vacuum_filled_by: str = ""` is a structural description of what narrative pattern filled an expertise or information vacuum around the claim. The scope discipline is strict: narrative patterns only, never named publishers, never named individuals, never named organisations.

The scope constraint is not an aesthetic choice. It is the Romulan/Holodeck-grade risk control that separates structural analysis from defamation. Naming a publisher as an expertise-vacuum filler creates publication liability in defamation-sensitive jurisdictions (UK OSA Section 179, EU DSA Article 34, and general common-law defamation) even when the factual content of the claim is accurate. Naming an individual creates personal liability exposure. Naming an organisation creates corporate liability exposure. Structural description of a narrative pattern creates none of these. The field's prompt constraint is enforced at the test level: `test_vacuum_filled_by_forbids_named_publishers` and `test_vacuum_filled_by_provides_acceptable_and_unacceptable_examples` are regression guards against a future prompt edit that silently loosens the scope.

The literature on why vacuum-filling matters: **Starbird, Arif, Wilson 2019** on the ecosystem-level dynamics of information voids during breaking news; **Marwick & Lewis 2017** on how "data voids" (Golebiewski & boyd) are filled by whoever ranks first, which is structurally independent of whoever is correct; and **Phillips 2018** on amplification asymmetries when legacy media does not cover a topic that non-legacy media saturates. These literatures are consistent that vacuum-filling is a structural signature, not an actor-specific signature. Describing the signature is analysis; naming the filler is attribution, and attribution is legally and evidentially costly. PR 3 does the first and not the second.

## 6. Prebunking Note — Technique Warning, Not New Factual Assertion

`prebunking_note: str = ""` is a one-sentence technique-recognition cue that a reader can carry forward to recognise similar claims. The field is additive to the Inferential Gap Map in Layer 4; it is not a substitute. The prompt enforces this explicitly so that a future edit cannot silently promote the prebunking note into the primary repair channel.

The literature justifying the field:

- **Roozenbeek, van der Linden, Goldberg, Rathje, Lewandowsky 2022** ("Psychological inoculation improves resistance against misinformation on social media") showed that brief prebunking videos produced durable improvements in readers' ability to identify manipulation techniques in the wild. The critical finding for the prebunking_note field: the effective prebunks were technique-specific, not topic-specific. Reading one prebunk about the "false dichotomy" technique improved readers' ability to identify false dichotomies across unrelated topics.
- **Lewandowsky, van der Linden 2021** ("Countering misinformation and fake news through inoculation and prebunking") established the general finding that prebunking is durable where debunking is transient, in the specific sense that a reader who has been taught a technique keeps the technique across topic domains, whereas a reader who has been corrected on a specific claim does not necessarily transfer the correction.

The prebunking_note field is the pipeline's seam for that technique-transfer. It must state the technique concretely ("watch for the fabricated-source-mimicry pattern in similar claims") rather than abstractly ("watch out for manipulation"), because the technique-specific finding is exactly the concrete-over-abstract contrast the literature establishes.

The field must never introduce a new factual assertion about any specific actor, because the prebunking_note is not part of the analysis — it is a teaching moment about structural recognition. Promoting a prebunking_note into a factual assertion would move the field from technique-naming into claim-making, which is the Auditor's territory, not the Bridge Builder's.

## 7. Revisit Triggers

The fields in this note are grounded in literature that is itself subject to replication and revision. The revisit triggers are:

- **Inoculation theory**: if a large preregistered replication of van der Linden 2020 or Roozenbeek & van der Linden 2022 fails, `inoculation_first` must be demoted from a literature-grounded posture to an experimental option and the prompt must be updated to flag this.
- **Common Humanity / Costello protocol**: if the Costello 2024 protocol fails replication or the Common Humanity scale shows poor psychometric properties in a cross-cultural study, `relational_first` becomes an open question and the prompt must be updated to note it.
- **Continued-influence effect / kernel+leap**: the kernel+leap structure assumes the continued-influence effect is real. If a major preregistered replication finds the effect is smaller than the Walter & Tukachinsky 2020 meta-analysis reports, the Inferential Gap Map remains the correct move for identity-threat conditions but its framing as "the reparative response" needs softening.
- **Apophenia literature / pattern density**: the Alter & Oppenheimer 2009 fluency effect is well-replicated; the specific "pattern density" operationalisation in this note is not a named construct in the literature and is a product decision, not a literature claim. If the operationalisation produces false positives in practice, it is a product bug, not a scientific revision.
- **Data voids literature**: the Golebiewski & boyd / Starbird et al. work on information voids is descriptive, not causal. If a future study shows that `vacuum_filled_by` descriptions are systematically misleading — that the flagged "vacuum" was not actually a vacuum — the field's prompt needs tightening on the definition of a vacuum.
- **Tiwari & Elmufti 2024 (in press)** publication resolution: the Common Humanity scale citation is currently to an in-press manuscript. If publication changes the scale's psychometric profile materially or if peer review blocks the paper, the `relational_first` grounding loses a component cite and must be re-sourced.
- **Briggs, Danyk, Weiss 2026 Zenodo citation**: the canonical author-initials form in H&M research notes is unified to `research/gorgon-trap-integration.md`'s Sprint 1 form (G, Y, S). Verification against the actual Zenodo record is pending at the time of writing; if verification reveals a different form, both notes must be updated together.

## 8. What This Note Does Not Claim

- It does not claim that `direct_correction`, `inoculation_first`, and `relational_first` exhaust the space of useful communication postures. They are three postures with independent literature support. A Sprint 3 revisit could add a fourth (e.g., "empathetic-witness" for the therapeutic register; "procedural-clarification" for epistemic disputes) if a literature-grounded case can be made.
- It does not claim that the Bridge Builder can automatically select the correct posture in all cases. The selection is an LLM judgement under prompt guidance. A Sprint 3 revisit could add a posture-selection rubric based on upstream signals (perception_gap, frame_capture_risk, hypothesis_crowding) rather than LLM inference.
- It does not claim that flagging `pattern_density_warning=True` reliably identifies claims that will persuade. The flag is a structural feature detector, not a persuasion predictor.
- It does not claim that the fields shipped in PR 3 are the complete set of Bridge diagnostics. It is a scoped increment grounded in specific literatures.

## 9. Related Documents

- `ANTI-WEAPONIZATION-CHARTER.md` — governing commitments, particularly Commitment 1 (no surveillance), Commitment 3 (protection of legitimate dissent), Commitment 7 (anti-bias vigilance).
- `research/gorgon-trap-integration.md` — parent note for the Gorgon Trap taxonomy decision and GT-001/002/003 signatures.
- `research/gorgon-trap-symmetric-actor-extension.md` — the Charter Commitment 7 precondition note covering actor-category symmetry for GT-family triggers.
- `CHANGELOG.md` — user-facing ship record for Sprint 2 PR 3.
- `src/huginn_muninn/contracts.py` — `BridgeOutput.communication_posture`, `pattern_density_warning`, `vacuum_filled_by`, `prebunking_note`.
- `src/huginn_muninn/agents/bridge.py` — Layer 4 (reparative Pattern-Injection response) and sections F/G/H/I of the build_prompt.
- `tests/test_orchestrator.py::TestVerificationPriorityFallback` — contains the two confidence-invariance tests that enforce BG-042 at runtime.
- `tests/test_agents.py::TestBridgePromptPreservation` — contains the load-bearing preservation tests for the inferential_gap / narrative_deconstruction / consensus_explanation instructions.

## 10. Citation List

The citation list below is alphabetical. Year pinned to state of literature as of April 2026.

- Alter, A. L., & Oppenheimer, D. M. (2009). Uniting the tribes of fluency to form a metacognitive nation. *Personality and Social Psychology Review*, 13(3).
- Briggs, G., Danyk, Y., & Weiss, S. (2026). *The Gorgon Trap: Entropy, Cognitive Paralysis, and the Mechanics of Cognitive Warfare.* Zenodo DOI 10.5281/zenodo.19326432. Author-initials form unified with `research/gorgon-trap-integration.md`; Sprint 2 PR 3 fleet review flagged a drift between an earlier transcription and the Sprint 1 canonical form, resolved here in favour of the Sprint 1 form. Verification against the published Zenodo record is a pending revisit trigger; see §7.
- Brugger, P. (2001). From haunted brain to haunted science: a cognitive neuroscience view of paranormal and pseudoscientific thought. In *Hauntings and poltergeists: multidisciplinary perspectives*.
- Costello, T. H., Pennycook, G., & Rand, D. G. (2024). Durably reducing conspiracy beliefs through dialogues with AI. *Science*, 385(6714).
- Fyfe, S., Williams, C., Mason, O. J., & Pickup, G. J. (2008). Apophenia, theory of mind and schizotypy: perceiving meaning and intentionality in randomness. *Cortex*, 44(10).
- Golebiewski, M., & boyd, d. (2019). *Data voids: where missing data can easily be exploited*. Data & Society Research Institute.
- Kappes, A., Harvey, A. H., Lohrenz, T., Montague, P. R., & Sharot, T. (2020). Confirmation bias in the utilization of others' opinion strength. *Nature Neuroscience*, 23(1).
- Lewandowsky, S., Ecker, U. K., Seifert, C. M., Schwarz, N., & Cook, J. (2012). Misinformation and its correction: continued influence and successful debiasing. *Psychological Science in the Public Interest*, 13(3).
- Lewandowsky, S., & van der Linden, S. (2021). Countering misinformation and fake news through inoculation and prebunking. *European Review of Social Psychology*, 32(2).
- Marwick, A., & Lewis, R. (2017). *Media manipulation and disinformation online*. Data & Society Research Institute.
- McGuire, W. J. (1964). Inducing resistance to persuasion: some contemporary approaches. *Advances in Experimental Social Psychology*, 1.
- Nyhan, B., & Reifler, J. (2010). When corrections fail: the persistence of political misperceptions. *Political Behavior*, 32(2).
- Oveis, C., Horberg, E. J., & Keltner, D. (2010). Compassion, pride, and social intuitions of self-other similarity. *Journal of Personality and Social Psychology*, 98(4).
- Perry, R., Priest, N., Paradies, Y., Barlow, F. K., & Sibley, C. G. (2018). Barriers to multicultural acceptance: a case for common humanity. *European Journal of Social Psychology*, 48(4).
- Phillips, W. (2018). *The oxygen of amplification*. Data & Society Research Institute.
- Roozenbeek, J., & van der Linden, S. (2019). Fake news game confers psychological resistance against online misinformation. *Palgrave Communications*, 5.
- Roozenbeek, J., & van der Linden, S. (2022). Inoculation interventions can build cognitive resistance to online misinformation. *Frontiers in Psychology*, 13.
- Roozenbeek, J., van der Linden, S., Goldberg, B., Rathje, S., & Lewandowsky, S. (2022). Psychological inoculation improves resistance against misinformation on social media. *Science Advances*, 8(34).
- Schwarz, N. (1998). Accessible content and accessibility experiences: the interplay of declarative and experiential information in judgment. *Personality and Social Psychology Review*, 2(2).
- Starbird, K., Arif, A., & Wilson, T. (2019). Disinformation as collaborative work: surfacing the participatory nature of strategic information operations. *Proceedings of the ACM on Human-Computer Interaction*, 3(CSCW).
- Tiwari, R., & Elmufti, S. (2024). The Common Humanity Scale: psychometric development and cross-cultural validation. *Journal of Cross-Cultural Psychology* (in press).
- Traberg, C. S., Roozenbeek, J., & van der Linden, S. (2022). Psychological inoculation against misinformation: current evidence and future directions. *The ANNALS of the American Academy of Political and Social Science*, 700(1).
- van der Linden, S., Leiserowitz, A., Rosenthal, S., & Maibach, E. (2017). Inoculating the public against misinformation about climate change. *Global Challenges*, 1(2).
- van der Linden, S. (2020). Conspiracy theories and the injection of doubt: the inoculation strategy. *Nature Human Behaviour*, 4.
- Walter, N., & Tukachinsky, R. (2020). A meta-analytic examination of the continued influence of misinformation in the face of correction: how powerful is it, why does it happen, and how to stop it? *Communication Research*, 47(2).
- Whittlesea, B. W. A., & Williams, L. D. (2001). The discrepancy-attribution hypothesis: I. The heuristic basis of feelings of familiarity. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 27(1).
- Wood, T., & Porter, E. (2019). The elusive backfire effect: mass attitudes' steadfast factual adherence. *Political Behavior*, 41(1).
