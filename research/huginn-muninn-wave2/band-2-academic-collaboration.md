# Band 2: Academic Collaboration Hypotheses & Experimental Design

**Research question**: How can H&M serve as a research instrument for ego development and conspiracy susceptibility research?
**Research conducted**: 2026-03-24

---

## 1. Joint Research Proposal Structure

### 1.1 Existing Templates and Precedents

Five recent studies provide structural templates and empirical grounding for a joint proposal:

**Costello, Pennycook & Rand (Science, 2024)** -- "Durably reducing conspiracy beliefs through dialogues with AI." This is the single most relevant precedent. The study engaged 2,190 conspiracy believers in personalized evidence-based dialogues with GPT-4 Turbo. The intervention reduced conspiracy belief by approximately 20%, an effect that persisted at 2-month follow-up, generalized across a wide range of conspiracy theories, and occurred even among deeply entrenched believers. The mechanism was evidence-based counterarguments tailored to each participant's stated reasons for belief. (https://www.science.org/doi/10.1126/science.adq1814)

**Becker et al. (ArXiv, 2025)** -- "Dialogues with AI Reduce Beliefs in Misinformation but Build No Lasting Discernment Skills." A 67-participant longitudinal study (3 sessions over 4 weeks) found that AI assistance produced immediate +21% accuracy improvements during assisted sessions, but unassisted performance on novel items declined by 15.3% by week 4 -- the "dependency paradox." Critically, Socratic questioning approaches (guiding/probing questions) showed the strongest positive correlation with independent detection skills (r=0.29), while confidence calibration and devil's advocate roleplay actually worsened unassisted performance (r=-0.42). Five participant trajectory types emerged, including "Dependency Developers" (21%) who progressed from active engagement to passive acceptance. (https://arxiv.org/html/2510.01537v1)

**Meyer et al. (Harvard Misinformation Review, 2025)** -- "Using an AI-powered 'street epistemologist' chatbot and reflection tasks to diminish conspiracy theory beliefs." Tested three interventions: AI chatbot probing belief justifications, self-reflection on uncertainties, and self-reflection on reasons. All reduced conspiracy belief strength, but individuals with high conspiracy predisposition or who reported accuracy importance were less responsive. (https://misinforeview.hks.harvard.edu/article/using-an-ai-powered-street-epistemologist-chatbot-and-reflection-tasks-to-diminish-conspiracy-theory-beliefs/)

**Socrates 2.0 (JMIR Research Protocols, 2024)** -- A CBT-based generative AI tool for Socratic dialogue. The protocol describes a mixed-methods feasibility study with 55 participants, using a three-layer AI architecture: AI therapist, AI supervisor, and AI rater. This architecture is directly analogous to what H&M could implement for stage-calibrated dialogue. (https://www.researchprotocols.org/2024/1/e58195/)

**TITAN Socratic AI Against Disinformation (ACM IMX 2024)** -- EU Horizon Europe project testing a Socratic AI chatbot prototype in four Co-Creation Labs across Belgium, Italy, Bulgaria, and Denmark (N=80). Each participant conversed with the chatbot about a news article containing disinformation signals, followed by quantitative assessment of critical thinking stimulation. (https://dl.acm.org/doi/10.1145/3639701.3663640)

### 1.2 Proposed Abstract Structure

**Working Title**: "Stage-Calibrated AI Dialogue as Intervention and Measurement Platform for Ego Development and Anti-Democratic Attitudes: A Randomized Controlled Trial"

**Abstract elements**:
1. Problem: Rising conspiracy mentality and anti-democratic attitudes lack scalable, individualized intervention approaches. Existing AI dialogue interventions (Costello et al. 2024) reduce conspiracy beliefs but do not build lasting discernment skills (Becker et al. 2025), suggesting the intervention mechanism matters as much as the content.
2. Theory: Loevinger's ego development model (E2-E9) as predictor of susceptibility to conspiracy mentality, authoritarianism, and science skepticism; Socratic dialogue as developmental catalyst that matches intervention to cognitive complexity level.
3. Innovation: First study combining (a) automated WUSCT scoring (Bronlet 2025, kappa=0.779) for developmental assessment, (b) stage-calibrated AI dialogue as intervention, and (c) scaffolding/fading protocol to build autonomous discernment rather than dependency.
4. Methods: Four-arm RCT (waitlist control, generic AI dialogue replicating Costello et al., stage-calibrated H&M Socratic dialogue, stage-calibrated H&M with scaffolding/fading) with pre/post/follow-up WUSCT and multi-scale belief measurement.
5. Expected outcomes: Differential intervention effects by ego stage; superior durability for stage-calibrated approaches; discernment skill acquisition in the scaffolding/fading condition.

### 1.3 Methodology Outline

**Phase 1 -- Instrument Development (Months 1-8)**:
- Adapt WUSCT automated scoring for H&M platform, building on Bronlet 2025 methodology (weighted kappa=0.779 using GPT-4 and Claude 3 against expert STAGES scorers). Bronlet's work validated group-level but not individual-level scoring; this phase must improve individual accuracy for clinical assignment to treatment arms. (https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1488102/full)
- Develop stage-calibrated dialogue protocols for each ego development stage (E3-E7; E2 and E8/E9 are too rare for adequate statistical power)
- Design scaffolding/fading protocol informed by Becker et al. findings that Socratic probing questions correlate with independent skill acquisition (r=0.29) while confidence calibration correlates with dependency (r=-0.42)
- Pilot test with N=40 for protocol refinement and inter-rater reliability

**Phase 2 -- Main Trial (Months 9-18)**:
- Four-arm RCT with pre-registration on OSF
- 8 dialogue sessions per participant over 6 weeks (consistent with Becker et al.'s finding that dependency effects emerge by week 4)
- Pre/post assessment battery: WUSCT (36-stem version), CMQ (Conspiracy Mentality Questionnaire; Bruder & Imhoff 2013), RWA scale (22-item; Altemeyer), science skepticism items, novel misinformation detection task (unassisted), calibrated confidence measure
- Follow-up at 2 months (matching Costello et al.) and 6 months

**Phase 3 -- Analysis and Dissemination (Months 19-30)**:
- Primary analysis: interaction effect of condition x ego stage on conspiracy belief change
- Secondary analyses: discernment skill acquisition by condition, dependency indicators, sub-stage developmental shifts
- Qualitative trajectory analysis following Becker et al.'s five-type classification
- ML analysis of dialogue patterns predictive of belief change and skill acquisition

### 1.4 Specific Research Aims

**Aim 1**: Validate automated WUSCT scoring at individual level (extending Bronlet 2025 from group-level to individual classification accuracy of kappa > 0.80).

**Aim 2**: Test whether ego development stage predicts conspiracy mentality, authoritarianism, science skepticism, and related anti-democratic attitudes (the researcher's H1-H7).

**Aim 3**: Test whether stage-calibrated Socratic dialogue produces more durable belief change than generic evidence-based dialogue (extending Costello et al. 2024).

**Aim 4**: Test whether scaffolding/fading design prevents the dependency paradox documented by Becker et al. 2025.

---

## 2. Additional Hypotheses Beyond the Researcher's Seven

### 2.1 Stage-Calibrated vs. Generic Dialogue Efficacy

**H8: Stage-calibrated Socratic dialogue produces more durable belief change than generic evidence-based dialogue, particularly at transitional ego stages (E4/E5 boundary).**

Rationale: Costello et al. (2024) demonstrated that evidence-based AI dialogue reduces conspiracy beliefs by ~20% at 2-month follow-up. However, Baillargeon et al. (Science, 2025) found in 76,977 participants that persuasive power comes primarily from post-training and prompting methods (up to 51% boost), not personalization. This suggests a ceiling for generic approaches. At the E4/E5 boundary (Conformist to Self-Aware), individuals begin recognizing multiple perspectives but lack integration skills. Stage-calibrated dialogue scaffolding this transition should exceed the generic 20% effect. (https://www.science.org/doi/10.1126/science.aea3884)

Predicted effect: Cohen's d = 0.35-0.50 for stage-calibrated vs. generic at E4/E5, compared to d = 0.20-0.25 for the generic condition alone, based on extrapolation from the inoculation literature where matched interventions show medium-to-large effects (d = 0.9-1.3 for inoculation, but these are pre-exposure effects; post-exposure correction effects are typically smaller). (https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0280902)

### 2.2 Common Humanity Framing by Stage

**H9: "Common Humanity" framing produces larger belief changes at E5-E6 (Self-Aware/Conscientious) than at E3-E4 (Self-Protective/Conformist), where "in-group loyalty" framing is more effective.**

Rationale: At pre-conventional and conventional stages (E2-E4), moral reasoning is organized around group membership and conformity. Common Humanity framing requires post-conventional cognitive structures emerging at E5+. For E3-E4 participants, framing corrections as in-group loyalty ("this conspiracy was designed by foreign actors to weaken our country") may be more developmentally appropriate. This hypothesis is testable as a moderation effect within the stage-calibrated condition.

### 2.3 Discernment vs. Dependency (The Scaffolding Hypothesis)

**H10: H&M usage with explicit scaffolding/fading builds autonomous discernment skills, while usage without scaffolding/fading creates the dependency paradox documented by Becker et al. (2025).**

Rationale: Becker et al. found that unassisted performance declined by 15.3% over 4 weeks of AI-assisted misinformation detection, with 21% of participants classified as "Dependency Developers." However, Socratic questioning approaches showed positive correlation with independent detection (r=0.29). H&M should implement a fading protocol: Sessions 1-3 (full AI scaffolding with Socratic probing), Sessions 4-6 (reduced scaffolding, AI asks questions but withholds analysis), Sessions 7-8 (participant leads analysis, AI provides feedback only on request). (https://arxiv.org/html/2510.01537v1)

Predicted measurement: Performance on novel misinformation detection task (unassisted) at post-test and follow-up. Scaffolding/fading condition should show improvement (positive slope), while standard condition should show decline (negative slope per Becker et al.).

### 2.4 The Developmental Dip Hypothesis

**H11: Ego development stage moderates conspiracy susceptibility with a non-linear pattern: highest susceptibility at E3 (Self-Protective), a temporary increase at the E4/E5 transition, and progressive decline at E6+.**

Rationale: The E4/E5 transition involves questioning conformist assumptions. Paradoxically, this can increase openness to counter-narratives, including conspiracy theories, before the cognitive complexity needed to evaluate them develops at E5+. This "developmental dip" would be novel in the literature and has practical implications: individuals at E4/E5 may need different protective interventions than those at E3 (where the mechanism is different -- threat-based reasoning rather than counter-conformity).

### 2.5 Micro-Development vs. Macro-Development

**H12: AI-mediated Socratic dialogue accelerates micro-developmental shifts (sub-stage movement within STAGES methodology) more readily than macro-developmental stage transitions, with measurable sub-stage shifts after 8+ sessions.**

Rationale: Full ego stage transitions typically require years. Within-stage sophistication (early vs. late within a stage) can improve more rapidly. The STAGES methodology used by Bronlet (2025) provides sub-stage resolution that the original WUSCT does not, making this hypothesis testable.

### 2.6 Epistemic Humility

**H13: H&M dialogue increases epistemic humility (measured by calibrated confidence on factual claims) regardless of ego stage, suggesting a mechanism independent of developmental level.**

Rationale: Becker et al. (2025) found that confidence calibration as an AI strategy worsened independent performance (r=-0.42), but this was for AI-initiated calibration. Self-generated epistemic humility from Socratic questioning may have different effects. Measuring calibration (confidence vs. actual accuracy) provides a continuous outcome variable independent of belief content.

### 2.7 More in Common Segment Mapping

**H14: More in Common societal segments (Hidden Tribes) map to ego stage distributions, with the "Exhausted Majority" segments (Traditional Liberals, Passive Liberals, Politically Disengaged, Moderates -- ~67% of the US population) clustering at E4-E5, and "Wings" (Progressive Activists, Devoted Conservatives) showing bimodal distributions at E3 and E6+.**

Rationale: The Hidden Tribes study (More in Common, 2018) identified seven political segments based on core beliefs and group identities. The Exhausted Majority is characterized by ideological flexibility, nuanced views, and fatigue with polarization -- traits consistent with E4-E5 (Conformist transitioning to Self-Aware). The "Wings" segments show strong ideological commitment, which could reflect either rigid E3 identity (Self-Protective: ideology as identity defense) or principled E6+ commitment (Conscientious/Individualistic: ideology as integrated values). This bimodal prediction would distinguish ego development from simple ideological commitment. (https://hiddentribes.us/)

---

## 3. Experimental Design for H&M as Intervention

### 3.1 Four-Arm RCT Design

**Arm 1 -- Waitlist Control**: No intervention. Complete assessment battery at same intervals. Receive access to H&M after study completion.

**Arm 2 -- Generic AI Dialogue (Active Control)**: Replicates Costello et al. (2024) approach. GPT-4-class model provides personalized, evidence-based counterarguments to participant's stated conspiracy beliefs. No developmental calibration. 8 sessions over 6 weeks.

**Arm 3 -- Stage-Calibrated H&M Dialogue**: Socratic dialogue calibrated to participant's WUSCT-assessed ego stage. Dialogue complexity, question types, and framing adapted to developmental level. 8 sessions over 6 weeks. Full AI support throughout.

**Arm 4 -- Stage-Calibrated H&M with Scaffolding/Fading**: Same as Arm 3, but with progressive reduction of AI support. Sessions 1-3: full scaffolding. Sessions 4-6: reduced scaffolding (AI asks questions, withholds analysis). Sessions 7-8: participant leads, AI provides feedback only on request. Informed by Becker et al. (2025) finding that probing questions correlate with independent skill acquisition.

### 3.2 Sample Size Calculations

Based on existing effect sizes in the literature:

- Costello et al. (2024): ~20% belief reduction, translating to approximately d=0.30-0.40 for the main effect of AI dialogue vs. control
- Inoculation literature (systematic review): d=0.9-1.3 for pre-exposure inoculation, d=0.3-0.5 for post-exposure debunking (https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0280902)
- Estimated interaction effect (condition x ego stage): smaller, likely d=0.20-0.30

For the primary hypothesis (interaction of condition x ego stage on conspiracy belief change), using:
- Alpha = 0.05 (two-tailed)
- Power = 0.80
- Expected interaction effect d = 0.25
- 4 arms, accounting for 3-4 ego stage groupings

A conservative estimate requires **N=75-100 per arm** (300-400 total), accounting for ~20% attrition over the 6-month follow-up period. This is consistent with the Therabot RCT (N=210 across 2 arms; NEJM AI, 2025), scaled for more conditions. (https://ai.nejm.org/doi/abs/10.1056/AIoa2400802)

For an external pilot study, the recommendation is at least 70 measured subjects (35 per group) when estimating the standard deviation for a continuous outcome. (https://pmc.ncbi.nlm.nih.gov/articles/PMC3256489/)

### 3.3 Outcome Measures

**Primary outcome**: Change in Conspiracy Mentality Questionnaire (CMQ) score. The CMQ is a validated cross-cultural instrument (English, German, Turkish versions) measuring generic conspiracy mentality as a one-dimensional construct, with demonstrated test-retest stability. Cross-cultural sample validation: N=7,766 (Study 1a), N=141 for stability (Study 1b). Convergent validity with RWA, social dominance orientation, schizotypy, and paranoid ideation. (https://pmc.ncbi.nlm.nih.gov/articles/PMC3639408/)

**Secondary outcomes**:
- Right-Wing Authoritarianism scale (RWA; 22-item Altemeyer; alpha = 0.85-0.94). Validated predictor of science skepticism: students endorsing authoritarian values more likely to oppose scientific consensus on climate, GM food, and vaccination. (https://journals.sagepub.com/doi/full/10.1177/1368430221990104)
- Science skepticism items (standardized measure)
- Novel misinformation detection task (unassisted accuracy; binary scoring per Becker et al.)
- Calibrated confidence measure (confidence vs. actual accuracy gap)
- WUSCT pre/post (automated scoring via LLM, validated at group level by Bronlet 2025)

**Process measures**:
- Therapeutic alliance (WAI; benchmark from Therabot: mean=3.59, SD=1.27)
- Engagement metrics (messages sent, session duration, days active; Therabot benchmark: avg 260 messages, 24 days active, 6.18 hours over 4 weeks)
- Conversational pattern analysis (agreement, independent thinking, probing behaviors per Becker et al. taxonomy)

**Dependency indicators** (novel):
- Ratio of AI-initiated to participant-initiated analysis
- Decline rate in unassisted performance over sessions
- Self-reported cognitive offloading (qualitative coding of participant language shifts)

### 3.4 Follow-Up Schedule

- Pre-test: Full battery
- Post-test (Week 7): Full battery + novel misinformation task
- 2-month follow-up: CMQ, RWA, novel misinformation task (matching Costello et al. 2024 timeline)
- 6-month follow-up: Full battery (testing long-term durability and skill retention)

### 3.5 Ethical Considerations

- Pre-registration required (OSF or AsPredicted)
- IRB/ethics board approval at all participating institutions
- Informed consent regarding AI nature of dialogue partner
- Safety monitoring protocol (Therabot experienced 15 safety events requiring staff intervention in N=210; similar monitoring needed)
- Debriefing protocol for control group with delayed access to intervention
- Data sharing plan for dialogue transcripts (de-identified; cf. Becker et al. releasing 7,203 conversation pairs)

---

## 4. Grant Funding Pathways

### 4.1 DFG Priority Programme "Rethinking Disinformation" (Re:DIS, SPP 2573)

**Status**: Active call. This is the single most relevant funding programme.

The DFG established Re:DIS in March 2025, funded with EUR 6.9 million for the first 3-year period (2026-2029). The programme adopts "an epistemic perspective on disinformation" defined as "publicly disseminated content that worsens the epistemic position of recipients," encompassing conspiracy theories, fake news, propaganda, and political lies. (https://www.dfg.de/en/news/news-topics/announcements-proposals/2025/ifr-25-45)

**Why H&M fits**: Re:DIS explicitly seeks interdisciplinary research "at intersections between philosophy, psychology, law, computer science, linguistics and the social and political sciences." The H&M project bridges psychology (ego development) and computer science (AI dialogue systems). The programme particularly welcomes projects exploring "sophisticated and less-studied forms of disinformation," which stage-calibrated intervention qualifies as.

**Practical details**:
- Submission deadline: 1 November 2025
- Registration deadline: 18 October 2025
- Project duration: 36 months
- Start: Summer 2026
- Coordinator: Dr. Romy Jaster, Humboldt-Universitat zu Berlin (re-dis.philosophie@hu-berlin.de)
- DFG contact: Dr. Niklas Hebing (niklas.hebing@dfg.de)
- Outreach requirement: projects must develop outreach initiatives engaging practitioners, journalists, educators, and civil society actors

**Grant size**: Individual DFG Research Grants typically range EUR 200,000-500,000 for 3 years. Within the SPP, 6.9M across ~12-15 projects suggests EUR 400,000-600,000 per project.

### 4.2 Volkswagen Foundation: "Transformational Knowledge on Democracies under Change"

**Status**: Active, with two funding lines.

**Collaborative Projects line**: Up to EUR 1.3 million for 4-5 years. Teams must include 2-3 researchers from different disciplines plus 2-3 partners from outside academia (NGOs, government, media). Lead applicant must be affiliated with a German university or research institution. Application deadline: 9 September 2025. (https://www.volkswagenstiftung.de/en/funding/funding-offer/transformational-knowledge-democracies-under-change-transdisciplinary-perspectives)

**Task Forces line**: Up to EUR 180,000 for 1 year. Up to two researchers working with civil society partners on acute democracy challenges. Next call expected autumn 2026.

**Why H&M fits**: The programme addresses "transformation processes of democracies in times of multiple crises" and explicitly mentions "the effects of digitalisation and AI on democracies under change" as a topic area. The foundation encourages "new creative methods" and "scientific risks." The required non-academic partners could include media literacy organizations or democratic education NGOs.

**Recent track record**: The foundation funded 9 projects totaling ~EUR 1.6 million in a recent cycle, suggesting meaningful but selective support.

### 4.3 EU Horizon Europe Cluster 2: Culture, Creativity and Inclusive Society

**Status**: Active calls in 2025; new calls opening May 2026.

Cluster 2 has a budget exceeding EUR 2 billion. The Democracy and Governance intervention area funds research on threats to democracy including disinformation and online polarisation. (https://rea.ec.europa.eu/funding-and-grants/horizon-europe-cluster-2-culture-creativity-and-inclusive-society/democracy-and-governance_en)

**2025 call topics** (closing September 2025 / March 2026 for two-stage):
- "Fighting against disinformation while ensuring the right to freedom of expression" -- EUR 10.5M total, ~EUR 3-3.5M per project
- Counter disinformation and foreign information manipulation and interference (FIMI)

**2026-2027 work programme** (calls opening May 2026):
- Counter disinformation and FIMI (new topics)
- Impact of AI, cyberviolence, and deepfakes on equality, democracy and inclusive societies (2027 topic, directly relevant)
- Economic inequalities and their impact on democracy

**Grant size**: Typically EUR 3-3.5M per project for Research and Innovation Actions. Requires consortium of 3+ partners from 3+ EU member states.

**Fit assessment**: Strong topical fit but requires consortium building. The TITAN project (ACM IMX 2024) was funded under Horizon Europe, providing a direct precedent for Socratic AI disinformation research. (https://dl.acm.org/doi/10.1145/3639701.3663640)

### 4.4 Stiftung Mercator: Digital Society Programme

**Status**: Active institutional and project funding.

Stiftung Mercator focuses on "the creation of a democratic digital public sphere" and has funded projects including AlgorithmWatch and the Alexander von Humboldt Institute for Internet and Society (HIIG; EUR 4M institutional grant jointly with two other foundations). Specific funding for individual research projects is less structured than DFG/VW Foundation, typically through targeted calls or responsive mode. (https://www.stiftung-mercator.de/en/what-we-work-on/digital-society/)

**Fit**: Good thematic alignment but less clear application pathway. Best approached after establishing a track record through DFG or VW Foundation funding.

### 4.5 NSF (US): Social, Behavioral and Economic Sciences

**Status**: Significantly restricted as of 2025.

NSF has terminated awards related to misinformation/disinformation research, stating it "will not support research with the goal of combating 'misinformation,' 'disinformation,' and 'malinformation' that could be used to infringe on the constitutionally protected speech rights of American citizens." Hundreds of grants were cancelled. (https://www.science.org/content/article/nsf-officials-break-silence-how-ai-and-quantum-now-drive-agency-grantmaking)

**Implication**: NSF is not a viable funding pathway for this research under the current US administration. The project should focus on European funding sources (DFG, VW Foundation, Horizon Europe). A US collaborator (necessary for the More in Common Hidden Tribes angle, H14) could be funded through the European grant as an associated partner.

### 4.6 Funding Strategy Recommendation

**Priority 1 -- DFG Re:DIS (SPP 2573)**: Deadline November 2025. Most targeted fit. Moderate budget (EUR 400-600K). Apply for Phase 1 (instrument development) + Phase 2 (pilot RCT). Requires German institutional PI.

**Priority 2 -- VW Foundation Collaborative Projects**: Deadline September 2025. Larger budget (up to EUR 1.3M) for 4-5 years, covering full RCT. Requires non-academic partners. The transdisciplinary requirement is a strength for H&M given its applied orientation.

**Priority 3 -- Horizon Europe 2026-2027**: Opening May 2026. Largest budgets (EUR 3-3.5M per project) but requires consortium of 3+ countries. Use DFG pilot data as preliminary results. Build consortium around existing TITAN network.

Realistic timeline: Apply VW Foundation (Sept 2025) and DFG Re:DIS (Nov 2025) simultaneously. If either funds, use results to apply for Horizon Europe scale-up in 2026/2027.

---

## 5. Precedents for AI as Research Instrument in Psychology

### 5.1 WUSCT Automated Scoring

Bronlet (2025), published in Frontiers in Psychology, tested LLaMA-3-Instruct-70B (local), ChatGPT 3.5, ChatGPT 4, and Claude 3 against expert STAGES scorers. The weighted kappa of 0.779 represents "substantial agreement." The study validates group-level automated scoring but explicitly cautions against individual-level automated assessment. For H&M's research use case, this means: (a) group-level analysis of ego stage distributions is validated, (b) individual stage assignment for treatment arm calibration requires either additional validation work or human expert backup for borderline cases. (https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1488102/full)

### 5.2 AI as Intervention Platform: The Costello Paradigm

Costello, Pennycook & Rand (Science, 2024) established the paradigm for AI-mediated conspiracy belief intervention. Their methodology -- asking participants to describe belief reasons, then deploying AI counterarguments tailored to those reasons -- achieved a ~20% reduction sustained at 2 months. The study used N=2,190 participants, demonstrating that large-scale AI-mediated psychological intervention is feasible. The effect was robust even for deeply entrenched beliefs. (https://www.science.org/doi/10.1126/science.adq1814)

A follow-up study (PNAS Nexus, 2025) showed that the persuasion effect was not dependent on participants knowing they were interacting with AI. The effect held regardless of perceived messenger identity, confirming the mechanism is the evidence quality rather than AI authority. (https://academic.oup.com/pnasnexus/article/4/11/pgaf325/8285733)

### 5.3 AI as Dual Intervention/Measurement Platform: The Therabot Precedent

The Therabot RCT (NEJM AI, 2025) provides the closest precedent for AI serving as BOTH intervention and measurement platform. In a study of N=210 adults with MDD, GAD, or CHR-FED, the generative AI chatbot simultaneously (a) delivered therapeutic intervention and (b) generated data for outcome measurement through its interaction logs. Key metrics: 95% engagement rate, average 260 messages per participant, 24 days active, 6.18 hours total use. Therapeutic alliance (WAI mean=3.59) was comparable to traditional outpatient psychotherapy. Safety: 15 events requiring staff intervention, 13 inappropriate responses requiring correction. (https://ai.nejm.org/doi/abs/10.1056/AIoa2400802)

**Implication for H&M**: Therabot demonstrates that an AI system can simultaneously serve as intervention delivery vehicle AND generate measurement data through naturalistic interaction. H&M could similarly use dialogue patterns as process measures while delivering the Socratic intervention.

### 5.4 AI Political Persuasion at Scale

The largest-scale study of AI persuasion (Science, 2025; N=76,977 responses from 42,357 participants across 707 political issues with 19 LLMs) found that persuasive power stems primarily from post-training methods (+51%) and prompting (+27%), not personalization or model scale. Critically, increased persuasiveness was accompanied by decreased factual accuracy, with roughly half of explainable persuasion variation traced to information density alone. (https://www.science.org/doi/10.1126/science.aea3884)

**Implication for H&M**: H&M's Socratic approach (questioning rather than asserting) may avoid the accuracy-persuasion tradeoff identified in this study, because the mechanism is not information density but guided self-reflection. This is a testable differentiator.

### 5.5 The Dependency Problem: Critical Gap

Becker et al. (2025) identified the central challenge for AI-mediated interventions: the dependency paradox. While AI assistance improves immediate performance by 21%, unassisted performance degrades by 15.3% over 4 weeks. The five participant trajectory types (Progressive Learners 27%, Consistently Collaborative 18%, Growing Skeptics 12%, Persistent Self-Reliant 22%, Dependency Developers 21%) provide a taxonomy for analyzing H&M participants. (https://arxiv.org/html/2510.01537v1)

The critical finding for H&M design: Socratic probing questions were the ONLY strategy that positively correlated with independent skill acquisition (r=0.29 in unassisted conditions). This validates H&M's Socratic approach specifically as a discernment-building mechanism, distinguishing it from the evidence-delivery approach of Costello et al. The scaffolding/fading design in Arm 4 of the proposed RCT directly addresses this gap.

### 5.6 Measurement Instruments Summary

For the proposed research, the following validated instruments are recommended:

| Instrument | Construct | Items | Reliability | Citation |
|---|---|---|---|---|
| WUSCT (STAGES) | Ego development (E2-E9) | 32-36 stems | kappa=0.779 (LLM) | Bronlet 2025 |
| CMQ | Conspiracy mentality | 5 items | 1-factor, cross-cultural | Bruder & Imhoff 2013 |
| RWA Scale | Authoritarianism | 22 items | alpha=0.85-0.94 | Altemeyer 1996 |
| WAI | Therapeutic alliance | 12 items (short form) | validated | Horvath & Greenberg |
| Novel misinfo task | Discernment skills | Custom | Per Becker et al. design | Becker et al. 2025 |

---

## 6. Synthesis and Strategic Recommendations

### 6.1 What Makes This Proposal Novel

No existing study has combined all three elements: (1) developmental assessment (WUSCT/ego development), (2) stage-calibrated AI intervention, and (3) scaffolding/fading to prevent dependency. The closest precedents address only one element each:
- Costello et al. 2024: AI intervention for conspiracy beliefs, but not developmentally calibrated, not scaffolded
- Bronlet 2025: Automated WUSCT scoring, but for assessment only, not linked to intervention
- Becker et al. 2025: Identified dependency problem and Socratic solution, but not in the context of ego development or conspiracy beliefs specifically

### 6.2 Recommended Collaboration Structure

- **Lead PI**: Developmental psychologist with WUSCT/STAGES expertise (ideally connected to Bronlet's network)
- **Co-PI 1**: Political psychologist with conspiracy/authoritarianism expertise
- **Co-PI 2**: Computer scientist (H&M technical lead)
- **Non-academic partner**: Media literacy organization or democratic education NGO (required for VW Foundation)
- **International collaborator**: US-based researcher with More in Common data access (for H14)
- **Advisory board**: Include Costello, Pennycook, or Rand for methodology credibility

### 6.3 Risk Factors

1. **Individual WUSCT scoring accuracy**: Bronlet 2025 validated group-level only. Individual assignment to treatment arms based on automated scoring may introduce misclassification noise. Mitigation: human expert backup for borderline cases; sensitivity analysis excluding misclassified participants.
2. **NSF funding freeze**: US funding for disinformation research is currently blocked. European pathways are viable alternatives.
3. **Ethical review complexity**: AI-mediated psychological intervention raises novel ethics questions, particularly around informed consent and the boundary between research tool and therapeutic device.
4. **Replication of Costello et al.**: The ~20% effect size was observed in an online sample of conspiracy believers. Academic samples may show ceiling effects (lower baseline conspiracy belief). Sample recruitment strategy must target populations with elevated conspiracy mentality.

---

## Sources (Complete)

- Becker et al. 2025 -- AI dialogues reduce misinformation but build no discernment: https://arxiv.org/html/2510.01537v1
- Bronlet 2025 -- LLM STAGES scoring: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2025.1488102/full
- Bruder & Imhoff 2013 -- CMQ conspiracy mentality questionnaire: https://pmc.ncbi.nlm.nih.gov/articles/PMC3639408/
- Costello, Pennycook & Rand 2024 -- Durably reducing conspiracy beliefs: https://www.science.org/doi/10.1126/science.adq1814
- Costello et al. 2025 -- AI reduces conspiracy beliefs regardless of perceived identity: https://academic.oup.com/pnasnexus/article/4/11/pgaf325/8285733
- DFG Re:DIS SPP 2573 call: https://www.dfg.de/en/news/news-topics/announcements-proposals/2025/ifr-25-45
- EU Horizon Europe Cluster 2: https://rea.ec.europa.eu/funding-and-grants/horizon-europe-cluster-2-culture-creativity-and-inclusive-society/democracy-and-governance_en
- Heinz et al. 2025 -- Therabot RCT: https://ai.nejm.org/doi/abs/10.1056/AIoa2400802
- Inoculation systematic review -- effect sizes: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0280902
- Kerr & Wilson 2021 -- RWA predicts science rejection: https://journals.sagepub.com/doi/10.1177/1368430221992126
- Meyer et al. 2025 -- Street epistemologist chatbot: https://misinforeview.hks.harvard.edu/article/using-an-ai-powered-street-epistemologist-chatbot-and-reflection-tasks-to-diminish-conspiracy-theory-beliefs/
- More in Common -- Hidden Tribes: https://hiddentribes.us/
- NSF funding restrictions: https://www.science.org/content/article/nsf-officials-break-silence-how-ai-and-quantum-now-drive-agency-grantmaking
- Science 2025 -- Levers of AI political persuasion (N=76,977): https://www.science.org/doi/10.1126/science.aea3884
- Socrates 2.0 protocol: https://www.researchprotocols.org/2024/1/e58195/
- Stiftung Mercator -- Digital Society: https://www.stiftung-mercator.de/en/what-we-work-on/digital-society/
- TITAN Socratic AI vs Disinformation (ACM IMX 2024): https://dl.acm.org/doi/10.1145/3639701.3663640
- VW Foundation -- Democracies under Change: https://www.volkswagenstiftung.de/en/funding/funding-offer/transformational-knowledge-democracies-under-change-transdisciplinary-perspectives

Status: COMPLETE
