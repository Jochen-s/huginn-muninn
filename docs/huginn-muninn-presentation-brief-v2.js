const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, BorderStyle, WidthType, ShadingType,
  VerticalAlign, LevelFormat, HeadingLevel, PageBreak, PageNumber,
  TableOfContents,
} = require("docx");

// --- Colors ---
const DARK = "1B2A4A";
const ACCENT = "2C3E80";
const TEAL = "16A085";
const LIGHT_BG = "F0F4F8";
const MID = "5D6D7E";
const WHITE = "FFFFFF";
const BLACK = "2C3E50";
const RED_ACCENT = "C0392B";
const GREEN = "27AE60";
const AMBER = "E67E22";

// --- Borders ---
const noBorder = { style: BorderStyle.NONE, size: 0 };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const thinBorder = (c) => ({ style: BorderStyle.SINGLE, size: 1, color: c });
const cellBorders = { top: thinBorder("DEE2E6"), bottom: thinBorder("DEE2E6"), left: thinBorder("DEE2E6"), right: thinBorder("DEE2E6") };

// --- Helpers ---
function spacer(before = 120) {
  return new Paragraph({ spacing: { before, after: 0 }, children: [] });
}

function body(texts, opts = {}) {
  const runs = texts.map(t => {
    if (typeof t === "string") return new TextRun({ text: t, font: "Arial", size: 22, color: BLACK });
    return new TextRun({ font: "Arial", size: 22, color: BLACK, ...t });
  });
  return new Paragraph({
    spacing: { before: opts.before || 60, after: opts.after || 60 },
    indent: opts.indent ? { left: opts.indent } : undefined,
    alignment: opts.align || AlignmentType.JUSTIFIED,
    children: runs,
  });
}

function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 120 },
    children: [new TextRun({ text, font: "Arial", size: 32, bold: true, color: DARK })],
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 100 },
    children: [new TextRun({ text, font: "Arial", size: 26, bold: true, color: ACCENT })],
  });
}

function heading3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 80 },
    children: [new TextRun({ text, font: "Arial", size: 23, bold: true, color: MID })],
  });
}

function partTitle(text) {
  return [
    new Paragraph({ children: [new PageBreak()] }),
    spacer(600),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 200 },
      children: [new TextRun({ text: text.toUpperCase(), font: "Arial", size: 36, bold: true, color: ACCENT, characterSpacing: 120 })],
    }),
    dividerLine(),
    spacer(200),
  ];
}

function dividerLine() {
  return new Table({
    columnWidths: [9360],
    rows: [new TableRow({
      children: [new TableCell({
        borders: { top: noBorder, bottom: thinBorder(ACCENT), left: noBorder, right: noBorder },
        width: { size: 9360, type: WidthType.DXA },
        children: [new Paragraph({ spacing: { before: 0, after: 0 }, children: [] })],
      })],
    })],
  });
}

function quoteBlock(text, citation) {
  const children = [
    new Paragraph({
      spacing: { before: 60, after: citation ? 40 : 60 },
      children: [new TextRun({ text, font: "Georgia", size: 22, italics: true, color: DARK })],
    }),
  ];
  if (citation) {
    children.push(new Paragraph({
      alignment: AlignmentType.RIGHT,
      spacing: { before: 0, after: 60 },
      children: [new TextRun({ text: citation, font: "Arial", size: 18, color: MID })],
    }));
  }
  return new Table({
    columnWidths: [120, 9240],
    rows: [new TableRow({
      children: [
        new TableCell({
          borders: noBorders,
          shading: { fill: TEAL, type: ShadingType.CLEAR },
          width: { size: 120, type: WidthType.DXA },
          children: [new Paragraph({ children: [] })],
        }),
        new TableCell({
          borders: noBorders,
          shading: { fill: LIGHT_BG, type: ShadingType.CLEAR },
          width: { size: 9240, type: WidthType.DXA },
          margins: { top: 80, bottom: 80, left: 180, right: 180 },
          children,
        }),
      ],
    })],
  });
}

// --- Numbering configs ---
const numberingConfig = [];
let bulletRef = 0;
function newBulletRef() {
  const ref = `bullets-${bulletRef++}`;
  numberingConfig.push({
    reference: ref,
    levels: [
      { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
      { level: 1, format: LevelFormat.BULLET, text: "\u2013", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 1080, hanging: 360 } } } },
    ],
  });
  return ref;
}

let numRef = 0;
function newNumberRef() {
  const ref = `numbered-${numRef++}`;
  numberingConfig.push({
    reference: ref,
    levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }],
  });
  return ref;
}

function bullet(text, ref, level = 0) {
  const runs = Array.isArray(text) ? text.map(t => {
    if (typeof t === "string") return new TextRun({ text: t, font: "Arial", size: 22, color: BLACK });
    return new TextRun({ font: "Arial", size: 22, color: BLACK, ...t });
  }) : [new TextRun({ text, font: "Arial", size: 22, color: BLACK })];
  return new Paragraph({
    numbering: { reference: ref, level },
    spacing: { before: 40, after: 40 },
    children: runs,
  });
}

function numbered(text, ref) {
  const runs = Array.isArray(text) ? text.map(t => {
    if (typeof t === "string") return new TextRun({ text: t, font: "Arial", size: 22, color: BLACK });
    return new TextRun({ font: "Arial", size: 22, color: BLACK, ...t });
  }) : [new TextRun({ text, font: "Arial", size: 22, color: BLACK })];
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { before: 40, after: 40 },
    children: runs,
  });
}

function headerCell(text, width) {
  return new TableCell({
    borders: cellBorders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: DARK, type: ShadingType.CLEAR },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 40, after: 40 },
      children: [new TextRun({ text, font: "Arial", size: 20, bold: true, color: WHITE })],
    })],
  });
}

function dataCell(texts, width, opts = {}) {
  const runs = Array.isArray(texts) ? texts.map(t => {
    if (typeof t === "string") return new TextRun({ text: t, font: "Arial", size: 20, color: BLACK });
    return new TextRun({ font: "Arial", size: 20, color: BLACK, ...t });
  }) : [new TextRun({ text: texts, font: "Arial", size: 20, color: BLACK })];
  return new TableCell({
    borders: cellBorders,
    width: { size: width, type: WidthType.DXA },
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      spacing: { before: 30, after: 30 },
      alignment: opts.align || AlignmentType.LEFT,
      children: runs,
    })],
  });
}

// Pre-create all bullet references
const bRef = {};
const sections = [
  "ch1a", "ch1b", "ch1c", "ch1d",
  "ch2a", "ch2b", "ch2c", "ch2d",
  "ch3a", "ch3b", "ch3c", "ch3d", "ch3e", "ch3f",
  "ch4a", "ch4b", "ch4c", "ch4d", "ch4e",
  "ch5a", "ch5b",
  "ch6a", "ch6b", "ch6c", "ch6d", "ch6e",
  "ch7a", "ch7b", "ch7c",
  "ch8a", "ch8b",
  "p2a", "p2b", "p2c", "p2d", "p2e",
  "qa1", "qa2", "qa3", "qa4", "qa5", "qa6",
];
sections.forEach(s => bRef[s] = newBulletRef());

const nRef = {};
["ch3agents", "ch4pillars", "ch4patterns", "ch6tactics", "ch7hyp", "p2slides"].forEach(s => nRef[s] = newNumberRef());


// ============================================================
// DOCUMENT CONTENT
// ============================================================

// --- TITLE PAGE ---
const titlePage = [
  spacer(1800),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 80 },
    children: [new TextRun({ text: "The Fact-Checker That Finds Common Ground", font: "Georgia", size: 52, bold: true, color: DARK })],
  }),
  spacer(60),
  dividerLine(),
  spacer(60),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 60 },
    children: [new TextRun({ text: "How AI Can Fight Disinformation", font: "Arial", size: 28, color: ACCENT })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 60 },
    children: [new TextRun({ text: "by Revealing Shared Humanity", font: "Arial", size: 28, color: ACCENT })],
  }),
  spacer(40),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 40 },
    children: [new TextRun({ text: "Updated with Research Findings from ~240 Sources", font: "Arial", size: 22, italics: true, color: MID })],
  }),
  spacer(600),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Jochen", font: "Arial", size: 24, color: DARK })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 40, after: 20 },
    children: [new TextRun({ text: "March 24, 2026", font: "Arial", size: 22, color: MID })],
  }),
  spacer(40),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Presented at PKM Summit 2026, Utrecht (March 20-21)", font: "Arial", size: 20, color: MID })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Preparing for academic presentations and conference submissions", font: "Arial", size: 20, color: MID })],
  }),
];

// --- TABLE OF CONTENTS ---
const tocSection = [
  new Paragraph({ children: [new PageBreak()] }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 240, after: 200 },
    children: [new TextRun({ text: "Table of Contents", font: "Arial", size: 28, bold: true, color: DARK })],
  }),
  new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
];

// ============================================================
// PART 1: THE SUBSTANCE (UPDATED)
// ============================================================

const part1 = [
  ...partTitle("Part 1: The Substance (Updated)"),

  // ---- Chapter 1: The Problem ----
  heading1("Chapter 1: The Problem"),

  body(["We are living through the golden age of disinformation. Not because lies are new, but because the infrastructure for spreading them has never been this efficient. Automated accounts, algorithmic amplification, and cross-platform virality have turned individual falsehoods into coordinated campaigns that reach millions within hours."]),

  heading2("The PKM Angle"),

  body(["Knowledge workers build \"second brains\": Obsidian vaults, Notion databases, Zettelkasten systems. These are powerful tools for collecting, connecting, and creating knowledge. But none of them have an immune system."]),

  body(["When the information you are curating is manipulated, your PKM system does not protect you. It amplifies the manipulation by giving it structure, permanence, and connections to your other thinking. The \"collect, connect, create\" cycle that PKM teaches becomes \"collect polluted data, connect it to clean data, create conclusions built on contaminated foundations.\""]),

  body(["This is not a theoretical risk. Studies show that false information travels six times faster than accurate information on social media (Vosoughi et al., Science, 2018). By the time a correction reaches you, the false version has already been filed, tagged, linked, and integrated into your thinking."]),

  heading2("The Manufactured Doubt Angle"),

  body(["The problem runs deeper than individual false claims. A systematic review by Goldberg, Vandenberg et al. (2021, Environmental Health) identified 28 distinct tactics used across five industries: tobacco, chemicals, sugar, alcohol, and mining. These are not ad hoc lies. They are a playbook, refined over decades, for creating confusion where scientific consensus exists."]),

  body([{ text: "Five of these 28 tactics appeared in every single industry studied: ", bold: true }, "attacking study design, gaining reputable support, misrepresenting data, using hyperbolic language, and influencing government. This is not coincidence. It is industrial-scale doubt manufacturing."]),

  body(["The fossil fuel industry knew about climate change in the 1970s and spent billions creating doubt (Supran & Oreskes, Science, 2017). The tobacco industry ran the same playbook for decades. The sugar industry funded research blaming fat instead of sugar for heart disease. The tactics are interchangeable because the underlying strategy is identical: exploit the gap between scientific certainty and public understanding."]),

  heading2("The Ego Development Connection"),

  body(["There is a developmental dimension to susceptibility that is rarely discussed outside academic psychology. Jane Loevinger's model of ego development describes a sequence of increasingly complex meaning-making structures. The E4 (Conformist) stage is characterized by strong group identification, black-and-white thinking, deference to in-group authority, and hostility to out-groups."]),

  body(["Research suggests that 55% or more of US adults may not yet operate at the developmental stage (E6, Conscientious, or above) required for the kind of pluralistic, evidence-based reasoning that democratic societies assume of their citizens (Holt, 1980; Manners & Durkin, 2001). This is not a statement about intelligence. It is a statement about psychosocial maturity: the capacity to hold multiple perspectives simultaneously, to tolerate ambiguity, and to evaluate evidence independently of group loyalty."]),

  body(["E4 individuals are maximally susceptible to conspiracy theories because conspiracies provide exactly what the E4 stage craves: simple explanations (us vs. them), clear authorities (the conspiracy leader), and defined out-groups (the conspirators). This insight reframes the problem: the target is not ignorance but developmental readiness."]),

  heading2("The Failure of Current Approaches"),

  body(["Fact-checking is necessary but insufficient. Facebook/Meta's fact-checking labels reduce resharing by only 10-15%. More importantly: telling people they are wrong triggers psychological reactance; the harder you push, the harder they push back. The goal should not be to win arguments but to build understanding."]),

  body(["A crucial clarification: the \"backfire effect,\" the idea that corrections make beliefs stronger, was once considered settled science but has largely failed replication (Wood & Porter, 2019 meta-analysis). Corrections do work. The question is how, not whether. The research has moved from \"should we correct?\" to \"how do we correct without triggering defensiveness?\""]),

  quoteBlock("The goal is not to build a better lie detector. It is to build a tool that reminds us what we share, because most of the time, it is more than we think."),


  // ---- Chapter 2: The Insight ----
  heading1("Chapter 2: The Insight"),

  heading2("The Research Breakthrough"),

  body(["In September 2024, Costello, Pennycook, and Rand published a landmark study in Science. They demonstrated that AI-driven Socratic dialogue produces a 20% durable reduction in conspiracy beliefs (N=2,190, with 2-month follow-up). Not temporary, not marginal: durable. This work subsequently won the 2026 AAAS Newcomb Cleveland Prize, the highest recognition for a paper published in Science."]),

  heading2("The Dependency Paradox"),

  body([{ text: "NEW FINDING: ", bold: true, color: RED_ACCENT }, "Bao et al. (2025, arXiv:2510.01537) conducted a longitudinal study that revealed a critical danger. Users of AI fact-checking tools showed +21.3% immediate accuracy improvement, but -15.3% decline in independent discernment by week 4. Twenty-one percent of participants became \"Dependency Developers\" who progressively lost the ability to evaluate claims without AI assistance."]),

  body(["This is the central paradox of AI-assisted thinking: the tool that helps you think better in the moment can make you think worse on your own. Every AI tool that provides answers creates this risk."]),

  heading2("The Solution: Cognitive Gymnasium, Not Oracle"),

  body([{ text: "The resolution: ", bold: true, color: GREEN }, "Bao et al. found that genuinely Socratic questioning (asking probing questions rather than providing answers) correlated positively with independent detection skills (r=0.29, p<0.01). System-regulated access (structured interaction schedules) produced 2x learning gains compared to on-demand access (Wharton, 2025)."]),

  body(["The reframe is fundamental: Huginn & Muninn is not an oracle. It is a cognitive gymnasium. The three questions are the exercise. The tool is the training wheels; the questions are the bicycle. The goal is to make the tool unnecessary."]),

  heading2("Why Socratic Works"),

  body(["Instead of telling people they are wrong (which triggers reactance), you ask questions that let them discover inconsistencies themselves. The key: acknowledge the kernel of truth in their concern first. People become defensive when their core identity is threatened. Socratic dialogue sidesteps this by treating the person as a thinking partner, not an adversary."]),

  heading2("Inoculation"),

  body(["The inoculation approach (van der Linden, Cambridge; Google/Jigsaw) complements this: teaching people to recognize manipulation techniques is more durable than debunking individual claims. In a large-scale field study, 5.4 million YouTube users showed a 5-10% improvement in detecting manipulation after seeing prebunking videos. A 2025 meta-analysis (N=37,075) confirmed that inoculation improves discernment without inducing response bias: participants did not become more skeptical of everything, only more accurate."]),

  heading2("The Perception Gap"),

  body(["More in Common (2019) and Beyond Conflict found that Americans overestimate how extreme the other side is by approximately 2x. But here is the surprising finding: people who consume the most news have the most distorted view of the other side, not the least. Knowledge alone does not fix this. The right kind of knowledge does."]),

  heading2("The Synthesis"),

  quoteBlock("What if you combined Socratic dialogue, inoculation, perception gap data, manufactured doubt detection, and dependency mitigation into a single tool that is designed to make itself unnecessary?"),

  body(["That is what Huginn & Muninn attempts. Not a better fact-checker, but a reconciliation engine that uses the best available research on how humans actually change their minds, while actively preventing the dependency that other AI tools create."]),


  // ---- Chapter 3: What We Built ----
  heading1("Chapter 3: What We Built"),

  heading2("The Name"),

  body(["Huginn and Muninn are Odin's two ravens in Norse mythology. Huginn means \"thought\" and Muninn means \"memory.\" Every day they fly across the world and return to whisper what they have seen. One scans for information; the other remembers and reflects. Together they report the truth. The tool carries this spirit: observe without judgment, remember without bias, report without agenda."]),

  heading2("The Three Questions"),

  body(["At the heart of Huginn & Muninn is a teachable framework consisting of three questions. These are not novel individually; what is novel is their combination into a self-correcting system."]),

  new Table({
    columnWidths: [2600, 6760],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [headerCell("Question", 2600), headerCell("Purpose", 6760)],
      }),
      new TableRow({ children: [
        dataCell([{ text: "1. What is true?", bold: true }], 2600),
        dataCell("Evidence-based verification with source tiering and confidence calibration. Not a verdict, but a map of the evidence landscape.", 6760),
      ]}),
      new TableRow({ children: [
        dataCell([{ text: "2. Who benefits from me feeling this way?", bold: true }], 2600),
        dataCell("Names the manipulation technique so you recognize it next time. Identifies financial, political, and ideological incentives behind the framing.", 6760),
      ]}),
      new TableRow({ children: [
        dataCell([{ text: "3. What do we actually share?", bold: true }], 2600),
        dataCell("Surfaces the common ground that divisive framing hides. Not abstract (\"we are all human\") but concrete shared circumstances.", 6760),
      ]}),
    ],
  }),

  spacer(80),

  body(["Every other fact-checking tool stops at Question 1. Huginn & Muninn delivers all three."]),

  heading2("Method 1: Quick Check"),

  body(["A single-prompt, two-pass verification system. Fast: approximately 10 seconds on consumer hardware. The first pass gathers evidence for and against the claim without rendering judgment. The second pass analyzes that evidence, produces a verdict with calibrated confidence, and generates a Common Ground section."]),

  body(["Every Quick Check output includes:"]),
  bullet([{ text: "Verdict: ", bold: true }, "true, mostly true, mixed, mostly false, false, or insufficient evidence"], bRef.ch3a),
  bullet([{ text: "Calibrated confidence score ", bold: true }, "(0.0 to 1.0) with explicit thresholds"], bRef.ch3a),
  bullet([{ text: "Evidence for and against ", bold: true }, "with source URLs and source tier ratings"], bRef.ch3a),
  bullet([{ text: "Common Ground section: ", bold: true }, "shared concern, named framing technique, technique explanation, and Socratic reflection question"], bRef.ch3a),
  bullet([{ text: "Escalation score: ", bold: true }, "auto-determines whether a deeper analysis is warranted"], bRef.ch3a),

  heading2("Method 2: Full Analysis (6-Agent Pipeline)"),

  body(["For complex, multi-actor, or heavily polarized claims, Method 2 deploys a pipeline of six specialized AI agents:"]),

  numbered([{ text: "Claim Decomposer: ", bold: true }, "Breaks complex claims into verifiable sub-claims, classifying each by type (factual, opinion, prediction) and verifiability."], nRef.ch3agents),
  numbered([{ text: "Origin Tracer: ", bold: true }, "Tracks where the claim originated, how it has mutated as it spread, and identifies the earliest known source."], nRef.ch3agents),
  numbered([{ text: "Network Mapper: ", bold: true }, "Maps the information flow: who is amplifying the claim, what are the relationships between actors, and what is the narrative structure."], nRef.ch3agents),
  numbered([{ text: "TTP Classifier: ", bold: true }, "Identifies manipulation techniques using the DISARM framework and the 28-tactic manufactured doubt taxonomy."], nRef.ch3agents),
  numbered([{ text: "Bridge Builder: ", bold: true }, "The core differentiator. Identifies universal human needs at stake, finds where opposing groups actually agree, deconstructs how the same concern was split into opposing narratives, and generates Socratic dialogue."], nRef.ch3agents),
  numbered([{ text: "Adversarial Auditor: ", bold: true }, "Red-teams the entire analysis. Checks for confirmation bias, overreach, false equivalence, and potential misuse. Can veto the output."], nRef.ch3agents),

  heading2("Phase 6 Features"),

  body(["Since the original presentation brief, Huginn & Muninn has added significant capabilities:"]),
  bullet([{ text: "Batch analysis: ", bold: true }, "Submit up to 50 claims for parallel processing via /api/batch"], bRef.ch3b),
  bullet([{ text: "Multi-model comparison: ", bold: true }, "Run the same claim through multiple LLMs and auto-reconcile divergent findings via /api/compare"], bRef.ch3b),
  bullet([{ text: "Web search enrichment: ", bold: true }, "Brave Search integration for real-time source verification"], bRef.ch3b),
  bullet([{ text: "OpenAI-compatible providers: ", bold: true }, "Support for any OpenAI-compatible API (OpenRouter, local endpoints, cloud providers)"], bRef.ch3b),
  bullet([{ text: "304 tests passing: ", bold: true }, "Comprehensive test coverage across all modules"], bRef.ch3b),

  heading2("The Chemtrails Test Case"),

  body(["To demonstrate the three-question framework in practice, we apply it to one of the most persistent conspiracy theories: chemtrails."]),

  heading3("Question 1: What is true?"),
  body(["Condensation trails (contrails) are well-understood atmospheric science. A 2016 Carnegie Science/UC Irvine survey of 77 atmospheric scientists found 76 (98.7%) saw no evidence of a secret spraying program. Weather modification programs (cloud seeding) DO exist and are publicly documented, creating a kernel of truth that conspiracy narratives exploit."]),

  heading3("Question 2: Who benefits from me believing this?"),
  body(["The chemtrail narrative employs multiple manufactured doubt tactics: exploiting scientific illiteracy (most people cannot explain condensation physics), hyperbolic language (\"they are poisoning us\"), and blame redirection (attributing health problems to spraying rather than documented causes). Content monetizers, political actors leveraging anti-government sentiment, and alternative medicine practitioners all benefit from sustained fear."]),

  heading3("Question 3: What do we share with chemtrail believers?"),
  body(["People who believe in chemtrails and people who do not share legitimate concerns: worry about environmental contamination, distrust of institutions that have historically lied about public health risks (tobacco, lead, asbestos, PFAS), desire to protect family health, and frustration with insufficient government transparency."]),

  quoteBlock("The bridge: \"You care about what is in the air your family breathes. So does everyone. The question is not whether to care, because that concern is entirely legitimate. The question is whether the chemtrail explanation actually helps you protect your family, or whether it redirects your energy away from the real environmental threats that are documented and actionable.\""),


  // ---- Chapter 4: The Design Decisions ----
  heading1("Chapter 4: The Design Decisions"),

  heading2("Why Local-First"),
  body(["Your data never leaves your machine. No cloud dependency. No API keys required for base usage. Complete data sovereignty. If you are analyzing sensitive political claims, you should not have to trust a third party with that data."]),

  heading2("Why Open Source"),
  body(["Transparency is non-negotiable for a trust tool. The algorithms that decide what is \"true\" and what is \"manipulation\" must be inspectable. If you cannot read the code, you cannot trust the output."]),

  heading2("Why Socratic, Not Declarative"),
  body(["The system never says \"this is false.\" It presents evidence and asks \"what do you make of this?\" Every output uses autonomy-supportive language only. No controlling phrases like \"experts agree,\" \"the truth is,\" or \"debunked.\""]),

  heading2("Moral Reframing: Downgraded"),

  body([{ text: "Intellectual honesty update: ", bold: true, color: RED_ACCENT }, "Moral reframing (Feinberg & Willer, 2015-2019) was originally a core pillar. Six or more preregistered replication attempts have failed to reproduce the original effects (Arpan 2018, Berkebile-Weinberg 2024, Crawford 2025, Hundemer 2023, Kim 2023, plus a 2026 study with N=2,009). We have downgraded moral reframing from core pillar to experimental module."]),

  body(["This is intellectual honesty, not weakness. A system that fights disinformation must hold itself to the same evidentiary standards it applies to others. When the evidence changes, the system must change."]),

  heading2("The 4-Pillar Dependency Mitigation Architecture"),

  body(["The dependency paradox (Bao et al., 2025) is the most significant threat to AI-mediated de-polarization. Our solution:"]),

  numbered([{ text: "Genuine Socratic Method: ", bold: true }, "Ask, do not tell. Bao et al. found that genuinely Socratic questioning correlated positively with independent detection skills (r=0.29, p<0.01)."], nRef.ch4pillars),
  numbered([{ text: "Mandatory Fading Schedule: ", bold: true }, "Scaffolding withdrawal over sessions. Early interactions provide substantial guidance; later interactions progressively remove support."], nRef.ch4pillars),
  numbered([{ text: "Desirable Difficulties (Bjork Lab, UCLA): ", bold: true }, "Spacing, interleaving, retrieval practice, and generation. Slower initial learning but dramatically better long-term retention and transfer."], nRef.ch4pillars),
  numbered([{ text: "System-Regulated Access (Wharton, 2025): ", bold: true }, "Structured interaction schedules produce 2x learning gains compared to on-demand access."], nRef.ch4pillars),

  heading2("Seven Concrete Design Patterns"),

  numbered([{ text: "Forced Self-Assessment: ", bold: true }, "Before showing any analysis, require users to state their own assessment."], nRef.ch4patterns),
  numbered([{ text: "Rate-Limiting: ", bold: true }, "Cap daily interactions to prevent passive consumption."], nRef.ch4patterns),
  numbered([{ text: "Progressive Fading: ", bold: true }, "Gradually reduce AI response detail over sessions."], nRef.ch4patterns),
  numbered([{ text: "Interleaving: ", bold: true }, "Mix claim types to build transferable reasoning skills."], nRef.ch4patterns),
  numbered([{ text: "Reflection Prompts: ", bold: true }, "After analysis, ask users to identify which question was most useful and why."], nRef.ch4patterns),
  numbered([{ text: "Independence Milestones: ", bold: true }, "Track and celebrate unassisted performance on novel claims."], nRef.ch4patterns),
  numbered([{ text: "Graduation Model: ", bold: true }, "\"Our goal is to make this tool unnecessary. The three questions are yours to keep.\""], nRef.ch4patterns),

  heading2("The Manufactured Doubt Detection Layer"),

  body(["The 28-tactic taxonomy (Goldberg et al., 2021) provides the backbone for automated detection of manufactured doubt. Five universal tactics serve as primary signals. Nine structural signatures distinguish manufactured doubt from genuine scientific uncertainty. An epistemic asymmetry decision tree helps users evaluate whether doubt is being manufactured or is genuinely warranted."]),

  heading2("The Guardrails"),
  body(["What the system refuses to do:"]),
  bullet("Cannot manufacture false common ground. If positions are genuinely irreconcilable, it says so.", bRef.ch4d),
  bullet("Cannot be used as a persuasion engine. It reveals manipulation; it does not employ it.", bRef.ch4d),
  bullet("Acknowledges when moral positions are genuinely irreconcilable.", bRef.ch4d),
  bullet("Profiles public narratives only: never surveils or profiles individuals.", bRef.ch4d),
  bullet("Verdicts are analysis aids, not automated censorship or takedown signals.", bRef.ch4d),

  quoteBlock("Not every disagreement is manufactured. Some are real. But the ones that are manufactured deserve to be seen."),


  // ---- Chapter 5: What We're Trying to Achieve ----
  heading1("Chapter 5: What We Are Trying to Achieve"),

  heading2("Mission Statement"),

  quoteBlock("De-polarize the world by helping people find each other as human beings."),

  body(["Not calling people stupid. Not lecturing them about truth. Facilitating genuine connection and understanding by teaching a transferable mental framework."]),

  heading2("The Graduation Model"),

  body(["Every other AI tool measures success by engagement and retention. Huginn & Muninn measures success by users who no longer need it. The graduation model explicitly frames the relationship as temporary:"]),

  quoteBlock("\"Our goal is to make this tool unnecessary. The three questions are yours to keep. Once you learn to ask them reflexively, you do not need us anymore.\""),

  body(["Users who consistently perform at expert level on novel claims are \"graduated\" with ceremony and recognition. This is not a business model decision; it is a design philosophy rooted in the dependency paradox research."]),

  heading2("The PKM Summit Question"),

  body([{ text: "At the PKM Summit in Utrecht (March 20-21, 2026), ", bold: true }, "the central question emerged: \"How do you reach people who believe in chemtrails without calling them stupid?\""]),

  body(["The answer is the three questions, applied with empathy and curiosity. You do not start with \"that is wrong.\" You start with \"I can see why that concerns you. Let us look at this together.\""]),

  heading2("Success Metrics"),
  bullet("15-20% reduction in conspiracy belief scores (Costello et al., Science, 2024)", bRef.ch5a),
  bullet("5-10% improvement in manipulation detection (van der Linden/Jigsaw inoculation)", bRef.ch5a),
  bullet("Maintained or improved independent discernment at 2-month follow-up (vs. Bao et al. baseline)", bRef.ch5a),
  bullet("Less than 5% of users reporting feeling lectured or condescended to", bRef.ch5a),
  bullet("Measurable perception gap reduction (More in Common framework)", bRef.ch5a),

  heading2("The Broader Aspiration"),

  body(["What if every news article, social media post, and viral claim could be accompanied not just by a fact-check, but by a reminder of what we share? Not to suppress disagreement, but to separate the real disagreements from the manufactured ones."]),

  body(["The disinformation industry profits from division. The antidote is not more argument but more understanding. Huginn & Muninn is a step in that direction: a tool that refuses to let you walk away from a fact-check feeling only anger at the other side. It always, without exception, shows you the common ground."]),


  // ---- Chapter 6: Research Foundation ----
  heading1("Chapter 6: Research Foundation"),

  heading2("Research Pillar Assessment"),

  body(["H&M integrates findings from six research pillars. What follows is an honest assessment including replications, failures, and caveats."]),

  // Research scorecard table
  new Table({
    columnWidths: [1800, 1600, 1600, 1600, 1200, 1560],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [
          headerCell("Pillar", 1800),
          headerCell("Replication", 1600),
          headerCell("Effect Size", 1600),
          headerCell("Cross-Cultural", 1600),
          headerCell("Caveats", 1200),
          headerCell("Overall", 1560),
        ],
      }),
      new TableRow({ children: [
        dataCell("Socratic AI Dialogue", 1800),
        dataCell([{ text: "Strong", color: GREEN }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "d=0.41", color: GREEN }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "US-only", color: AMBER }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Dependency", color: AMBER }], 1200, { align: AlignmentType.CENTER }),
        dataCell([{ text: "STRONG", bold: true, color: GREEN }], 1560, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("Inoculation", 1800),
        dataCell([{ text: "Best replicated", color: GREEN }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "5-10%", color: AMBER }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Multi-language", color: GREEN }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Transfer gap", color: AMBER }], 1200, { align: AlignmentType.CENTER }),
        dataCell([{ text: "MOD-STRONG", bold: true, color: GREEN }], 1560, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("Perception Gap", 1800),
        dataCell([{ text: "No replication", color: RED_ACCENT }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "2x overestimate", color: AMBER }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "US-only", color: RED_ACCENT }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Single study", color: RED_ACCENT }], 1200, { align: AlignmentType.CENTER }),
        dataCell([{ text: "WEAK", bold: true, color: RED_ACCENT }], 1560, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("Moral Reframing", 1800),
        dataCell([{ text: "6+ failures", color: RED_ACCENT }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Null", color: RED_ACCENT }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Failed", color: RED_ACCENT }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "DOWNGRADED", color: RED_ACCENT }], 1200, { align: AlignmentType.CENTER }),
        dataCell([{ text: "WEAK", bold: true, color: RED_ACCENT }], 1560, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("Narrative Complexity", 1800),
        dataCell([{ text: "Lab only", color: AMBER }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "No RCT", color: AMBER }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Not tested", color: AMBER }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Theory only", color: AMBER }], 1200, { align: AlignmentType.CENTER }),
        dataCell([{ text: "WEAK-MOD", bold: true, color: AMBER }], 1560, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("Redirect Method", 1800),
        dataCell([{ text: "Engagement only", color: AMBER }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Wrong metric", color: AMBER }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Limited", color: AMBER }], 1600, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Not belief Chg.", color: AMBER }], 1200, { align: AlignmentType.CENTER }),
        dataCell([{ text: "MODERATE", bold: true, color: AMBER }], 1560, { align: AlignmentType.CENTER }),
      ]}),
    ],
  }),

  spacer(120),

  heading2("The 28-Tactic Manufactured Doubt Taxonomy"),

  body(["Goldberg, Vandenberg et al. (2021) identified 28 tactics across tobacco (T), chemicals (C), sugar (S), alcohol (A), and mining (M). The five universal tactics appearing in all industries:"]),

  new Table({
    columnWidths: [500, 2500, 6360],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [headerCell("#", 500), headerCell("Universal Tactic", 2500), headerCell("Description", 6360)],
      }),
      new TableRow({ children: [
        dataCell("1", 500, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Attack Study Design", bold: true }], 2500),
        dataCell("Challenge methodology, sample sizes, statistical methods to discredit inconvenient findings", 6360),
      ]}),
      new TableRow({ children: [
        dataCell("2", 500, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Gain Reputable Support", bold: true }], 2500),
        dataCell("Recruit credentialed scientists, form industry-funded research institutes, publish in sponsored supplements", 6360),
      ]}),
      new TableRow({ children: [
        dataCell("3", 500, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Misrepresent Data", bold: true }], 2500),
        dataCell("Cherry-pick studies, conflate correlation with causation, present misleading statistics", 6360),
      ]}),
      new TableRow({ children: [
        dataCell("4", 500, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Hyperbolic Language", bold: true }], 2500),
        dataCell("\"Junk science,\" \"nanny state,\" \"alarmist\" to delegitimize opponents", 6360),
      ]}),
      new TableRow({ children: [
        dataCell("5", 500, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Influence Government", bold: true }], 2500),
        dataCell("Lobby regulators, influence policy committees, delay regulation through requests for \"more research\"", 6360),
      ]}),
    ],
  }),

  spacer(80),

  body([{ text: "Source: ", italics: true, color: MID }, "Goldberg, R. F. & Vandenberg, L. N. et al. (2021). Environmental Health, 20(1), 89. PMC7996119."]),

  heading2("The Dependency Paradox and Its Solution"),

  body(["The dependency paradox is not a minor caveat; it is the central design challenge. Without addressing it, AI-mediated de-polarization would create a new form of cognitive dependence that undermines the very capacity it seeks to develop."]),

  body(["H&M's four-pillar solution (Chapter 4) draws on Vygotsky's Zone of Proximal Development, the \"Zone of No Development\" paper (arXiv:2511.12822) on how persistent AI assistance prevents genuine skill acquisition, Bjork's desirable difficulties research, and the Wharton Learning Lab's findings on structured vs. on-demand access."]),

  quoteBlock("The graduation framing is essential. Every other AI tool measures success by engagement and retention. H&M measures success by users who no longer need it.", "Halpern, D. F. (1998). Teaching critical thinking for transfer across domains."),


  // ---- Chapter 7: Academic Collaboration ----
  heading1("Chapter 7: Academic Collaboration"),

  heading2("Research Partnership: Ego Development"),

  body(["H&M's most innovative research direction is calibrating Socratic dialogue to the user's ego development stage using Loevinger's model. Bronlet (2025, Frontiers in Psychology) demonstrated automated WUSCT (Washington University Sentence Completion Test) scoring using large language models, achieving kappa=0.779 inter-rater reliability. This approaches clinical reliability thresholds, suggesting a viable path toward automated stage assessment."]),

  heading2("14 Testable Hypotheses"),

  heading3("Hypotheses H1-H7: From Ego Development Research"),
  numbered([{ text: "H1: ", bold: true }, "Stage-calibrated AI dialogue reduces conspiracy mentality (CMQ scores) more effectively than generic AI dialogue, exceeding Costello et al.'s 20% at 2-month follow-up."], nRef.ch7hyp),
  numbered([{ text: "H2: ", bold: true }, "Reduction in RWA (Right-Wing Authoritarianism) scores correlates with ego development stage advancement from E4 to E5."], nRef.ch7hyp),
  numbered([{ text: "H3: ", bold: true }, "Anti-feminist attitudes decrease as a secondary effect of de-polarization interventions, mediated by increased perspective-taking capacity."], nRef.ch7hyp),
  numbered([{ text: "H4: ", bold: true }, "Science skepticism decreases through Question 2's manipulation literacy component, enabling users to distinguish manufactured doubt from genuine uncertainty."], nRef.ch7hyp),
  numbered([{ text: "H5: ", bold: true }, "Market-radical attitudes correlate with ego development stage and are modifiable through perspective-taking interventions at the E4-E5 transition."], nRef.ch7hyp),
  numbered([{ text: "H6: ", bold: true }, "Endorsement of political violence decreases with ego development advancement, particularly at the E4 to E5 transition."], nRef.ch7hyp),
  numbered([{ text: "H7: ", bold: true }, "H&M's effectiveness varies by More in Common hidden tribe segment, with \"Passive Liberals\" and \"Politically Disengaged\" showing largest effects."], nRef.ch7hyp),

  heading3("Hypotheses H8-H14: Formulated Through H&M Research"),
  numbered([{ text: "H8: ", bold: true }, "Stage-calibrated Socratic dialogue produces larger effect sizes than generic Socratic dialogue across all measured outcomes."], nRef.ch7hyp),
  numbered([{ text: "H9: ", bold: true }, "The Common Humanity component has differential effectiveness by stage: minimal at E3-E4, maximum at E5-E6, attenuated at E7+."], nRef.ch7hyp),
  numbered([{ text: "H10: ", bold: true }, "Progressive scaffolding with mandatory fading prevents the dependency effect (Bao et al., 2025). Scaffolding users maintain or improve independent discernment at follow-up."], nRef.ch7hyp),
  numbered([{ text: "H11: ", bold: true }, "Users at the E4/E5 transition show a temporary \"developmental dip\" in confidence before stabilizing at higher discernment."], nRef.ch7hyp),
  numbered([{ text: "H12: ", bold: true }, "Eight or more sessions produce measurable micro-developmental shifts in WUSCT scores, detectable through item-level analysis."], nRef.ch7hyp),
  numbered([{ text: "H13: ", bold: true }, "Epistemic humility increases as a stage-independent mechanism across all ego development levels."], nRef.ch7hyp),
  numbered([{ text: "H14: ", bold: true }, "More in Common's seven hidden tribe segments map onto ego development stages with predictable correspondence."], nRef.ch7hyp),

  heading2("Four-Arm RCT Design"),

  body(["The proposed experimental design uses four arms (N=300-400, 75-100 per arm):"]),
  bullet([{ text: "Arm 1 (Waitlist Control): ", bold: true }, "No intervention. Controls for maturation and testing effects."], bRef.ch7a),
  bullet([{ text: "Arm 2 (Generic AI Dialogue): ", bold: true }, "Standard AI fact-checking without stage calibration or the three-question framework."], bRef.ch7a),
  bullet([{ text: "Arm 3 (Stage-Calibrated H&M): ", bold: true }, "Full three-question framework with ego development stage calibration, but without scaffolding/fading."], bRef.ch7a),
  bullet([{ text: "Arm 4 (H&M with Scaffolding): ", bold: true }, "Complete H&M design with stage calibration, progressive scaffolding withdrawal, and system-regulated access."], bRef.ch7a),

  body([{ text: "Primary outcome: ", bold: true }, "Conspiracy Mentality Questionnaire (CMQ; Bruder et al., 2013). Pre/post/2-month/6-month follow-up."]),

  heading2("Funding Pathways"),
  bullet([{ text: "DFG SPP 2573 (Re:DIS): ", bold: true }, "German Research Foundation programme specifically targeting disinformation research."], bRef.ch7b),
  bullet([{ text: "Volkswagen Foundation: ", bold: true }, "Supports interdisciplinary collaborations between social sciences and computational approaches."], bRef.ch7b),
  bullet([{ text: "EU Horizon Europe Cluster 2: ", bold: true }, "Funds research on democratic resilience, disinformation, and social cohesion."], bRef.ch7b),

  body([{ text: "Note: ", italics: true, color: MID }, "NSF funding for disinformation research is effectively blocked under the current US administration (2025-). European and German national funding sources are the primary pathway."]),


  // ---- Chapter 8: Open Questions & Future ----
  heading1("Chapter 8: Open Questions and Future Directions"),

  body(["Huginn & Muninn is a functional, research-grounded prototype, but several important challenges remain:"]),

  heading2("Untested Combinations"),
  body(["No study has tested the combined effect of Socratic dialogue + inoculation + perception gap correction + manufactured doubt detection in a single intervention. Each component has individual evidence; the system effect is theorized but unvalidated. The four-arm RCT is designed to address this."]),

  heading2("Cross-Cultural Validation"),
  body(["Most supporting research uses WEIRD (Western, Educated, Industrialized, Rich, Democratic) samples. Moral foundations differ across cultures. Socratic dialogue patterns vary by language and cultural context. Ego development distributions may differ. Cross-cultural validation is essential before claiming generalizability."]),

  heading2("Long-Term Internalization"),
  body(["Costello et al. demonstrated durability at 2 months. Whether the three-question framework produces genuine long-term internalization (years, not months) is unknown. The graduation model and scaffolding design are intended to promote this, but longitudinal evidence is needed."]),

  heading2("Multilingual Support"),
  body(["The current system is English-focused. Extending it to other languages requires not just translation but cultural adaptation of the Socratic dialogue, manufactured doubt taxonomy, and common ground components."]),

  heading2("Community and Open Source"),
  body(["The open-source model (MIT license) enables transparency, community audit, and academic collaboration. Contributing to Huginn & Muninn means contributing to a tool that is designed to make itself unnecessary: the rarest kind of technology project."]),

  quoteBlock("The disinformation industry profits from division. The antidote is not more argument but more understanding."),
];


// ============================================================
// PART 2: PRESENTATION GUIDE (UPDATED)
// ============================================================

const part2 = [
  ...partTitle("Part 2: Presentation Guide (Updated)"),

  body([{ text: "Context: ", bold: true }, "This guide is updated for academic presentations and future conference submissions. The PKM Summit (March 20-21, 2026, Utrecht) has concluded. The audience for future presentations is researchers, conference attendees, and potential academic collaborators."]),

  heading1("Suggested Slide Deck"),

  body(["24 slides for a 35-40 minute academic presentation. Each slide includes content guidance."]),

  new Table({
    columnWidths: [600, 2400, 4000, 1200, 1160],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [
          headerCell("#", 600),
          headerCell("Slide Title", 2400),
          headerCell("Content", 4000),
          headerCell("Time", 1200),
          headerCell("Notes", 1160),
        ],
      }),
      ...([
        ["1", "Title Slide", "\"The Fact-Checker That Finds Common Ground\"", "0:30", "Clean"],
        ["2", "The Golden Age of Disinformation", "Scale statistics. 28-tactic playbook headline.", "1:30", "Hook"],
        ["3", "Your Second Brain Has No Immune System", "PKM collect-connect-create contamination risk", "2:00", "Personal"],
        ["4", "Manufactured Doubt", "28 tactics, 5 universal. Tobacco-to-climate pipeline.", "2:00", "NEW"],
        ["5", "The Ego Development Connection", "55%+ at E4 or below. Not intelligence: maturity.", "1:30", "NEW"],
        ["6", "The Fact-Checking Paradox", "10-15% reshare reduction. Reactance theory.", "1:30", "Setup"],
        ["7", "Audience Interaction", "\"Have you ever changed someone's mind by proving them wrong?\"", "1:00", "Poll"],
        ["8", "The Breakthrough", "Costello et al.: 20% durable, AAAS Prize", "2:00", "Core"],
        ["9", "The Dependency Paradox", "Bao et al.: +21.3% then -15.3%. 21% Dependency Developers.", "2:00", "NEW"],
        ["10", "The Solution", "4 pillars: Socratic, fading, desirable difficulties, regulated access", "2:00", "NEW"],
        ["11", "Three Questions", "What is true? Who benefits? What do we share?", "1:30", "Framework"],
        ["12", "H&M Architecture", "6-agent pipeline diagram + Phase 6 features", "1:30", "Technical"],
        ["13", "The Bridge Builder", "Common Humanity layer deep dive", "2:00", "Diff."],
        ["14", "Chemtrails Test Case", "All three questions applied to real example", "2:30", "NEW"],
        ["15", "Research Scorecard", "6 pillars with honest ratings. Moral reframing WEAK.", "1:30", "Honesty"],
        ["16", "Manufactured Doubt Taxonomy", "5 universal tactics table", "1:30", "NEW"],
        ["17", "Design Decisions", "Local-first, Socratic, mandatory common ground", "1:00", "Trust"],
        ["18", "The Guardrails", "What the system refuses to do", "1:00", "Trust"],
        ["19", "Live Demo", "Run a claim through the system", "3:00", "Backup"],
        ["20", "Ego Development Research", "14 hypotheses, 4-arm RCT design", "2:00", "NEW"],
        ["21", "Graduation Model", "\"Our goal is to make this tool unnecessary\"", "1:00", "Vision"],
        ["22", "Funding & Collaboration", "DFG, VW Foundation, Horizon Europe", "1:00", "Call"],
        ["23", "Open Source & Next Steps", "MIT license, community, PKM integration", "1:00", "Action"],
        ["24", "Closing", "\"Not every disagreement is manufactured...\"", "1:00", "Quote"],
      ].map(([num, title, content, time, notes]) =>
        new TableRow({
          children: [
            dataCell(num, 600, { align: AlignmentType.CENTER }),
            dataCell([{ text: title, bold: true }], 2400),
            dataCell(content, 4000),
            dataCell(time, 1200, { align: AlignmentType.CENTER }),
            dataCell(notes, 1160, { align: AlignmentType.CENTER }),
          ],
        })
      )),
    ],
  }),

  spacer(200),

  heading1("Opening and Closing"),

  heading2("Opening Hook"),

  quoteBlock("\"Show of hands: how many of you have ever used an AI tool to help you evaluate a claim or check a fact? [hands go up] Great. Now: how many of you have thought about what happens to your ability to evaluate claims on your own after you stop using that tool? [few hands] That is the dependency paradox, and it is what I want to talk about today.\""),

  heading2("Closing Line"),

  quoteBlock("\"The goal is not to build a better lie detector. It is to build a tool that teaches you three questions, and then gets out of your way. Because those three questions are yours to keep. Our measure of success is not how many people use Huginn & Muninn. It is how many people graduate from it.\""),


  heading1("Q&A Preparation"),

  heading2("\"How do you reach people who believe in chemtrails without calling them stupid?\""),
  body([{ text: "[Asked at PKM Summit, Utrecht, March 2026] ", italics: true, color: MID }, "You apply the three questions with empathy and curiosity. You start with \"I can see why that concerns you.\" You acknowledge the kernel of truth (weather modification is real, governments have lied about contamination). You ask \"who benefits from you believing this specific version?\" And you find the shared ground: \"You care about what your family breathes. So do I. Let us look at where our energy would be most effective.\""]),

  heading2("\"Can this be weaponized?\""),
  body(["Yes, any analysis tool can be misused. That is why we have the Adversarial Auditor (which red-teams every output), anti-weaponization guardrails, and open-source transparency. The Socratic approach is inherently harder to weaponize than declarative systems: asking questions is less effective at implanting beliefs than providing answers."]),

  heading2("\"What about the dependency paradox?\""),
  body(["This is the question we take most seriously. Bao et al. (2025) showed that unrestricted AI fact-checking creates dependency. Our four-pillar architecture (Socratic method, mandatory fading, desirable difficulties, system-regulated access) is specifically designed to prevent this. The graduation model makes our intent explicit: the tool should make itself unnecessary."]),

  heading2("\"Why local models instead of GPT-4 or Claude?\""),
  body(["Data sovereignty. If you are analyzing sensitive political claims, you should not trust a third party with that data. Additionally: no API costs, no rate limits, works offline. For users who want higher quality, the system also supports OpenAI-compatible APIs."]),

  heading2("\"Does this actually work?\""),
  body(["The underlying research does: Costello et al. in Science is peer-reviewed and won the AAAS Newcomb Cleveland Prize. Our implementation applies these principles but has not been independently validated yet. The four-arm RCT design (Chapter 7) is our plan for rigorous validation."]),

  heading2("\"Isn't AI fact-checking just replacing one authority with another?\""),
  body(["That is exactly why the system never declares truth. It presents evidence, names techniques, and asks questions. You decide. The Socratic approach builds your discernment, not dependence on the tool. And because it is open source, you can verify exactly how it arrives at every output."]),


  heading1("Technical Appendix"),

  heading2("Architecture Overview"),
  body(["Huginn & Muninn is a Python application built on FastAPI, using Pydantic for data validation and Ollama for local LLM inference. The web interface is a lightweight vanilla JavaScript frontend."]),

  heading2("Core Stack"),
  bullet("Python 3.12+ with FastAPI (REST API)", bRef.p2d),
  bullet("Pydantic models for strict I/O contracts", bRef.p2d),
  bullet("Ollama for local LLM inference (default: qwen3.5:9b)", bRef.p2d),
  bullet("SQLite for caching, history, sessions, and feedback", bRef.p2d),
  bullet("Docker support for one-command deployment", bRef.p2d),
  bullet("Optional: OpenAI-compatible API support, Brave Search integration", bRef.p2d),
  bullet("304 tests passing across all modules", bRef.p2d),

  heading2("API Endpoints"),

  new Table({
    columnWidths: [2800, 1200, 5360],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [headerCell("Endpoint", 2800), headerCell("Method", 1200), headerCell("Description", 5360)],
      }),
      ...([
        ["/api/check", "POST", "Method 1: Quick check with common ground"],
        ["/api/analyze", "POST", "Method 2: Full 6-agent pipeline"],
        ["/api/check-and-escalate", "POST", "Auto-escalation from Method 1 to 2"],
        ["/api/batch", "POST/GET", "Batch submission (up to 50 claims)"],
        ["/api/compare", "POST", "Cross-model comparison and reconciliation"],
        ["/api/sessions", "POST/GET", "Research session management"],
        ["/api/feedback", "POST", "User feedback collection"],
        ["/api/webhooks", "CRUD", "Webhook management for integrations"],
        ["/api/health", "GET", "LLM backend health check"],
      ].map(([ep, method, desc]) =>
        new TableRow({
          children: [
            dataCell([{ text: ep, bold: true }], 2800),
            dataCell(method, 1200, { align: AlignmentType.CENTER }),
            dataCell(desc, 5360),
          ],
        })
      )),
    ],
  }),

  spacer(200),

  // Final quote
  quoteBlock("Not every disagreement is manufactured. Some are real. But the ones that are manufactured deserve to be seen."),

  spacer(120),

  body([{ text: "Huginn & Muninn", bold: true }, " | Open Source (MIT) | Local-First | DISARM-Compatible | 304 Tests Passing"], { align: AlignmentType.CENTER }),
  body(["Version updated March 24, 2026, with findings from ~240 research sources across two deep research waves."], { align: AlignmentType.CENTER }),
];


// ============================================================
// ASSEMBLE DOCUMENT
// ============================================================

const doc = new Document({
  creator: "Jochen",
  title: "The Fact-Checker That Finds Common Ground: How AI Can Fight Disinformation by Revealing Shared Humanity",
  description: "Updated Presentation Brief with Research Findings from ~240 Sources",
  styles: {
    default: {
      document: {
        run: { font: "Arial", size: 22, color: BLACK },
      },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: DARK, font: "Arial" },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: ACCENT, font: "Arial" },
        paragraph: { spacing: { before: 280, after: 100 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 23, bold: true, color: MID, font: "Arial" },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 },
      },
    ],
  },
  numbering: { config: numberingConfig },
  sections: [
    {
      properties: {
        page: {
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
          pageNumbers: { start: 1 },
        },
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: "Huginn & Muninn: Presentation Brief v2", font: "Arial", size: 16, color: MID, italics: true })],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "Page ", font: "Arial", size: 18, color: MID }),
              new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 18, color: MID }),
              new TextRun({ text: " of ", font: "Arial", size: 18, color: MID }),
              new TextRun({ children: [PageNumber.TOTAL_PAGES], font: "Arial", size: 18, color: MID }),
            ],
          })],
        }),
      },
      children: [
        ...titlePage,
        ...tocSection,
        ...part1,
        ...part2,
      ],
    },
  ],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("C:/LocalAgent/Products/huginn_muninn/docs/Huginn-Muninn-Presentation-Brief-v2.docx", buffer);
  console.log("Document created: Huginn-Muninn-Presentation-Brief-v2.docx");
});
