# Band 4: Adversarial Review & Research Robustness

**Analyst focus**: Red-team assessment of Huginn & Muninn's research foundations
**Date**: 2026-03-24

---

## 1. Criticisms of Costello et al. (2024)

### 1.1 The Study and Its Claims

Costello, Pennycook, and Rand published "Durably reducing conspiracy beliefs through dialogues with AI" in *Science* (2024), reporting that personalized AI dialogues using GPT-4 Turbo reduced conspiracy beliefs by approximately 20% in 2,190 participants, with effects persisting at 2-month follow-up. The study won the 2026 AAAS Newcomb Cleveland Prize (https://www.science.org/doi/10.1126/science.aeg6310).

### 1.2 The Discernment Gap: Belief Change Without Skill Transfer

The most significant critique comes from a 2025 longitudinal study (Bao et al., "Dialogues with AI Reduce Beliefs in Misinformation but Build No Lasting Discernment Skills," arXiv:2510.01537). This study directly extends Costello's work and finds a critical paradox:

- **Immediate accuracy gains**: +21.3 percentage points when AI-assisted
- **Long-term independent judgment decline**: -15.3% by week 4 in unassisted performance
- **Statistical significance of decline**: Linear decay beta = -0.077, SE = 0.022, t = -3.52, p < 0.001
- **Fake news detection specifically**: beta = -0.129, SE = 0.028, t = -4.56, p < .001 (substantial decline)

The study tracked 67 participants over 4 weeks and found five distinct behavioral trajectories, with 21% becoming "Dependency Developers" who shifted from active self-reliance to passive acceptance. Human agreement with AI increased from 23.0% to 28.5% over the study period, while independent thinking remained consistently low (7.2% to 7.6%).

The core critique: Costello et al. measured *belief change* regarding specific claims, but this does not translate to *skill acquisition*. As the authors state: "if the goal is simply to reduce the belief in specific falsehoods in the moment, AI can be effective. But if the goal is to build people's skills to recognize falsehoods on their own, our results suggest current AI approaches may fail -- or even backfire by fostering reliance" (https://arxiv.org/html/2510.01537v1).

**Implication for H&M**: The Socratic dialogue approach may produce temporary belief shifts without building lasting critical thinking. Users could become dependent on the tool rather than developing independent discernment.

### 1.3 Methodological Concerns

Several methodological concerns warrant attention:

1. **Sample composition**: The Costello study used online recruitment (likely Prolific/MTurk), which skews toward younger, more educated, and more politically engaged participants. The arXiv replication used 76.1% US-based and 23.9% UK-based participants -- both WEIRD populations.

2. **Demand characteristics**: Participants knew they were in a study about conspiracy beliefs. The Hawthorne effect may inflate apparent belief change, as participants may report reduced belief to appear more rational.

3. **Follow-up duration**: While the 2-month follow-up is longer than typical interventions, it remains insufficient to establish true durability. The arXiv study showing decline over just 4 weeks raises questions about what happens at 6 or 12 months.

4. **Ecological validity**: The controlled dialogue setting differs substantially from real-world contexts where people encounter conspiracy theories in emotionally charged social environments, not clean text-based exchanges with an AI.

5. **Causal mechanisms remain unclear**: The authors themselves acknowledge that "the causal mechanisms underpinning our results remain unformalized" and "the specific cognitive or psychological processes through which this change occurs are unusually difficult to confirm."

### 1.4 Science Commentary

*Science* published an editorial response, "The problem with AI dialogue at scale" (https://www.science.org/doi/10.1126/science.adu1526), which raises concerns about scalability and unintended consequences of deploying persuasive AI systems broadly.

---

## 2. Weaponization Risks of the Socratic Approach

### 2.1 Can Socratic Dialogue Reduce Belief in True Things?

This is a critical vulnerability. The Costello et al. methodology works by having AI provide "factual counterevidence and alternative explanations." But the same persuasive architecture could be directed at undermining true beliefs. Key risks:

**Epistemic attack vector**: Research on autonomy risks in generative chatbots identifies that Socratic AI systems can be weaponized for "epistemic attack" -- a user disguises an opponent's opinion as their own, prompts the system to analyze it, and selectively shares responses as seemingly neutral critique to strategically destruct others' beliefs (https://pmc.ncbi.nlm.nih.gov/articles/PMC12657563/).

**Persuasive AI as a double-edged sword**: The arXiv study found that persuasive AI strategies that produce the highest immediate accuracy gains (confident, tailored factual answers) are also "those most likely to induce reliance." If the AI's factual grounding is compromised -- through hallucination, adversarial prompting, or deliberate manipulation of its knowledge base -- the same mechanism that reduces conspiracy beliefs could reduce belief in verified truths.

**Confidence calibration backfire**: The arXiv study found that "confidence calibration" strategies *severely undermined* unassisted performance (r = -0.42), suggesting that AI interventions that adjust users' confidence levels are particularly dangerous when misdirected.

### 2.2 Common Humanity Layer: False Equivalence Risks

H&M's Bridge Builder agent creates "common humanity" connections between opposing viewpoints. This introduces a specific risk:

- **"Both sides" framing can legitimize extremism**: When the system finds common ground between a moderate position and an extreme position, it implicitly elevates the extreme position as having legitimate grievances. For example, finding "common humanity" between vaccine advocates and anti-vaccine conspiracy theorists could normalize the framing that both positions have equal epistemic standing.

- **Moral equivalence trap**: The perception gap research (More in Common) shows people overestimate opponent extremism by 2x. But the inverse risk exists: a system designed to reduce perception gaps could *underestimate* genuine extremism, treating it as merely misperceived moderation.

- **Guardrails needed**: The system requires explicit thresholds for when "common humanity" framing is inappropriate -- e.g., when one position involves denial of well-established scientific consensus, incitement to violence, or dehumanization of groups. Without these guardrails, the Bridge Builder becomes a false-equivalence generator.

### 2.3 Required Safeguards

Based on the literature, H&M would need:
1. Epistemic asymmetry detection -- recognizing when one side has overwhelming evidentiary support
2. Red lines for common humanity framing -- topics where bridge-building is inappropriate
3. Source verification for AI-generated counterevidence to prevent hallucinated citations
4. Adversarial testing against prompt injection attempts to redirect the Socratic engine

---

## 3. Robustness of the Other Five Research Foundations

### 3.1 Inoculation Theory / Prebunking

**Replication status**: A 2025 meta-analysis using Signal Detection Theory across 33 experiments (N = 37,075) found that "inoculation improves discernment between reliable and unreliable news without inducing response bias" (https://www.sciencedirect.com/science/article/pii/S2352250X25002076). This is a positive signal for replication.

**Effect size concerns**: However, a June 2025 study in *PNAS Nexus* found "limited effectiveness of psychological inoculation against misinformation in a social media feed" (https://academic.oup.com/pnasnexus/article/4/6/pgaf172/8151956), suggesting that lab-validated effects may not transfer to realistic social media contexts.

**Cross-cultural evidence**: The Bad News prebunking game showed "significant and meaningful reductions in the perceived reliability of manipulative content across all languages" (https://misinforeview.hks.harvard.edu/article/global-vaccination-badnews/), suggesting cross-cultural applicability. However, the Google/Jigsaw prebunking video trials at 5.4M user scale have not been independently replicated at that scale.

**Key vulnerability for H&M**: The gap between lab and real-world effectiveness is substantial. Inoculation effects that work in controlled settings may attenuate significantly in the noisy, emotionally charged environment of social media feeds. The *PNAS Nexus* study is a red flag that effect sizes in realistic contexts may be much smaller than headline figures suggest.

### 3.2 Perception Gap (More in Common, 2019)

**US-specificity**: The original More in Common "Perception Gap" study (2019) was conducted exclusively with US participants and focused on American political polarization (https://moreincommon.substack.com/p/what-we-get-wrong-about-each-other). The finding that Americans overestimate opponent extremism by approximately 2x has not been systematically replicated cross-culturally.

**Cross-cultural validity concerns**: Research on cross-cultural measurement validity warns that "Western-derived measurements may not fully capture intercultural competence in non-Western regions" and that "bias signals a lack of equivalence, meaning score differences do not accurately reflect true psychological construct differences across groups." The perception gap construct may be deeply tied to the specific structure of American two-party political polarization and may not generalize to multi-party systems, consensus-oriented political cultures, or non-Western contexts.

**Key vulnerability for H&M**: If H&M is deployed internationally, the perception gap framework may produce inaccurate assessments of how different groups perceive each other. The 2x overestimation figure should be treated as US-specific until cross-cultural replication is available.

### 3.3 Moral Reframing (Feinberg & Willer, 2015-2019)

**Replication failures**: This is the weakest link in H&M's research foundation. Multiple independent studies have failed to replicate Feinberg and Willer's findings:

- A 2026 preregistered study found "no evidence that reframing political positions and issues to moral foundations shifted support among conservatives and liberals" (https://www.sciencedirect.com/science/article/pii/S0022103126000016)
- A preregistered study with 2,009 conservative Republicans found "moral reframing intervention had no significant direct effect on the accuracy of headline ratings" (https://misinforeview.hks.harvard.edu/article/increasing-accuracy-motivations-using-moral-reframing-does-not-reduce-republicans-belief-in-false-news/)
- Multiple additional failures: Arpan et al. (2018), Berkebile-Weinberg et al. (2024), Crawford (2025), Hundemer et al. (2023), Kim et al. (2023)
- The theoretical foundation itself is questioned: "the evidence for cultural variation in moral psychology is at best weak, and the theoretical argument for moral reframing is flawed" (https://moral-psychology.butterfill.com/docs/lecture_09/moral_reframing_revisited/)

**Partial replications**: A 2025 study found that moral reframing accuracy can be enhanced through empathic perspective-taking training (https://constructivedialogue.org/assets/Selterman-Welker-Duong-2025-Moral-Reframing.pdf), suggesting the technique may work under specific conditions but not as a general-purpose tool.

**Key vulnerability for H&M**: Moral reframing is presented as one of six research pillars, but it has the worst replication record of all six. Any H&M component that relies on automatically reframing arguments to match audience moral foundations is building on empirically shaky ground. This should be downgraded from a core pillar to an experimental feature with appropriate caveats.

### 3.4 Narrative Complexity (Peter Coleman, Columbia)

**Empirical vs. theoretical**: Coleman's work is primarily theoretical and framework-oriented, grounded in complexity science and dynamical systems theory applied to conflict. He directs Columbia's Advanced Consortium on Cooperation, Conflict, and Complexity (AC4) and authored "The Way Out: How to Overcome Toxic Polarization" (Columbia University Press) (https://behavioralscientist.org/toxic-polarization-feeds-on-simplicity-peter-coleman-offers-complexity-as-a-way-out/).

Coleman has empirical work, including studies on the Israeli-Palestinian conflict, and is described as wanting "to be able to do research with data to see if systemic metaphors could help understand conflicts."

**Lack of controlled intervention studies**: However, compared to the other five pillars, narrative complexity lacks large-scale randomized controlled trials demonstrating that *increasing narrative complexity* causally reduces polarization or improves discourse quality. The framework is compelling as a theoretical lens but has thinner empirical support as an intervention methodology.

**Key vulnerability for H&M**: The narrative complexity pillar is the most theoretically sophisticated but least empirically validated as an intervention. Using it to guide system design is reasonable; claiming it as evidence that H&M's approach will work is an overstatement of the current evidence base.

### 3.5 Redirect Method (Moonshot)

**The 224% figure**: The 224% increase in watch time refers to a specific playlist designed to undermine white supremacist narratives. At-risk users searching for content like "Prepare for race war" consumed alternative program content at 224% higher rates when targeted with redirect ads (https://moonshotteam.com/the-redirect-method/).

**Independent verification**: RAND Corporation evaluated the Redirect Method USA deployment and found it "showed promise" (https://www.rand.org/content/dam/rand/pubs/research_reports/RR2800/RR2813/RAND_RR2813.pdf). Moonshot's Canada deployment included structured inter-rater reliability testing managed by an external consultant (https://moonshotteam.com/wp-content/uploads/Final-Public-Report_Canada-Redirect_English.pdf).

**Methodological concerns**: The 224% metric measures *engagement* (watch time), not *belief change* or *behavioral change*. Someone watching more counter-narrative content does not necessarily mean they changed their mind. The metric conflates exposure with persuasion. Additionally, RAND's assessment used softer language ("showed promise") rather than strong causal claims.

**Key vulnerability for H&M**: The Redirect Method's headline metric is an engagement proxy, not an outcome measure. If H&M cites this as evidence that redirect-style interventions change beliefs, it is making a logical leap not supported by the evidence. The method demonstrates you can get people to *view* alternative content, not that viewing it changes their minds.

---

## 4. Competitive Landscape Analysis

### 4.1 Google/Jigsaw (Prebunking Videos + Redirect Method)

**What they do**: Jigsaw takes a two-pronged approach. Their prebunking arm produces short videos teaching users to recognize manipulation tactics (scapegoating, false dilemmas, emotional manipulation) before encountering them. Their largest campaign reached 120M+ YouTube users before the 2024 EU elections across 12 nations, improving manipulation discernment and sharing decisions (https://www.nature.com/articles/s44271-025-00379-3). Their earlier US deployment exposed 5.4M YouTubers to inoculation videos, increasing manipulation recognition by 5% on average (https://www.science.org/doi/10.1126/sciadv.abo6254).

**What they do that H&M doesn't**: Massive platform-native distribution (YouTube, Meta ad networks), preventive inoculation rather than reactive analysis, and direct integration with the platforms where misinformation spreads.

**Limitations**: Prebunking experts caution "you can't really expect miracles in a sense that, all of a sudden after one of these videos, people begin to behave completely differently online" (https://time.com/6970488/google-jigsaw-eu-elections-misinformation-prebunking/). The approach requires continuous reinforcement and does not address claims users have already absorbed.

### 4.2 Full Fact (Automated Fact-Checking API + ClaimReview)

**What they do**: Full Fact has operated since 2009, combining AI-powered real-time monitoring of claims across social media and web domains with human fact-checker verification. Their AI helps fact-checkers prioritize what is important and uses ClaimReview schema (part of schema.org) to tag fact-check articles for search engines and platforms (https://fullfact.org/automated).

**What they do that H&M doesn't**: Real-time claim monitoring at scale, structured data output (ClaimReview) that integrates with Google Search and social platforms, and a decade of institutional credibility with media and government partners.

**Limitations**: Full Fact acknowledges AI is not a panacea and that much fact-checking "requires a kind of judgement and sensitivity to context that remains far out of reach for fully automated verification" (https://reutersinstitute.politics.ox.ac.uk/our-research/understanding-promise-and-limits-automated-fact-checking). Their tools have language-specific limitations and are less reliable for non-English text and video.

### 4.3 ClaimBuster (NLP Claim Detection)

**What they do**: Developed at the University of Texas at Arlington, ClaimBuster uses NLP and supervised learning to identify check-worthy claims in real-time, achieving 0.96 precision for top 100 sentences. It compares detected claims against previously fact-checked ones using both token-based similarity (Elasticsearch) and semantic similarity (https://idir.uta.edu/claimbuster/).

**What they do that H&M doesn't**: Automated claim detection in live speech/text (e.g., political debates), direct comparison against existing fact-check databases, and a focus on identifying *which* claims merit checking rather than attempting to adjudicate truth.

**Limitations**: RAND stopped reviewing ClaimBuster as of December 2020. The system identifies check-worthy claims but does not itself verify them. Recent work (IndicClaimBuster, 2025) has extended to multilingual support (Hindi, Bengali) but the core detection approach has limitations with novel claim types (https://aclanthology.org/2025.ijcnlp-long.133/).

### 4.4 Logically.ai (Enterprise Disinformation Detection)

**What they do**: Logically used a Human-in-the-Loop AI framework called HAMLET to detect coordinated messaging, sentiment surges, and influencer alignment across 200+ platforms. They visualized narrative networks and detected coordination patterns (https://logically.ai/).

**What they do that H&M doesn't**: Network-level analysis (detecting coordinated inauthentic behavior, not just individual claims), threat intelligence reporting for government and enterprise clients, and cross-platform surveillance at scale.

**Critical caveat**: Logically lost its contracts with TikTok and Meta in July 2025 and was sold to Kreatur Ltd through administration (https://en.wikipedia.org/wiki/Logically_(company)). This represents a cautionary tale for the business model of enterprise disinformation detection.

### 4.5 Meedan/Check (Collaborative Verification)

**What they do**: Meedan's Check platform enables collaborative verification across organizations, with tiplines on WhatsApp and other messaging apps where the public can submit claims for verification. The system uses multilingual AI for image, video, and text analysis, and intelligent deduplication to prevent duplicated verification effort. In 2024, it connected 33,645 people to verified articles about major political contests worldwide (https://meedan.org/check).

**What they do that H&M doesn't**: Community-driven tipline infrastructure, cross-organization collaboration workflows, and direct reach into messaging platforms (WhatsApp) where misinformation spreads most virally in the Global South.

### 4.6 The Habermas Machine (Google DeepMind) -- Emerging Competitor

**What they do**: Published in *Science* (2024), the Habermas Machine is an AI mediator trained to generate group consensus statements during deliberation. Participants chose AI-generated statements over human-mediator statements 56% of the time, and groups were less divided after AI-mediated deliberation (https://www.science.org/doi/10.1126/science.adq2852).

**What they do that H&M doesn't**: Direct consensus-building in group deliberation contexts, rather than individual-level belief change.

**Limitations**: The model cannot handle fact-checking, staying on topic, or moderating discourse in its current form.

### 4.7 What H&M Does That None of Them Do

H&M's unique contribution is the **Common Humanity layer** -- the Bridge Builder agent that connects opposing viewpoints through shared human values rather than simply correcting facts or detecting claims. None of the competitors listed above attempt to:

1. **Map the emotional and identity-level drivers** of belief (TTP Classifier analyzing tactics, techniques, and procedures)
2. **Build bridges between opposing groups** rather than declaring one side right and the other wrong
3. **Combine Socratic dialogue with structural analysis** of how narratives exploit psychological vulnerabilities
4. **Integrate six distinct research traditions** into a single pipeline (decomposition, tracing, mapping, classification, bridge-building, adversarial auditing)

However, this uniqueness is also a vulnerability: no one else does it because it is empirically untested as a combined approach, and several of the component research foundations (moral reframing, narrative complexity) have weak or contested evidence bases.

---

## 5. Known Failure Modes of AI-Driven Fact-Checking

### 5.1 Hallucinated Citations and False Confidence

AI-generated fact-checks carry a fundamental credibility problem. A Tow Center study found that over 60% of responses from AI-powered search engines contained inaccuracies (https://edmo.eu/blog/part-of-the-problem-and-part-of-the-solution-the-paradox-of-ai-in-fact-checking/). Gemini and Grok 3 were the worst offenders, providing more fabricated links than correct links across 200 tests (https://www.niemanlab.org/2025/03/ai-search-engines-fail-to-produce-accurate-citations-in-over-60-of-tests-according-to-new-tow-center-study/).

Most critically for H&M: many popular AI search engines "lean towards blind confidence in their response language," with ChatGPT using hedging language in only 15 of 134 incorrect citations. When an AI system presents fabricated evidence confidently during a Socratic dialogue, users who have been primed to trust the system's expertise may internalize false information more deeply than if they had never engaged with the tool at all.

### 5.2 The Confidence-Competence Paradox

Research on AI fact-checking at scale reveals a "Dunning-Kruger effect" in language models (https://arxiv.org/html/2509.08803v1):

- **Smaller models** (Llama-7B, Mistral-7B): 88% certainty but only ~60% accuracy
- **Larger models** (GPT-4o): 89% accuracy but <40% certainty
- **Cost implications**: Llama-2-7B costs <$0.10 per 1,000 claims; GPT-4o costs $2.22; o1-preview costs $88.75

This creates an equity problem: resource-constrained organizations that can only afford smaller models get the most confidently wrong answers. If H&M targets underresourced communities or civil society organizations, model cost directly determines accuracy, and cheaper deployments may cause more harm than good.

### 5.3 AI Fact-Checks Can Decrease Discernment

A landmark 2024 PNAS study (DeVerna et al.) found that AI fact-checks can actually *worsen* headline discernment (https://www.pnas.org/doi/10.1073/pnas.2322823121):

- **AI mislabels true headlines as false**: 12.75% decrease in belief for true headlines incorrectly flagged (p < 0.001)
- **AI uncertainty about false headlines**: 9.12% *increase* in belief for false headlines where ChatGPT expressed uncertainty (p = 0.03)
- **Human fact-checks outperform AI**: Human fact-checks improved discernment by 18.06% (belief) and 8.98% (sharing); AI fact-checks showed no significant improvement
- **Selection bias**: Participants who *chose* to view AI fact-checks became more likely to share both true and false news, suggesting they sought confirmation rather than correction

The mechanism: people perceive AI as objective, making them particularly susceptible to its errors while simultaneously disregarding accurate warnings. This is devastating for H&M's premise -- if users perceive the AI's Socratic analysis as authoritative, its mistakes will be amplified rather than filtered.

### 5.4 Prior Beliefs Override AI Corrections

A 2025 study (N = 1,372) found that prior beliefs significantly predict continued misinformation endorsement even after AI correction, with r = .25 (https://pmc.ncbi.nlm.nih.gov/articles/PMC12875456/). Key findings:

- When AI systems are perceived as less than fully accurate (67% condition), stance-misinformation correlation strengthened (b = .43, p < .001)
- Even at 97% stated accuracy, belief-consistent bias was not eliminated (b = .28, p < .001)
- Users "discredit corrections contradicting their worldview, using perceived system fallibility as justification"

**Implication for H&M**: Users who are deeply committed to a conspiracy belief will use any perceived flaw in the AI's reasoning as evidence that the system cannot be trusted, thereby reinforcing their original belief. This is the "backfire effect" operating through a new medium.

### 5.5 Inability to Handle Novel Claims

AI fact-checking tools have "limited utility in real-world applications, such as when applied to unseen claims, for which there are no curated evidence documents or fact-checking articles" (https://dl.acm.org/doi/full/10.1145/3706598.3713277). Language models do not receive explicit "true/false" labels during pretraining, making it structurally difficult to distinguish valid facts from plausible-sounding fabrications (https://news.stanford.edu/stories/2025/11/ai-language-models-facts-belief-human-understanding-research).

For H&M, this means the system will be least effective against the most dangerous claims: novel conspiracy theories that have not yet been fact-checked or debunked by existing sources. The Socratic engine may generate confident but unfounded counterarguments, or worse, fail to recognize that a novel claim is actually true.

### 5.6 Cultural and Linguistic Bias

AI fact-checking tools are "less reliable for non-English text and video, as well as for non-Western accents in English" (https://reutersinstitute.politics.ox.ac.uk/news/generative-ai-already-helping-fact-checkers-its-proving-less-useful-small-languages-and). The confidence-competence study found that Portuguese and Hindi claims showed up to 4.3% accuracy decreases relative to English, and Global South claims saw accuracy declines of 6.2%-12.1% for most models.

A "geo-political veracity gradient" exists in training data: models perform best on claims from the Global North and worst on claims from the Global South, precisely where misinformation may have the most severe real-world consequences (election manipulation, health misinformation, ethnic violence).

### 5.7 Adversarial Prompt Injection

The AI safety landscape in 2025 reveals that large reasoning models can achieve 97.14% jailbreak success rates across model combinations (https://www.nature.com/articles/s41467-026-69010-1). Chain-of-thought jailbreaks can hijack safety mechanisms by inserting malicious instructions into a model's own reasoning process. Adversarial embeddings can be crafted to match arbitrary queries while containing malicious content, poisoning retrieval at the mathematical level.

**Implication for H&M**: A sophisticated adversary could craft inputs designed to make the Socratic engine argue *for* conspiracy theories rather than against them, or to generate outputs that appear to debunk legitimate concerns. The adversarial auditor agent in H&M's pipeline may catch some of these attacks, but the adversarial surface is vast.

### 5.8 Automation Bias: Over-Trust in AI Verdicts

Automation bias -- the tendency to accept AI outputs without critical evaluation -- is a documented and growing concern (https://link.springer.com/article/10.1007/s00146-025-02422-7). In the context of AI fact-checking, this manifests as users treating AI verdicts as authoritative without independent verification. The arXiv study on Costello's methodology found that 21% of participants became "Dependency Developers" within just 4 weeks, suggesting that repeated exposure to AI-mediated fact-checking may erode independent critical thinking over time.

For H&M, this creates a paradox: the more effective the tool is at reducing conspiracy beliefs in the short term, the more it may cultivate dependence on AI-mediated epistemology, leaving users *more* vulnerable when the tool is unavailable or encounters claims outside its competence.

---

## 6. Summary: Research Foundation Scorecard

| Research Pillar | Replication Status | Effect Size Confidence | Cross-Cultural Validity | Overall Rating |
|---|---|---|---|---|
| Socratic AI Dialogue (Costello 2024) | Published in *Science*; critiqued for skill transfer gap | 20% belief reduction; but discernment declines long-term | WEIRD samples only | MODERATE -- strong initial finding, significant caveats |
| Inoculation/Prebunking (van der Linden) | Meta-analysis supports (N=37,075); real-world effects weaker | Lab effects significant; *PNAS Nexus* shows limited field transfer | Cross-cultural game evidence positive | MODERATE-STRONG -- best replicated but real-world gap |
| Perception Gap (More in Common) | No systematic cross-cultural replication | US-specific 2x overestimation | US-only | WEAK -- single-country, single-study foundation |
| Moral Reframing (Feinberg & Willer) | Multiple preregistered replication failures | Inconsistent; null results in several large studies | Untested | WEAK -- worst replication record of all six pillars |
| Narrative Complexity (Coleman) | Primarily theoretical; limited RCTs | No intervention effect sizes available | Applied to intl. conflict but not tested as intervention | WEAK-MODERATE -- compelling theory, thin empirical base |
| Redirect Method (Moonshot) | RAND: "showed promise"; no independent replication of 224% | Engagement metric, not belief/behavior change | Deployed in US, Canada, EU | MODERATE -- but measures the wrong outcome |

**Overall assessment**: Of the six research pillars, only two (Socratic dialogue and inoculation/prebunking) have strong empirical support, and both carry significant caveats. One pillar (moral reframing) has actively failed to replicate. Two pillars (perception gap, narrative complexity) are either US-specific or primarily theoretical. The redirect method measures engagement rather than belief change. H&M's research foundation is thinner than it appears at first glance.

---

## Sources

- https://www.science.org/doi/10.1126/science.adq1814
- https://arxiv.org/html/2510.01537v1
- https://www.science.org/doi/10.1126/science.adu1526
- https://www.science.org/doi/10.1126/science.adu6608
- https://www.science.org/doi/10.1126/science.aeg6310
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12657563/
- https://www.sciencedirect.com/science/article/pii/S2352250X25002076
- https://academic.oup.com/pnasnexus/article/4/6/pgaf172/8151956
- https://misinforeview.hks.harvard.edu/article/global-vaccination-badnews/
- https://moreincommon.substack.com/p/what-we-get-wrong-about-each-other
- https://www.sciencedirect.com/science/article/pii/S0022103126000016
- https://misinforeview.hks.harvard.edu/article/increasing-accuracy-motivations-using-moral-reframing-does-not-reduce-republicans-belief-in-false-news/
- https://moral-psychology.butterfill.com/docs/lecture_09/moral_reframing_revisited/
- https://constructivedialogue.org/assets/Selterman-Welker-Duong-2025-Moral-Reframing.pdf
- https://behavioralscientist.org/toxic-polarization-feeds-on-simplicity-peter-coleman-offers-complexity-as-a-way-out/
- https://moonshotteam.com/the-redirect-method/
- https://www.rand.org/content/dam/rand/pubs/research_reports/RR2800/RR2813/RAND_RR2813.pdf
- https://moonshotteam.com/wp-content/uploads/Final-Public-Report_Canada-Redirect_English.pdf
- https://www.nature.com/articles/s44271-025-00379-3
- https://www.science.org/doi/10.1126/sciadv.abo6254
- https://time.com/6970488/google-jigsaw-eu-elections-misinformation-prebunking/
- https://fullfact.org/automated
- https://reutersinstitute.politics.ox.ac.uk/our-research/understanding-promise-and-limits-automated-fact-checking
- https://idir.uta.edu/claimbuster/
- https://aclanthology.org/2025.ijcnlp-long.133/
- https://logically.ai/
- https://en.wikipedia.org/wiki/Logically_(company)
- https://meedan.org/check
- https://www.science.org/doi/10.1126/science.adq2852
- https://edmo.eu/blog/part-of-the-problem-and-part-of-the-solution-the-paradox-of-ai-in-fact-checking/
- https://www.niemanlab.org/2025/03/ai-search-engines-fail-to-produce-accurate-citations-in-over-60-of-tests-according-to-new-tow-center-study/
- https://arxiv.org/html/2509.08803v1
- https://www.pnas.org/doi/10.1073/pnas.2322823121
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12875456/
- https://dl.acm.org/doi/full/10.1145/3706598.3713277
- https://news.stanford.edu/stories/2025/11/ai-language-models-facts-belief-human-understanding-research
- https://reutersinstitute.politics.ox.ac.uk/news/generative-ai-already-helping-fact-checkers-its-proving-less-useful-small-languages-and
- https://www.nature.com/articles/s41467-026-69010-1
- https://link.springer.com/article/10.1007/s00146-025-02422-7

Status: COMPLETE
