# Band 3: Manufactured Doubt Detection Implementation

Research for Huginn & Muninn -- Wave 2 Sensor Sweep
Date: 2026-03-24

---

## 1. The Complete 28-Tactic Taxonomy (PMC7996119)

**Source**: Goldberg, Vandenberg, et al. (2021). "The science of spin: targeted strategies to manufacture doubt with detrimental effects on environmental and public health." *Environmental Health*, 20, 33. (https://pmc.ncbi.nlm.nih.gov/articles/PMC7996119/)

### Study Overview

The researchers examined scholarly books, peer-reviewed articles, investigative journalism, and legal evidence from five industries: tobacco, coal/fossil fuel, sugar, the pesticide atrazine (Syngenta), and the George C. Marshall Institute (climate denial). They iteratively identified 28 distinct tactics used to manufacture doubt about science, organized by target audience (scientific community, government, lay public, legal system).

### The Five Universal Tactics (Used by ALL Five Industries)

These five tactics appeared across every industry studied, making them the strongest signals for manufactured doubt detection:

1. **Attack Study Design** -- Emphasize minor methodological flaws (sample size, confounders, bias) to undermine findings, even when flaws are trivial or standard. Industries used this to demand impossibly high standards of proof.
2. **Gain Support from Reputable Individuals** -- Recruit politicians, scientists, physicians, or other credible figures to defend industry positions. Creates an illusion of scientific disagreement.
3. **Misrepresent Data** -- Cherry-pick findings, design studies intended to fail, or construct misleading meta-analyses. Selective data presentation to support predetermined conclusions.
4. **Employ Hyperbolic or Absolutist Language** -- Use loaded buzzwords like "junk science" vs. "sound science," absolutist terms, and emotionally charged framing. Creates a false dichotomy between industry-approved and independent science.
5. **Influence Government/Laws** -- Gain inappropriate access to regulatory bodies, exploit the "revolving door" between industry and government, encourage pro-industry policy.

### Complete 28-Tactic List

Key: T=Tobacco, C=Coal/Fossil Fuel, S=Sugar, A=Atrazine/Syngenta, M=Marshall Institute/Climate Denial

| # | Tactic | Description | Industries |
|---|--------|-------------|-----------|
| 1 | Attack Study Design | Exaggerate minor methodological flaws to discredit research | T,C,S,A,M |
| 2 | Gain Support from Reputable Individuals | Recruit credible experts, politicians, physicians as defenders | T,C,S,A,M |
| 3 | Misrepresent Data | Cherry-pick data, design failing studies, misleading meta-analyses | T,C,S,A,M |
| 4 | Suppress Incriminating Information | Hide internal research showing harm; withhold counter-evidence | T,C,S,A |
| 5 | Contribute Misleading Literature | Publish ghostwritten studies, false information in journals | T,C,S,A |
| 6 | Host Conferences or Seminars | Organize one-sided scientific meetings with pro-industry speakers | T,C,S |
| 7 | Avoid/Abuse Peer-Review | Bypass peer review or hide funding sources in published work | T,C,S |
| 8 | Employ Hyperbolic Language | Use absolutist terms, loaded buzzwords ("junk science"), emotional framing | T,C,S,A,M |
| 9 | Blame Other Causes | Propose alternative explanations to deflect from actual cause (e.g., sugar industry blamed dietary fat) | T,C,S,A |
| 10 | Invoke Liberties/Censorship/Overregulation | Frame opposition as anti-freedom, regulatory overreach | T,C |
| 11 | Define Measurement Standards | Set guidelines that undermine contrary research; redefine exposure metrics | T,C,S,A |
| 12 | Exploit Scientific Illiteracy | Confuse lay audiences with technical complexity; deliberately obscure explanations | T,C,S,A |
| 13 | Pose as Defender of Health/Truth | Frame industry goals as health-conscious or truth-seeking | T,C,S,A |
| 14 | Obscure Involvement | Use ghostwriting, shell companies, attorney-client privilege to hide industry role | T,C |
| 15 | Develop PR Strategy | Target public audiences systematically through media campaigns | T,C,S |
| 16 | Appeal to Mass Media | Invoke journalistic "balance" to get equal airtime for minority positions | T,C,S |
| 17 | Exploit Victims' Lack of Resources | Silence opposition through legal/financial power; outspend critics | T,C |
| 18 | Normalize Negative Outcomes | Make harms seem inevitable or acceptable; normalize disease prevalence | T,C,S |
| 19 | Impede Government Regulation | Overwhelm regulatory agencies with submissions, slow agency function | T,C |
| 20 | Alter Product Appearance | Modify product to seem safer without addressing actual harm (e.g., filter cigarettes) | T |
| 21 | Influence Government/Laws | Revolving door employment, regulatory capture, pro-industry legislation | T,C,S,A,M |
| 22 | Attack Opponents | Undermine professional/personal reputations of critics (e.g., targeting Tyrone Hayes) | T,C,S |
| 23 | Appeal to Emotion | Manipulate emotional responses with fear-based messaging | T,C |
| 24 | Inappropriately Question Causality | Deny causation despite strong evidence; weaponize "correlation isn't causation" | T |
| 25 | Make Straw Man Arguments | Refute arguments not actually made by opponents | M |
| 26 | Abuse Credentials | Use expertise from one field to claim authority in another (e.g., physicists on climate) | M |
| 27 | Abuse Data Access Requests | Misuse FOIA or Shelby Amendment to obtain and attack researchers' data | C,S |
| 28 | Claim Slippery Slope | Falsely warn of catastrophic consequences from regulation | M |

### Key Structural Findings

**Audience Targeting**: Different tactics target different audiences. Scientific communities receive study design attacks (#1, #3, #7); the lay public receives emotional appeals and simplified falsehoods (#8, #12, #16, #23); government officials receive selectively displayed data and lobbying (#19, #21); the legal system faces resource imbalances (#17).

**Manufacturers vs. Perpetuators**: The study distinguishes between "manufacturers" of doubt (PR firms, hired scientists who directly manipulate information) and "perpetuators" (journalists, bloggers, citizens who unknowingly spread industry messages). This distinction is critical for H&M: detecting the *manufactured* origin matters more than detecting individual perpetuation. (https://pmc.ncbi.nlm.nih.gov/articles/PMC7996119/)

**Logical Fallacies**: Twelve of the 28 tactics rely on identifiable logical fallacies: appeal to authority (#2, #26), straw man (#25), ad hominem (#22), false cause (#9, #24), appeal to emotion (#23), slippery slope (#28), and others. These are computationally detectable.

**Financial Requirement**: Most tactics require substantial funding, meaning manufactured doubt campaigns tend to be coordinated and well-resourced, leaving organizational traces.

---

## 2. Computational Detection of Manufactured Doubt

### 2.1 The CARDS Framework: State-of-the-Art Climate Denial Detection

The most directly relevant computational system is **CARDS** (Computer Assisted Recognition of Denial and Skepticism), a supervised machine learning system for detecting and categorizing contrarian claims about climate change. (https://www.nature.com/articles/s41598-021-01714-4)

**Technical Architecture**: The CARDS model uses a simple ensemble of a logistic classifier and the RoBERTa transformer architecture (via the simpletransformers library). The training corpus was constructed from conservative think-tank websites and contrarian blogs spanning 20+ years. (https://github.com/traviscoan/cards)

**Hierarchical Classification**: An enhanced "Augmented CARDS" model uses a two-stage architecture: (1) a binary classifier distinguishes "convinced" from "contrarian" claims using supplementary Twitter data, then (2) a secondary classifier categorizes contrarian claims into their specific typology. This hierarchical approach addresses category imbalance, which is a common problem in misinformation detection. (https://arxiv.org/html/2404.15673v1)

**Scale**: The Augmented CARDS model was applied to five million climate-themed tweets over a six-month period in 2022, finding that over half of contrarian climate claims on Twitter involve attacks on climate actors, with spikes coinciding with political events, natural events, and influencer activity. (https://www.nature.com/articles/s43247-024-01573-7)

**Key Implication for H&M**: The CARDS approach demonstrates that manufactured doubt follows identifiable textual patterns that can be classified at scale. The two-stage "is it contrarian? then what type?" architecture maps directly to H&M's need: first detect manufactured doubt, then classify which of the 28 tactics is being used.

### 2.2 The FLICC Taxonomy and Fallacy Detection

The FLICC framework (Fake experts, Logical fallacies, Impossible expectations, Cherry picking, Conspiracy theories) provides a complementary taxonomy with **26 subtypes** across five main categories. Developed by John Cook and used in the Denial101x MOOC, FLICC identifies the rhetorical techniques underlying science denial across all domains, not just climate. (https://skepticalscience.com/history-flicc-5-techniques-science-denial.html)

A study combining FLICC with CARDS achieved computational detection of **12 fallacy types** in climate misinformation using microsoft/deberta-base-v2-xlarge fine-tuned with focal loss (gamma=4). Training data: 2,509 manually annotated examples. The model achieved **F1 score of 0.73**, a 2.5-3.5x improvement over prior work (0.21-0.29). (https://arxiv.org/html/2405.08254v1; published in *Scientific Reports*: https://www.nature.com/articles/s41598-024-76139-w)

The 12 detected fallacies split into two categories:

*Structural fallacies* (detectable from text form alone): ad hominem, anecdote, cherry picking, conspiracy theory, fake experts, false choice, false equivalence, impossible expectations.

*Background knowledge fallacies* (requiring factual context): misrepresentation, oversimplification, single cause, slothful induction.

**Critical Mapping to 28-Tactic Taxonomy**: The FLICC fallacies map onto the Science of Spin tactics:

| FLICC Fallacy | Maps to Tactic # |
|---|---|
| Fake experts | #2, #26 (Reputable Individuals, Abuse Credentials) |
| Cherry picking | #3, #9 (Misrepresent Data, Blame Other Causes) |
| Impossible expectations | #1, #24 (Attack Study Design, Question Causality) |
| Conspiracy theory | #13 (Pose as Defender of Truth) |
| Ad hominem | #22 (Attack Opponents) |
| False equivalence | #16 (Appeal to Mass Media / false balance) |
| Anecdote | #12 (Exploit Scientific Illiteracy) |
| Straw man | #25 (Make Straw Man Arguments) |

### 2.3 SemEval Propaganda Technique Detection

The SemEval-2020 Task 11 established a benchmark for fine-grained propaganda technique detection in news articles, with **14 propaganda techniques** including: Loaded Language, Name Calling/Labeling, Repetition, Exaggeration/Minimization, Doubt, Appeal to Fear/Prejudice, Flag-Waving, Causal Oversimplification, Slogans, Appeal to Authority, Black-and-White Fallacy, Thought-terminating Cliches, Bandwagon/Reductio ad Hitlerum, and Straw Men/Whataboutism/Red Herring. (https://aclanthology.org/2020.semeval-1.186/)

The task provided a labeled corpus of 536 articles from 13 propaganda and 36 non-propaganda news outlets, with two subtasks: span identification (locating propaganda text fragments) and technique classification. Top systems used pre-trained transformer ensembles. 250 teams registered, 44 submitted on the test set.

**H&M relevance**: The SemEval propaganda techniques overlap significantly with the 28-tactic taxonomy. The "Doubt" technique maps directly to manufactured doubt. The span-identification subtask is particularly relevant: H&M could identify not just that a text contains manufactured doubt, but *which specific passages* employ which tactics.

### 2.4 Linguistic Markers of Deception (General)

Research on computational deception detection provides additional foundation. Key linguistic features:

- **Shorter, less detailed responses** with fewer sensory or concrete details (https://www.sciencedirect.com/science/article/pii/S0950705123001727)
- **More negative emotion words** and language reflecting cognitive load
- **Hedging patterns**: Words like "possible," "sort of," "perhaps" used strategically rather than naturally (https://direct.mit.edu/coli/article/45/4/819/93386/Negation-and-Speculation-Detection)
- **Certainty markers used deceptively**: Words like "always," "never," "definitely" appearing in contexts where genuine uncertainty would be expected
- **Proximity patterns**: The distance between linguistic markers (hedges, certainty words, negation) forms predictive patterns

Machine learning models trained on these features achieve 69.4-77.3% accuracy in detecting deception, compared to 54.7% for naive human judges and 59.4% for expert judges. (https://journals.sagepub.com/doi/10.1177/0261927X251316883)

### 2.5 Coordinated Inauthentic Behavior Detection

For detecting organized doubt campaigns (as opposed to individual claims):

- **Graph-based approaches**: Model coordination as a graph classification task using random weighted walks biased by local density measures (degree, core number, truss number). Skip-gram embeddings produce density-aware structural embeddings. (https://arxiv.org/pdf/2506.13912)
- **Community detection**: Coordination networks based on repost relationships with GNN-based community classification. (https://ceur-ws.org/Vol-3138/paper6_jot.pdf)
- **LLM-augmented detection**: Frameworks encode both structural and textual propagation tree information as text, then use prompt engineering and RAG to detect organized astroturf campaigns. (https://arxiv.org/pdf/2501.11849)

### 2.6 LLM-Based Detection and Correction

State-of-the-art models (GPT-4, LLaMA-3, RoBERTa-large) are being used to identify, classify, and generate scientifically grounded corrections for climate misinformation. (https://www.mdpi.com/2504-2289/10/1/34)

A separate line of research traces hidden rhetorical strategies in LLM-generated propaganda itself, analyzing over 340,000 articles across GPT variants and finding that all models rely heavily on cognitive language to simulate deliberation combined with consistent moral framing. (https://www.sciencedirect.com/science/article/abs/pii/S0306457325003449)

**H&M relevance**: The LLM backbone can serve as both detector and corrector, identifying manufactured doubt tactics and then generating inoculation-style counter-narratives (see Section 5.4).

### 2.7 Proposed Feature Set for H&M's Doubt Detector

Synthesizing across all computational approaches surveyed, H&M's manufactured doubt detector should use the following feature categories:

**Tier 1: Text-level features (per-claim analysis)**
- FLICC fallacy classification (12 types, structural + background knowledge)
- SemEval propaganda technique detection (14 types including "Doubt")
- Certainty/hedging marker density and distribution
- Loaded language detection ("junk science," "sound science," "alarmist," "hoax")
- Rhetorical question density
- Appeal-to-authority pattern detection (credential claims, institutional affiliations)
- Straw man detection (misrepresentation of opposing arguments)

**Tier 2: Source-level features (per-source analysis)**
- Funding disclosure presence/absence
- Conflict of interest indicators
- Publication venue quality (peer-reviewed vs. blog/opinion)
- Author credential relevance (in-domain vs. out-of-domain expertise, i.e., Tactic #26)
- Historical accuracy of source

**Tier 3: Network-level features (campaign detection)**
- Coordinated posting patterns (timing, content similarity)
- Source network centrality (do many claims trace to few organizations?)
- Cross-platform amplification patterns
- Tactic co-occurrence patterns (multiple tactics from the 28-tactic list in same campaign)

---

## 3. Distinguishing Manufactured Doubt from Genuine Scientific Uncertainty

### 3.1 Agnotology: The Theoretical Framework

The field of agnotology, coined by Robert Proctor (Stanford), studies culturally induced ignorance. Three forms of ignorance (Proctor, 2008):
1. **Native ignorance**: not yet knowing (normal science)
2. **Selective ignorance**: choosing not to know (prioritization)
3. **Actively constructed ignorance**: manufactured doubt (strategic deception)

Only the third is manufactured doubt. The key diagnostic: manufactured doubt is designed to *prevent action*, while genuine uncertainty is designed to *invite more research*. (https://wp.unil.ch/serendip/files/2018/10/Agnotology-Ch-1-Proctor-2008.pdf)

### 3.2 Structural Signatures That Distinguish the Two

Based on the research surveyed, the following structural signatures differentiate manufactured from genuine doubt:

**Manufactured Doubt Signatures:**
1. **Direction of conclusion**: Always concludes toward inaction/delay, never toward precaution
2. **Funding source correlation**: Claims systematically align with funder interests
3. **Uncertainty conflation**: Conflates probabilistic uncertainty (normal science) with epistemic unreliability (manufactured framing). Smithson (2008) identifies this as a core mechanism. (https://en.wikipedia.org/wiki/Agnotology)
4. **Asymmetric scrutiny**: Demands impossibly high proof standards for inconvenient findings while accepting weak evidence for convenient ones (Tactic #1, #11)
5. **Absence of constructive proposals**: Never proposes studies that could resolve the uncertainty; goal is permanent doubt
6. **Internal-external contradiction**: Internal documents acknowledge what public statements deny (the Exxon pattern)
7. **Tactic co-occurrence**: Multiple tactics from the 28-tactic taxonomy appear together in coordinated campaigns
8. **Source network structure**: Claims trace back to a small number of funded organizations, think tanks, or PR firms
9. **Temporal persistence**: Manufactured doubt persists unchanged despite accumulating counter-evidence; genuine uncertainty narrows over time

**Genuine Scientific Uncertainty Signatures:**
1. **Bidirectional conclusions**: Can lead to either more research, precaution, or revised understanding
2. **Specific and bounded**: Identifies specific knowledge gaps rather than blanket doubt
3. **Constructive engagement**: Proposes experiments or studies that could resolve the uncertainty
4. **Peer-review engagement**: Seeks peer review rather than avoiding it
5. **Transparent methodology**: Openly acknowledges limitations and funding sources
6. **Consensus-building**: Aims to converge on shared understanding, not to sustain disagreement indefinitely
7. **Self-correction**: Updates positions as new evidence emerges

### 3.3 The Supran-Oreskes Methodology: Gold Standard for Detection

Supran and Oreskes (2017) developed a rigorous methodology for comparing internal vs. external statements. They performed document-by-document textual content analysis of 187 ExxonMobil climate change communications: peer-reviewed papers, non-peer-reviewed publications, internal company documents, and paid advertorials in The New York Times. (https://cssn.org/wp-content/uploads/2020/12/Assessing-ExxonMobils-climate-change-communications-1977%E2%80%932014-Geoffrey-Supran-.pdf)

Key finding: They scored each document on whether it positioned climate change as real, human-caused, serious, and solvable. In all four dimensions, "as documents become more publicly accessible, they increasingly communicate doubt." The company's own scientists' projections were "consistent with, and at least as skillful as, those of independent academic and government models." (https://www.science.org/doi/10.1126/science.abk0063)

This internal-external contradiction is the most reliable single indicator of manufactured doubt. For H&M, the practical heuristic is: when a source's technical/internal statements contradict its public messaging, flag for manufactured doubt.

### 3.4 Programmatic Decision Framework for H&M

Based on the research, H&M can implement the following decision tree:

```
INPUT: A claim expressing doubt about a scientific finding

Step 1: CONSENSUS CHECK
  - Is there established scientific consensus on this topic? (>90% expert agreement)
  - If YES: elevated suspicion for manufactured doubt. Proceed to Step 2.
  - If NO: likely genuine uncertainty. Mark as "legitimate debate" and proceed to nuanced analysis.

Step 2: TACTIC PATTERN SCAN
  - Run FLICC fallacy detection on the text
  - Run 28-tactic pattern matching
  - Count distinct tactics present
  - If 0-1 tactics: low confidence of manufacture
  - If 2-3 tactics: medium confidence
  - If 4+ tactics: high confidence (manufactured doubt campaigns typically deploy multiple tactics simultaneously)

Step 3: SOURCE ANALYSIS
  - Check funding source and conflict of interest
  - Check author credential relevance (in-domain vs. out-of-domain)
  - Check if source has history of doubt manufacturing on this topic
  - If source has documented COI: elevate confidence

Step 4: STRUCTURAL CHECK
  - Does the doubt conclude toward inaction/delay? (+weight for manufactured)
  - Does it propose constructive research to resolve uncertainty? (-weight for manufactured)
  - Is the doubt specific and bounded, or blanket? (blanket = +weight for manufactured)

Step 5: OUTPUT CLASSIFICATION
  - Score 0-3: "Genuine uncertainty" -- Bridge Builder may engage
  - Score 4-6: "Possible manufactured doubt" -- flag for human review, Bridge Builder uses caution
  - Score 7+: "Likely manufactured doubt" -- epistemic asymmetry override, no false balance
```

---

## 4. Historical Case Studies and Training Data Sources

### 4.1 UCSF Industry Documents Library

The Truth Tobacco Industry Documents Library (formerly Legacy Tobacco Documents Library) at UCSF contains over **16 million items** (80+ million pages) of previously secret internal corporate documents from major tobacco companies. Created in 2002, it covers advertising, manufacturing, marketing, sales, and scientific research activities. (https://www.industrydocuments.ucsf.edu/tobacco/)

The library provides:
- Full-text search across all documents
- XML API for metadata access
- OCR text available for download for computational research
- Documents from multiple litigation rounds

**H&M relevance**: This is the single largest corpus of documented manufactured doubt. Internal documents acknowledging harm alongside public statements denying it provide ground-truth positive examples. The famous Brown & Williamson memo ("Doubt is our product since it is the best means of competing with the 'body of fact' that exists in the mind of the general public") provides the defining example.

### 4.2 ExxonMobil Climate Documents

Supran and Oreskes analyzed 187 ExxonMobil communications (1977-2014), comparing internal scientific documents with public advertorials. The full dataset is available through Climate Files. (https://www.climatefiles.com/harvard/assessing-exxonmobils-global-warming-projections-science-january-2023-supran-rahmstorf-oreskes-reference-documents/)

Exxon's own climate projections (1977-2003) were quantitatively evaluated and found to be highly accurate, providing a unique "ground truth" where the company's internal science was correct while its public messaging contradicted it. (https://www.science.org/doi/10.1126/science.abk0063)

### 4.3 COVID-19 Misinformation Datasets

Multiple labeled datasets exist for COVID misinformation detection:

- **CoronaVirusFacts Alliance dataset**: 7,544 items from international fact-checkers (Kaggle)
- **Poynter fact-checked dataset**: 5,500 claim-explanation pairs from 70+ countries
- **FakeCovid**: 5,182 fact-checked news articles in 40 languages from 105 countries
- **COVIDLIES**: 6,761 expert-annotated COVID-19-related tweets

(All cited in: https://pmc.ncbi.nlm.nih.gov/articles/PMC9987189/)

- **CHECKED**: Chinese COVID-19 misinformation dataset, 2,104 verified microblogs (https://pubmed.ncbi.nlm.nih.gov/34178179/)

**Limitation**: These datasets label claims as true/false but do not specifically label *manufactured* doubt (organized campaigns) vs. organic misinformation. Additional labeling would be needed.

### 4.4 CARDS Climate Contrarianism Corpus

The CARDS project provides a labeled corpus from conservative think-tank websites and contrarian blogs spanning 20+ years, with claims classified into a hierarchical taxonomy of climate contrarianism. Replication code and data links: https://github.com/traviscoan/cards

### 4.5 SemEval-2020 Propaganda Corpus

The PTC-SemEval20 corpus contains 536 articles from 13 propaganda and 36 non-propaganda news outlets, annotated for 14 propaganda techniques with span-level annotations. Available via https://zenodo.org/records/3952415

### 4.6 Additional Resources

- **Four Shades of Life Sciences** (2025): Labeled disinformation in life sciences (https://arxiv.org/html/2507.03488v1)
- **Comprehensive Misinformation Dataset Guide** (2024): Survey of all available datasets by type, language, and annotation methodology (https://arxiv.org/html/2411.05060v1)
- **Climate Social Science Network (CSSN)**: Academic network tracking organized climate denial with published analyses (https://cssn.org/)

---

## 5. When Epistemic Asymmetry Should Override Bridge-Building

### 5.1 The False Balance Problem

False balance occurs when a viewpoint conflict is presented as though opposing sides enjoy comparable epistemic standing, when they do not. Research demonstrates concrete harm: exposure to falsely balanced discussions measurably damages attitudes and behavioral intentions. A study with 887 university students across three experiments found that "watching the public debate significantly damaged individuals' attitudes towards vaccination and their intention to get vaccinated." (https://pmc.ncbi.nlm.nih.gov/articles/PMC7528676/)

The BBC's own independent review (the Jones Report, 2011) concluded that "over-rigid" insistence on due impartiality risked giving "undue attention to marginal opinion" on scientific questions, putting fringe views on a par with well-established facts on issues including climate change, GM foods, and the MMR vaccine. (https://blogs.lse.ac.uk/medialse/2014/04/02/false-balance-in-climate-reporting-reveals-bbcs-sensitivity-to-political-pressure/)

### 5.2 Consensus Thresholds

Scientific consensus measurement provides quantitative thresholds:

- **Climate change**: Cook et al. (2013) found 97% consensus among publishing climate scientists that human activities cause global warming, based on analysis of 11,944 abstracts (1991-2011). A 2021 study found consensus exceeds 99%. (https://skepticalscience.com/global-warming-scientific-consensus.htm)
- **Vaccine safety**: Similar high consensus among immunologists and epidemiologists
- **Evolution**: Effectively universal consensus among biologists

The key insight is not a magic number but a pattern: when the remaining debate in the field "has moved on to other topics" and "the number of papers actually rejecting the consensus is a vanishingly small proportion of published research," the debate is settled for practical purposes. (https://theconversation.com/the-97-climate-consensus-is-over-now-its-well-above-99-and-the-evidence-is-even-stronger-than-that-170370)

### 5.3 Framework for H&M's Epistemic Asymmetry Override

Based on the research surveyed, H&M should override bridge-building (avoid "both sides" framing) when:

**Automatic Override Conditions** (any one sufficient):
1. Expert consensus exceeds 95% on the specific claim being disputed
2. The doubt source scores 7+ on the manufactured doubt decision tree (Section 3.4)
3. The doubt employs 3+ tactics from the universal tactics list (#1, #2, #3, #8, #21)
4. The source has documented funding from industries with direct financial interest in the doubt

**Weight-of-Evidence Approach** (when automatic conditions are not met):
Rather than presenting two sides as equal, H&M should adopt the "weight-of-evidence" approach recommended by science communication researchers: present the actual distribution of expert opinion. If 97% of experts agree, the response should reflect that ratio, not present a 50/50 split. (https://pmc.ncbi.nlm.nih.gov/articles/PMC7528676/)

**Forewarning Strategy**: Research shows that forewarning audiences about false-balance bias is consistently effective at protecting against manufactured doubt, while "outnumbering" (having more experts counter the contrarian) shows no measurable protective effect. The forewarning approach works across all three experiments tested and does not require specific rebuttals. (https://pmc.ncbi.nlm.nih.gov/articles/PMC7528676/)

This means H&M's responses should, when manufactured doubt is detected:
1. Name the tactic being used (forewarning/inoculation)
2. Present the actual consensus weight
3. Explain why the doubt appears manufactured rather than genuine
4. NOT present the manufactured doubt position as equally valid

### 5.4 Inoculation Theory: Prebunking as Active Defense

Psychological inoculation theory provides the scientific basis for H&M's counter-strategy. The approach works by exposing people to "weakened doses" of misinformation followed by strong rebuttals, building "mental antibodies" against future fake news. (https://misinforeview.hks.harvard.edu/article/global-vaccination-badnews/)

LLM-generated prebunking has been shown to be as effective as human-written prebunking in reducing belief in misinformation. A study on election rumors found that "purely AI-generated messages proved as effective as human-reviewed versions" at reducing belief in false claims and increasing confidence in election integrity. (https://arxiv.org/html/2410.19202v1)

**H&M implementation**: When the system detects manufactured doubt in a debate topic, it can generate inoculation-style responses that:
1. Identify the specific tactic being used (from the 28-tactic taxonomy)
2. Show a weakened example of how the tactic works
3. Provide the scientific counter-evidence
4. Explain why this pattern indicates manufactured rather than genuine doubt

Google's prebunking guide provides practical templates for this approach. (https://prebunking.withgoogle.com/docs/A_Practical_Guide_to_Prebunking_Misinformation.pdf)

### 5.5 Fact-Checking Organization Approaches

Fact-checking organizations aligned with the International Fact-Checking Network (IFCN) Code of Principles follow specific methodological standards:
- Provide at least two sources to verify central claims
- Prioritize claims with the most potential to cause harm
- Do not advocate or take policy positions on issues they check
- Draw on publicly available information with links to primary sources
- Distinguish between areas of genuine debate and settled science

Full Fact (UK) and AFP Fact Check both meet IFCN certification standards and prioritize harm-potential in their claim selection. (https://fullfact.org/about/how-we-fact-check/; https://ifcncodeofprinciples.poynter.org/application/public/afp-fact-checking/661a8b04ba7689d481419130)

**H&M adoption**: The IFCN principle of "prioritize by harm potential" provides a practical triage framework. When epistemic asymmetry is detected, H&M should assess the harm potential of the manufactured doubt (health harm, environmental harm, policy harm) and calibrate its response accordingly.

---

## 6. Implementation Synthesis for Huginn & Muninn

### 6.1 Architecture: Three-Layer Doubt Detection

**Layer 1: Claim-Level Analysis (per source text)**
- Run FLICC fallacy classification (8 structural + 4 background knowledge types)
- Run 28-tactic pattern matching using the Science of Spin taxonomy
- Detect loaded language markers ("junk science," "alarmist," "hoax," etc.)
- Detect SemEval propaganda techniques (14 types)
- Score: doubt_tactic_count, doubt_confidence

**Layer 2: Source-Level Analysis (per source/author)**
- Funding disclosure check
- Conflict of interest detection
- Author credential relevance (in-domain vs. cross-domain)
- Historical reliability score
- Score: source_credibility, coi_flag

**Layer 3: Campaign-Level Analysis (across multiple sources)**
- Coordinated posting pattern detection
- Source network centrality analysis
- Tactic co-occurrence across sources
- Cross-platform amplification patterns
- Score: coordination_score, campaign_flag

### 6.2 Decision Output

The three layers feed into a decision matrix:

| Doubt Score | Source Score | Campaign Score | Classification | Bridge Builder Behavior |
|---|---|---|---|---|
| Low | Clean | None | Genuine uncertainty | Normal bridge-building |
| Medium | Some COI | None | Possible manufactured | Cautious bridge-building with caveats |
| High | Documented COI | Coordinated | Likely manufactured | Epistemic asymmetry override |
| Any | Any | Strong coordination | Campaign detected | Full inoculation response |

### 6.3 Training Data Strategy

1. **Bootstrap from existing corpora**: CARDS (climate), UCSF Tobacco Library (tobacco), SemEval-2020 (propaganda), COVID datasets (health)
2. **Cross-domain transfer**: Train on tobacco/climate where labels are strongest, test on emerging domains
3. **LLM-as-classifier**: Use the LLM backbone itself for zero-shot and few-shot classification using the 28-tactic taxonomy as the classification schema
4. **Active learning**: Flag uncertain cases for human review, add to training data

### 6.4 Key Design Principles

1. **Detect tactics, not opinions**: The system should identify rhetorical tactics, not classify opinions as right or wrong. An opinion can be wrong without being manufactured doubt; manufactured doubt is specifically about the *process* of doubt creation, not the conclusion.
2. **Distinguish manufacturers from perpetuators**: A citizen sharing a tobacco industry talking point unknowingly is a perpetuator, not a manufacturer. H&M should help perpetuators understand they are being used, not attack them.
3. **Preserve genuine dissent**: Not all minority scientific opinions are manufactured doubt. The system must have high specificity (low false positive rate) to avoid suppressing legitimate scientific debate.
4. **Transparency**: When H&M flags manufactured doubt, it should explain which tactics were detected and why, with citations to the taxonomy. The user should be able to evaluate the system's reasoning.

---

## Sources

- Goldberg, Vandenberg, et al. (2021). "The science of spin." *Environmental Health*, 20, 33. https://pmc.ncbi.nlm.nih.gov/articles/PMC7996119/
- Boussalis, Coan, Cook, Nanko. "Computer-assisted classification of contrarian claims about climate change." *Scientific Reports*. https://www.nature.com/articles/s41598-021-01714-4
- CARDS replication code and data. https://github.com/traviscoan/cards
- Augmented CARDS. https://arxiv.org/html/2404.15673v1 and https://www.nature.com/articles/s43247-024-01573-7
- Fallacy detection in climate misinformation. https://arxiv.org/html/2405.08254v1 and https://www.nature.com/articles/s41598-024-76139-w
- FLICC taxonomy history. https://skepticalscience.com/history-flicc-5-techniques-science-denial.html
- SemEval-2020 Task 11. https://aclanthology.org/2020.semeval-1.186/
- Supran & Oreskes (2017). "Assessing ExxonMobil's climate change communications." https://cssn.org/wp-content/uploads/2020/12/Assessing-ExxonMobils-climate-change-communications-1977%E2%80%932014-Geoffrey-Supran-.pdf
- Supran, Rahmstorf, Oreskes (2023). "Assessing ExxonMobil's global warming projections." *Science*. https://www.science.org/doi/10.1126/science.abk0063
- UCSF Industry Documents Library. https://www.industrydocuments.ucsf.edu/tobacco/
- Climate Files (ExxonMobil reference documents). https://www.climatefiles.com/harvard/assessing-exxonmobils-global-warming-projections-science-january-2023-supran-rahmstorf-oreskes-reference-documents/
- COVID-19 misinformation detection survey. https://pmc.ncbi.nlm.nih.gov/articles/PMC9987189/
- Proctor (2008). "Agnotology: The Making and Unmaking of Ignorance." https://wp.unil.ch/serendip/files/2018/10/Agnotology-Ch-1-Proctor-2008.pdf
- Weight-of-evidence strategies. https://pmc.ncbi.nlm.nih.gov/articles/PMC7528676/
- BBC false balance review (Jones Report). https://blogs.lse.ac.uk/medialse/2014/04/02/false-balance-in-climate-reporting-reveals-bbcs-sensitivity-to-political-pressure/
- False balance effects. https://effectiviology.com/false-balance/
- Cook et al. climate consensus. https://skepticalscience.com/global-warming-scientific-consensus.htm
- Prebunking/inoculation theory. https://misinforeview.hks.harvard.edu/article/global-vaccination-badnews/
- AI-assisted inoculation. https://arxiv.org/html/2410.19202v1
- Google prebunking guide. https://prebunking.withgoogle.com/docs/A_Practical_Guide_to_Prebunking_Misinformation.pdf
- Deception detection via linguistic markers. https://www.sciencedirect.com/science/article/pii/S0950705123001727
- Deception detection accuracy. https://journals.sagepub.com/doi/10.1177/0261927X251316883
- Coordinated inauthentic behavior detection. https://arxiv.org/pdf/2506.13912 and https://ceur-ws.org/Vol-3138/paper6_jot.pdf
- LLM propaganda detection. https://www.sciencedirect.com/science/article/abs/pii/S0306457325003449
- LLM climate misinformation detection. https://www.mdpi.com/2504-2289/10/1/34
- Full Fact methodology. https://fullfact.org/about/how-we-fact-check/
- IFCN Code of Principles. https://ifcncodeofprinciples.poynter.org/
- Misinformation dataset guide. https://arxiv.org/html/2411.05060v1
- Four Shades of Life Sciences. https://arxiv.org/html/2507.03488v1

Status: COMPLETE
