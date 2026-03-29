# Band 1: Inoculation Through Naming

Status: COMPLETE
Date: 2026-03-28
Research cycles: 4 (broad survey, depth on duration/format, Biddlestone 2025, Google/Jigsaw field data)

---

## Does Naming Manipulation Techniques Reduce Susceptibility?

**Key finding: Yes, with strong evidence.** Psychological inoculation theory, developed by William McGuire in 1961, demonstrates that preemptive exposure to weakened forms of manipulation techniques builds cognitive resistance -- analogous to biological vaccination.

The mechanism operates through two components:

1. **Threat/forewarning**: Warning people they will encounter manipulative content activates a "mental immune system."
2. **Refutational preemption (prebunking)**: Providing the means to recognize and counter misleading arguments before encountering them in the wild.

A meta-analysis (2025, N=37,075) confirms that technique-based inoculation significantly improves misinformation discernment across populations. The Cambridge Social Decision-Making Lab (van der Linden, Roozenbeek, and colleagues) has been the primary research group advancing this work over the past decade.

**Critical nuance**: A 2025 study in PNAS Nexus found that inoculation effects were attenuated when content appeared within a realistic social media feed with distracting content. This "noise effect" suggests that real-world effectiveness may be lower than laboratory results indicate.

Sources:
- [van der Linden & Roozenbeek - Countering misinformation through inoculation (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0065260123000266)
- [Prebunking in the Modern Digital Age (NCBI Bookshelf)](https://www.ncbi.nlm.nih.gov/books/NBK609022/)
- [Limited effectiveness in social media feed (PNAS Nexus)](https://academic.oup.com/pnasnexus/article/4/6/pgaf172/8151956)
- [Inoculation to Resist Misinformation (PubMed)](https://pubmed.ncbi.nlm.nih.gov/38753337/)

---

## How Does Prebunking Compare to Debunking?

**Key finding: Debunking is slightly more effective per-exposure, but prebunking has strategic advantages.**

A meta-analytic study published jointly by the EU Joint Research Centre (2024) found:

- Both prebunking and debunking reduce agreement with false claims, reduce perceived credibility, and reduce sharing likelihood.
- **Debunking has a slight edge** in direct comparison because it refutes specific narratives with concrete evidence, making it feel more relevant.
- **Prebunking is perceived as more manipulative** (31.56% vs 25.87% of respondents felt the intervention was trying to manipulate them) but offers scalability advantages.

However, prebunking has a crucial strategic advantage: **the continued influence effect**. Once misinformation has been encountered, corrections struggle against the "illusory truth effect" -- repeated exposure to a falsehood increases its perceived truth regardless of corrections. Prebunking prevents this initial encoding.

**Systematic reviews consistently find "prevention is better than cure"** -- it is easier to prevent false belief formation than to correct it after the fact.

**Implication for H&M**: The current architecture labels manipulation techniques in every output (debunking mode). Adding a prebunking layer -- where users learn to recognize techniques before encountering them in disinformation -- would complement the existing approach. The "Name the Trick" (v5) feature already moves in this direction.

Sources:
- [EU JRC: Both prebunking and debunking work](https://joint-research-centre.ec.europa.eu/jrc-news-and-updates/misinformation-and-disinformation-both-prebunking-and-debunking-work-fighting-it-2024-10-25_en)
- [Comparison of prebunking and debunking (British Journal of Psychology)](https://bpspsychub.onlinelibrary.wiley.com/doi/10.1111/bjop.12551)
- [Source trust in prebunks and debunks across 4 EU countries (Nature Scientific Reports)](https://www.nature.com/articles/s41598-024-71599-6)
- [Prebunking chapter (Cambridge)](https://www.sdmlab.psychol.cam.ac.uk/files/media/countering.pdf)

---

## Key Studies: Bad News Game, Go Viral, and Google/Jigsaw

### Bad News (Cambridge, 2018-present)

The Bad News game is the flagship implementation of gamified inoculation. Players take the role of a fake news producer and master six manipulation techniques: polarization, emotional exploitation, conspiracy theories, trolling, deflecting blame, and impersonation.

**Results**:
- Significant reductions in perceived reliability of manipulative content across all languages tested.
- Improved ability to detect misinformation techniques compared to gamified control group.
- Crucially: also increases confidence in participants' own judgments (reducing the "learned helplessness" that can come from misinformation exposure).
- Cross-cultural validation: tested across multiple countries and languages with consistent effects.

Sources:
- [Good News about Bad News (Journal of Cognition, PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6952868/)
- [Fake news game confers psychological resistance (Nature Humanities & Social Sciences)](https://www.nature.com/articles/s41599-019-0279-9)
- [Bad News Game - Cambridge SDL Lab](https://www.sdmlab.psychol.cam.ac.uk/research/bad-news-game)

### Go Viral! (Cambridge + UK Government, 2020)

Developed during COVID-19 in partnership with the UK Cabinet Office. Simulates an environment for creating viral COVID misinformation. Shorter format than Bad News (5-7 minutes vs 15-20 minutes).

Source:
- [Cambridge: Go Viral game pre-bunks coronavirus conspiracies](https://www.cam.ac.uk/stories/goviral)

### Google/Jigsaw YouTube Field Experiment (2022)

The largest real-world inoculation deployment to date.

**Scale**: 5.4 million US YouTube users exposed to 90-second inoculation videos. Nearly 1 million watched for at least 30 seconds. 22,632 users completed voluntary test questions within 24 hours.

**Videos targeted**: Scapegoating, deliberate incoherence, emotionally manipulative language, false dichotomies.

**Results**:
- 5% average improvement in ability to recognize manipulation techniques.
- Effect was consistent across liberals and conservatives (no partisan asymmetry).
- Proof of concept that inoculation can scale to hundreds of millions of users at low cost.

**Follow-up**: Jigsaw deployed prebunking campaigns in Poland, Slovakia, and Czech Republic targeting Ukrainian refugee disinformation, and before the 2024 EU Elections reached 120M+ YouTube users across 12 nations.

Sources:
- [Cambridge: Social media experiment (ScienceDaily)](https://www.sciencedaily.com/releases/2022/08/220824152220.htm)
- [Psychological inoculation on social media (Science Advances)](https://www.science.org/doi/10.1126/sciadv.abo6254)
- [YouTube inoculation experiment (phys.org)](https://phys.org/news/2022-08-youtube-reveals-potential-inoculate-millions.html)

### Biddlestone et al. (2025, Political Psychology)

Most recent validation study. Tested six inoculation videos in two pre-registered experiments:

**Study 1 (N=1,583)**: Three videos targeting manipulation tactics (polarization, conspiracy theories, fake experts). All three increased detection of manipulative content vs. control. However, only the polarization video increased overall discernment (ability to distinguish manipulative from non-manipulative content).

**Study 2 (N=1,603)**: Three videos targeting logical fallacies (whataboutism, moving the goalposts, strawman). Detection improved in all conditions. Only the strawman video increased overall discernment.

**Key implication**: Not all technique labels are equally effective. Some tactics (polarization, strawman) are easier to learn to detect than others (conspiracy thinking, whataboutism). This has direct implications for which techniques H&M should prioritize in its "Name the Trick" feature.

Sources:
- [Biddlestone et al. 2025 (Political Psychology)](https://onlinelibrary.wiley.com/doi/full/10.1111/pops.70015)
- [Video inoculation across 12 EU nations (Communications Psychology)](https://www.nature.com/articles/s44271-025-00379-3)

---

## What Is the Optimal Format for Naming Techniques?

Research suggests a hierarchy of effectiveness based on format:

### Format Options (from research)

1. **Technique name + mechanic explanation + example** (most effective): The Bad News game uses this three-part structure. Players learn the name ("polarization"), understand the mechanic ("amplifying divisions to create us-vs-them framing"), and practice with an example (creating a divisive social media post). This produces the strongest inoculation effects.

2. **Short video with narrative example** (scalable): The Google/Jigsaw 90-second clips use humor and purposeful exaggeration to demonstrate tactics. Effective at scale but produces smaller effect sizes than interactive formats.

3. **Technique name alone** (minimal effect): Simply labeling a technique without explaining the mechanic or showing an example produces the weakest inoculation. The label needs the "refutational preemption" component to activate cognitive immunity.

4. **Historical/real-world parallel** (untested but theoretically strong): McGuire's original 1964 work used historical propaganda examples. The Institute for Propaganda Analysis (founded 1938) used real-world examples effectively. No modern RCT directly compares historical parallels to abstract explanations, but cognitive science principles (concrete > abstract, narrative > exposition) suggest this would be highly effective.

### Practical Recommendation for H&M

The optimal format for H&M's technique labeling would be a three-layer structure:
- **Layer 1**: Technique name (single word or short phrase): "Scapegoating"
- **Layer 2**: Mechanic explanation (one sentence): "Blaming a specific group for a complex problem to create an enemy and deflect accountability."
- **Layer 3**: Parallel example (concrete): "This is the same tactic used by tobacco companies when they blamed individual choice for lung cancer rates instead of their product."

This maps directly to the inoculation research: name + mechanic + weakened dose.

---

## How Long Does Inoculation Last? Does It Need Boosters?

**Key finding: Effects decay within weeks without reinforcement. Boosters are necessary.**

### Duration Without Boosters

- **Text-based and video-based inoculation**: Effects remain detectable for approximately one month, then decay significantly.
- **Game-based inoculation (Bad News)**: When paired with added testing, effects of a single play last at least three months. Without retesting, game-based effects decay more rapidly than video-based formats.

### Booster Research

A 2025 study in Nature Communications (Roozenbeek et al.) tested psychological "booster shots" targeting memory:

- **Study design**: Inoculation at baseline, measurement at 0/10/30 days, with a booster group receiving reinforcement at day 10.
- **Key finding**: Memory (not motivation) is the primary predictor of intervention longevity. Participants who better remembered the manipulation techniques showed more durable effects.
- **Booster effectiveness**: The booster at day 10 significantly extended effectiveness through the 30-day measurement point.

### Implications for Decay

Earlier smoking prevention research (inoculation applied to health behaviors) showed effects lasting up to two years when boosters were provided periodically. This suggests the decay problem is solvable with appropriate reinforcement schedules.

Sources:
- [Psychological booster shots (Nature Communications)](https://www.nature.com/articles/s41467-025-57205-x)
- [Inoculation Theory (Wikipedia)](https://en.wikipedia.org/wiki/Inoculation_theory)
- [Psychological Inoculation: Current Evidence (SAGE)](https://journals.sagepub.com/doi/10.1177/00027162221087936)
- [Inoculation Theory overview (Arizona Open Textbooks)](https://opentextbooks.library.arizona.edu/immersivetruth/chapter/inoculation-theory-new/)

---

## Practical Implications for Huginn & Muninn

### What the research confirms

1. **H&M's technique labeling in every output is well-supported.** The TTP Classifier (DISARM framework) and the manufactured doubt taxonomy (Goldberg et al.) both function as inoculation -- naming the trick reduces its power.

2. **The "Name the Trick" (v5) feature is the right direction.** Moving from passive labeling (H&M names techniques for the user) to active recognition (user learns to name techniques themselves) aligns with the strongest inoculation research (Bad News game model).

3. **The three-layer format (name + mechanic + parallel) should be the standard.** Simply labeling a technique is insufficient. Each technique label should include the mechanic and a concrete example.

### What the research warns about

1. **Decay is real.** H&M should build in spaced repetition or periodic review of previously learned techniques. The mandatory fading architecture already exists; adding "booster" encounters with previously learned techniques during the fading process would address this.

2. **Not all techniques are equally learnable.** Biddlestone (2025) found that polarization and strawman fallacies are more detectable after inoculation than conspiracy thinking or whataboutism. H&M should prioritize teaching the most learnable techniques first and scaffold harder ones.

3. **Social media noise attenuates effects.** Real-world effectiveness will be lower than controlled-setting results. H&M's Socratic dialogue format may partially address this by creating a focused, low-distraction context for learning.

4. **Prebunking can feel manipulative.** 31.56% of participants in one study felt prebunking was trying to manipulate them. H&M's transparency-first approach (showing reasoning, not declaring verdicts) should mitigate this, but the risk should be monitored.

### Specific design recommendations

- Add a "technique library" that users build over time, reviewing previously learned techniques with spaced repetition
- Use the three-layer format (name + mechanic + parallel) for all technique labels
- Sequence technique learning from most to least learnable (polarization, strawman first; abstract conspiracy logic later)
- Include "booster" encounters at roughly 10-day intervals for techniques already learned
- Frame technique naming as empowerment ("you now have a word for this") rather than correction ("this is what they did to you")

---

## Sources

- Biddlestone, M. et al. (2025). Tune in to the prebunking network! Development and validation of six inoculation videos. *Political Psychology*. [Wiley](https://onlinelibrary.wiley.com/doi/full/10.1111/pops.70015)
- EU Joint Research Centre (2024). Misinformation and disinformation: both prebunking and debunking work. [JRC](https://joint-research-centre.ec.europa.eu/jrc-news-and-updates/misinformation-and-disinformation-both-prebunking-and-debunking-work-fighting-it-2024-10-25_en)
- McGuire, W. J. (1964). Inducing resistance to persuasion. *Advances in Experimental Social Psychology*.
- Roozenbeek, J. & van der Linden, S. (2019). Fake news game confers psychological resistance against online misinformation. *Palgrave Communications*. [Nature](https://www.nature.com/articles/s41599-019-0279-9)
- Roozenbeek, J. et al. (2022). Psychological inoculation improves resilience against misinformation on social media. *Science Advances*. [Science](https://www.science.org/doi/10.1126/sciadv.abo6254)
- Roozenbeek, J. et al. (2025). Psychological booster shots targeting memory increase long-term resistance against misinformation. *Nature Communications*. [Nature](https://www.nature.com/articles/s41467-025-57205-x)
- Roozenbeek, J., Basol, M. et al. (2020). Prebunking interventions based on inoculation theory can reduce susceptibility to misinformation across cultures. *Harvard Kennedy School Misinformation Review*. [HKS](https://misinforeview.hks.harvard.edu/article/global-vaccination-badnews/)
- Tay, L. Q. et al. (2022). A comparison of prebunking and debunking interventions. *British Journal of Psychology*. [Wiley](https://bpspsychub.onlinelibrary.wiley.com/doi/10.1111/bjop.12551)
- Video inoculation across 12 EU nations (2025). *Communications Psychology*. [Nature](https://www.nature.com/articles/s44271-025-00379-3)
