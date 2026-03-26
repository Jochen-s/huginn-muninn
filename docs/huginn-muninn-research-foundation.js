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

function statusBadge(status, color) {
  return new TextRun({ text: ` [${status}] `, font: "Arial", size: 20, bold: true, color });
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

function bullet(text, ref, level = 0, opts = {}) {
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

function numbered(text, ref, opts = {}) {
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

// Table helpers
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

// Pre-create all bullet references we need
const bRef = {};
const sections = [
  "ch1", "ch2", "ch3p1", "ch3p2", "ch3p3", "ch3p4", "ch3p5", "ch3p6",
  "ch4", "ch5", "ch6", "ch7", "ch8", "ch9q1", "ch9q2", "ch9q3", "ch10",
  "ch11a", "ch11b", "ch12", "ch13", "ch14", "ch15",
  "appA", "appB", "appC",
  "dep1", "dep2", "dep3", "dep4", "dep5", "dep6", "dep7",
  "sig1", "sig2",
  "ego1", "ego2",
  "meth1", "meth2",
  "fund1",
];
sections.forEach(s => bRef[s] = newBulletRef());

const nRef = {};
["ch4pillars", "ch4patterns", "ch8strat", "ch12arms", "hyp1", "hyp2", "ch5tactics"].forEach(s => nRef[s] = newNumberRef());


// ============================================================
// DOCUMENT CONTENT
// ============================================================

// --- TITLE PAGE ---
const titlePage = [
  spacer(1800),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 80 },
    children: [new TextRun({ text: "Huginn & Muninn", font: "Georgia", size: 56, bold: true, color: DARK })],
  }),
  spacer(60),
  dividerLine(),
  spacer(60),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 60 },
    children: [new TextRun({ text: "Research Foundation for AI-Mediated", font: "Arial", size: 28, color: ACCENT })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 60 },
    children: [new TextRun({ text: "De-Polarization Through Common Humanity", font: "Arial", size: 28, color: ACCENT })],
  }),
  spacer(120),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 40 },
    children: [new TextRun({ text: "A Comprehensive Research Brief for Academic Collaboration", font: "Arial", size: 22, italics: true, color: MID })],
  }),
  spacer(600),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Jochen", font: "Arial", size: 24, color: DARK })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "March 24, 2026", font: "Arial", size: 22, color: MID })],
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
// PART 1: THE MISSION
// ============================================================

const part1 = [
  ...partTitle("Part 1: The Mission"),

  // Chapter 1
  heading1("Chapter 1: Why This Matters"),

  body(["The world is fracturing along manufactured lines. Conspiracy theories, authoritarianism, and political polarization threaten democracies globally. From QAnon in the United States to anti-vaccine movements across Europe, from climate denial campaigns funded by fossil fuel interests to state-sponsored disinformation operations, the information ecosystem has become weaponized against the very populations it was meant to serve."]),

  body(["The conventional response, fact-checking, has proven insufficient. Fact-checks reach a fraction of the audience that misinformation does, and they often trigger backfire effects in those most committed to false beliefs. Platform moderation is a game of whack-a-mole that fails to address root causes. Media literacy campaigns teach people to evaluate sources but not to understand the psychological mechanisms being exploited."]),

  quoteBlock("The key insight: The problem is not that people are stupid. The problem is that they are being systematically manipulated, and they lack the cognitive tools to see it."),

  body(["Huginn & Muninn (H&M) takes a fundamentally different approach. Named after the two ravens of Norse mythology who fly across the world gathering knowledge for Odin, H&M is designed to de-polarize by helping people find each other as human beings. It is not an oracle that dispenses truth from authority. It is a cognitive gymnasium that teaches a transferable mental framework: three questions that, once internalized, make the tool itself unnecessary."]),

  body(["This is the critical distinction. Every other tool in this space creates dependency. H&M is designed to create independence. The measure of its success is not continued usage, but graduation: users who no longer need it because they have internalized its method of thinking."]),

  // Chapter 2
  heading1("Chapter 2: The Three Questions"),

  body(["At the heart of Huginn & Muninn is a teachable framework consisting of three questions. These questions are not novel individually; what is novel is their combination into a self-correcting system where each question addresses the failure modes of the others."]),

  heading2("Question 1: What is true?"),

  body(["Deconstruct claims. Trace actors and their objectives. Find what is objectively verifiable. Understand the evidence landscape. This is not about declaring truth from authority; it is about mapping the evidence so users can reason for themselves."]),

  body(["This question teaches evidence evaluation: What do we actually know? What is the quality of the evidence? Who conducted the research, and were they independent? Can the findings be replicated? What does the scientific consensus look like, and what are the legitimate areas of uncertainty?"]),

  body(["Crucially, Question 1 does not produce a verdict. It produces a map. Users learn to distinguish between what is well-established, what is genuinely uncertain, and what is being deliberately obscured."]),

  heading2("Question 2: Who benefits from me feeling this way?"),

  body(["This is the manipulation literacy question. Who profits from your anger, fear, or distrust? What actors are involved in distorting the picture? What are their financial incentives, political objectives, or ideological commitments?"]),

  quoteBlock("This is a skill you carry forever. You do not need a tool for it. Once you learn to ask this question reflexively, you become resistant to manipulation across all domains."),

  body(["Question 2 teaches users to recognize the manufactured doubt playbook (see Chapter 5): the tactics used across industries, from tobacco to fossil fuels to anti-vaccine movements, to create confusion where scientific consensus exists. It builds a transferable skill in identifying cui bono, the ancient question of who benefits, in any information context."]),

  heading2("Question 3: What do we share?"),

  body(["The Common Humanity question. Not abstract (\"we are all human\") but concrete shared circumstances. \"You and the people you fear both worry about providing for your families.\" \"You and the people you distrust both want your children to grow up in a safe community.\" This is the healing question, the one that reconnects people across manufactured divides."]),

  body(["Question 3 is what makes H&M different from every fact-checking tool. Verification alone does not heal polarization. People do not change their minds because they are shown evidence; they change their minds when they feel safe enough to reconsider. Common Humanity creates that safety by making the \"other side\" recognizably human."]),

  heading2("The System Effect"),

  body(["The three questions work as a self-correcting system:"]),

  body([
    { text: "Question 1 grounds the analysis in evidence. ", bold: true },
    "Without it, Questions 2 and 3 become untethered speculation. You need to know what is actually true before you can assess who is manipulating the picture or find genuine common ground."
  ]),
  body([
    { text: "Question 2 builds manipulation literacy that prevents cynicism. ", bold: true },
    "Without it, Question 1 becomes naive (susceptible to sophisticated disinformation) and Question 3 becomes false equivalence (\"both sides have a point\" when one side is manufactured)."
  ]),
  body([
    { text: "Question 3 heals the rifts that manipulation created. ", bold: true },
    "Without it, Questions 1 and 2 produce technically correct analyses that leave people more isolated and cynical. Understanding that you are being manipulated, without a path back to human connection, is a recipe for nihilism."
  ]),

  body(["Each question corrects the others' weaknesses. Truth alone creates dependency on authority. Manipulation literacy alone creates cynicism. Common humanity alone creates false equivalence. Together, they form a cognitive framework that is both rigorous and humane."]),
];

// ============================================================
// PART 2: THE RESEARCH FOUNDATION
// ============================================================

const part2 = [
  ...partTitle("Part 2: The Research Foundation"),

  // Chapter 3
  heading1("Chapter 3: Research Pillar Assessment"),

  body(["H&M's design is grounded in six research pillars drawn from psychology, communication science, and computational social science. What follows is an honest assessment of each pillar, including replications, failures, and caveats. Academic credibility requires acknowledging what we do not know."]),

  // Pillar 1
  heading2("Pillar 1: Socratic AI Dialogue"),
  body([{ text: "Primary source: ", bold: true }, "Costello, Pennycook & Rand, \"Durably reducing conspiracy beliefs through dialogues with AI,\" Science, 2024."]),

  body([{ text: "Finding: ", bold: true }, "A 20% durable reduction in conspiracy beliefs through AI-mediated dialogue (N=2,190, with 2-month follow-up). The study used GPT-4 to engage conspiracy believers in individualized, evidence-based conversations tailored to their specific beliefs. This work won the 2026 AAAS Newcomb Cleveland Prize, the highest recognition for a paper published in Science."]),

  body([{ text: "Critical caveat: ", bold: true, color: RED_ACCENT }, "Bao et al. (2025, arXiv:2510.01537) conducted a longitudinal study finding a -15.3% decline in independent discernment by week 4 among users of AI fact-checking tools. Twenty-one percent of participants became \"Dependency Developers\" who progressively lost the ability to evaluate claims without AI assistance."]),

  body([{ text: "Resolution: ", bold: true, color: GREEN }, "The dependency is a design failure, not inherent to the method. Bao et al. found that genuinely Socratic questioning (asking probing questions rather than providing answers) correlated positively with independent detection skills (r=0.29, p<0.01). Furthermore, system-regulated access (structured interaction schedules) produced 2x learning gains compared to on-demand access (Wharton, 2025). H&M's architecture explicitly addresses this through scaffolding withdrawal and graduation design (see Chapter 4)."]),

  body([{ text: "Status: ", bold: true }, "STRONG with design caveats."]),
  body([{ text: "Citations: ", italics: true, color: MID }, "Costello, G., Pennycook, G. & Rand, D. G. (2024). Durably reducing conspiracy beliefs through dialogues with AI. Science, 385(6714), 1222-1227. Bao, Z. et al. (2025). The Double-Edged Sword of AI Fact-Checking. arXiv:2510.01537. Wharton Learning Lab (2025). Structured vs. On-Demand AI Tutoring."]),

  // Pillar 2
  heading2("Pillar 2: Inoculation / Prebunking"),
  body([{ text: "Primary sources: ", bold: true }, "van der Linden & Roozenbeek, Cambridge Social Decision-Making Lab; Google/Jigsaw collaboration."]),

  body([{ text: "Finding: ", bold: true }, "Teaching manipulation techniques (rather than debunking specific claims) creates lasting resilience against misinformation. The approach is analogous to biological inoculation: expose people to weakened forms of manipulation so they build cognitive antibodies. A large-scale YouTube study (5.4 million users) showed 5-10% improvement in manipulation technique recognition after viewing short prebunking videos (Roozenbeek et al., Science Advances, 2022)."]),

  body([{ text: "Meta-analysis (2025, N=37,075): ", bold: true }, "Inoculation improves discernment without inducing response bias. This is critical: participants did not become more skeptical of everything, only more accurate at distinguishing manipulation from legitimate persuasion."]),

  body([{ text: "Caveat: ", bold: true, color: AMBER }, "A PNAS Nexus study (June 2025) found limited real-world transfer from laboratory inoculation settings. Participants who performed well in controlled environments showed reduced gains when encountering novel manipulation in naturalistic social media feeds."]),

  body([{ text: "Cross-cultural validation: ", bold: true }, "The Bad News prebunking game has been tested across multiple languages and cultural contexts with consistent effects, suggesting the manipulation taxonomy is not culturally bound."]),

  body([{ text: "Status: ", bold: true }, "MODERATE-STRONG (best replicated pillar, but real-world transfer gap)."]),
  body([{ text: "Citations: ", italics: true, color: MID }, "van der Linden, S. & Roozenbeek, J. (2022). Inoculation against manipulation. Science Advances, 8(29). Cambridge 30K YouTube replication. PNAS Nexus (2025). Bad News game cross-cultural studies."]),

  // Pillar 3
  heading2("Pillar 3: Perception Gap"),
  body([{ text: "Primary source: ", bold: true }, "More in Common, \"The Perception Gap,\" 2019."]),

  body([{ text: "Finding: ", bold: true }, "Americans systematically overestimate the extremism of their political opponents by approximately 2x. Democrats believe 50% of Republicans are extreme; the actual figure is closer to 25%. The pattern is symmetric: Republicans similarly overestimate Democratic extremism. This \"perception gap\" is largest among the most politically engaged and those who consume the most news."]),

  body([{ text: "Caveat: ", bold: true, color: RED_ACCENT }, "This is a single-country study that has not been cross-culturally replicated with the same methodology. While similar perception gaps have been observed anecdotally in other democracies, the specific 2x overestimation figure cannot be generalized beyond the US context."]),

  body([{ text: "Status: ", bold: true }, "WEAK (single country, single study, no replication)."]),
  body([{ text: "Citations: ", italics: true, color: MID }, "More in Common (2019). The Perception Gap. https://perceptiongap.us/"]),

  // Pillar 4
  heading2("Pillar 4: Moral Reframing"),
  body([{ text: "Primary sources: ", bold: true }, "Feinberg & Willer, Stanford/University of Toronto, 2015-2019."]),

  body([{ text: "Original finding: ", bold: true }, "Reframing political arguments in terms of the moral foundations valued by the target audience (e.g., framing environmental protection in terms of purity/sanctity for conservative audiences) could increase cross-partisan persuasion."]),

  body([{ text: "DOWNGRADED: ", bold: true, color: RED_ACCENT }, "Six or more preregistered replication attempts have failed to reproduce the original effects:"]),

  bullet("Arpan et al. (2018): Failed to replicate moral reframing effects on climate attitudes", bRef.ch3p4),
  bullet("Berkebile-Weinberg et al. (2024): No significant reframing effects across multiple moral foundations", bRef.ch3p4),
  bullet("Crawford (2025): Null results with improved methodology and larger samples", bRef.ch3p4),
  bullet("Hundemer (2023): Failed replication across three experimental paradigms", bRef.ch3p4),
  bullet("Kim (2023): No effects in preregistered study with Korean sample", bRef.ch3p4),
  bullet("2026 study (N=2,009): Adequately powered preregistered study found null effects", bRef.ch3p4),

  body([{ text: "Status: ", bold: true }, "WEAK. Theoretical foundation questioned. Retained as experimental module only, not core pillar."]),
  body([{ text: "Citations: ", italics: true, color: MID }, "Feinberg, M. & Willer, R. (2015, 2019). Multiple replication failures: Arpan 2018, Berkebile-Weinberg 2024, Crawford 2025, Hundemer 2023, Kim 2023."]),

  // Pillar 5
  heading2("Pillar 5: Narrative Complexity"),
  body([{ text: "Primary source: ", bold: true }, "Peter Coleman, Columbia University, Dynamics of Conflict Lab."]),

  body([{ text: "Finding: ", bold: true }, "Coleman's work applies complexity science to intractable conflict, demonstrating that conflicts become intractable when they are perceived as simple (us vs. them). Introducing narrative complexity, multiple perspectives, historical context, and acknowledgment of legitimate grievances on all sides, can shift conflicts from intractable to tractable. The theoretical framework draws on attractor dynamics: simple narratives create strong attractors that trap thinking; complex narratives create multiple weaker attractors that allow cognitive flexibility."]),

  body([{ text: "Caveat: ", bold: true, color: AMBER }, "While the theoretical framework is compelling and supported by laboratory studies, there are no large-scale randomized controlled trials demonstrating that narrative complexity interventions reduce polarization or conspiracy beliefs at scale."]),

  body([{ text: "Status: ", bold: true }, "WEAK-MODERATE (strong theory without intervention-level evidence)."]),
  body([{ text: "Citations: ", italics: true, color: MID }, "Coleman, P. T. (2011). The Five Percent. PublicAffairs. Coleman, P. T. et al. (2021). The Way Out. Columbia University Press."]),

  // Pillar 6
  heading2("Pillar 6: Redirect Method"),
  body([{ text: "Primary source: ", bold: true }, "Moonshot (formerly Jigsaw/Google partnership)."]),

  body([{ text: "Finding: ", bold: true }, "The Redirect Method targets individuals searching for extremist content with curated counter-narrative content, primarily through YouTube advertising. The headline figure of 224% increase in engagement has been widely cited."]),

  body([{ text: "Critical caveat: ", bold: true, color: AMBER }, "The 224% figure measures engagement (watch time with counter-narrative videos), NOT belief change. There is no evidence that watching counter-narrative content changed attitudes or behavior. The RAND Corporation evaluation used notably soft language: \"showed promise\" without quantifying attitudinal effects."]),

  body([{ text: "Status: ", bold: true }, "MODERATE (measures wrong outcome; engagement is not belief change)."]),
  body([{ text: "Citations: ", italics: true, color: MID }, "Moonshot (2017). The Redirect Method. RAND Corporation evaluation. YouTube counter-narrative engagement study."]),

  // Chapter 4
  heading1("Chapter 4: The Dependency Paradox and Its Solution"),

  body(["The most significant threat to AI-mediated de-polarization is not that it will fail, but that it will succeed in a way that creates dependency. Bao et al. (2025) demonstrated this empirically: users of AI fact-checking tools showed a -15.3% decline in independent discernment by week 4, with 21% becoming \"Dependency Developers\" who progressively lost the ability to evaluate claims without AI assistance."]),

  body(["This finding aligns with Vygotsky's Zone of Proximal Development (ZPD) framework: scaffolding that is never withdrawn does not produce learning; it produces learned helplessness. More recently, the \"Zone of No Development\" paper (arXiv:2511.12822) documented how persistent AI assistance can prevent the cognitive struggle necessary for genuine skill acquisition."]),

  quoteBlock("H&M is not an oracle. It is a thinking exercise. The three questions are the curriculum, not the tool. The tool is the training wheels; the questions are the bicycle."),

  heading2("The Solution Architecture: Four Pillars"),

  numbered([{ text: "Genuine Socratic Method. ", bold: true }, "Ask, do not tell. Instead of providing verdicts, H&M guides users through the three questions with prompts that require active reasoning. Bao et al. found that genuinely Socratic questioning correlated positively with independent detection skills (r=0.29, p<0.01)."], nRef.ch4pillars),
  numbered([{ text: "Mandatory Fading Schedule. ", bold: true }, "Scaffolding withdrawal over sessions. Early interactions provide substantial guidance; later interactions progressively remove support. By session 8+, users should be applying the three questions with minimal AI involvement."], nRef.ch4pillars),
  numbered([{ text: "Desirable Difficulties (Bjork Lab, UCLA). ", bold: true }, "Incorporate spacing (distributed practice), interleaving (mixing question types), retrieval practice (asking users to recall previous analyses), and generation (requiring users to produce their own framings before seeing AI suggestions). These techniques produce slower initial learning but dramatically better long-term retention and transfer."], nRef.ch4pillars),
  numbered([{ text: "System-Regulated Access (Wharton, 2025). ", bold: true }, "Structured interaction schedules produce 2x learning gains compared to on-demand access. Users cannot simply query H&M whenever they encounter a claim; the system manages interaction frequency to optimize for learning rather than convenience."], nRef.ch4pillars),

  heading2("Seven Concrete Design Patterns"),

  numbered([{ text: "Forced Self-Assessment: ", bold: true }, "Before showing any analysis, require users to state their own assessment of a claim. This creates a baseline against which learning can be measured and triggers generation effects."], nRef.ch4patterns),
  numbered([{ text: "Rate-Limiting: ", bold: true }, "Cap daily interactions to prevent binge usage that leads to passive consumption rather than active learning."], nRef.ch4patterns),
  numbered([{ text: "Progressive Fading: ", bold: true }, "Gradually reduce the detail and directiveness of AI responses over sessions. Early sessions provide step-by-step guidance; later sessions provide only prompts and let users fill in the reasoning."], nRef.ch4patterns),
  numbered([{ text: "Interleaving: ", bold: true }, "Mix claim types (health, politics, science, conspiracy) rather than clustering similar claims. This prevents overfitting to domain-specific cues and builds transferable reasoning skills."], nRef.ch4patterns),
  numbered([{ text: "Reflection Prompts: ", bold: true }, "After completing an analysis, ask users to identify which of the three questions was most useful and why. This metacognitive step strengthens transfer."], nRef.ch4patterns),
  numbered([{ text: "Independence Milestones: ", bold: true }, "Track unassisted performance on novel claims. When users consistently demonstrate accurate independent analysis, celebrate the milestone and reduce access frequency."], nRef.ch4patterns),
  numbered([{ text: "Graduation Model: ", bold: true }, "Explicitly frame the relationship as temporary. \"Our goal is to make this tool unnecessary.\" Users who consistently perform at expert level on novel claims are \"graduated\" with ceremony and recognition."], nRef.ch4patterns),

  quoteBlock("The graduation framing is essential. Every other AI tool measures success by engagement and retention. H&M measures success by users who no longer need it.", "Halpern, D. F. (1998). Teaching critical thinking for transfer across domains."),

  body([{ text: "Citations: ", italics: true, color: MID }, "Bjork, R. A. & Bjork, E. L. (2011). Making things hard on yourself, but in a good way. UCLA. Vygotsky, L. S. (1978). Mind in Society. Zone of No Development (2025, arXiv:2511.12822). Wharton Learning Lab (2025). Halpern, D. F. (1998). Teaching critical thinking for transfer across domains. American Psychologist, 53(4), 449-455."]),

  // Chapter 5
  heading1("Chapter 5: Manufactured Doubt Detection"),

  body(["Understanding manufactured doubt is central to Question 2 (\"Who benefits from me feeling this way?\"). Decades of research have documented the systematic tactics used by industries and political actors to create uncertainty where scientific consensus exists."]),

  heading2("The 28-Tactic Taxonomy"),

  body([{ text: "Primary source: ", bold: true }, "Goldberg, Vandenberg et al. (2021). \"Strategies and tactics used to undermine the credibility of science and scientists.\" Environmental Health, 20(1), 89. PMC7996119."]),

  body(["This landmark systematic review analyzed manufactured doubt campaigns across five industries: Tobacco (T), Chemicals (C), Sugar (S), Alcohol (A), and Mining (M). The researchers identified 28 distinct tactics organized into categories, with five tactics appearing universally across all industries."]),

  heading3("The 5 Universal Tactics"),

  bullet([{ text: "Attack Study Design: ", bold: true }, "Challenge methodology, sample sizes, statistical methods, or confounders to discredit inconvenient findings."], bRef.ch5),
  bullet([{ text: "Gain Reputable Support: ", bold: true }, "Recruit credentialed scientists, form industry-funded research institutes, publish in legitimate journals through sponsored supplements."], bRef.ch5),
  bullet([{ text: "Misrepresent Data: ", bold: true }, "Cherry-pick studies, conflate correlation with causation (or deny correlation), present misleading statistics."], bRef.ch5),
  bullet([{ text: "Hyperbolic Language: ", bold: true }, "Use emotionally charged framing (\"junk science,\" \"nanny state,\" \"alarmist\") to delegitimize opponents."], bRef.ch5),
  bullet([{ text: "Influence Government: ", bold: true }, "Lobby regulators, influence policy committees, delay regulation through requests for \"more research.\""], bRef.ch5),

  body(["The complete 28-tactic taxonomy is provided in Appendix B."]),

  heading2("Structural Signatures: Manufactured Doubt vs. Genuine Uncertainty"),

  body(["A critical capability for H&M is distinguishing manufactured doubt from genuine scientific uncertainty. The following structural signatures differentiate them:"]),

  heading3("9 Signatures of Manufactured Doubt"),
  bullet("Funding source concealment or industry ties to researchers", bRef.sig1),
  bullet("Internal documents contradicting public statements (the Supran-Oreskes methodology)", bRef.sig1),
  bullet("Coordinated messaging across nominally independent actors", bRef.sig1),
  bullet("Selective citation of minority studies while ignoring systematic reviews", bRef.sig1),
  bullet("Demand for impossible certainty (\"we need more research\" as a delay tactic)", bRef.sig1),
  bullet("Ad hominem attacks on consensus scientists", bRef.sig1),
  bullet("Creation of false balance (\"teach the controversy\" where none exists)", bRef.sig1),
  bullet("Astroturfing: manufactured grassroots opposition", bRef.sig1),
  bullet("Revolving door between industry and regulatory bodies", bRef.sig1),

  heading3("7 Signatures of Genuine Scientific Uncertainty"),
  bullet("Transparent funding disclosure", bRef.sig2),
  bullet("Specific, addressable methodological concerns", bRef.sig2),
  bullet("Engagement with the broader literature, not selective citation", bRef.sig2),
  bullet("Proposed studies to resolve the uncertainty", bRef.sig2),
  bullet("Willingness to accept evidence that resolves the question", bRef.sig2),
  bullet("Consistent public and private positions", bRef.sig2),
  bullet("Published in peer-reviewed venues with open peer review", bRef.sig2),

  heading2("Computational Detection"),

  body(["Several computational approaches enable automated detection of manufactured doubt tactics:"]),

  bullet([{ text: "CARDS (Computer-Assisted Recognition of Denial and Skepticism): ", bold: true }, "RoBERTa-based classifier trained on climate denial discourse (Coan et al., Nature, 2021)."], bRef.ch3p5),
  bullet([{ text: "FLICC+CARDS: ", bold: true }, "Combined taxonomy using DeBERTa architecture, achieving F1=0.73 on manufactured doubt detection across domains."], bRef.ch3p5),
  bullet([{ text: "SemEval Propaganda Detection: ", bold: true }, "Shared task on fine-grained propaganda technique detection in news articles, providing labeled training data and baseline models."], bRef.ch3p5),
  bullet([{ text: "Supran-Oreskes Methodology: ", bold: true }, "Systematic comparison of internal industry documents with public communications to identify deliberate contradiction (Supran & Oreskes, Science, 2017)."], bRef.ch3p5),

  body([{ text: "Citations: ", italics: true, color: MID }, "Goldberg, R. F. & Vandenberg, L. N. et al. (2021). Environmental Health, 20(1), 89. PMC7996119. Supran, G. & Oreskes, N. (2017). Assessing ExxonMobil's climate change communications. Science, 355(6332). Coan, T. G. et al. (2021). Computer-assisted recognition of denial and skepticism. Nature Scientific Data."]),

  // Chapter 6
  heading1("Chapter 6: Common Humanity as Cognitive Filter"),

  body(["Common Humanity is not a feel-good appendage to H&M's analytical framework; it is a cognitive filter that enables learning transfer. Without it, truth-finding and manipulation literacy produce accurate but isolated individuals. With it, they produce citizens capable of bridging divides."]),

  heading2("Cognitive Apprenticeship"),

  body([{ text: "Framework: ", bold: true }, "Collins, Brown & Newman (1989) described a six-stage model for transferring complex cognitive skills: modeling, coaching, scaffolding, articulation, reflection, and exploration. H&M maps directly onto this framework:"]),

  bullet([{ text: "Modeling: ", bold: true }, "H&M demonstrates the three-question analysis on user-submitted claims."], bRef.ch6),
  bullet([{ text: "Coaching: ", bold: true }, "H&M provides guidance and feedback as users attempt their own analyses."], bRef.ch6),
  bullet([{ text: "Scaffolding: ", bold: true }, "Structured prompts guide users through each question systematically."], bRef.ch6),
  bullet([{ text: "Articulation: ", bold: true }, "Users must explain their reasoning, making tacit knowledge explicit."], bRef.ch6),
  bullet([{ text: "Reflection: ", bold: true }, "Post-analysis prompts ask users to evaluate their own reasoning process."], bRef.ch6),
  bullet([{ text: "Exploration: ", bold: true }, "Graduated users apply the framework independently to novel claims."], bRef.ch6),

  heading2("Perspective-Taking: Trainable but Nuanced"),

  body(["Research demonstrates that perspective-taking is trainable and effects are stable for 5 months or longer. However, empathic concern (feeling what others feel) can backfire in intergroup contexts by increasing distress without productive channel for action. H&M therefore focuses on cognitive perspective-taking (understanding what others think and why) rather than affective empathy (feeling what others feel)."]),

  heading2("The Three-Layer Reinforcement"),

  body(["The theoretical justification for combining all three questions rests on a three-layer reinforcement argument:"]),

  bullet([{ text: "Truth alone creates dependency. ", bold: true }, "Users learn to seek authoritative answers rather than developing reasoning skills. Bao et al. (2025) demonstrated this empirically."], bRef.ch3p6),
  bullet([{ text: "Manipulation literacy alone creates cynicism. ", bold: true }, "Users who learn to see manipulation everywhere but lack tools for establishing truth or finding common ground become nihilistic (\"everyone is lying, nothing matters\")."], bRef.ch3p6),
  bullet([{ text: "Common humanity alone creates false equivalence. ", bold: true }, "Without truth-grounding and manipulation literacy, appeals to common ground can excuse genuine wrongdoing (\"both sides have valid points\" when one side is manufactured)."], bRef.ch3p6),

  body(["Together, each layer corrects the failure mode of the others. This is not an additive benefit; it is a multiplicative one."]),

  heading2("Theoretical Foundations"),

  body([{ text: "Common Ingroup Identity Model (Gaertner & Dovidio): ", bold: true }, "Recategorizing outgroup members as members of a shared superordinate category reduces intergroup bias. H&M's Question 3 performs this recategorization by identifying concrete shared circumstances."]),

  body([{ text: "Bohm Dialogue: ", bold: true }, "David Bohm's concept of \"proprioception of thought\", becoming aware of one's own thinking processes, is a design principle for H&M. The three questions externalize and make visible the reasoning process, enabling the kind of metacognitive awareness that Bohm argued is necessary for genuine dialogue."]),

  body([{ text: "Citations: ", italics: true, color: MID }, "Collins, A., Brown, J. S., & Newman, S. E. (1989). Cognitive apprenticeship. In Knowing, Learning, and Instruction. Gaertner, S. L. & Dovidio, J. F. (2000). Reducing Intergroup Bias. Bohm, D. (1996). On Dialogue. Cambridge inoculation transfer studies."]),
];

// ============================================================
// PART 3: THE ARCHITECTURE
// ============================================================

const part3 = [
  ...partTitle("Part 3: The Architecture"),

  // Chapter 7
  heading1("Chapter 7: How H&M Works"),

  body(["H&M provides two modes of analysis, calibrated to different needs and contexts."]),

  heading2("Method 1: Quick Check"),

  body(["A two-pass verification designed for rapid assessment (approximately 10 seconds). The system submits a claim to two independent LLM passes: the first evaluates evidence, the second checks the first pass for errors and biases. The output is a concise verdict with confidence level, key evidence points, and a Common Ground section."]),

  body(["Quick Check is designed for everyday use: a friend shares a claim on social media, a news article makes a surprising assertion, a politician makes a factual statement that seems too convenient. It provides enough information to make an informed judgment without requiring deep engagement."]),

  heading2("Method 2: Six-Agent Pipeline"),

  body(["For claims requiring deeper analysis, H&M deploys a six-agent pipeline where each agent serves a distinct analytical function:"]),

  bullet([{ text: "Decomposer: ", bold: true }, "Breaks composite claims into atomic sub-claims that can be individually evaluated. A single conspiracy theory often bundles 5-10 distinct factual claims, some true, some false, some unfalsifiable."], bRef.ch7),
  bullet([{ text: "Tracer: ", bold: true }, "Traces claims to their origins. When did this claim first appear? Who originated it? How has it mutated as it spread? This genealogy often reveals that claims presented as grassroots observations originated from coordinated campaigns."], bRef.ch7),
  bullet([{ text: "Mapper: ", bold: true }, "Maps the actor network around a claim. Who is promoting it? What are their relationships, funding sources, and track records? This answers the \"cui bono\" question systematically."], bRef.ch7),
  bullet([{ text: "Classifier: ", bold: true }, "Identifies which of the 28 manufactured doubt tactics (see Chapter 5) are present in the claim and its promotion. This is the manipulation literacy layer."], bRef.ch7),
  bullet([{ text: "Bridge Builder: ", bold: true }, "Finds concrete common ground between the claim's adherents and its critics. This agent runs on every analysis, ensuring that every output includes a path back to human connection."], bRef.ch7),
  bullet([{ text: "Auditor: ", bold: true }, "Reviews the entire analysis for errors, biases, false equivalence, and internal consistency. The Auditor specifically checks whether the Bridge Builder has created false equivalence by granting unwarranted legitimacy to manufactured positions."], bRef.ch7),

  heading2("Example Output: Policy Debate"),

  body(["Consider a claim: \"Immigration is destroying the economy.\" H&M's analysis would produce three sections:"]),

  heading3("Section 1: What Is True"),
  body(["Economic research consistently shows that immigration has net positive effects on GDP in receiving countries, though distributional effects are uneven. Low-wage workers in directly competing sectors may experience short-term wage pressure (Borjas, 2003), while the broader economy benefits from increased demand, entrepreneurship, and fiscal contributions (National Academies, 2017). The claim as stated is not supported by the economic consensus, though the underlying concern about distributional fairness is legitimate."]),

  heading3("Section 2: Manipulation Mechanics"),
  body(["The framing uses tactic #8 (Hyperbolic Language: \"destroying\") and #9 (Blame Other Causes: attributing complex economic dynamics to a single factor). The narrative benefits political actors who gain electoral advantage from anti-immigration sentiment, and media outlets that monetize outrage. The economic anxieties being exploited are real; the attribution to immigration is manufactured."]),

  heading3("Section 3: Common Ground"),
  body(["Both people who worry about immigration and immigrants themselves share a core concern: economic security for their families. The worker in Ohio who fears job loss and the immigrant in Texas who works two jobs to provide for their children are responding to the same economic system that concentrates gains at the top. Framing this as a conflict between them serves those who benefit from both groups remaining too divided to demand structural reform."]),

  // Chapter 8
  heading1("Chapter 8: The Ego Development Connection"),

  body(["One of H&M's most innovative features is calibrating its Socratic dialogue to the user's developmental stage, as assessed through Loevinger's model of ego development."]),

  heading2("Loevinger's Model"),

  body(["Jane Loevinger's ego development framework describes a sequence of increasingly complex meaning-making structures, from pre-conventional through conventional to post-conventional stages. Each stage represents a qualitatively different way of constructing meaning, handling ambiguity, and relating to authority."]),

  // Ego development table
  new Table({
    columnWidths: [1000, 2200, 6160],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [headerCell("Stage", 1000), headerCell("Name", 2200), headerCell("Characteristics", 6160)],
      }),
      new TableRow({ children: [dataCell("E2", 1000), dataCell("Impulsive", 2200), dataCell("Dependent, exploitative; focused on immediate needs", 6160)] }),
      new TableRow({ children: [dataCell("E3", 1000), dataCell("Self-Protective", 2200), dataCell("Opportunistic, manipulative; rules are obstacles", 6160)] }),
      new TableRow({ children: [dataCell([{ text: "E4", bold: true }], 1000, { fill: "FFF3CD" }), dataCell([{ text: "Conformist", bold: true }], 2200, { fill: "FFF3CD" }), dataCell([{ text: "Group-identified; rules are absolute; black-and-white thinking", bold: true }], 6160, { fill: "FFF3CD" })] }),
      new TableRow({ children: [dataCell("E5", 1000), dataCell("Self-Aware", 2200), dataCell("Emerging self-reflection; recognizes exceptions to rules; beginning nuance", 6160)] }),
      new TableRow({ children: [dataCell("E6", 1000), dataCell("Conscientious", 2200), dataCell("Self-evaluated standards; conceptual complexity; long-term goals", 6160)] }),
      new TableRow({ children: [dataCell("E7", 1000), dataCell("Individualistic", 2200), dataCell("Tolerates ambiguity; recognizes inner conflict; respects individuality", 6160)] }),
      new TableRow({ children: [dataCell("E8", 1000), dataCell("Autonomous", 2200), dataCell("Copes with conflict; integrates opposing ideas; respects autonomy", 6160)] }),
      new TableRow({ children: [dataCell("E9", 1000), dataCell("Integrated", 2200), dataCell("Identity consolidation; reconciles paradox; wisdom", 6160)] }),
    ],
  }),

  spacer(80),

  heading2("E4 Conformist as Peak Conspiracy Susceptibility"),

  body(["The E4 Conformist stage is characterized by strong group identification, adherence to in-group norms, black-and-white thinking, and deference to perceived authority. This maps directly onto what the Leipzig Authoritarianism Studies (Decker et al., ongoing since 2002) identify as the authoritarian character: conventional, submissive to in-group authorities, and aggressive toward out-groups."]),

  body(["E4 individuals are maximally susceptible to conspiracy theories because conspiracies provide simple explanations (us vs. them), identify clear authorities (the conspiracy leader), and define clear out-groups (the conspirators). The developmental task at E4 is precisely what conspiracy theories exploit: the need for belonging, certainty, and clear rules."]),

  heading2("Stage-Calibrated Socratic Dialogue"),

  body(["H&M calibrates its approach based on assessed developmental stage:"]),

  numbered([{ text: "E3-E4 (Authority-Aligned): ", bold: true }, "Use trusted authority figures and in-group values as entry points. \"Experts at your favorite university found...\" Do not challenge the authority structure; work within it to introduce evidence."], nRef.ch8strat),
  numbered([{ text: "E5 (Perspective-Taking): ", bold: true }, "Introduce the idea that reasonable people can see the same evidence differently. \"What if someone you respect looked at this and reached a different conclusion? Why might that happen?\""], nRef.ch8strat),
  numbered([{ text: "E6 (Evidence-Based Socratic): ", bold: true }, "Full Socratic method with evidence evaluation. \"What would convince you this is true? What would convince you it is false? Are those standards symmetric?\""], nRef.ch8strat),
  numbered([{ text: "E7+ (Systems-Thinking): ", bold: true }, "Engage with structural complexity. \"What systemic factors make this narrative appealing? What function does it serve for the communities that adopt it?\""], nRef.ch8strat),

  heading2("WUSCT Automation"),

  body(["Stage assessment relies on the Washington University Sentence Completion Test (WUSCT), traditionally scored by trained human raters. Bronlet (2025, Frontiers in Psychology) demonstrated automated WUSCT scoring using large language models, achieving kappa=0.779 inter-rater reliability. This approaches but does not yet match the 0.80+ threshold for clinical reliability, suggesting a viable path toward automated stage assessment for calibrating H&M's dialogue approach."]),

  body([{ text: "Citations: ", italics: true, color: MID }, "Loevinger, J. & Le Xuan Hy (1996). Measuring Ego Development (2nd ed.). Mahwah, NJ: Erlbaum. Leipzig Authoritarianism Studies (Decker, O. et al., 2002-present). Bronlet, M. (2025). Automated scoring of ego development. Frontiers in Psychology."]),
];

// ============================================================
// PART 4: TEST CASE -- CHEMTRAILS
// ============================================================

const part4 = [
  ...partTitle("Part 4: Test Case -- Chemtrails"),

  heading1("Chapter 9: Applying the Three Questions to Chemtrails"),

  body(["To demonstrate the three-question framework in practice, we apply it to one of the most persistent conspiracy theories: chemtrails."]),

  heading2("Question 1: What is true?"),

  body(["Condensation trails (contrails) are a well-understood atmospheric phenomenon. Water vapor from jet engine exhaust condenses in cold air at altitude, forming ice crystals that appear as white trails. Persistence depends on humidity and temperature: in dry air, contrails dissipate within seconds; in humid air, they can persist for hours and spread into cirrus-like cloud formations."]),

  body(["The \"chemtrails\" conspiracy claims that government aircraft deliberately spray chemicals for purposes ranging from weather modification to population control to mind control. Variants include claims about barium, aluminum, strontium, and various biological agents."]),

  body([{ text: "Evidence: ", bold: true }, "Atmospheric science confirms the contrail explanation. A 2016 Carnegie Science/UC Irvine survey of 77 atmospheric scientists found 76 (98.7%) saw no evidence of a secret large-scale chemical spraying program. The single dissenting scientist cited a single unexplained observation, not evidence of a program."]),

  body([{ text: "Important nuance: ", bold: true }, "Weather modification programs DO exist. Cloud seeding with silver iodide has been practiced since the 1940s and is publicly documented by organizations like the World Meteorological Organization. The US military's Project Popeye (cloud seeding in Vietnam, 1967-1972) was real and declassified. This creates a kernel of truth that conspiracy narratives exploit: real weather modification exists, therefore secret chemical spraying is plausible. The logical gap, between documented cloud seeding and the claimed global chemtrail program, is where manipulation operates."]),

  heading2("Question 2: Who benefits from me believing this?"),

  body(["Fear of chemtrails drives distrust of government, science, and institutions. This distrust serves several actors:"]),

  bullet([{ text: "Content monetizers: ", bold: true }, "Creators and influencers who monetize fear through views, subscriptions, and product sales. The chemtrail ecosystem supports a significant market in air purifiers, detoxification supplements, orgonite devices, and alternative health products."], bRef.ch9q2),
  bullet([{ text: "Political actors: ", bold: true }, "Individuals and organizations that benefit from general institutional distrust. Chemtrail beliefs correlate strongly with broader anti-government sentiment that can be mobilized for political purposes."], bRef.ch9q2),
  bullet([{ text: "Alternative medicine industry: ", bold: true }, "Practitioners who position themselves as alternatives to \"compromised\" mainstream medicine and science."], bRef.ch9q2),

  body(["The chemtrail narrative employs several manufactured doubt tactics from the 28-tactic taxonomy:"]),

  bullet([{ text: "Tactic #12 (Exploit Scientific Illiteracy): ", bold: true }, "Most people cannot explain condensation physics, making contrails seem mysterious."], bRef.ch9q3),
  bullet([{ text: "Tactic #8 (Hyperbolic Language): ", bold: true }, "\"They are poisoning us\" creates urgency and fear."], bRef.ch9q3),
  bullet([{ text: "Tactic #9 (Blame Other Causes): ", bold: true }, "Attribute health problems and weather patterns to spraying rather than documented causes."], bRef.ch9q3),
  bullet([{ text: "Tactic #2 (Gain Reputable-seeming Support): ", bold: true }, "Cite credentialed individuals who have endorsed chemtrail claims."], bRef.ch9q3),

  body([{ text: "The feeling exploited: ", bold: true }, "Legitimate anxiety about environmental contamination and government transparency, redirected toward a false target. These anxieties are real. Governments have historically lied about environmental contamination (tobacco, lead paint, asbestos, PFAS). The manipulation lies not in creating the anxiety but in redirecting it."]),

  heading2("Question 3: What do we share with chemtrail believers?"),

  body(["The shared concern is real. People who believe in chemtrails and people who do not share:"]),

  bullet("Worry about environmental contamination and the air their families breathe", bRef.ch10),
  bullet("Distrust of institutions that have historically lied about public health risks", bRef.ch10),
  bullet("Desire to protect family health and especially children", bRef.ch10),
  bullet("Feeling powerless against forces beyond individual control", bRef.ch10),
  bullet("Frustration with insufficient government transparency", bRef.ch10),

  quoteBlock("The perception gap: chemtrail believers are not stupid. Many are expressing legitimate anxiety about environmental threats through a framework that gives them a sense of understanding and agency. Dismissing them as irrational fails to engage with the real concern that drives the belief."),

  body([{ text: "The bridge: ", bold: true }, "\"You care about what is in the air your family breathes. So does everyone. The question is not whether to care, because that concern is entirely legitimate. The question is whether the chemtrail explanation actually helps you protect your family, or whether it redirects your energy away from the real environmental threats that are documented and actionable: industrial air pollution, PFAS contamination, particulate matter from combustion.\""]),

  body([{ text: "The Socratic close: ", bold: true }, "\"If the government were spraying chemicals, what evidence would convince you it was happening? And what evidence would convince you it was not? Is there a difference in your standards of proof for each direction?\" This question, once genuinely engaged with, reveals asymmetric standards of evidence, the cognitive signature of motivated reasoning, without accusing anyone of being irrational."]),

  // Chapter 10
  heading1("Chapter 10: How H&M Would Handle This Interaction"),

  body(["User submits: \"The government is spraying chemicals from planes to control the weather/population.\""]),

  heading2("Method 1: Quick Check Output"),

  body([{ text: "Verdict: MIXED. ", bold: true }, "Government weather modification programs (cloud seeding) are real and documented. Large-scale secret chemical spraying for population control is not supported by evidence. The claim conflates documented weather modification with unsubstantiated population control narratives."]),

  body([{ text: "Evidence for: ", bold: true }, "Cloud seeding exists (WMO documentation). Project Popeye was real (declassified 1971). Some countries conduct operational weather modification (UAE, China)."]),

  body([{ text: "Evidence against: ", bold: true }, "98.7% of atmospheric scientists found no evidence of secret spraying (Carnegie/UCI, 2016). No whistleblowers from the thousands of people required to maintain such a program. Contrail physics fully explains observed phenomena."]),

  body([{ text: "Common Ground: ", bold: true }, "Your concern about what is in the air is legitimate. Documented air quality threats (industrial emissions, PFAS, wildfire smoke) affect millions. The question is whether the chemtrail narrative helps or hinders addressing those real threats."]),

  heading2("Method 2: Six-Agent Pipeline Output"),

  bullet([{ text: "Decomposer: ", bold: true }, "Breaks claim into sub-claims: (a) the government controls aircraft, (b) chemicals are sprayed from them, (c) the purpose is weather/population control, (d) this is secret. Sub-claim (a) is trivially true. Sub-claim (b) is true for documented cloud seeding. Sub-claims (c) and (d) lack supporting evidence."], bRef.ch11a),
  bullet([{ text: "Tracer: ", bold: true }, "Traces modern chemtrail conspiracy to the late 1990s, following the 1996 USAF \"Weather as a Force Multiplier\" research paper (a speculative academic paper, not a program document). Significant amplification through early internet forums and Art Bell's Coast to Coast AM radio program."], bRef.ch11a),
  bullet([{ text: "Mapper: ", bold: true }, "Identifies key actors: content creators with monetized channels, supplement companies advertising to chemtrail audiences, political organizations leveraging anti-government sentiment."], bRef.ch11a),
  bullet([{ text: "Classifier: ", bold: true }, "Identifies tactics #8 (Hyperbolic Language), #9 (Blame Other Causes), #12 (Exploit Scientific Illiteracy), #2 (Gain Reputable-seeming Support)."], bRef.ch11a),
  bullet([{ text: "Bridge Builder: ", bold: true }, "Identifies shared environmental concern as primary bridge. Both sides want clean air and accountable government. Bridges to documented air quality issues where advocacy can make a measurable difference."], bRef.ch11a),
  bullet([{ text: "Auditor: ", bold: true }, "Checks that Bridge Builder did not create false equivalence. Confirms: the analysis acknowledges legitimate government secrecy concerns without validating the specific chemtrail claim. No false balance detected."], bRef.ch11a),

  heading2("Stage-Calibrated Dialogue Example"),

  body([{ text: "For an E4 (Conformist) user: ", bold: true }, "\"The Air Force itself published that weather paper, and even they called it speculation. The people you trust in your community, your doctor, your local pilot, if you asked them about the trails they see, what do you think they would say based on their training and experience?\""]),

  body([{ text: "For an E6 (Conscientious) user: ", bold: true }, "\"Let us look at this systematically. We have 77 atmospheric scientists surveyed, 76 found no evidence. We have documented weather modification (cloud seeding) and speculative military papers. What would a research design look like that could actually test the chemtrail hypothesis? What evidence would be sufficient to confirm or disconfirm it? And is your standard of evidence the same in both directions?\""]),
];

// ============================================================
// PART 5: ACADEMIC COLLABORATION
// ============================================================

const part5 = [
  ...partTitle("Part 5: Academic Collaboration"),

  // Chapter 11
  heading1("Chapter 11: Research Hypotheses"),

  heading2("Hypotheses H1-H7: From the Ego Development Researcher"),

  body(["The following hypotheses emerge from the ego development research tradition and would be tested in collaboration with ego development researchers:"]),

  numbered([{ text: "H1 (Conspiracy Mentality): ", bold: true }, "Stage-calibrated AI dialogue reduces conspiracy mentality (CMQ scores) more effectively than generic AI dialogue, with effect sizes exceeding Costello et al.'s 20% at 2-month follow-up."], nRef.hyp1),
  numbered([{ text: "H2 (Authoritarianism): ", bold: true }, "Reduction in RWA (Right-Wing Authoritarianism) scores correlates with ego development stage advancement from E4 to E5."], nRef.hyp1),
  numbered([{ text: "H3 (Antifeminism): ", bold: true }, "Anti-feminist attitudes, often bundled with conspiracy mentality, decrease as a secondary effect of de-polarization interventions, mediated by increased perspective-taking capacity."], nRef.hyp1),
  numbered([{ text: "H4 (Science Skepticism): ", bold: true }, "Science skepticism decreases through the three-question framework, specifically through Question 2's manipulation literacy component, which enables users to distinguish manufactured doubt from genuine scientific uncertainty."], nRef.hyp1),
  numbered([{ text: "H5 (Market-Radical Attitudes): ", bold: true }, "Market-radical attitudes correlate with ego development stage and are modifiable through perspective-taking interventions at the E4-E5 transition."], nRef.hyp1),
  numbered([{ text: "H6 (Political Violence): ", bold: true }, "Endorsement of political violence decreases with ego development advancement, particularly at the E4 to E5 transition where black-and-white thinking begins to soften."], nRef.hyp1),
  numbered([{ text: "H7 (More in Common Segments): ", bold: true }, "H&M's effectiveness varies by More in Common hidden tribe segment, with \"Passive Liberals\" and \"Politically Disengaged\" showing largest effects due to lower ideological rigidity."], nRef.hyp1),

  heading2("Hypotheses H8-H14: Formulated Through H&M Research"),

  numbered([{ text: "H8 (Stage-Calibrated Efficacy): ", bold: true }, "Stage-calibrated Socratic dialogue (adjusting approach based on assessed ego development level) produces larger effect sizes than generic Socratic dialogue across all measured outcomes."], nRef.hyp2),
  numbered([{ text: "H9 (Common Humanity Stage-Dependency): ", bold: true }, "The Common Humanity component (Question 3) has differential effectiveness by stage: minimal impact at E3-E4 (concrete operational), maximum impact at E5-E6 (emerging perspective-taking), attenuated at E7+ (already practicing perspective-taking independently)."], nRef.hyp2),
  numbered([{ text: "H10 (Scaffolding Prevents Dependency): ", bold: true }, "Progressive scaffolding with mandatory fading prevents the dependency effect documented by Bao et al. (2025). Users in the scaffolding condition maintain or improve independent discernment at 2-month follow-up, while users in the unrestricted access condition show the -15.3% decline."], nRef.hyp2),
  numbered([{ text: "H11 (Developmental Dip): ", bold: true }, "Users at the E4/E5 transition show a temporary dip in confidence and certainty (increased epistemic humility) before stabilizing at a higher level of discernment. This \"developmental dip\" is a feature, not a bug: it represents the discomfort of transitioning from simple certainty to complex understanding."], nRef.hyp2),
  numbered([{ text: "H12 (Micro-Developmental Shifts): ", bold: true }, "Eight or more sessions with H&M produce measurable micro-developmental shifts in WUSCT scores, even in the absence of full stage transitions. These shifts are detectable through item-level analysis rather than stage-level analysis."], nRef.hyp2),
  numbered([{ text: "H13 (Epistemic Humility): ", bold: true }, "Epistemic humility (calibrated confidence, appropriate uncertainty) increases as a stage-independent mechanism across all ego development levels. This effect is mediated by the three-question framework's requirement that users confront the limits of their own knowledge."], nRef.hyp2),
  numbered([{ text: "H14 (More in Common Segment Mapping): ", bold: true }, "More in Common's seven hidden tribe segments map onto ego development stages with predictable correspondence: \"Devoted Conservatives\" and \"Progressive Activists\" cluster at E4-E5 (high certainty, group-identified), while \"Exhausted Majority\" segments cluster at E5-E6 (emerging complexity, reduced group identification)."], nRef.hyp2),

  // Chapter 12
  heading1("Chapter 12: Experimental Design"),

  heading2("Four-Arm Randomized Controlled Trial"),

  numbered([{ text: "Arm 1 -- Waitlist Control: ", bold: true }, "No intervention. Completes all assessments at the same time points. Controls for maturation and testing effects."], nRef.ch12arms),
  numbered([{ text: "Arm 2 -- Generic AI Dialogue: ", bold: true }, "Standard AI-mediated fact-checking without stage calibration, without the three-question framework, and without scaffolding/fading. This controls for the general effect of interacting with AI about contested claims."], nRef.ch12arms),
  numbered([{ text: "Arm 3 -- Stage-Calibrated H&M: ", bold: true }, "Full three-question framework with ego development stage calibration, but without explicit scaffolding/fading. On-demand access. Tests the added value of the three-question framework and stage calibration."], nRef.ch12arms),
  numbered([{ text: "Arm 4 -- Stage-Calibrated H&M with Scaffolding/Fading: ", bold: true }, "Full three-question framework with stage calibration, progressive scaffolding withdrawal, and system-regulated access. The complete H&M design. Tests whether scaffolding prevents the dependency effect."], nRef.ch12arms),

  heading2("Sample and Power"),

  body([{ text: "Target N: ", bold: true }, "300-400 participants (75-100 per arm). Power analysis based on Costello et al.'s d=0.41 effect size suggests N=75 per arm provides 80% power at alpha=0.05 for detecting a medium effect."]),

  heading2("Measures"),

  body([{ text: "Primary outcome: ", bold: true }, "Conspiracy Mentality Questionnaire (CMQ; Bruder et al., 2013). Pre/post/follow-up."]),

  body([{ text: "Secondary outcomes:", bold: true }]),
  bullet("Right-Wing Authoritarianism scale (RWA; Altemeyer)", bRef.ch12),
  bullet("Washington University Sentence Completion Test (WUSCT; Loevinger & Le Xuan Hy, 1996)", bRef.ch12),
  bullet("Novel misinformation detection (unassisted): custom measure presenting previously unseen claims for independent evaluation without AI support", bRef.ch12),
  bullet("Calibrated confidence: accuracy-confidence correlation on factual claims", bRef.ch12),
  bullet("Perceived bridging: perceived common ground with outgroup members", bRef.ch12),

  heading2("Follow-Up"),

  body(["Assessments at baseline, post-intervention, 2 months, and 6 months. The 2-month follow-up matches Costello et al.'s design for direct comparison. The 6-month follow-up tests durability beyond existing literature."]),

  body([{ text: "Pre-registration: ", bold: true }, "Full protocol, hypotheses, and analysis plan pre-registered on the Open Science Framework (OSF) before data collection begins."]),

  // Chapter 13
  heading1("Chapter 13: Funding Pathways"),

  body(["Several funding mechanisms are appropriate for this research:"]),

  bullet([{ text: "DFG Priority Programme SPP 2573 (Re:DIS -- Resilience against Disinformation): ", bold: true }, "German Research Foundation programme specifically targeting disinformation research. Check next call cycle for timing."], bRef.ch13),
  bullet([{ text: "Volkswagen Foundation Collaborative Projects: ", bold: true }, "Supports interdisciplinary research collaborations between humanities/social sciences and computational approaches. Well-suited for H&M's combination of ego development theory and AI architecture."], bRef.ch13),
  bullet([{ text: "EU Horizon Europe Cluster 2 (Culture, Creativity, and Inclusive Society): ", bold: true }, "Funds research on democratic resilience, disinformation, and social cohesion. Large-scale funding appropriate for multi-site RCTs."], bRef.ch13),

  quoteBlock("Note: NSF funding for disinformation research is effectively blocked under the current US administration (2025-). European and German national funding sources are the primary pathway."),
];

// ============================================================
// PART 6: PRODUCT STRATEGY AND NEXT STEPS
// ============================================================

const part6 = [
  ...partTitle("Part 6: Product Strategy and Next Steps"),

  // Chapter 14
  heading1("Chapter 14: Deployment Path"),

  heading2("Phase 1: Open Source Local Tool (Current)"),

  body(["H&M is currently deployed as a local tool with CLI, API, and Docker support. Fully open-source, enabling transparency and community audit. Privacy-preserving by design: all analysis runs locally, no user data leaves the machine. This phase establishes the technical foundation and builds trust through transparency."]),

  heading2("Phase 2: Hosted SaaS"),

  body(["Hosted service with OpenRouter multi-model gateway, enabling access to the best available LLMs without vendor lock-in. EU-hosted infrastructure for GDPR compliance. Freemium model: free tier for individual use, paid tier for organizations and researchers."]),

  heading2("Phase 3: Institutional Licensing and API"),

  body(["API access for newsrooms, fact-checking organizations, and educational institutions. Academic partnership program for researchers. Institutional licensing for schools, universities, and civic organizations."]),

  heading2("Structural Model: Meedan/Check"),

  body(["Meedan's Check platform provides a structural model: open source + non-profit governance + EU hosting. This combination maximizes trust (open source for transparency, non-profit for aligned incentives, EU hosting for privacy protection). The Logically.ai collapse (venture-funded fact-checking startup that pivoted away from public benefit under investor pressure) serves as a cautionary tale for alternative models."]),

  body([{ text: "Privacy as competitive moat: ", bold: true }, "In a market where every competitor requires cloud processing and data collection, H&M's local-first, privacy-preserving architecture is a genuine differentiator. Users evaluating politically sensitive claims need assurance that their queries are not logged, profiled, or monetized."]),

  // Chapter 15
  heading1("Chapter 15: Corrected Timeline and Next Steps"),

  body([{ text: "Current date: ", bold: true }, "March 24, 2026"]),

  body([{ text: "PKM Summit: ", bold: true }, "COMPLETED (March 20-21, 2026). H&M concepts presented to personal knowledge management community."]),

  heading2("Immediate Priorities"),
  bullet("Implement dependency mitigation architecture (the four pillars from Chapter 4)", bRef.ch15),
  bullet("Build manufactured doubt detection module (28-tactic classifier, Phase 7)", bRef.ch15),
  bullet("Develop WUSCT integration for automated stage assessment", bRef.ch15),

  heading2("Near-Term (Q2 2026)"),
  bullet("Prepare academic collaboration proposal with ego development researcher", bRef.ch14),
  bullet("Draft pre-registration protocol for four-arm RCT", bRef.ch14),
  bullet("Build Common Humanity agent with concrete bridging logic", bRef.ch14),

  heading2("Mid-Term (Q3 2026)"),
  bullet("Submit to next DFG SPP 2573 / VW Foundation / Horizon Europe call", bRef.appA),
  bullet("Launch hosted SaaS beta with OpenRouter gateway", bRef.appA),
  bullet("Begin pilot study with academic partner", bRef.appA),

  heading2("Ongoing"),
  bullet("Community building and open-source contributor development", bRef.appB),
  bullet("Academic partnership cultivation", bRef.appB),
  bullet("Inoculation curriculum development for educational settings", bRef.appB),
];

// ============================================================
// APPENDICES
// ============================================================

const appendices = [
  ...partTitle("Appendices"),

  // Appendix A
  heading1("Appendix A: Research Foundation Scorecard"),

  new Table({
    columnWidths: [2000, 1800, 1800, 1800, 1960],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [
          headerCell("Pillar", 2000),
          headerCell("Replication", 1800),
          headerCell("Effect Size", 1800),
          headerCell("Cross-Cultural", 1800),
          headerCell("Overall", 1960),
        ],
      }),
      new TableRow({ children: [
        dataCell("1. Socratic AI Dialogue", 2000),
        dataCell([{ text: "Strong", color: GREEN }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "d=0.41 (robust)", color: GREEN }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "US-only (so far)", color: AMBER }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "STRONG", bold: true, color: GREEN }], 1960, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("2. Inoculation", 2000),
        dataCell([{ text: "Best replicated", color: GREEN }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "5-10% (moderate)", color: AMBER }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Multi-language", color: GREEN }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "MOD-STRONG", bold: true, color: GREEN }], 1960, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("3. Perception Gap", 2000),
        dataCell([{ text: "No replication", color: RED_ACCENT }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "2x overestimate", color: AMBER }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "US-only", color: RED_ACCENT }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "WEAK", bold: true, color: RED_ACCENT }], 1960, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("4. Moral Reframing", 2000),
        dataCell([{ text: "6+ failures", color: RED_ACCENT }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Null", color: RED_ACCENT }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Failed cross-cult.", color: RED_ACCENT }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "WEAK", bold: true, color: RED_ACCENT }], 1960, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("5. Narrative Complexity", 2000),
        dataCell([{ text: "Lab only", color: AMBER }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Unknown (no RCT)", color: AMBER }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Not tested", color: AMBER }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "WEAK-MOD", bold: true, color: AMBER }], 1960, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("6. Redirect Method", 2000),
        dataCell([{ text: "Engagement only", color: AMBER }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "224% (wrong metric)", color: AMBER }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "Limited", color: AMBER }], 1800, { align: AlignmentType.CENTER }),
        dataCell([{ text: "MODERATE", bold: true, color: AMBER }], 1960, { align: AlignmentType.CENTER }),
      ]}),
    ],
  }),

  spacer(200),

  // Appendix B
  heading1("Appendix B: 28-Tactic Manufactured Doubt Taxonomy"),

  body(["Complete taxonomy from Goldberg, Vandenberg et al. (2021). Industry columns: T=Tobacco, C=Chemicals, S=Sugar, A=Alcohol, M=Mining."]),

  spacer(40),

  // Tactic table - split into sections for readability
  new Table({
    columnWidths: [400, 2800, 600, 600, 600, 600, 600, 3160],
    rows: [
      new TableRow({
        tableHeader: true,
        children: [
          headerCell("#", 400), headerCell("Tactic", 2800),
          headerCell("T", 600), headerCell("C", 600), headerCell("S", 600),
          headerCell("A", 600), headerCell("M", 600), headerCell("Description", 3160),
        ],
      }),
      ...[
        ["1", "Attack Study Design", "Y", "Y", "Y", "Y", "Y", "Challenge methodology to discredit findings"],
        ["2", "Gain Reputable Support", "Y", "Y", "Y", "Y", "Y", "Recruit credentialed scientists, form institutes"],
        ["3", "Misrepresent Data", "Y", "Y", "Y", "Y", "Y", "Cherry-pick, conflate correlation/causation"],
        ["4", "Hyperbolic Language", "Y", "Y", "Y", "Y", "Y", "\"Junk science,\" \"alarmist,\" \"nanny state\""],
        ["5", "Influence Government", "Y", "Y", "Y", "Y", "Y", "Lobby regulators, delay policy action"],
        ["6", "Fund Alternative Research", "Y", "Y", "Y", "Y", "", "Commission studies designed to create doubt"],
        ["7", "Blame Other Causes", "Y", "Y", "Y", "Y", "", "Attribute harm to lifestyle, genetics, etc."],
        ["8", "Create Front Groups", "Y", "Y", "Y", "", "Y", "Astroturf organizations with neutral names"],
        ["9", "Exploit Scientific Illiteracy", "Y", "Y", "", "Y", "Y", "Leverage public misunderstanding of science"],
        ["10", "Suppress Research", "Y", "Y", "Y", "Y", "", "Prevent publication of unfavorable findings"],
        ["11", "Claim Dose Makes Poison", "Y", "Y", "", "Y", "", "Argue harm only at implausible exposures"],
        ["12", "Appeal to Freedom", "Y", "", "Y", "Y", "", "Frame regulation as threat to liberty"],
        ["13", "Attack Researchers", "Y", "Y", "Y", "", "", "Ad hominem attacks on scientists"],
        ["14", "Emphasize Economic Harm", "Y", "Y", "", "", "Y", "Regulation will destroy jobs/economy"],
        ["15", "Offer Voluntary Standards", "Y", "", "Y", "Y", "", "Self-regulate to prevent binding rules"],
        ["16", "Promote Safer Products", "Y", "", "", "Y", "", "\"Light\" cigarettes, \"moderate\" drinking"],
        ["17", "Deny Addiction/Harm", "Y", "", "", "Y", "", "Product is not addictive or harmful"],
        ["18", "Target Vulnerable Groups", "Y", "", "Y", "Y", "", "Market to youth, minorities, developing nations"],
        ["19", "Co-opt Public Health", "Y", "", "Y", "", "", "Partner with health organizations"],
        ["20", "Create Confusion", "Y", "Y", "", "", "", "Flood information space with contradictions"],
        ["21", "Stall with \"More Research\"", "Y", "Y", "", "", "Y", "Demand impossible certainty"],
        ["22", "Normalize Consumption", "", "", "Y", "Y", "", "\"Part of a balanced lifestyle\""],
        ["23", "Greenwash/Healthwash", "", "Y", "", "", "Y", "False environmental/health claims"],
        ["24", "Discredit Regulation", "", "Y", "", "", "Y", "Regulatory science is \"politicized\""],
        ["25", "Promote Harm Reduction", "", "", "", "Y", "", "Shift from abstinence to moderation"],
        ["26", "Control Expert Panels", "Y", "Y", "", "", "", "Stack advisory committees"],
        ["27", "Legal Intimidation", "Y", "Y", "", "", "Y", "SLAPP suits against critics"],
        ["28", "Capture Standards Bodies", "", "Y", "", "", "Y", "Influence exposure/safety standards"],
      ].map(([num, tactic, t, c, s, a, m, desc]) =>
        new TableRow({
          children: [
            dataCell(num, 400, { align: AlignmentType.CENTER }),
            dataCell([{ text: tactic, bold: num <= "5" }], 2800),
            dataCell(t, 600, { align: AlignmentType.CENTER, fill: t === "Y" ? "E8F8E8" : undefined }),
            dataCell(c, 600, { align: AlignmentType.CENTER, fill: c === "Y" ? "E8F8E8" : undefined }),
            dataCell(s, 600, { align: AlignmentType.CENTER, fill: s === "Y" ? "E8F8E8" : undefined }),
            dataCell(a, 600, { align: AlignmentType.CENTER, fill: a === "Y" ? "E8F8E8" : undefined }),
            dataCell(m, 600, { align: AlignmentType.CENTER, fill: m === "Y" ? "E8F8E8" : undefined }),
            dataCell(desc, 3160),
          ],
        })
      ),
    ],
  }),

  body([{ text: "Source: ", italics: true, color: MID }, "Goldberg, R. F. & Vandenberg, L. N. et al. (2021). Strategies and tactics used to undermine the credibility of science and scientists. Environmental Health, 20(1), 89. PMC7996119."]),

  spacer(200),

  // Appendix C
  heading1("Appendix C: Sources and Citations"),

  heading2("Chapter 1-2: Mission and Framework"),
  bullet("General background on polarization and conspiracy theories: multiple sources cited throughout.", bRef.dep1),

  heading2("Chapter 3: Research Pillars"),
  bullet("Costello, G., Pennycook, G. & Rand, D. G. (2024). Durably reducing conspiracy beliefs through dialogues with AI. Science, 385(6714), 1222-1227.", bRef.dep2),
  bullet("Bao, Z. et al. (2025). The Double-Edged Sword of AI Fact-Checking: Longitudinal Effects on Independent Discernment. arXiv:2510.01537.", bRef.dep2),
  bullet("Wharton Learning Lab (2025). Structured vs. On-Demand AI Tutoring: Implications for Learning Outcomes.", bRef.dep2),
  bullet("van der Linden, S. & Roozenbeek, J. (2022). Inoculation against manipulation techniques. Science Advances, 8(29).", bRef.dep2),
  bullet("PNAS Nexus (June 2025). Real-world transfer limitations of inoculation interventions.", bRef.dep2),
  bullet("More in Common (2019). The Perception Gap. https://perceptiongap.us/", bRef.dep2),
  bullet("Feinberg, M. & Willer, R. (2015). From Gulf to Bridge. Personality and Social Psychology Bulletin.", bRef.dep2),
  bullet("Replication failures: Arpan (2018), Berkebile-Weinberg (2024), Crawford (2025), Hundemer (2023), Kim (2023).", bRef.dep2),
  bullet("Coleman, P. T. (2011). The Five Percent. PublicAffairs.", bRef.dep2),
  bullet("Moonshot (2017). The Redirect Method. RAND Corporation evaluation.", bRef.dep2),

  heading2("Chapter 4: Dependency Paradox"),
  bullet("Bjork, R. A. & Bjork, E. L. (2011). Making things hard on yourself, but in a good way: Creating desirable difficulties. UCLA.", bRef.dep3),
  bullet("Vygotsky, L. S. (1978). Mind in Society: Development of Higher Psychological Processes. Harvard University Press.", bRef.dep3),
  bullet("Zone of No Development (2025). arXiv:2511.12822.", bRef.dep3),
  bullet("Halpern, D. F. (1998). Teaching critical thinking for transfer across domains. American Psychologist, 53(4), 449-455.", bRef.dep3),

  heading2("Chapter 5: Manufactured Doubt"),
  bullet("Goldberg, R. F. & Vandenberg, L. N. et al. (2021). Environmental Health, 20(1), 89. PMC7996119.", bRef.dep4),
  bullet("Supran, G. & Oreskes, N. (2017). Assessing ExxonMobil's climate change communications. Science, 355(6332), 1-10.", bRef.dep4),
  bullet("Coan, T. G. et al. (2021). Computer-assisted recognition of denial and skepticism. Nature Scientific Data.", bRef.dep4),

  heading2("Chapter 6: Common Humanity"),
  bullet("Collins, A., Brown, J. S. & Newman, S. E. (1989). Cognitive apprenticeship: Teaching the crafts of reading, writing, and mathematics. In L. B. Resnick (Ed.), Knowing, Learning, and Instruction.", bRef.dep5),
  bullet("Gaertner, S. L. & Dovidio, J. F. (2000). Reducing Intergroup Bias: The Common Ingroup Identity Model. Psychology Press.", bRef.dep5),
  bullet("Bohm, D. (1996). On Dialogue. Routledge.", bRef.dep5),

  heading2("Chapter 8: Ego Development"),
  bullet("Loevinger, J. & Le Xuan Hy (1996). Measuring Ego Development (2nd ed.). Mahwah, NJ: Erlbaum.", bRef.dep6),
  bullet("Decker, O. et al. (2002-present). Leipzig Authoritarianism Studies. University of Leipzig.", bRef.dep6),
  bullet("Bronlet, M. (2025). Automated scoring of ego development using large language models. Frontiers in Psychology.", bRef.dep6),

  heading2("Chapter 9-10: Chemtrails Test Case"),
  bullet("Shearer, C. et al. (2016). Quantifying expert consensus against the existence of a secret large-scale atmospheric spraying program. Environmental Research Letters, 11(8).", bRef.dep7),
  bullet("World Meteorological Organization. WMO Register of National Weather Modification Activities.", bRef.dep7),
  bullet("US Department of Defense (1996). Weather as a Force Multiplier: Owning the Weather in 2025. AF 2025 research paper.", bRef.dep7),

  heading2("Chapter 11-13: Academic Design"),
  bullet("Bruder, M. et al. (2013). Measuring Individual Differences in Generic Beliefs in Conspiracy Theories. Frontiers in Psychology.", bRef.ego1),
  bullet("Altemeyer, B. (1981, 2006). Right-Wing Authoritarianism / The Authoritarians.", bRef.ego1),

  heading2("Chapter 14-15: Product Strategy"),
  bullet("Meedan/Check platform. https://meedan.com/check", bRef.ego2),
  bullet("Logically.ai (case study in venture-funded fact-checking sustainability).", bRef.ego2),
];


// ============================================================
// ASSEMBLE DOCUMENT
// ============================================================

const doc = new Document({
  creator: "Jochen",
  title: "Huginn & Muninn: Research Foundation for AI-Mediated De-Polarization Through Common Humanity",
  description: "A Comprehensive Research Brief for Academic Collaboration",
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
    // Title page
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
            children: [new TextRun({ text: "Huginn & Muninn: Research Foundation", font: "Arial", size: 16, color: MID, italics: true })],
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
        ...part3,
        ...part4,
        ...part5,
        ...part6,
        ...appendices,
      ],
    },
  ],
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("C:/LocalAgent/Products/huginn_muninn/docs/Huginn-Muninn-Research-Foundation.docx", buffer);
  console.log("Document created: Huginn-Muninn-Research-Foundation.docx");
});
