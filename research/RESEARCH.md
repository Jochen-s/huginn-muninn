# Huginn & Muninn: Research Foundation

**A comprehensive review of the scientific literature informing AI-mediated de-polarization through common humanity**

*Last updated: March 2026*

---

## Abstract

Huginn & Muninn is an open-source AI framework designed for disinformation analysis and de-polarization. Unlike conventional fact-checking tools, the framework addresses three sequential questions: What is true? Who benefits from this manipulation? What do we share as human beings? The framework integrates findings from seven research domains spanning approximately 370 reviewed sources, including AI-mediated Socratic dialogue, psychological inoculation, manufactured doubt detection, developmental psychology, cognitive apprenticeship theory, perspective-taking research, epistemic trust, and motivated reasoning. This document presents the scientific foundation for each pillar, provides an honest assessment of evidence strength, identifies known limitations and replication failures, describes proposed mitigations -- particularly for the AI dependency paradox and the depolarization durability challenge -- and proposes 15 testable hypotheses for academic collaboration. The goal is to make the framework's empirical basis transparent and subject to rigorous external evaluation.

---

## 1. Introduction: The Case for a New Approach

Disinformation is not primarily a problem of ignorance. People do not hold conspiratorial beliefs because they lack access to correct information; they hold them because those beliefs address real psychological needs -- for coherence, for in-group belonging, for explanations that match the felt experience of social grievance (Costello, Pennycook & Rand, 2024). This distinction matters because it shapes the design of any effective intervention.

Traditional fact-checking is necessary but demonstrably insufficient as a standalone mechanism. Studies of Facebook and Meta's fact-checking labels show reductions in resharing of approximately 10-15% -- meaningful, but far short of what a genuine de-polarization tool requires (van der Linden et al., 2022). More troublingly, AI-generated fact-checks can actively reduce epistemic quality under certain conditions. DeVerna et al. (2024) found that AI mislabeling true headlines as false reduced belief in those headlines by 12.75%, suggesting that the scalability advantage of automated fact-checking comes with a corresponding risk of scaled error propagation.

The so-called "backfire effect" -- the hypothesis that corrections to false beliefs cause those beliefs to strengthen -- has largely failed to replicate in recent literature and should be treated as a measurement artifact rather than a genuine psychological phenomenon. Studies pointing to backfire relied on individual difference measures that do not generalize across experimental conditions (Wood & Porter, 2019; PMC9283209, 2022). Standalone correction studies have similarly failed to demonstrate the effect under preregistered conditions (PMC10317933, 2023). A specific variant, the "familiarity backfire effect," also failed in a PLoS ONE 2023 replication. A 2020 meta-analysis found no reliable evidence for backfire across a broad set of experimental conditions. Corrections do work. What is essential, however, is to distinguish the debunked backfire effect from the continued influence effect (CIE), which is well-supported: corrected misinformation continues to influence reasoning even after people have accepted the correction. The CIE is real, durable, and constitutes the actual practical challenge facing de-polarization efforts.

A separate and foundational concern involves the relationship between persuasion and accuracy in AI dialogue systems. Bai, Voelkel et al. (2025, Science, doi:10.1126/science.aea3884) conducted a study across approximately 77,000 participants and 91,000 AI dialogues and found that the more persuasive an AI model is, the less accurate its information tends to be. This persuasion-accuracy tradeoff is not a flaw in any particular system; it appears to be a structural feature of language models optimizing for engagement. This finding directly shapes the design philosophy of the present framework: rather than optimizing for persuasion outcomes, the framework optimizes for reasoning capacity transfer. The goal is not to change minds directly but to equip minds to change themselves through improved reasoning. An AI system that produces belief change through persuasion rather than evidence-based reasoning is producing the wrong kind of change, for the wrong reasons, and likely with the wrong durability profile.

A separate body of evidence documents the active manufacture of public doubt by well-resourced actors. Goldberg, Vandenberg et al. (2021) identified 28 distinct tactics deployed across five industries -- tobacco, fossil fuel, sugar, pesticide, and climate denial -- over several decades. Five of those tactics appear in all five industries, suggesting a replicable playbook rather than spontaneous skepticism. This manufactured doubt infrastructure represents a systematic assault on public epistemic capacity that fact-checking alone is structurally unable to address.

What is needed is not a faster or more accurate fact-checker. What is needed is a tool that builds lasting critical-thinking capacity, transfers across topics, and reveals the shared circumstances that manufactured divisions are designed to obscure. The three-question framework is an attempt to construct such a tool on the available scientific evidence.

---

## 2. The Three-Question Framework

The framework organizes analysis around three sequential questions, each grounded in a distinct body of research.

**Question 1: "What is true?"** The first question deconstructs specific claims, traces actors and objectives, and maps the available evidence landscape. The goal is not to declare truth from algorithmic authority -- which replicates the dependency problems documented by Rani et al. (2025) and the persuasion-accuracy tradeoff documented by Bai et al. (2025) -- but to enable and model independent reasoning. The Socratic dialogue engine (Section 3.1) is the primary mechanism here.

**Question 2: "Who benefits from me feeling this way?"** The second question addresses manipulation literacy. It identifies which actors profit from the anger, fear, or distrust a piece of content is designed to generate, and maps the specific tactics being deployed against the Goldberg et al. (2021) taxonomy. This question is designed as a transferable cognitive skill: a person who learns to ask it about one piece of content is better equipped to ask it about the next. This directly addresses the manufactured doubt infrastructure described in Section 3.3.

**Question 3: "What do we share?"** The third question is the Common Humanity question. It is grounded in the Common Ingroup Identity Model (Gaertner & Dovidio, 2000) and deliberately focuses on concrete shared circumstances rather than abstract appeals. The critical distinction here -- developed further in Section 3.6 -- is between cognitive perspective-taking (which reduces polarization) and empathic concern (which can amplify it).

The three questions form a self-correcting system. Truth-checking alone creates dependency on external verdicts. Manipulation literacy alone produces cynicism without a constructive exit. Common humanity framing alone risks false equivalence between genuine scientific dispute and manufactured doubt. Together, each corrects the failure mode of the others.

The three questions also map directly to Pierre's (2025) 3M integrative model: Mistrust (addressed by Q3), Misinformation (addressed by Q1), and Motivated Reasoning (addressed by Q2). This correspondence suggests the framework has implicit theoretical coherence that will be made explicit in Section 4.5.

---

## 3. Core Research Pillars

### 3.1 Socratic AI Dialogue

The primary scientific foundation for AI-mediated Socratic dialogue is Costello, Pennycook and Rand (2024), published in Science. Across 2,190 participants, AI-driven Socratic dialogue produced a 20% durable reduction in conspiracy beliefs persisting at 2-month follow-up. The study received the 2026 AAAS Newcomb Cleveland Prize, the oldest prize in American science. The effect is notable both for its magnitude and its durability -- most attitude-change interventions decay significantly within weeks.

A key replication concern is addressed by Boissin et al. (2025, PNAS Nexus). In a preregistered study with N=955 participants, Socratic AI dialogue reduced conspiracy beliefs by 10 points. Critically, the effect persisted regardless of whether participants were informed they were speaking to an AI or believed they were speaking to a human (BF01 = 518,181.1 for the null hypothesis on messenger identity). This Bayes factor is exceptionally strong evidence that the framing of the dialogue as AI-delivered versus human-delivered does not explain the effect -- a finding that directly addresses the authority-framing objection raised in peer review.

Further support comes from Meyer et al. (2024, Harvard Kennedy School Misinformation Review), who tested a street epistemologist chatbot across N=2,036 participants. Reflective dialogue alone -- without introducing new factual content -- reduced conspiracy beliefs (d=0.37 for chatbot condition, d=0.42 for guided reflection on reservations). This result is significant: it demonstrates that the mechanism is not information delivery but reasoning facilitation. A notable limitation is that individuals with high conspiracy belief scores showed resistance rather than responsiveness, suggesting a ceiling or floor effect for extreme pre-existing commitment.

Stasielowicz (2026, European Journal of Social Psychology) provides essential context through the first comprehensive meta-analysis of conspiracy belief interventions: 273 effect sizes, N=27,996, average Hedges' g=0.16. Costello et al.'s 20% reduction is substantially above the meta-analytic average. Tailoring interventions to specific beliefs rather than generic belief systems pushes effect sizes above g=0.3. This analysis grounds the framework's effect size expectations in the actual distribution of findings across the literature rather than in the exceptional performance of a single landmark study.

This foundation is, however, substantially complicated by Rani et al. (2025, arXiv:2510.01537). Across a 4-week longitudinal design, Rani et al. found that while AI dialogue improved accuracy on targeted claims by 21.3%, it simultaneously degraded independent discernment skills by -15.3% by week four. Twenty-one percent of participants were classified as "Dependency Developers" -- users whose unassisted accuracy declined measurably while assisted accuracy improved. This is the dependency paradox, and it cannot be dismissed.

Note on the Rani et al. (2025) findings: this study remains an arXiv preprint as of March 2026 and has not completed peer review. The study's sample size (N=67) is small relative to the claims being made. The distinction between Socratic and directive dialogue approaches comes from a subgroup analysis within their own data, which may be underpowered to support the strength of claims drawn from it. The dependency paradox is a testable prediction that the present framework treats as a genuine risk to be mitigated; it is framed here as a strong hypothesis requiring replication rather than an established finding.

The resolution to the dependency paradox, where the evidence currently supports one, is in the methodological detail. Rani et al.'s own data distinguishes between dialogue design approaches. "Guiding and probing questions" -- genuine Socratic method -- correlated positively with independent detection skills (r = 0.29). Directive correction methods, where the AI asserts the correct answer rather than scaffolding the reasoning process, were associated with the dependency effects. The degradation of discernment is not inherent to AI dialogue; it is a predictable consequence of directive design. Section 5 develops the full mitigation architecture.

The formal peer critique of Costello et al. was published by Nabavi et al. (2025, Science, doi:10.1126/science.adu1526), raising scalability concerns regarding AI Socratic dialogue. Costello et al. responded directly (doi:10.1126/science.adu6608), addressing the scalability objections. These concerns are acknowledged and inform the staged deployment design of the framework, which is not designed for indiscriminate mass deployment but for opt-in use by individuals motivated to examine their own reasoning.

**Evidence assessment: STRONG foundation for the Socratic mechanism, with one unreplicated preprint (Rani et al.) identifying a critical design risk that is architecturally addressable. The persuasion-accuracy tradeoff (Bai et al. 2025, Science) mandates Socratic rather than persuasive interaction design.**

### 3.2 Inoculation and Prebunking

Psychological inoculation, developed principally by van der Linden and Roozenbeek at Cambridge, exposes people to weakened forms of manipulation techniques before full exposure -- analogous to a vaccine. The result is increased resistance to those techniques when encountered in the wild.

Google and Jigsaw deployed inoculation-based prebunking to 5.4 million YouTube users, measuring a 5-10% improvement in manipulation detection (van der Linden et al., Science Advances, 2022). The Cambridge field experiment with approximately 30,000 YouTube participants demonstrated that improved manipulation recognition extends to real-world conditions, not just laboratory tasks.

The most ecologically valid evidence to date comes from van der Linden et al. (2026), an Instagram field study with 375,597 users. A 19-second inoculation video produced a measurable effect (66% correct identification in the treatment group vs. 44% in control), with this difference maintained at 5-month follow-up (h=0.45). This directly addresses the real-world transfer gap identified in prior reviews: inoculation effects can persist in actual social media environments, not only in controlled laboratory settings.

A 2025 meta-analysis across 33 experiments (N=37,075) found that "inoculation improves discernment between reliable and unreliable news without inducing response bias" -- a critical finding, because many de-polarization interventions produce overcorrection (Simchon et al., 2025). Cross-cultural testing of the Bad News prebunking game showed effectiveness across all tested languages (Harvard Misinformation Review).

A JMIR meta-analysis across 42 studies (N=42,530, PMC10498317) extends this picture with an important caveat: inoculation improves credibility assessment but does not significantly influence sharing intention. People learn to identify misinformation but continue to share it at similar rates. This inoculation-sharing gap is a genuine limitation: if the behavioral target is reduced spread rather than reduced belief, inoculation alone is insufficient.

Five manipulation techniques have been validated as cross-topic transferable: emotionally manipulative language, incoherence, false dichotomies, scapegoating, and ad hominem attacks (Royal Society Open Science, 2022). These five techniques are computationally identifiable, making them natural targets for automated inoculation at scale.

A further limitation deserves explicit acknowledgment: inoculation hesitancy. Johnson and Madsen (2024, PMC11296080) found that those most in need of inoculation -- individuals with high existing conspiracy belief or strong partisan identity -- are least likely to voluntarily engage with prebunking interventions. This creates a systematic coverage gap: the population most at risk is the hardest to reach through opt-in mechanisms. The framework addresses this through embedded rather than standalone delivery, but the gap cannot be fully closed through design alone.

A significant limitation was identified by PNAS Nexus research in June 2025: "limited effectiveness of psychological inoculation against misinformation in a social media feed." Laboratory-validated effects may attenuate substantially in real-world social media contexts where competing stimuli, emotional arousal, and scrolling behavior are not controlled. The Instagram field study (van der Linden et al. 2026) provides partial reassurance, but this real-world transfer gap remains an active research question.

**Evidence assessment: MODERATE-STRONG. Best-replicated pillar in the framework, with new ecological validity evidence from a large Instagram field study. The inoculation-sharing gap and inoculation hesitancy are genuine unresolved limitations.**

### 3.3 Manufactured Doubt Detection

Goldberg, Vandenberg et al. (2021, Environmental Health, PMC7996119) conducted a documentary analysis identifying 28 tactics across five industries: tobacco, coal and fossil fuel, sugar, Atrazine/Syngenta pesticides, and the Marshall Institute's climate denial campaign. This work builds on and extends earlier scholarship by Proctor (1995) and Oreskes and Conway (2010).

An important methodological note: Goldberg et al. is documentary analysis, not a systematic review in the epidemiological sense. The authors acknowledge that no established coding criteria existed for this type of analysis and that attributing intent to organizational communications involves interpretive challenges. The strength of this work lies in its breadth across industries and its identification of converging tactical patterns; readers should calibrate their confidence accordingly and treat the specific tactic counts as heuristic rather than precise enumerations.

Five tactics appear universally across all five industries, constituting a core playbook:

1. Attack Study Design
2. Gain Support from Reputable Individuals
3. Misrepresent Data
4. Employ Hyperbolic Language
5. Influence Government and Laws

The complete Goldberg et al. taxonomy includes:

| Tactic | Tobacco | Fossil Fuel | Sugar | Pesticide | Climate Denial |
|---|---|---|---|---|---|
| Attack Study Design | Y | Y | Y | Y | Y |
| Gain Support from Reputable Individuals | Y | Y | Y | Y | Y |
| Misrepresent Data | Y | Y | Y | Y | Y |
| Employ Hyperbolic Language | Y | Y | Y | Y | Y |
| Influence Government/Laws | Y | Y | Y | Y | Y |
| Fund Biased Research | Y | Y | Y | Y | N |
| Manufacture Uncertainty | Y | Y | Y | N | Y |
| Conduct Stealth PR | Y | Y | Y | Y | N |
| Attack Researchers/Individuals | Y | Y | N | Y | Y |
| Reframe the Debate | Y | N | Y | Y | Y |
| Create/Fund Front Groups | Y | Y | Y | Y | N |
| Cherry-Pick Evidence | Y | Y | Y | Y | N |
| Withhold Negative Information | Y | Y | Y | N | Y |
| Shift Harm Framing | Y | Y | Y | N | N |
| Suppress Research | Y | Y | N | Y | N |
| Engage Think Tanks | Y | N | Y | N | Y |
| Exploit Regulatory Gaps | N | Y | Y | Y | N |
| Promote Alternative Hypotheses | Y | N | N | Y | Y |
| Delay/Undermine Policy | Y | Y | N | N | Y |
| Manipulate Media Narrative | Y | Y | N | N | Y |
| Litigation Strategy | Y | Y | N | Y | N |
| Astroturfing | Y | Y | Y | N | N |
| Intimidate Whistleblowers | Y | Y | N | Y | N |
| Use Social Media Amplification | N | Y | Y | N | Y |
| Appeal to Consumer Choice | Y | N | Y | N | N |
| Exploit Regulatory Capture | N | Y | N | Y | Y |
| Invoke Economic Threat | Y | Y | N | N | Y |
| Promote Self-Regulation | Y | Y | N | N | N |

The manufactured doubt playbook is not static. Coan et al. (2026, Communications Sustainability, PMC12983461) document a CARDS taxonomy revision reflecting a tactical evolution: modern denial has shifted from contesting the science directly to obstructing solutions -- accepting the scientific findings while manufacturing doubt about the feasibility, cost, or equity implications of proposed responses. This "solution obstruction" phase requires detection approaches that go beyond identifying science-denial rhetoric to identifying delay and obstruction framing.

Computational detection infrastructure also merits acknowledgment. Existing systems include: the CARDS classifier (RoBERTa-based, tested on 5 million tweets, Nature 2021); the FLICC+CARDS fallacy detector (DeBERTa architecture, F1=0.73); and the SemEval-2020 propaganda detection system covering 14 technique types with span-level identification. The DISARM framework provides a MITRE ATT&CK-style computational taxonomy of Tactics, Techniques, and Procedures (TTPs) for influence operations that complements the Goldberg et al. conceptual taxonomy with operationalized detection criteria.

Twelve of the 28 tactics rely on identifiable logical fallacies, making them candidates for computational detection. The framework distinguishes manufactured doubt from genuine scientific uncertainty using nine structural signatures. Manufactured doubt consistently concludes toward inaction regardless of evidence weight, shows funding-source correlation with regulated industries, applies asymmetric scrutiny to studies threatening industry interests, and shows documented internal-external contradiction -- the pattern Supran and Oreskes (2017) identified in ExxonMobil's internal research versus public communications. Genuine scientific uncertainty is specific and bounded, proposes constructive research programs, and engages peer review transparently.

A dual-use concern must be acknowledged explicitly. The same large language models capable of detecting manufactured doubt are also capable of generating it. Foundation for Defense of Democracies research (2026) found state-aligned propaganda in 57% of LLM responses when the models were not specifically constrained. This dual-use reality means detection systems must be designed with adversarial robustness in mind, not merely optimized for accuracy on clean test sets. The framework's anti-weaponization constraints (Section 8) address this at the design level, but the arms-race dynamic between detection and generation is an ongoing structural challenge.

**Evidence assessment: STRONG for tactic identification and historical documentation. Moderate for computational detection, which is advancing rapidly. The dual-use risk is real and requires explicit design constraints.**

### 3.4 The Perception Gap

More in Common (2019) found that Americans overestimate how extreme the other side's views are by approximately a factor of two. Counterintuitively, people who consume the most news have the most distorted perception -- not the least. Active news consumers tend to be exposed to the most extreme voices, which are also the most algorithmically amplified.

This finding carries an important limitation that requires explicit disclosure. The study was conducted exclusively with United States participants and has not been systematically replicated in other national contexts. The 2x overestimation figure may reflect specific features of the American two-party system, including the structural incentives of a winner-takes-all electoral arrangement that reward base activation over coalition-building. Whether the perception gap is comparable in multiparty systems, in non-democratic contexts, or across different cultural models of political conflict is not established by the available evidence.

**Evidence assessment: WEAK as a standalone pillar. The framework uses this finding cautiously as supportive context, not as a primary mechanism.**

### 3.5 Cognitive Apprenticeship and Framework Transfer

Collins, Brown and Newman (1989) identified a six-stage model of cognitive apprenticeship -- modeling, coaching, scaffolding, articulation, reflection, and exploration -- which predicts that delivering analysis outputs without progressive scaffolding will fail to produce internalized reasoning skills. A user who receives correct answers without working through the reasoning process may improve their accuracy on specific claims while remaining as vulnerable as before on novel ones. This maps directly to the dependency paradox identified by Rani et al. (2025).

Cohn et al. (2025, arXiv:2508.01503) provide contemporary empirical grounding for adaptive scaffolding with LLM agents, demonstrating 59-66% Zone of Proximal Development (ZPD) fidelity in an adaptive scaffolding framework. While an arXiv preprint requiring replication, this finding suggests that automated ZPD calibration is computationally feasible at the relevant precision levels. Tomisu et al. (2025, Frontiers in Education) independently developed a "Cognitive Mirror" framework applying reflective scaffolding to AI-assisted learning, converging on similar design principles through a different theoretical lineage.

The three-question framework is designed for transfer. Its value is not in any specific analysis output but in becoming an internalized habit of mind -- comparable to the scientific method or legal reasoning. The framework functions as a metacognitive prompt system in the sense defined by Halpern (1998): a four-part model for critical thinking with transfer, where thinking skills are accompanied by the metacognitive awareness of when and why to apply them.

Transfer research in educational psychology supports the generalizability of metacognitive skills. Skills trained in one domain -- including skills trained via AI-assisted practice -- generalize to novel contexts when the training is structured to develop principled understanding rather than surface-level pattern recognition (Metacognition and Learning, 2020). The three questions are designed to be domain-agnostic: they apply equally to a piece of climate disinformation, a political campaign message, or a corporate press release.

**Evidence assessment: STRONG. Decades of replication in educational psychology, with convergent contemporary evidence for automated scaffolding feasibility. Design implications are clear and well-specified.**

### 3.6 Perspective-Taking and Common Humanity

A critical distinction in the perspective-taking literature separates two mechanisms that are often conflated. Cognitive perspective-taking -- the intellectual effort to understand another person's viewpoint, circumstances, and reasoning -- consistently reduces intergroup polarization in experimental settings. Empathic concern -- feeling the other person's emotions -- can increase polarization by intensifying ingroup distress (Journal of Experimental Political Science). The framework targets cognitive perspective-taking specifically.

This distinction has now received cross-cultural replication beyond WEIRD samples. A study in the Netherlands (Journal of Experimental Political Science, Vol. 12, Issue 2, Summer 2025), N=1,258, confirmed the pattern in a multiparty European context: empathic concern fuels polarization while perspective-taking reduces it. This is significant because the Netherlands operates under a proportional representation system with high party fragmentation, quite different from the US two-party context where the original findings were obtained. The replication partially addresses the WEIRD limitation, though it remains within a Western European democratic framework.

The Common Ingroup Identity Model (Gaertner & Dovidio, 2000) provides the theoretical foundation for the third question. When two groups are recategorized as members of a superordinate "we" rather than an "us" and a "them," intergroup bias decreases measurably. The practical implication is that common humanity framing must invoke concrete shared circumstances -- shared economic vulnerability, shared environmental exposure, shared aspirations for children and community -- rather than abstract appeals to shared humanness, which are too cognitively diffuse to produce recategorization.

A design risk deserves explicit acknowledgment: the Common Ingroup Identity Model carries a known backfire risk for individuals with high subgroup identification. For these individuals, recategorization into a superordinate identity can threaten their subgroup identity, producing reactance rather than reduced bias. The dual identity model (maintaining subgroup salience while adding superordinate membership) mitigates this risk by framing common humanity as complementary to group identity rather than as a replacement for it. The framework's implementation should adopt dual identity framing rather than pure superordinate recategorization.

Relational frame theory-based perspective-taking training has shown effects stable at 5-month follow-up (PLOS ONE, 2025), suggesting that trained perspective-taking produces durable rather than ephemeral change. Technique-based inoculation -- the "Who benefits?" question -- similarly creates lasting resilience that transfers across topics and persists for months, connecting the manipulation literacy pillar directly to the common humanity pillar.

**Evidence assessment: MODERATE. Cognitive perspective-taking is trainable and durable; the empathic concern distinction must be maintained carefully in design. The dual identity framing should replace pure superordinate recategorization to reduce backfire risk.**

---

## 4. Limitations and Downgraded Pillars

### 4.1 Moral Reframing (Downgraded)

Moral reframing was originally considered as a core pillar, based on the program of research by Feinberg and Willer (2015-2019), which argued that political persuasion is more effective when messages are framed in terms of the target audience's moral foundations rather than the communicator's own. The intervention showed initial promise in laboratory conditions.

The pillar has since been downgraded to experimental-only status following six or more preregistered replication failures: Arpan et al. (2018), Berkebile-Weinberg et al. (2024), Crawford (2025), Hundemer et al. (2023), Kim et al. (2023), and a 2026 study with 2,009 conservative participants. The theoretical foundation is also questioned: "the evidence for cultural variation in moral psychology is at best weak" (moral-psychology.butterfill.com). If moral foundations are less culturally variable than the original theory assumed, the persuasion mechanism may be correspondingly weaker.

Moral reframing is retained in the framework as an opt-in experimental feature with explicit disclosure of the limited and contested evidence base. It is not presented as a validated mechanism.

### 4.2 Redirect Method (Contextual)

Moonshot's Redirect Method has cited a 224% engagement improvement. This figure measures watch time, not belief change or behavioral change. The RAND Corporation's assessment described the method as showing "promise" -- notably soft language that does not support causal claims about de-radicalization effectiveness. The method is retained as a potentially useful complementary signal for user engagement, not as a primary mechanism for belief change.

### 4.3 The WEIRD Sample Problem

The majority of foundational studies reviewed here used Western, Educated, Industrialized, Rich, Democratic (WEIRD) populations. Costello et al. (2024), More in Common (2019), Rani et al. (2025), and most of the moral reframing literature fall into this category. This limits the confidence with which findings generalize to Global South populations, non-democratic political contexts, or societies with fundamentally different media ecologies.

AI fact-checking accuracy compounds this concern. Available evidence suggests a "geo-political veracity gradient" in AI performance: accuracy declines by 6.2-12.1% for claims originating in the Global South, likely reflecting the geographic and linguistic distribution of AI training data. The Dutch replication (Section 3.6) partially addresses the concern for European multiparty contexts, but cross-cultural validation of all six pillars remains an active and open research gap.

### 4.4 The Depolarization Durability Challenge

The most significant structural challenge facing any depolarization intervention is not whether effects exist but whether they persist. Holliday, Lelkes and Westwood (2025, PNAS, Vol. 122, Issue 39) conducted the most comprehensive meta-analysis of depolarization treatment effects available: 77 treatments drawn from 25 published studies, finding an average 5.4-point shift on a 101-point affective polarization scale. Critically, approximately 75% of this effect decayed within one week of the intervention ending. This is not a finding specific to any single approach -- it holds across studies and designs. Any framework that does not explicitly address durability is building on a known fault line.

The picture is more nuanced, however. Hall et al. (2025, PNAS), using a multi-treatment-over-time design with N=2,184 participants, found that repeated exposure to depolarization interventions produced durable effects at four-week follow-up (-3.92 points on general affective polarization, -2.60 on interpersonal affective polarization). The contrast between Holliday et al. and Hall et al. suggests that single-shot interventions produce ephemeral warmth toward the outparty, while multi-session interventions that accumulate over time can produce durable attitude change.

This distinction is theoretically significant for the present framework. Holliday et al.'s decaying effects are primarily attributable to interventions targeting affective warmth -- how positively participants feel toward political outgroups. Affective warmth is a fluctuating emotional state; it is expected to decay when situational reinforcement is removed. The three-question framework does not primarily target affective warmth. It targets cognitive skill transfer: the ability to recognize manipulation tactics, reason about evidence, and deploy perspective-taking intentionally. Educational psychology has a well-established literature demonstrating that skills trained to criterion through spaced practice with desirable difficulties persist significantly longer than attitude changes induced through exposure (Bjork, 1994). The framework's multi-session Socratic design aligns with Hall et al.'s positive durability findings rather than with the single-shot interventions driving Holliday et al.'s decay findings.

The honest assessment, however, is that this argument is a theoretical prediction, not an empirical finding specific to this framework. The RCT design proposed in Section 7 specifically includes six-month follow-up measurement to test whether the skill-transfer mechanism does in fact produce the greater durability the theory predicts.

### 4.5 Missing Theoretical Frameworks

Several theoretical frameworks with direct empirical relevance to the three-question approach have not been explicitly integrated into the framework's published architecture. This section addresses that gap.

**Epistemic trust (Fonagy).** Fonagy's model of epistemic trust, developed from attachment theory and mentalization research, proposes that human beings are pre-wired to learn from "ostensive cues" -- signals that a communicator is trustworthy and relevant to personal circumstances. In this model, conspiracy beliefs and receptivity to manufactured doubt are not failures of intelligence but failures of calibrated epistemic vigilance: the regulatory system governing what information sources are treated as trustworthy has become miscalibrated, either toward excessive credulity (in mainstream information sources) or excessive skepticism (which manufactured doubt campaigns deliberately induce). Three recent empirical studies connect epistemic trust to conspiracy belief specifically: Tanzer et al. (2024), Hauschild et al. (2024), and a 2025 medRxiv preprint. Importantly, the epidemiology here is not straightforward: Hauschild et al. found that high epistemic trust can correlate with both reduced misinformation susceptibility and increased paranoid ideation, suggesting that the goal is calibrated epistemic vigilance rather than simply increasing trust. This refinement is operationally important for the framework's design.

**Motivated reasoning (Kunda, 1990; updated Saucier et al., 2025).** Kunda's foundational work established that people engage in motivated reasoning -- reasoning backward from preferred conclusions rather than forward from evidence -- when their identity or emotional investment is engaged. Kahan's subsequent program of research on identity-protective cognition extends this finding in a counterintuitive direction: the most cognitively sophisticated people (by numeracy, scientific literacy, and reflective reasoning measures) are often the most polarized, because greater cognitive capacity is deployed in defense of identity-consistent conclusions rather than in pursuit of accurate ones. This finding has direct implications for the framework's design priorities. If cognitive skill in the abstract were sufficient, more educated people would be less polarized. They are not. This supports the priority given to Q3 (common humanity framing) alongside Q1 (cognitive skills): the question "What do we share?" is not supplementary to critical thinking; it addresses the motivated context in which critical thinking operates.

**Need for cognitive closure (Kruglanski).** The Need for Cognitive Closure (NCC) construct describes individual differences in tolerance for ambiguity and desire for definitive answers. Individuals high in NCC are more susceptible to belief systems that offer comprehensive explanatory frameworks -- including conspiracy theories, which explain complex and threatening events through coherent intentional agency. Socratic dialogue directly targets NCC by deliberately holding closure in abeyance: rather than providing answers, it requires the interlocutor to engage with uncertainty. This is not a side effect of the Socratic method but one of its core mechanisms of action.

**Pierre's (2025) 3M model.** Joseph Pierre's integrative model of conspiracy belief proposes three interacting factors: Mistrust (of institutions and mainstream sources), Misinformation (exposure to false content), and Motivated Reasoning (identity-protective cognition). The three questions of the present framework map cleanly to these three factors: Q3 (common humanity) addresses the social Mistrust that drives outgroup attribution; Q1 (what is true?) addresses Misinformation directly; Q2 (who benefits?) addresses Motivated Reasoning by surfacing the manipulation design. While Pierre's 3M model has not been empirically tested as an integrative framework -- as of March 2026 it remains a theoretical proposal -- the structural correspondence provides theoretical grounding for why the three questions address the problem comprehensively rather than partially.

**The rational conspiracy believer challenge (Synthese, 2025).** A 2025 philosophical critique published in Synthese challenges the implicit assumption in many conspiracy belief interventions that conspiratorial reasoning is inherently irrational. The critique argues that conspiracy-adjacent reasoning can be "rationally reconstructed" in formal terms, and that interventions that simply assert the incorrectness of conspiracy beliefs "lack the diagnostic tools to distinguish between rational and irrational belief updating." The historical record supports this concern: Watergate was a genuine conspiracy. The Tuskegee syphilis study was a genuine government conspiracy. The tobacco industry's internal suppression of smoking-cancer research was a genuine corporate conspiracy. A framework that dismisses conspiracy reasoning categorically will misclassify historically vindicated beliefs alongside clearly false ones. The Socratic method is the strongest available response to this challenge precisely because it does not assert the incorrectness of any belief. It builds reasoning capacity without asserting conclusions, leaving the interlocutor to reach and own their own judgments.

---

## 5. The Dependency Paradox and Its Resolution

The dependency paradox identified by Rani et al. (2025) is the most significant internal challenge to the framework's stated goals. If AI dialogue simultaneously improves accuracy on AI-assisted tasks and degrades independent discernment skills, then a framework designed to build lasting critical thinking capacity is at risk of producing the opposite effect at scale.

The paradox is, however, resolvable. It is not an inherent property of AI dialogue; it is a predictable consequence of directive design. Four architectural pillars address it:

**Pillar 1: Genuine Socratic method.** The dialogue engine is constrained to ask rather than tell. Rani et al.'s (2025) own data shows that guiding and probing questions correlate positively with independence (r=0.29), while directive correction correlates with dependency. Every interaction is designed to model the three-question reasoning process, not to deliver its conclusions. The persuasion-accuracy tradeoff (Bai et al. 2025) reinforces this constraint: a dialogue engine optimizing for persuasion would move users toward both incorrect information and diminished autonomy.

**Pillar 2: Mandatory scaffolding with fading.** Vygotsky's Zone of Proximal Development applied to AI assistance predicts that without systematic withdrawal of support over time, AI creates what arXiv:2511.12822 (2025) terms a "Zone of No Development" -- a persistent state of assisted competence that never matures into autonomous skill. The framework implements a progressive fading schedule: early sessions provide fuller scaffolding; later sessions require greater independent effort before AI feedback is provided.

**Pillar 3: Desirable difficulties.** Bjork (1994) identified a class of conditions -- spacing, interleaving, retrieval practice, and generation effects -- that slow initial acquisition but improve long-term retention by up to 80% compared to standard training. The framework requires users to attempt analysis before seeing AI output (generation effect), interleaves assisted and unassisted practice sessions, and spaces review of covered material. These conditions are deliberately uncomfortable; that discomfort is the mechanism.

**Pillar 4: System-regulated access.** Wharton research (2025) found that system-regulated AI access -- where the system controls when assistance is available -- produces 64% learning gains versus 30% for unrestricted on-demand access. When users can always obtain AI assistance immediately, they optimally do so; when the system enforces independent effort periods, learning accumulates. The framework implements rate-limiting and forced self-assessment sequences to structure access.

Seven concrete design patterns implement these pillars: forced self-assessment before AI feedback is available; session-level rate-limiting; a progressive fading schedule with explicit milestones; interleaving of assisted and unassisted practice; reflection prompts requiring users to articulate their reasoning in their own words; independence milestones tracked across sessions; and a graduation model in which users who demonstrate sustained independent discernment are flagged for reduced scaffolding.

The graduation model encapsulates the framework's core commitment: the tool is designed to make itself unnecessary. The three questions belong to the user. The AI system is a temporary scaffold, not a permanent prosthesis.

---

## 6. The Ego Development Connection

Jane Loevinger's model of ego development (stages E2-E9) describes psychosocial maturity as a sequential developmental process independent of intelligence, personality, or socioeconomic status (Loevinger & Le Xuan Hy, 1996). Cross-cultural validity has been demonstrated in international longitudinal studies (Dehgani et al., 2021; Le Xuan Hy, 1998). The model describes the development of increasingly complex and differentiated ways of making meaning -- not better values, but greater capacity to hold complexity, tolerate ambiguity, and maintain a self-authored rather than socially scripted identity.

**The susceptibility gradient as an untested hypothesis.** The following discussion of differential conspiracy susceptibility by ego stage is a theoretical prediction, not an established empirical finding. No published study has directly administered the WUSCT or STAGES instrument alongside a validated conspiracy belief measure (such as the CMQ) and reported the correlation. The hypothesis that ego stage negatively predicts conspiracy belief is highly plausible given the theoretical alignment of stage characteristics with known risk factors for conspiracy belief, but it is a hypothesis awaiting empirical test. Readers should interpret the following discussion as theoretical grounding for H1 and H15, not as documentation of confirmed findings.

Stage E4 (Conformist) is of particular theoretical relevance. It is characterized by: highest susceptibility to conspiracy theories and authoritarian belief systems (on theoretical grounds); dichotomous ingroup/outgroup thinking; orientation toward group and authority norms as the primary source of identity and moral guidance; and low tolerance for plurality or ambiguity. These characteristics map directly to Adorno's authoritarian character structure. At this stage, manufactured doubt tactics that leverage ingroup loyalty and authority endorsement would be expected -- on theoretical grounds -- to be maximally effective.

Stage E6 (Conscientious) and above are characterized by: internalized moral codes not contingent on group membership; tolerance of diversity and individual differences; self-reflection; and the capacity to hold conflicting perspectives simultaneously. These characteristics predict resilience against ideologization. Research by Holt (1980) suggested that at least 55% of the US adult population may not yet operate at E6, a finding with implications for estimating the scale of population-level vulnerability to manufactured doubt campaigns.

A further complication is introduced by Pennycook et al. (2025), who found that overconfidence in one's own reasoning ability -- rather than low reasoning ability per se -- is among the most reliable predictors of conspiracy belief endorsement. This finding is consistent with the motivated reasoning literature (Kahan): the relevant risk factor is not insufficient cognitive capacity but a metacognitive failure to recognize the limits of one's own reasoning. A 2025 study on metacognitive sensitivity deficits found that conspiracy-prone individuals show reduced ability to detect when their own reasoning has gone wrong -- they generate incorrect answers with high confidence rather than with appropriate uncertainty. These overconfidence and metacognitive sensitivity findings should be treated as candidate mediating variables in the ego development-conspiracy belief relationship.

Recent work by Bronlet (2025, Frontiers in Psychology) achieved a weighted kappa of 0.779 using GPT-4o for automated WUSCT (Washington University Sentence Completion Test) scoring, approaching the 0.80 threshold conventionally considered reliable measurement. It should be noted that this validation was conducted on a sample of 58 cases only, which is small for establishing psychometric reliability. Replication with larger and more diverse samples is required before large-scale automated ego stage assessment can be treated as validated. The finding is promising but preliminary.

The practical implication -- subject to empirical confirmation -- is that dialogue design should be calibrated to developmental stage. At E3-E4, authority-aligned framing and clear ingroup benefit are the appropriate entry points. At E5 (Self-Aware), guided perspective-taking becomes accessible. At E6, evidence-based Socratic questioning is developmentally appropriate. At E7 and above, systems thinking and meta-cognitive reflection are both accessible and motivating.

---

## 7. Testable Hypotheses

The framework generates the following testable hypotheses, each of which can be addressed through the proposed experimental design below or through independent replication.

**H1:** Conspiracy belief, measured by the Conspiracy Mentality Questionnaire (Bruder et al., 2013), negatively correlates with ego development stage in a linear relationship.

**H2:** Authoritarian attitudes (Right-Wing Authoritarianism scale, Altemeyer, 1996) are less prevalent at E6+ than at E2-E4.

**H3:** Antifeminism and reactionary masculinity norms are less prevalent at E6+ than at E2-E4.

**H4:** Science skepticism is less prevalent at E6+ than at E2-E4.

**H5:** Market-radical attitudes (support for unregulated markets as a moral good) are less prevalent at E6+ than at E2-E4.

**H6:** Political violence endorsement is less prevalent at E6+ than at E2-E4.

**H7:** More in Common (2019) societal types (Open, Stabilizers, Established, Angry, Pragmatic, Disillusioned) map to significantly different ego stage distributions.

**H8:** Stage-calibrated Socratic dialogue produces more durable belief change than generic AI dialogue, particularly at the E4/E5 transition, where developmental susceptibility and cognitive openness intersect.

**H9:** Common Humanity framing is more effective at E5-E6 than at E3-E4, where ingroup loyalty framing is developmentally appropriate and concrete shared circumstances outperform abstract appeals.

**H10:** Scaffolding with systematic fading prevents AI dependency, measured by unassisted performance on novel claims not covered in prior sessions.

**H11:** There is a non-linear "developmental dip" at the E4/E5 transition, where the loosening of conformist identity structures temporarily increases openness to counter-narratives, including conspiratorial ones, before consolidating at a more differentiated level.

**H12:** AI-mediated dialogue produces measurable sub-stage shifts after 8 or more sessions, though full stage transitions require longer timeframes and likely require real-world experiential conditions beyond what an AI dialogue system can provide.

**H13:** Epistemic humility -- calibrated confidence in one's own assessments -- increases as a stage-independent effect of Socratic dialogue, independent of initial ego development stage.

**H14:** More in Common segment membership interacts with ego development stage to predict differential intervention response patterns, with segment membership accounting for context-specific values and stage accounting for meaning-making structure.

**H15:** Ego development stage, assessed by WUSCT automated scoring (Bronlet, 2025), negatively predicts conspiracy belief (CMQ), with overconfidence (as measured by calibration tasks) and metacognitive sensitivity (as measured by signal detection paradigms) as mediating variables.

### Proposed Experimental Design

A four-arm randomized controlled trial is proposed, complying with SPIRIT-AI reporting requirements for AI-involved clinical and behavioral trials:

- **Arm 1 (active control):** AI conversation on an unrelated topic (matched for session duration and conversational engagement, but without any misinformation-relevant content). This replaces a passive waitlist control to allow separation of non-specific AI conversation effects from specific Socratic misinformation dialogue effects.
- **Arm 2 (generic AI dialogue):** AI dialogue without stage calibration or Socratic constraints
- **Arm 3 (stage-calibrated dialogue):** AI dialogue calibrated to assessed ego stage without scaffolding fading
- **Arm 4 (stage-calibrated with scaffolding/fading):** Full framework as designed

**N = 2,460 total (615 per arm)**

The power analysis is updated from the original proposal. Based on the Stasielowicz (2026) meta-analytic average of g=0.16 as the minimum detectable effect, and targeting 80% power at alpha=0.05 for the primary comparison (Arm 1 vs. Arm 4), N=615 per arm is required. This replaces the prior estimate of 75-100 per arm, which was underpowered for realistic effect sizes.

**Primary outcome:** Conspiracy Mentality Questionnaire (CMQ; Bruder et al., 2013)

**Secondary outcomes:**
- Right-Wing Authoritarianism scale (RWA; Altemeyer, 1996)
- Washington University Sentence Completion Test automated scoring (WUSCT; Bronlet, 2025)
- Novel misinformation detection accuracy on unassisted tasks (behavioral measure)
- Calibrated confidence scores assessing metacognitive accuracy (behavioral measure)
- Epistemic Trust and Mistrust in Others -- Conspiracy Questionnaire (ETMCQ; Hauschild et al., 2024) as a mediating variable

**Behavioral outcome measures** are included alongside self-report to enable detection of the inoculation-sharing gap: participants will encounter novel misinformation content during follow-up assessments and their behavioral responses (sharing intent, sharing behavior via simulated feed) will be measured, not only their self-reported beliefs.

**Follow-up:** 2 months and 6 months post-intervention

**Pre-registration:** Open Science Framework (osf.io) prior to data collection

---

## 8. Epistemic Safeguards

The framework implements four categories of epistemic safeguard to prevent harm, weaponization, and false equivalence.

**Epistemic asymmetry detection.** When scientific consensus is overwhelming -- defined operationally as greater than 95% agreement among relevant experts in peer-reviewed literature -- bridge-building framing is overridden. The framework does not create false equivalence between well-established science and manufactured doubt. This applies unconditionally to climate change, vaccine safety, evolutionary biology, and other domains where the manufactured doubt playbook has been documented.

**Red lines.** Three categories of content trigger non-negotiable refusal: scientific consensus claims supported by documented manufactured doubt campaigns; content involving dehumanization of individuals or groups; and content that constitutes incitement to violence. These red lines are not subject to context-based override.

**Anti-weaponization constraints.** The Socratic dialogue engine is constrained against redirection toward undermining belief in verified truths. An adversarial review function red-teams every analysis for bias, overreach, and false equivalence before output is delivered. This is a structural safeguard, not a post-hoc review.

**Source verification.** All AI-generated counterevidence must trace to verifiable sources. The Tow Center (2025) found that AI search engines have citation inaccuracy rates exceeding 60%, making source verification non-optional rather than a quality enhancement. Given documented jailbreak success rates of 97.14% for large reasoning models (Nature Communications, 2026), mandatory adversarial testing is required before any public-facing deployment.

---

## 9. Open Research Questions

The following questions are currently unresolved and represent opportunities for academic collaboration:

- **Combined-system efficacy:** No study has tested the three-question framework as an integrated intervention. All component-level evidence comes from separate studies. The integrated effect may differ substantially from the sum of component effects.

- **Cross-cultural validation:** All six core pillars require validation beyond WEIRD populations. This includes both the psychological mechanisms (Socratic dialogue, perspective-taking) and the detection systems (manufactured doubt taxonomy, computational classifiers trained primarily on English-language Western content).

- **Long-term internalization measurement:** No validated psychometric instrument currently measures whether a cognitive framework has been genuinely internalized versus temporarily accessible. This is a methodological gap that limits the testability of the framework's core claim.

- **The developmental dip (H11):** The hypothesis that the E4/E5 transition involves a period of heightened vulnerability to counter-narratives is theoretically grounded but empirically untested. It has significant implications for how the framework should handle users at this transition point.

- **Manufactured doubt in non-Western contexts:** The Goldberg et al. (2021) taxonomy was derived from Western corporate contexts. State-sponsored disinformation -- a different structural actor with different tactical repertoires -- may not be fully captured by the existing taxonomy. The DISARM framework addresses influence operations more broadly, but the overlap and gaps between the two require systematic mapping.

- **Multilingual Socratic dialogue:** Socratic questioning that is productive in one cultural context may be face-threatening or counterproductive in another. This question is empirically unaddressed at the level of cultural pragmatics.

- **Interaction between ego development stage and manufactured doubt susceptibility:** H1-H6 address univariate relationships. The multivariate interaction -- whether certain stages are differentially susceptible to specific manufactured doubt tactics -- is unstudied.

- **Ego development-conspiracy direct correlation:** The absence of a published study directly correlating WUSCT/STAGES scores with CMQ scores is a fundamental gap. H15 directly addresses this and should be treated as a research priority.

- **Epistemic trust as a mechanism:** Whether epistemic trust mediates the relationship between ego development and conspiracy belief (as proposed in Section 4.5) is theoretically plausible but empirically untested as a mediation model.

- **Inoculation-sharing gap at the behavioral level:** The JMIR meta-analysis finding that inoculation does not reduce sharing intention has not been tested with behavioral rather than self-reported sharing measures. The discrepancy between stated intent and actual behavior may reduce or amplify this gap.

---

## References

Altemeyer, B. (1996). *The authoritarian specter*. Harvard University Press.

Arpan, L. M., et al. (2018). Moral reframing of climate change: A failed experiment. *Environmental Communication*. Preregistered replication.

Bai, H., Voelkel, J. G., Eichstaedt, J. C., & Willer, R. (2025). Artificial intelligence can persuade humans on many topics; topic characteristics predict persuasion. *Science*. doi:10.1126/science.aea3884

Rani, A., Danry, V., Liang, P. P., Lippman, A. B., & Maes, P. (2025). Dialogues with AI reduce beliefs in misinformation but build no lasting discernment skills. arXiv:2510.01537. [Preprint, not peer-reviewed]

Berkebile-Weinberg, M., et al. (2024). Preregistered replication of moral reframing effects. Unpublished manuscript.

Bjork, R. A. (1994). Memory and metamemory considerations in the training of human beings. In J. Metcalfe & A. Shimamura (Eds.), *Metacognition: Knowing about knowing*. MIT Press.

Boissin, E., Costello, T. H., Spinoza-Martin, D., Rand, D. G., & Pennycook, G. (2025). Dialogues with large language models reduce conspiracy beliefs even when the AI is perceived as human. *PNAS Nexus*, *4*(11), pgaf325. doi:10.1093/pnasnexus/pgaf325

Bronlet, T. (2025). Leveraging large language models to classify sentences: A case study applying STAGES scoring methodology. *Frontiers in Psychology*. doi:10.3389/fpsyg.2025.1488102

Bruder, M., Haffke, P., Neave, N., Nouripanah, N., & Imhoff, R. (2013). Measuring individual differences in generic beliefs in conspiracy theories across cultures. *Frontiers in Psychology*, *4*, 225.

Coan, T. G., Malla, R., Nanko, M. O., Kattrup, W., Roberts, J. T., Cook, J., & Boussalis, C. (2026). Large language model reveals an increase in climate contrarian speech in the United States Congress. *Communications Sustainability*, *1*(1). PMC12983461. doi:10.1038/s44458-025-00029-z

Cohn, C., et al. (2025). Adaptive scaffolding with LLM agents: ZPD fidelity in AI-assisted learning. arXiv:2508.01503. [Preprint, not peer-reviewed]

Collins, A., Brown, J. S., & Newman, S. E. (1989). Cognitive apprenticeship: Teaching the crafts of reading, writing, and mathematics. In L. B. Resnick (Ed.), *Knowing, learning, and instruction*. Lawrence Erlbaum.

Costello, T. H., Pennycook, G., & Rand, D. G. (2024). Durably reducing conspiracy beliefs through dialogues with AI. *Science*, *385*(6714). doi:10.1126/science.adq1814

Crawford, J. T. (2025). Preregistered failure to replicate moral reframing. Unpublished preprint.

Dehgani, S., et al. (2021). Cross-cultural validation of Loevinger's ego development model. *International Journal of Behavioral Development*, *45*(3), 210-221.

DeVerna, M. R., et al. (2024). AI fact-checking and the risk of overcorrection. *PNAS*, 2322823121. doi:10.1073/pnas.2322823121

Feinberg, M., & Willer, R. (2015). From gulf to bridge: When do moral arguments facilitate political influence? *Personality and Social Psychology Bulletin*, *41*(12), 1665-1681.

Fonagy, P., & Allison, E. (2014). The role of mentalizing and epistemic trust in the therapeutic relationship. *Psychotherapy*, *51*(3), 372-380.

Gaertner, S. L., & Dovidio, J. F. (2000). *Reducing intergroup bias: The Common Ingroup Identity Model*. Psychology Press.

Goldberg, R. F., Vandenberg, L. N., et al. (2021). The science of spin: Targeted strategies to manufacture doubt with the public health community's research. *Environmental Health*, *20*, 33. PMC7996119. doi:10.1186/s12940-021-00723-0

Hall, M. E. K., Solomon, B. C., Voelkel, J. G., Stagnaro, M. N., Chu, J. Y., & Willer, R. (2025). Durably reducing partisan animosity through multiple scalable treatments. *PNAS*, *122*(19), e2424414122. doi:10.1073/pnas.2424414122

Halpern, D. F. (1998). Teaching critical thinking for transfer across domains. *American Psychologist*, *53*(4), 449-455.

Hauschild, S., Kasper, L. A., Berning, A., & Taubner, S. (2023). The relationship between epistemic stance, mentalizing, paranoid distress and conspiracy mentality: An empirical investigation. *Research in Psychotherapy: Psychopathology, Process and Outcome*, *26*(3), 706. doi:10.4081/ripppo.2023.706

Holliday, D., Lelkes, Y., & Westwood, S. J. (2025). Why depolarization is hard: A meta-analysis of affective polarization treatments. *PNAS*, *122*(39), e2508827122. doi:10.1073/pnas.2508827122

Holt, R. R. (1980). Loevinger's measure of ego development: Reliability and national norms for male and female short forms. *Journal of Personality and Social Psychology*, *39*(5), 909-920.

Hundemer, G., et al. (2023). Preregistered test of moral reframing on immigration attitudes. *Political Psychology*.

Johnson, H. M., & Madsen, J. K. (2024). Inoculation hesitancy: Who engages with prebunking and who does not. *Royal Society Open Science*, *11*(6). PMC11296080. doi:10.1098/rsos.231711

Kim, Y., et al. (2023). Replication attempt of moral reframing effects across political topics. *Journal of Experimental Social Psychology*, *104*, 104420.

Kruglanski, A. W. (1989). *Lay epistemics and human knowledge: Cognitive and motivational bases*. Plenum Press.

Kunda, Z. (1990). The case for motivated reasoning. *Psychological Bulletin*, *108*(3), 480-498.

Le Xuan Hy, & Loevinger, J. (1998). *Measuring ego development* (2nd ed.). Lawrence Erlbaum.

Loevinger, J., & Le Xuan Hy. (1996). *Measuring ego development* (2nd ed.). Lawrence Erlbaum.

Metacognition and Learning. (2020). Transfer of metacognitive skills across domains: A review. *Metacognition and Learning*, *15*, 1-28.

Meyer, M., Enders, A., Klofstad, C., Stoler, J., & Uscinski, J. (2024). Using an AI-powered "street epistemologist" chatbot and reflection tasks to diminish conspiracy theory beliefs. *Harvard Kennedy School Misinformation Review*, *5*(6). doi:10.37016/mr-2020-164

More in Common. (2019). *The perception gap: How false impressions of each other divide American democracy*. moreincommon.com.

Nabavi, R., et al. (2025). Scalability concerns for AI Socratic dialogue. *Science*. doi:10.1126/science.adu1526

Oreskes, N., & Conway, E. M. (2010). *Merchants of doubt: How a handful of scientists obscured the truth on issues from tobacco smoke to global warming*. Bloomsbury Press.

Pierre, J. M. (2025). *False: How mistrust, disinformation, and motivated reasoning make us believe things that aren't true*. Oxford University Press. ISBN: 9780197765272.

Proctor, R. N. (1995). *Cancer wars: How politics shapes what we know and don't know about cancer*. Basic Books.

Roozenbeek, J., et al. (2022). Psychological inoculation improves resilience against misinformation on social media. *Science Advances*, *8*(34). doi:10.1126/sciadv.abo6254

Royal Society Open Science. (2022). Cross-topic transferable manipulation technique recognition. *Royal Society Open Science*, *9*(5).

Saucier, C. J., Walter, N., & Demetriades, S. Z. (2025). Thirty years since Kunda: Addressing critiques to reimagine a model of motivated reasoning. *Annals of the International Communication Association*, *49*(1), 1-13. doi:10.1093/anncom/wlae001

Simchon, A., Zipori, T., Teitelbaum, L., Lewandowsky, S., & van der Linden, S. (2025). A signal detection theory meta-analysis of psychological inoculation against misinformation. *Current Opinion in Psychology*, *67*, 102194. doi:10.1016/j.copsyc.2025.102194

Stasielowicz, L. (2026). How effective are conspiracy belief reduction interventions? A meta-analysis. *European Journal of Social Psychology*, *56*(1), 275-291. doi:10.1002/ejsp.70041

Supran, G., & Oreskes, N. (2017). Assessing ExxonMobil's climate change communications (1977-2014). *Environmental Research Letters*, *12*(8), 084019. doi:10.1088/1748-9326/aa815f

Tanzer, M., Campbell, C., Saunders, R., Booker, T., Luyten, P., & Fonagy, P. (2024). The role of epistemic trust and epistemic disruption in vaccine hesitancy, conspiracy thinking and the capacity to identify fake news. *PLOS Global Public Health*, *4*(12), e0003941. doi:10.1371/journal.pgph.0003941

Tomisu, H., Ueda, J., & Yamanaka, T. (2025). The cognitive mirror: A framework for AI-powered metacognition and self-regulated learning. *Frontiers in Education*, *10*. doi:10.3389/feduc.2025.1697554

van der Linden, S., Roozenbeek, J., & Compton, J. (2022). Inoculating against fake news about COVID-19. *Frontiers in Psychology*, *11*, 566790.

van der Linden, S., Louison-Lavoy, D., Blazer, N., Noble, N. S., & Roozenbeek, J. (2026). Prebunking misinformation techniques in social media feeds: Results from an Instagram field study. *Harvard Kennedy School Misinformation Review*, *7*(1). doi:10.37016/mr-2020-193

Wood, T., & Porter, E. (2019). The elusive backfire effect: Mass attitudes' steadfast factual adherence. *Political Behavior*, *41*(1), 135-163.

---

*This document represents the scientific foundation of the Huginn & Muninn framework as understood in March 2026. The authors welcome engagement from researchers seeking to replicate, challenge, or extend any of the findings reviewed here. Preregistered studies testing the 15 hypotheses above are the most valuable contribution external collaborators can make.*
