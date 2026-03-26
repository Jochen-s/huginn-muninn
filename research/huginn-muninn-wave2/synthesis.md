# Long-Range Sensor Sweep Wave 2: Dependency Mitigation, Academic Collaboration & Implementation

**Date**: 2026-03-24
**Bands deployed**: 4
**Bands completed**: 4/4
**Total sources**: ~125 unique sources
**Wave 1 reference**: `../huginn-muninn-strategic-research/synthesis.md`

---

## Executive Summary

Wave 2 resolves the dependency paradox identified in Wave 1. The Bao et al. (2025) finding -- that AI dialogue degrades independent discernment by 15.3% -- is not inherent to AI dialogue but is a **design failure specific to directive correction**. The Wharton study demonstrates that system-regulated AI access produces 64% learning gains versus 30% for on-demand access. Genuine Socratic questioning (not telling, but asking) correlates positively with independent detection skills (r=0.29). H&M's three-question framework ("What is true? How am I being played? What do we share?") functions as a metacognitive scaffold that, when combined with mandatory fading, desirable difficulties, and system-regulated access, builds lasting critical thinking capacity rather than dependency. The manufactured doubt detection architecture is immediately implementable using the 28-tactic taxonomy with three validated ML systems (CARDS, FLICC, SemEval). Academic collaboration is viable through the DFG Re:DIS programme (EUR 6.9M, deadline November 2025) with a four-arm RCT testing stage-calibrated Socratic dialogue as intervention. The Common Humanity layer's three-layer reinforcement (truth + manipulation literacy + shared humanity) is theoretically stronger than any single intervention because each layer corrects the others' weaknesses.

---

## Key Findings

### Dependency Mitigation (Band 1)

1. **[CRITICAL] The dependency paradox is a design failure, not an inherent limitation.** Bao et al.'s own data shows that "guiding and probing questions" (Socratic methods) correlated positively with independent detection (r=0.29), while directive methods (confidence calibration, devil's advocate framing) undermined learning. The problem is not AI dialogue; it is directive AI dialogue. [HIGH -- supported by Bao et al. 2025 + Wharton study + ZND paper]

2. **[HIGH] System-regulated access produces 2x the learning gains of on-demand access.** Wharton research: students with on-demand AI access achieved 30% gains; system-regulated access achieved 64% gains. On-demand users outsourced decision-making every 3-4 moves by month three. Users cannot be trusted to self-limit AI reliance; the system must enforce fading. (Wharton, 2025)

3. **[HIGH] The Zone of No Development explains the dependency mechanism.** When AI scaffolding never fades, Vygotsky's ZPD collapses into a Zone of No Development (ZND). The learner's comfort zone ceases to expand. Explicit fading mechanisms are mandatory, not optional. (arXiv:2511.12822, 2025)

4. **[HIGH] Seven concrete design patterns prevent dependency.** (1) Forced self-assessment before AI feedback, (2) rate-limiting and delayed access, (3) progressive scaffolding withdrawal on a 4-phase schedule, (4) interleaving AI-assisted and unassisted practice, (5) reflection prompts and metacognitive monitoring, (6) independence milestones with competence signaling, (7) the "graduation" model -- H&M is designed to make itself unnecessary.

5. **[HIGH] Bjork's desirable difficulties improve retention by up to 80%.** Spacing, interleaving, retrieval practice, and generation effects all slow short-term performance but dramatically improve long-term retention and transfer. H&M should incorporate all four: space out dialogues, mix claim types, require self-assessment before AI input, and force generation before exposure to analysis. (Bjork Lab, UCLA)

### Academic Collaboration (Band 2)

6. **[HIGH] DFG Re:DIS (SPP 2573) is the primary funding pathway.** EUR 6.9M programme specifically addressing conspiracy theories through interdisciplinary research. Deadline November 2025. Directly matches H&M's ego development + AI intervention proposal. VW Foundation Collaborative Projects (up to EUR 1.3M, deadline September 2025) is the secondary pathway. NSF is blocked under current US administration. EU Horizon Europe Cluster 2 opens new calls May 2026. [Multiple sources]

7. **[HIGH] Seven additional hypotheses formulated (H8-H14).** H8: Stage-calibrated dialogue outperforms generic. H9: Common Humanity framing is stage-dependent (effective at E5+, not E3-E4). H10: Scaffolding/fading prevents dependency. H11: Non-linear "developmental dip" at E4/E5 transition. H12: Micro-developmental shifts detectable after 8+ sessions. H13: Epistemic humility increases independent of ego stage. H14: More in Common segments map to different ego stage distributions.

8. **[HIGH] Four-arm RCT design specified.** Arms: (1) waitlist control, (2) generic AI dialogue, (3) stage-calibrated H&M, (4) stage-calibrated with scaffolding/fading. N=300-400 (75-100 per arm). Primary outcome: Conspiracy Mentality Questionnaire. Secondary: RWA scale, WUSCT, novel misinformation detection (unassisted), calibrated confidence scores. Follow-up at 2 and 6 months. Pre-registered on OSF.

9. **[MEDIUM] No existing study combines developmental assessment + stage-calibrated AI intervention + scaffolding/fading.** This would be the first. Closest precedent: Therabot RCT (NEJM AI, 2025; N=210) for AI as simultaneous intervention and measurement platform. Bronlet (2025) validates LLM-based WUSCT scoring at kappa=0.779.

### Manufactured Doubt Detection (Band 3)

10. **[HIGH] Complete 28-tactic taxonomy extracted with implementation mapping.** All 28 tactics cataloged with descriptions, industry usage (tobacco/coal/sugar/pesticide/climate), and examples. Five universal tactics form the highest-confidence detection signal. Twelve tactics rely on identifiable logical fallacies that are computationally detectable. (PMC7996119)

11. **[HIGH] Three validated ML systems ready for adaptation.** (1) CARDS: RoBERTa two-stage classifier, tested on 5M tweets, hierarchical "is it contrarian? then what type?" architecture. (2) FLICC+CARDS: DeBERTa fallacy detector, F1=0.73, 12 fallacy types mapped to the 28-tactic taxonomy. (3) SemEval-2020 propaganda detection: 14 technique types with span-level identification.

12. **[HIGH] Nine structural signatures distinguish manufactured from genuine doubt.** Manufactured: always concludes toward inaction, funding-source correlation, asymmetric scrutiny, internal-external contradiction (the Exxon pattern), absence of constructive proposals, tactic co-occurrence, concentrated source networks. Genuine: bidirectional conclusions, specific and bounded uncertainty, constructive engagement, transparent methodology.

13. **[HIGH] Programmatic 5-step decision tree for epistemic asymmetry.** Automatic Bridge Builder override when: scientific consensus >95%, doubt score 7+, 3+ universal tactics detected, documented industry funding trail. This resolves the false equivalence risk identified in Wave 1.

14. **[MEDIUM] Six curated training datasets identified.** UCSF Tobacco Library (16M documents), ExxonMobil climate files, CARDS corpus (20+ years), SemEval-2020 (536 annotated articles), COVID misinformation datasets (25K+ items), Four Shades of Life Sciences (2025).

### Common Humanity as Cognitive Filter (Band 4)

15. **[HIGH] Cognitive apprenticeship provides the transfer mechanism.** Collins/Brown/Newman's six-stage model (modeling, coaching, scaffolding, articulation, reflection, exploration) predicts that delivering analysis outputs will NOT produce internalization. Only the full progression from modeling to independent exploration creates lasting framework transfer.

16. **[HIGH] Perspective-taking is trainable and durable (5 months+), but empathic concern backfires.** Cognitive perspective-taking reduces polarization with effects stable at 5 months. But empathic concern (feeling what others feel) can increase polarization by intensifying ingroup distress. H&M's "What do we share?" must promote cognitive understanding, not emotional resonance. Concrete shared experiences work; abstract humanity appeals are weak.

17. **[HIGH] Technique-based inoculation transfers across topics and persists for months.** Teaching HOW manipulation works (scapegoating, false dichotomy, emotional amplification) creates lasting resilience that generalizes to novel claims. Five validated techniques map directly to H&M's "How am I being played?" question. Cambridge's 30,000-participant YouTube study confirms real-world effectiveness.

18. **[HIGH] The three-layer reinforcement is H&M's theoretical moat.** Truth-checking alone creates dependency. Manipulation literacy alone creates cynicism. Common humanity alone creates false equivalence. But together: truth-checking grounds the analysis, manipulation literacy builds independent detection skills, and common humanity prevents the cynicism that manipulation literacy can create. Each layer corrects the others' weaknesses. No competitor implements this combination.

19. **[MEDIUM] Common Ingroup Identity Model validates the "What do we share?" mechanism.** Gaertner and Dovidio's research shows recategorization from "us vs. them" to "we" reduces intergroup bias. Superordinate identity priming reduces vulnerability to polarizing narratives. This is the theoretical basis for H&M's bridge-building as inoculant against tribalism-based manipulation.

---

## Cross-Band Themes

### Theme 1: The Dependency Paradox Is Solved

Across all four bands, a consistent solution architecture emerges: genuine Socratic questioning (Band 1) + progressive scaffolding with mandatory fading (Bands 1, 4) + system-regulated access (Band 1) + the three-question framework as metacognitive scaffold (Band 4) + stage-calibrated dialogue (Band 2). The dependency paradox is not a fundamental limitation of AI dialogue; it is a predictable consequence of directive design that is preventable through established educational psychology principles.

### Theme 2: H&M as Research Instrument, Not Just Product

Bands 2 and 3 converge on H&M's highest-value near-term positioning: a research instrument for studying the relationship between ego development, conspiracy susceptibility, and AI-mediated intervention. The DFG Re:DIS funding pathway, the novel four-arm RCT design, and the first-of-its-kind combination of developmental assessment + stage-calibrated intervention make academic publication the clearest path to credibility and adoption.

### Theme 3: The Three Questions as Metacognitive Framework

All four bands reference H&M's three questions as the core transferable asset. Band 1 validates their design as metacognitive prompts. Band 3 grounds "How am I being played?" in the 28-tactic taxonomy. Band 4 grounds "What do we share?" in the Common Ingroup Identity Model. Band 2 designs experiments to test their stage-differential effectiveness. The three questions are not just an output format; they are the curriculum.

### Theme 4: Implementability Gradient

The findings have a clear implementability gradient: manufactured doubt detection (Band 3) is immediately implementable with existing ML systems. Dependency mitigation design patterns (Band 1) are implementable in the next development phase. Academic collaboration (Band 2) requires 3-6 months of proposal development. Common Humanity internalization (Band 4) requires the longest validation timeline.

---

## Contradictions and Tensions

### Tension 1: Socratic Purity vs. Beginner Accessibility

Band 1 identifies that pure non-directiveness fails beginners (LLMs show "hesitancy to provide clear corrective feedback" that paradoxically hinders novice understanding). But directive correction creates dependency. The resolution: stage-calibrated dialogue. At E3-E4 (Conformist), use authority-aligned framing with more guidance. At E6+ (Conscientious), use pure Socratic questioning. The system adapts to the user's developmental capacity.

### Tension 2: System-Regulated Access vs. User Autonomy

The Wharton finding that system-regulated access outperforms on-demand creates a tension with H&M's autonomy-supportive philosophy. Rate-limiting and forced self-assessment could feel paternalistic. The resolution: frame constraints as part of the training program. "You're building a skill. Like any training program, the structure is part of what makes it work."

### Tension 3: Academic Rigor vs. Open-Source Speed

The RCT design (Band 2) requires 30 months. The open-source community wants releases now. The resolution: release the tool with dependency mitigation built in and explicit caveats about empirical validation status. Run the RCT in parallel with community adoption. Publish interim findings.

---

## Research Gaps

1. **No study has tested the three-layer reinforcement.** The theoretical argument that truth + manipulation literacy + common humanity is stronger than any single layer is compelling but untested. The four-arm RCT should include this as an exploratory analysis.

2. **Stage-calibrated fading schedules are unvalidated.** The 4-phase fading model (full scaffolding -> partial -> minimal -> independence check) is derived from educational psychology theory but has not been tested in a disinformation context.

3. **Cross-cultural manufactured doubt patterns.** The 28-tactic taxonomy was developed from Anglo-American corporate cases. Whether the same structural signatures appear in non-Western manufactured doubt campaigns (e.g., state-sponsored disinformation in authoritarian regimes) is unknown.

4. **Long-term internalization measurement.** No validated instrument measures whether a cognitive framework like the three questions has been "internalized." A behavioral measure (spontaneous application in novel contexts without prompting) would need to be developed.

5. **The "developmental dip" hypothesis (H11).** The prediction that E4/E5 transition temporarily increases conspiracy susceptibility is theoretically grounded but empirically untested.

---

## Recommendations

1. **Implement the 4-pillar dependency mitigation architecture immediately.** (a) Genuine Socratic method (ask, don't tell), (b) mandatory fading schedule, (c) desirable difficulties (spacing, interleaving, retrieval practice, generation), (d) system-regulated access with rate-limiting. This is the pre-deployment blocker from Wave 1, and Wave 2 provides the complete solution.

2. **Submit a DFG Re:DIS proposal by November 2025.** The four-arm RCT design is ready. Partner with the ego development researcher for the WUSCT component. Budget: EUR 500K-800K for 30-month project. This is the highest-priority external action item.

3. **Build the manufactured doubt detection layer as Phase 7.** Adapt the CARDS two-stage classifier architecture. Train on UCSF tobacco documents + CARDS climate corpus. Implement the 5-step epistemic asymmetry decision tree. This is the most immediately implementable finding from both waves.

4. **Frame H&M publicly as a "cognitive gymnasium" with a graduation model.** The positioning: "Huginn & Muninn is designed to teach you a mental framework, not to be your permanent fact-checker. The three questions are yours to keep. Our goal is to make this tool unnecessary." This reframes the dependency concern from liability to feature.

5. **Pursue VW Foundation Collaborative Projects as secondary funding (deadline September 2025).** Up to EUR 1.3M for interdisciplinary AI + democracy research. Earlier deadline than DFG Re:DIS. Could fund the instrument development phase while the larger DFG proposal is prepared.

6. **Design H&M's "What do we share?" for cognitive perspective-taking, not empathic concern.** Use concrete shared circumstances, not abstract humanity. "You and the people described in this article both worry about providing for your families" rather than "We're all human." The research is clear: empathic concern can increase polarization.

7. **Add the 28-tactic manufactured doubt taxonomy to the presentation brief.** This is a powerful visual for the PKM Summit talk and academic presentations. A single slide showing the five universal tactics across five industries tells the story of manufactured doubt more effectively than any argument.

8. **Prepare an EU Horizon Europe Cluster 2 proposal for the May 2026 call.** Larger budget (EUR 3-3.5M per project), longer timeline, broader consortium. Use the DFG Re:DIS data (if funded) as preliminary results. This is the scale-up pathway.

---

## Band Reports

- [Band 1: Socratic Skill Transfer & Dependency Mitigation](band-1-socratic-skill-transfer.md) -- COMPLETE
- [Band 2: Academic Collaboration Hypotheses & Experimental Design](band-2-academic-collaboration.md) -- COMPLETE
- [Band 3: Manufactured Doubt Detection Implementation](band-3-manufactured-doubt.md) -- COMPLETE
- [Band 4: Common Humanity as Teachable Cognitive Filter](band-4-common-humanity-filter.md) -- COMPLETE
