# Band 1: Socratic Skill Transfer & Dependency Mitigation

**Research question**: How can H&M mitigate the dependency paradox through Socratic skill transfer?

---

## 1. Directive Correction vs. Genuine Socratic Questioning

### The Core Distinction

The fundamental difference between directive AI correction and genuine Socratic questioning lies in who does the cognitive work. Directive correction provides answers, corrections, and information directly to the user; Socratic questioning guides the user to construct understanding through their own reasoning.

Research from a 2025 Frontiers in Education study comparing ChatGPT and human tutors found that AI systems delivering information directly may promote dependency and reduce students' cognitive abilities, while those guiding students through Socratic questioning strengthen critical thinking skills and engagement (https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1528603/full).

### Grounding in the Bao et al. (2025) Findings

The paper "Dialogues with AI Reduce Beliefs in Misinformation but Build No Lasting Discernment Skills" (Bao et al., 2025) provides the concrete evidence for the dependency paradox (https://arxiv.org/html/2510.01537v1). Key findings:

- **Immediate gains**: +21.3 percentage point improvement in accuracy during AI-assisted sessions
- **Dependency formation**: Unassisted performance declined by -15.3 percentage points by week 4
- **Mechanism**: Human agreement with AI increased from 23.0% to 28.5% over four weeks, while independent thinking remained consistently low (~7%)
- **Pattern shift**: Participants shifted from active questioning to passive reliance on AI validation -- they increasingly relied on AI validation rather than internalizing detection strategies
- **Critical finding**: "Guiding and probing questions" (Socratic methods) correlated with independent detection abilities (r=0.29), while directive methods like confidence calibration and devil's advocate approaches undermined learning

This directly maps to the directive vs. Socratic distinction. The AI in the Bao et al. study was primarily directive -- it told users whether content was misinformation and explained why. A genuinely Socratic approach would instead ask: "What makes you think this claim is true? What evidence would change your mind? Who benefits from you believing this?" -- forcing the user to do the cognitive work.

### Didactic vs. Socratic Tutoring in the Literature

A comparative evaluation of Socratic versus didactic tutoring found that Socratic tutoring emphasizes "eliciting information from students through directed reasoning, with tutors avoiding giving information away as much as possible" (https://www.researchgate.net/publication/2847554_A_Comparative_Evaluation_of_Socratic_versus_Didactic_Tutoring). The Socratic tutor's role is to ask questions that lead the student to discover inconsistencies in their own reasoning, not to point out errors directly.

Non-directive facilitation -- where tutors focus on guiding rather than leading -- encourages students to construct stronger arguments and engage critically with diverse perspectives (https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1528603/full).

### The "Cognitive Scaffolding Addiction" Risk

Even Socratic approaches carry a dependency risk if poorly designed. Research warns that over-reliance on AI questioning can create "cognitive scaffolding addiction" -- students begin to expect the AI to do the hard thinking, structuring every step of their reasoning process (https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1528603/full). This is a critical design consideration for Huginn & Muninn: the three questions must become the user's *own* mental framework, not a crutch they only use when the AI is present.

### What Makes Socratic Questioning "Genuine"

Structured, multi-turn questioning sequences that transition from broad exploration to targeted inquiry empower learners to construct knowledge through guided self-discovery, strengthening self-efficacy and cultivating critical thinking by challenging learners to articulate their reasoning (https://aicompetence.org/ai-socratic-tutors/). The key design principle: the AI should never articulate a conclusion that the user could reach themselves with the right question.

A 2025 paper on Socratic LLMs ("Discerning Minds or Generic Tutors?") evaluates whether LLMs can provide genuine instructional guidance rather than generic tutoring, finding that current LLMs often show hesitancy to provide clear corrective feedback, which paradoxically may hinder novice understanding (https://arxiv.org/html/2508.06583v1). This suggests a nuanced design challenge: pure non-directiveness fails beginners, while pure directiveness creates dependency.

---

## 2. Scaffolding and Fading: From ZPD Theory to AI Design

### Vygotsky's Zone of Proximal Development

Vygotsky's foundational concept of the Zone of Proximal Development (ZPD), developed in the 1920s-1930s and published posthumously in *Mind in Society* (1978), describes the space between what a learner can do independently and what they can achieve with guidance from a More Knowledgeable Other (MKO) (https://www.simplypsychology.org/zone-of-proximal-development.html). In H&M's context, the ZPD is the gap between a user's current ability to critically evaluate information and their potential ability when guided by the three-question framework.

### Bruner's Scaffolding Theory

Jerome Bruner, David Wood, and Gail Ross introduced "scaffolding" in their 1976 paper "The Role of Tutoring in Problem Solving," describing the temporary support system that helps learners progress through their ZPD until they can perform tasks independently (https://www.simplypsychology.org/zone-of-proximal-development.html). The critical feature is that scaffolding is *temporary* -- it must be gradually withdrawn as competence grows.

### The Zone of No Development (ZND) -- Critical Warning

A major 2025 finding directly relevant to H&M's design: when AI assistance never fades, the learner's comfort zone ceases to expand, and the ZPD gradually transforms into a "Zone of No Development" (ZND). The paper argues that "productive struggle, self-regulation, and first-principles reasoning remain essential for durable learning, and responsible use of AI in education must include explicit mechanisms to end its help when mastery begins" (https://arxiv.org/html/2511.12822v1).

This is the theoretical grounding for the Bao et al. dependency finding. If AI Socratic dialogue never fades -- if the AI always asks the questions for users rather than training them to ask questions themselves -- the ZPD collapses into a ZND, and independent discernment degrades.

### What Fading Looks Like in an AI Dialogue System

AI systems have emerged as MKOs within learners' ZPDs, offering unique forms of scaffolding previously unavailable (https://link.springer.com/article/10.1007/s42087-022-00304-8). But the fading component is where most AI systems fail. Based on the literature, fading in an AI dialogue system should involve:

1. **Phase 1 (Full scaffolding)**: AI asks all three questions explicitly, models the reasoning process
2. **Phase 2 (Partial scaffolding)**: AI prompts with one question, user generates the others
3. **Phase 3 (Minimal scaffolding)**: AI presents the information/claim; user applies the framework independently, AI validates afterward
4. **Phase 4 (Independence check)**: AI presents scenarios without any prompting; measures whether user spontaneously applies the framework

Real-time adjustment of scaffolding is now possible through intelligent tutoring systems that adapt to learner progress (https://www.oreateai.com/blog/scaffolding-learning-vygotskys-insights-in-the-age-of-ai/51f46497c074de92ea86080ae4b627dd).

---

## 3. Metacognitive Skill Transfer

### Teaching Users to Ask the Right Questions

The core goal for H&M is metacognitive skill transfer: teaching users not just *what* to think about disinformation, but *how* to think about it -- specifically, training them to internalize and spontaneously apply the three-question framework.

### Halpern's Four-Part Model for Critical Thinking Transfer

Diane Halpern (1998) proposed a 4-part empirically-based model for teaching critical thinking with transfer: (a) a dispositional component to prepare learners for effortful cognitive work, (b) instruction in critical thinking skills, (c) training in the structural aspects of problems and arguments to promote transcontextual transfer, and (d) a metacognitive component including checking for accuracy and monitoring progress toward the goal (https://pubmed.ncbi.nlm.nih.gov/9572008/). Components (c) and (d) are most relevant to H&M: the three questions *are* the structural framework, and metacognitive monitoring is the user's ability to recognize when they should apply them.

### Metacognitive Strategies in Practice

Research shows that metacognition can be developed through "applying questions aimed at the relevant tasks which must be undertaken regarding a task (meta-knowledge questions)" and these reflective questions facilitate supervising knowledge level, resource use, and the quality of the product achieved (https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.913219/full). This directly supports H&M's three-question design: the questions *are* metacognitive prompts that, when internalized, become self-directed monitoring tools.

### Transfer of Metacognitive Skills Across Domains

A key study on metacognitive skill transfer found that "hybrid training, which addresses both metacognitive skills and cognitive strategies, supports near transfer" of metacognitive skills, and that "metacognitive skills are task-general and transferable to a wide variety of learning tasks" (https://link.springer.com/article/10.1007/s11409-020-09237-5). This is encouraging for H&M: if the three-question framework is taught as a metacognitive skill (not domain-specific knowledge), it should transfer to novel disinformation contexts the user has never encountered.

### Question-Generation Training

Results from research on metacognitive strategies showed significant improvements in substantive and dialogic dimensions and associated basic skills for those who used tools promoting metacognitive strategies (https://www.jotse.org/index.php/jotse/article/view/2721/879). Training users to *generate* questions (rather than just answer them) is a higher-order metacognitive skill that builds independence.

---

## 4. Self-Regulated Learning and Desirable Difficulties

### Zimmerman's SRL Model and AI Tutoring

Barry Zimmerman's three-phase model of self-regulated learning (SRL) guides learners through: (1) forethought (goal-setting, strategic planning), (2) performance (monitoring, strategy deployment), and (3) self-reflection (evaluating outcomes, adjusting approach) (https://www.researchgate.net/publication/237065878_Becoming_a_Self-Regulated_Learner_An_Overview). AI tutoring systems predominantly influence the performance phase -- providing real-time guidance and monitoring -- but often neglect the forethought and self-reflection phases that build independence (https://educationaltechnologyjournal.springeropen.com/articles/10.1186/s41239-023-00406-5).

For H&M, this means the system must explicitly support all three phases: prompting users to set their own analysis goals ("What am I trying to determine about this claim?"), monitoring their reasoning process during dialogue, and reflecting afterward ("Did my initial instinct match my conclusion? What changed my mind?").

### The On-Demand vs. System-Regulated Access Discovery

A landmark finding from Wharton research directly quantifies the dependency problem: students with on-demand access to an AI tutor achieved only 30% performance gains, while those with system-regulated (structured, automatic) access achieved 64% gains -- more than double (https://knowledge.wharton.upenn.edu/article/when-does-ai-assistance-undermine-learning/). The researchers found that on-demand users increasingly outsourced decision-making to the AI, requesting help every 3-4 moves by month three, while system-regulated users preserved independent problem-solving.

This is perhaps the single most actionable finding for H&M: unrestricted access to AI dialogue creates dependency, while structured access builds independence. The study's lead researcher noted: "Self-regulation is hard, even when you know something isn't good for you" -- meaning users cannot be trusted to self-limit their AI reliance.

### Bjork's Desirable Difficulties Framework

Robert Bjork (1994) identified four key "desirable difficulties" that slow learning in the short term but dramatically improve long-term retention and transfer (https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/04/EBjork_RBjork_2011.pdf):

1. **Spacing**: Distributing practice over time rather than massing it
2. **Interleaving**: Mixing different types of problems rather than blocking by type
3. **Retrieval practice**: Testing oneself rather than re-reading material
4. **Generation**: Producing answers before being shown them

Bjork's research demonstrates that "conditions that lend themselves to rapid performance gains often fail to support long-term retention, whereas the conditions that do seem to create challenges and slow the rate of apparent learning" (https://www.researchgate.net/publication/284097727_Making_things_hard_on_yourself_but_in_a_good_way_Creating_desirable_difficulties_to_enhance_learning). This creates a paradox that Bjork terms the "illusion of knowing" -- fluent re-reading feels like mastery, but is often shallow familiarity.

Desirable difficulties like spaced practice and interleaving improve retention by up to 80% compared to traditional cramming methods (https://www.structural-learning.com/post/desirable-difficulties).

### Application to H&M: Making Disinformation Analysis Harder

The desirable difficulties framework has direct implications for H&M's design:

- **Spacing**: Don't let users binge-analyze claims. Space out Socratic dialogues and introduce delays between AI interactions.
- **Interleaving**: Mix genuine and misleading content; mix different types of manipulation techniques; don't let the user get comfortable with one pattern.
- **Retrieval practice**: Before showing any AI analysis, ask users to retrieve and apply the three-question framework from memory. The pretesting effect shows consistent advantages even when pretests generate errors (https://journalofcognition.org/articles/10.5334/joc.455).
- **Generation**: Have users generate their own assessment before seeing any AI input. The generation effect ensures deeper encoding when learners produce answers rather than passively receiving them.

### The Feedback Timing Question

Research on delayed vs. immediate feedback shows nuanced findings. While immediate feedback is generally preferred, delayed feedback creates a spacing effect that can improve long-term retention through the "elaborative retrieval hypothesis" -- retrieving information activates semantically related concepts, creating richer associative networks (https://www.nature.com/articles/s41599-024-03983-6). For H&M, this suggests that the AI should not immediately validate or correct user analyses; instead, a brief delay forces users to sit with their own judgment.

---

## 5. Design Patterns That Prevent Dependency

### Pattern 1: Forced Self-Assessment Before AI Feedback ("Think First")

The generation effect and pretesting research converge on a single principle: users must commit to their own analysis *before* receiving any AI input. The Bao et al. study found that participants who engaged with guiding and probing questions showed a positive correlation with independent detection abilities (r=0.29), while those who passively received AI assessments showed increasing dependency (https://arxiv.org/html/2510.01537v1).

**H&M Implementation**: Before any Socratic dialogue begins, the system should require the user to complete a brief self-assessment: "Before we analyze this together, what is your initial read? Apply the three questions yourself first." This transforms the interaction from "AI analyzes for me" to "I analyze, then AI helps me check my work."

### Pattern 2: Rate-Limiting and Delayed Access

The Wharton research provides specific mechanisms: introducing a 30-second delay before users can access AI help, or limiting help requests per session, dramatically increases independent problem-solving (https://knowledge.wharton.upenn.edu/article/when-does-ai-assistance-undermine-learning/). The key finding: system-level design constraints matter more than user motivation or skill level.

**H&M Implementation**: Rate-limit Socratic dialogues per session. After a user analyzes 3-4 claims with full AI support, require them to analyze the next 2-3 independently before unlocking more AI-assisted analysis.

### Pattern 3: Progressive Scaffolding Withdrawal (the Fading Schedule)

The Zone of No Development research establishes that scaffolding must explicitly fade (https://arxiv.org/html/2511.12822v1). The Prompt-to-Primal (P2P) framework proposes structured disconnection phases where learners must work without AI assistance, followed by assessment confirming independent capability.

**H&M Implementation**: Track user proficiency across sessions. As users demonstrate competence with the three-question framework, progressively reduce AI support:
- Sessions 1-3: Full Socratic dialogue with all three questions modeled
- Sessions 4-6: AI asks one question, prompts user to generate the other two
- Sessions 7-9: AI presents claim only; user applies framework; AI provides feedback afterward
- Sessions 10+: "Independence checkpoints" where user analyzes claims alone, with AI reviewing only upon request

### Pattern 4: Interleaving AI-Assisted and Unassisted Practice

The FACT assessment framework (Frontiers in Education, 2025) provides a validated model for balancing AI and non-AI work: fundamental skills assessed without AI assistance, applied skills with AI assistance, conceptual understanding through independent assessment, and critical thinking through complex multi-step analysis (https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1596462/full).

**H&M Implementation**: Alternate between assisted and unassisted claim analyses within a single session. The user might analyze Claims 1, 3, 5 with AI support and Claims 2, 4, 6 independently. Track performance on both types to measure growing independence.

### Pattern 5: Reflection Prompts and Metacognitive Monitoring

Self-assessment develops metacognitive awareness by requiring students to examine their own thinking processes (https://schoolbox.education/blog/what-does-self-assessment-and-self-reflection-bring-to-the-learning-journey/). End-of-session reflection is critical for SRL's self-reflection phase (Zimmerman's Phase 3).

**H&M Implementation**: After each Socratic dialogue session, present reflection prompts:
- "Which of the three questions was hardest to apply today? Why?"
- "Did you notice any assumptions you held that you weren't aware of before?"
- "What would you do differently if you encountered a similar claim tomorrow?"
- "Rate your confidence in analyzing similar claims independently (1-10)."

### Pattern 6: Independence Milestones and Competence Signaling

Users need visible markers of their growing competence to internalize the shift from dependent to independent analysis. The SRL literature emphasizes that self-efficacy beliefs are critical drivers of self-regulated behavior (https://www.researchgate.net/publication/237065878_Becoming_a_Self-Regulated_Learner_An_Overview).

**H&M Implementation**: Define and communicate clear independence milestones:
- "You correctly identified the manipulation technique without any hints -- that's a Level 3 analysis."
- "You've now independently applied all three questions in 5 consecutive sessions."
- Track and surface metrics like "unassisted accuracy rate" and "time-to-framework-application" to make skill growth visible.

### Pattern 7: The "Graduation" Model

The ultimate anti-dependency design: explicitly tell users that the goal is for them to no longer need the AI. This is the meta-design principle that distinguishes a thinking exercise from an oracle. The P2P framework's "Creation Phase" requires learners to demonstrate competence without any AI assistance (https://arxiv.org/html/2511.12822v1).

**H&M Implementation**: Frame the entire experience as a training program with a graduation point: "Huginn & Muninn is designed to teach you a mental framework, not to be your permanent fact-checker. The three questions -- What is true? How am I being played? What do we share? -- are yours to keep. Our goal is to make this tool unnecessary."

---

## 6. Synthesis: The H&M Dependency Mitigation Architecture

Drawing from all five research areas, the dependency mitigation strategy for H&M rests on four pillars:

**Pillar 1: Genuine Socratic Method (not directive correction)**
The AI never tells users what to conclude. It asks questions that guide them to discover inconsistencies, identify manipulation techniques, and find common ground themselves. The three questions are the structural framework; the AI's role is to ensure users apply them rigorously, not to apply them *for* users.

**Pillar 2: Explicit Scaffolding with Mandatory Fading**
Following Vygotsky/Bruner theory and the ZND warning, the system must have a built-in fading schedule that reduces AI support as user competence grows. Without explicit fading mechanisms, any AI system -- even a Socratic one -- risks creating the Zone of No Development.

**Pillar 3: Desirable Difficulties by Design**
Incorporate Bjork's four desirable difficulties: space out practice, interleave claim types, require retrieval before feedback, and force generation before exposure to AI analysis. These make the experience harder in the short term but build durable, transferable skills.

**Pillar 4: System-Regulated Access (not on-demand)**
The Wharton research is unequivocal: unrestricted AI access creates dependency regardless of user motivation. H&M must implement rate-limiting, forced self-assessment before AI dialogue, interleaving of assisted/unassisted practice, and explicit independence checkpoints.

The core insight aligns with the user's original intuition: H&M is a thinking exercise, not an oracle. The three questions are a metacognitive framework designed for internalization. The dependency paradox identified by Bao et al. is not inherent to AI dialogue -- it is a design failure that occurs when the AI does the thinking instead of teaching the user to think. Every design pattern above serves one purpose: ensuring the cognitive work stays with the user.

---

## Sources

- Bao et al. (2025) -- Dialogues with AI Reduce Beliefs in Misinformation: https://arxiv.org/html/2510.01537v1
- Frontiers in Education (2025) -- Socratic wisdom in the age of AI: https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1528603/full
- Comparative Evaluation of Socratic vs Didactic Tutoring: https://www.researchgate.net/publication/2847554_A_Comparative_Evaluation_of_Socratic_versus_Didactic_Tutoring
- AI Socratic Tutors: https://aicompetence.org/ai-socratic-tutors/
- Discerning Minds or Generic Tutors (2025): https://arxiv.org/html/2508.06583v1
- Simply Psychology -- ZPD: https://www.simplypsychology.org/zone-of-proximal-development.html
- Scaffolding Human Champions -- AI as MKO: https://link.springer.com/article/10.1007/s42087-022-00304-8
- Zone of No Development (2025): https://arxiv.org/html/2511.12822v1
- Oreate AI -- Scaffolding Learning: https://www.oreateai.com/blog/scaffolding-learning-vygotskys-insights-in-the-age-of-ai/51f46497c074de92ea86080ae4b627dd
- Halpern (1998) -- Critical Thinking Transfer: https://pubmed.ncbi.nlm.nih.gov/9572008/
- Metacognitive Strategies and Critical Thinking: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.913219/full
- Transfer of Metacognitive Skills in SRL: https://link.springer.com/article/10.1007/s11409-020-09237-5
- Power of Metacognitive Strategies (JOTSE): https://www.jotse.org/index.php/jotse/article/view/2721/879
- Zimmerman -- Becoming a Self-Regulated Learner: https://www.researchgate.net/publication/237065878_Becoming_a_Self-Regulated_Learner_An_Overview
- AI and SRL in Online Learning: https://educationaltechnologyjournal.springeropen.com/articles/10.1186/s41239-023-00406-5
- Wharton -- When Does AI Assistance Undermine Learning: https://knowledge.wharton.upenn.edu/article/when-does-ai-assistance-undermine-learning/
- Bjork Lab -- Creating Desirable Difficulties: https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/04/EBjork_RBjork_2011.pdf
- Making Things Hard on Yourself (Bjork): https://www.researchgate.net/publication/284097727_Making_things_hard_on_yourself_but_in_a_good_way_Creating_desirable_difficulties_to_enhance_learning
- Desirable Difficulties -- Structural Learning: https://www.structural-learning.com/post/desirable-difficulties
- Pretesting Effect: https://journalofcognition.org/articles/10.5334/joc.455
- Feedback Timing and Retrieval Practice: https://www.nature.com/articles/s41599-024-03983-6
- FACT Assessment Framework: https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2025.1596462/full
- Self-Assessment and Reflection in Learning: https://schoolbox.education/blog/what-does-self-assessment-and-self-reflection-bring-to-the-learning-journey/

Status: COMPLETE
