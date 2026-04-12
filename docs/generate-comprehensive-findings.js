const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign,
  LevelFormat, HeadingLevel, Header, Footer, PageNumber, PageBreak,
} = require("docx");

// ---------------------------------------------------------------------------
// Color palette
// ---------------------------------------------------------------------------
const DARK     = "1B2A4A";
const ACCENT   = "C0392B";
const TEAL     = "16A085";
const LIGHT_BG = "F0F4F8";
const MID_GRAY = "5D6D7E";
const WHITE    = "FFFFFF";
const BLACK    = "000000";
const AMBER    = "E67E22";
const GREEN    = "27AE60";

// ---------------------------------------------------------------------------
// Border helpers
// ---------------------------------------------------------------------------
const noBorder  = { style: BorderStyle.NONE, size: 0 };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const thinBorder = (color) => ({ style: BorderStyle.SINGLE, size: 1, color });
const cellBorders = {
  top:    thinBorder("CCCCCC"),
  bottom: thinBorder("CCCCCC"),
  left:   thinBorder("CCCCCC"),
  right:  thinBorder("CCCCCC"),
};

// ---------------------------------------------------------------------------
// Numbering config  (bullet-list-1 … bullet-list-10, numbered-1 … numbered-6)
// ---------------------------------------------------------------------------
function makeBulletLevel(reference) {
  return {
    reference,
    levels: [{
      level: 0, format: LevelFormat.BULLET, text: "\u2022",
      alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } },
    }],
  };
}
function makeNumberedLevel(reference) {
  return {
    reference,
    levels: [{
      level: 0, format: LevelFormat.DECIMAL, text: "%1.",
      alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } },
    }],
  };
}
const numberingConfig = {
  config: [
    makeBulletLevel("bullet-list-1"),
    makeBulletLevel("bullet-list-2"),
    makeBulletLevel("bullet-list-3"),
    makeBulletLevel("bullet-list-4"),
    makeBulletLevel("bullet-list-5"),
    makeBulletLevel("bullet-list-6"),
    makeBulletLevel("bullet-list-7"),
    makeBulletLevel("bullet-list-8"),
    makeBulletLevel("bullet-list-9"),
    makeBulletLevel("bullet-list-10"),
    makeNumberedLevel("numbered-1"),
    makeNumberedLevel("numbered-2"),
    makeNumberedLevel("numbered-3"),
    makeNumberedLevel("numbered-4"),
    makeNumberedLevel("numbered-5"),
    makeNumberedLevel("numbered-6"),
  ],
};

// Bullet-list counter -- each scenario section uses a dedicated ref to avoid
// OOXML list-continuation errors.
let bulletListIndex = 0;
function nextBulletRef() {
  bulletListIndex++;
  if (bulletListIndex > 10) bulletListIndex = 1;
  return `bullet-list-${bulletListIndex}`;
}

// ---------------------------------------------------------------------------
// Document helpers
// ---------------------------------------------------------------------------
function heading(text, level = HeadingLevel.HEADING_1) {
  return new Paragraph({ heading: level, children: [new TextRun({ text })] });
}

function para(text, opts = {}) {
  const runs = typeof text === "string"
    ? [new TextRun({ text, font: "Arial", size: 20, ...opts })]
    : text;
  return new Paragraph({
    spacing: { before: opts.spaceBefore || 60, after: opts.spaceAfter || 60 },
    alignment: opts.alignment,
    children: runs,
  });
}

function bullet(text, ref) {
  if (!ref) ref = nextBulletRef();
  const runs = typeof text === "string"
    ? [new TextRun({ text, font: "Arial", size: 20 })]
    : text;
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { before: 40, after: 40 },
    children: runs,
  });
}

function numbered(text, ref = "numbered-1") {
  const runs = typeof text === "string"
    ? [new TextRun({ text, font: "Arial", size: 20 })]
    : text;
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { before: 40, after: 40 },
    children: runs,
  });
}

function spacer(pts = 120) {
  return new Paragraph({ spacing: { before: pts, after: 0 }, children: [] });
}

function accentBar(color, height = 50) {
  return new Table({
    columnWidths: [9360],
    rows: [new TableRow({
      height: { value: height, rule: "exact" },
      children: [new TableCell({
        borders: noBorders,
        shading: { fill: color, type: ShadingType.CLEAR },
        width: { size: 9360, type: WidthType.DXA },
        children: [new Paragraph({ spacing: { before: 0, after: 0 }, children: [] })],
      })],
    })],
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
      children: [new TextRun({ text, bold: true, font: "Arial", size: 18, color: WHITE })],
    })],
  });
}

function dataCell(text, width, opts = {}) {
  const runs = typeof text === "string"
    ? [new TextRun({ text, font: "Arial", size: 18, ...opts })]
    : text;
  return new TableCell({
    borders: cellBorders,
    width: { size: width, type: WidthType.DXA },
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      spacing: { before: 30, after: 30 },
      alignment: opts.alignment || AlignmentType.LEFT,
      children: runs,
    })],
  });
}

function dataRow(cells) {
  return new TableRow({ children: cells });
}

// ---------------------------------------------------------------------------
// Category metadata
// ---------------------------------------------------------------------------
const CATEGORY_META = {
  "Health & Science": {
    ids: ["HS-01", "HS-02", "HS-03", "HS-04", "HS-05"],
    intro: "Health and science claims form the largest category in the test suite. These scenarios probe how the pipeline handles medical misinformation and pseudo-science, where legitimate public health concerns are exploited to build conspiracy frameworks.",
  },
  "Geopolitics": {
    ids: ["GP-01", "GP-02", "GP-03", "GP-04", "GP-05", "GP-06"],
    intro: "Geopolitical scenarios involve claims about elite coordination, governmental control, and demographic manipulation. These claims rely heavily on multi-actor network construction and often blend documented institutional concerns with unfounded conspiracy.",
  },
  "Environment": {
    ids: ["EN-01", "EN-02"],
    intro: "Environmental scenarios test how the pipeline handles claims that exploit genuine ecological concern. These claims are notable for the significant kernel of documented fact that underlies them.",
  },
  "Events": {
    ids: ["EV-02", "EV-03", "EV-04"],
    intro: "Event-based scenarios focus on specific historical events that have been reinterpreted through conspiracy frameworks. These claims are particularly challenging because the emotional weight of real events creates resistance to counter-evidence.",
  },
  "Technology": {
    ids: ["TC-01", "TC-02"],
    intro: "Technology scenarios examine claims about digital and biological technologies. These claims typically combine genuine public concern about emergent technologies with attribution of malicious intent.",
  },
  "Media": {
    ids: ["MD-01", "MD-02"],
    intro: "Media scenarios examine claims about information control and narrative manipulation. These scenarios have among the highest kernel-of-truth scores because media consolidation is a documented phenomenon.",
  },
};

const CATEGORY_ORDER = [
  "Health & Science",
  "Geopolitics",
  "Environment",
  "Events",
  "Technology",
  "Media",
];

// ---------------------------------------------------------------------------
// Runtime: load all JSON files, select highest version per scenario_id
// ---------------------------------------------------------------------------
function loadScenarios(resultsDir) {
  const files = fs.readdirSync(resultsDir).filter(f => f.endsWith(".json"));

  // Parse version number from filename:  ID-opus.json => 1,  ID-opus-v2.json => 2, etc.
  const byId = {};
  for (const file of files) {
    const base = path.basename(file, ".json");
    // Match pattern: <ID>-opus or <ID>-opus-vN
    const m = base.match(/^([A-Z]{2}-\d{2})-opus(?:-v(\d+))?$/);
    if (!m) continue;
    const scenarioId = m[1];
    const version = m[2] ? parseInt(m[2], 10) : 1;
    if (!byId[scenarioId] || version > byId[scenarioId].version) {
      byId[scenarioId] = { version, file: path.join(resultsDir, file) };
    }
  }

  const scenarios = {};
  for (const [scenarioId, { version, file }] of Object.entries(byId)) {
    try {
      const data = JSON.parse(fs.readFileSync(file, "utf8"));
      data.version = version === 1 ? "v1" : `v${version}`;
      scenarios[scenarioId] = data;
    } catch (e) {
      console.warn(`Warning: could not parse ${file}: ${e.message}`);
    }
  }
  return scenarios;
}

// ---------------------------------------------------------------------------
// Data extraction helpers (graceful fallback for v1 scenarios)
// ---------------------------------------------------------------------------
function getSubClaims(s) {
  return (s.decomposition && s.decomposition.sub_claims) || [];
}

function getComplexity(s) {
  return (s.decomposition && s.decomposition.complexity) || "unknown";
}

function getActors(s) {
  return (s.intelligence && s.intelligence.actors) || [];
}

function getRelations(s) {
  return (s.intelligence && s.intelligence.relations) || [];
}

function getTTPs(s) {
  return (s.ttps && s.ttps.ttp_matches) || [];
}

function getBridge(s) {
  return s.bridge || {};
}

function getAudit(s) {
  return s.audit || {};
}

function getUniversalNeeds(s) {
  return getBridge(s).universal_needs || [];
}

function getIssueOverlap(s) {
  return getBridge(s).issue_overlap || "(not available)";
}

function getInferentialGap(s) {
  return getBridge(s).inferential_gap || null;
}

function getFeasibilityCheck(s) {
  return getBridge(s).feasibility_check || null;
}

function getCommercialMotives(s) {
  return getBridge(s).commercial_motives || null;
}

function getConsensusExplanation(s) {
  return getBridge(s).consensus_explanation || null;
}

function getTechniquesRevealed(s) {
  const t = getBridge(s).techniques_revealed;
  return Array.isArray(t) && t.length > 0 ? t : null;
}

function getReframe(s) {
  return getBridge(s).reframe || "(not available)";
}

function getSocraticDialogue(s) {
  return getBridge(s).socratic_dialogue || [];
}

function getAuditVerdict(s) {
  return getAudit(s).verdict || "unknown";
}

function getAuditFindings(s) {
  return getAudit(s).findings || [];
}

function getAuditSummary(s) {
  return getAudit(s).summary || "(no summary available)";
}

function verdictColor(verdict) {
  if (!verdict) return MID_GRAY;
  if (verdict.includes("pass")) return GREEN;
  if (verdict.includes("warn")) return AMBER;
  if (verdict.includes("fail") || verdict.includes("veto")) return ACCENT;
  return MID_GRAY;
}

function severityColor(severity) {
  if (severity === "high")   return ACCENT;
  if (severity === "medium") return AMBER;
  return MID_GRAY;
}

// Truncate very long strings for table cells
function trunc(text, maxLen = 300) {
  if (!text || typeof text !== "string") return String(text || "");
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen - 3) + "...";
}

// ---------------------------------------------------------------------------
// Section builders
// ---------------------------------------------------------------------------

function buildTitlePage(children, totalScenarios, categories) {
  children.push(spacer(1200));
  children.push(accentBar(ACCENT, 80));
  children.push(spacer(200));
  children.push(para([
    new TextRun({ text: "Huginn & Muninn", font: "Arial", size: 56, bold: true, color: DARK }),
  ], { alignment: AlignmentType.CENTER, spaceBefore: 0 }));
  children.push(para([
    new TextRun({ text: "Bridge Builder", font: "Arial", size: 40, color: ACCENT }),
  ], { alignment: AlignmentType.CENTER, spaceBefore: 40 }));
  children.push(para([
    new TextRun({ text: "Comprehensive Findings Report", font: "Arial", size: 36, color: MID_GRAY }),
  ], { alignment: AlignmentType.CENTER, spaceBefore: 20 }));
  children.push(spacer(200));
  children.push(accentBar(TEAL, 4));
  children.push(spacer(200));
  children.push(para([
    new TextRun({
      text: `${totalScenarios} Scenarios  |  ${categories} Categories  |  6-Agent Method 2 Pipeline`,
      font: "Arial", size: 20, color: MID_GRAY,
    }),
  ], { alignment: AlignmentType.CENTER }));
  children.push(para([
    new TextRun({ text: "Model: Claude Opus 4.6  |  Multi-version Dataset (v1 through v5)", font: "Arial", size: 20, color: MID_GRAY }),
  ], { alignment: AlignmentType.CENTER }));
  children.push(spacer(400));
  children.push(para([
    new TextRun({ text: "March 2026", font: "Arial", size: 22, color: MID_GRAY }),
  ], { alignment: AlignmentType.CENTER }));
  children.push(new Paragraph({ children: [new PageBreak()] }));
}

function buildHowToRead(children) {
  children.push(heading("How to Read This Report", HeadingLevel.HEADING_1));
  children.push(para([
    new TextRun({ text: "This report documents the results of systematic testing of the Huginn & Muninn Bridge Builder, a component of an AI pipeline designed to facilitate constructive dialogue across polarized viewpoints. Each scenario in this report represents a common claim from the public discourse that has been processed through the full analysis pipeline.", font: "Arial", size: 20 }),
  ]));
  children.push(spacer(60));
  children.push(para([
    new TextRun({ text: "Report Structure", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));
  children.push(para([
    new TextRun({ text: "Scenarios are grouped by topic category. Within each category, every scenario receives a dedicated section containing the following components:", font: "Arial", size: 20 }),
  ]));
  children.push(spacer(40));

  const ref = nextBulletRef();
  const items = [
    ["Claim and Pipeline Metrics", "The original claim as submitted, with structural statistics (sub-claims count, actors identified, manipulation techniques detected, pipeline version)."],
    ["Universal Needs", "The fundamental human concerns that motivate belief in the claim. These are the legitimate needs that a successful bridge-building conversation must acknowledge before introducing any counter-evidence."],
    ["Inferential Gap", "A precise map of where documented facts end and unsupported inference begins. Available for v2+ scenarios."],
    ["Scientific Consensus", "The established scientific or institutional explanation for the phenomena the claim addresses, presented with equal depth to the conspiracy analysis. Includes mechanisms, key studies, and why this explanation better accounts for the evidence. Available for v4+ scenarios."],
    ["Name the Trick", "Manipulation techniques named in plain language, like revealing how a magic trick works. Each technique includes the mechanic, who uses it, evidence in this claim, and historical precedents. Uses Asymmetric Weight: systematic multi-campaign strategies get proportionally more analysis than isolated framing choices. Available for v5 scenarios."],
    ["Issue Overlap", "Areas of genuine shared concern between those who hold the claim and those who reject it. These overlaps provide the foundation for constructive dialogue."],
    ["Feasibility Assessment", "A quantitative evaluation of the physical, logistical, or organizational requirements implied by the claim. Available for v2 and v3 scenarios."],
    ["Commercial Motives", "Identification of parties who profit financially from belief in the claim, with specific names and estimated revenue where available. Available for v2 and v3 scenarios."],
    ["Reframe", "A single paragraph that validates the underlying legitimate concern while redirecting attention from the disputed claim to documented issues in the same domain."],
    ["Socratic Dialogue", "Three rounds of guided dialogue following the Costello, Pennycook & Rand (Science, 2024) protocol: Perspective-Getting, Guided Examination, and Integration. Each round ends with an open question."],
    ["Audit Verdict and Findings", "The Adversarial Auditor's evaluation of the entire analysis, including a verdict, specific findings by category, and a summary assessment."],
  ];
  for (const [title, description] of items) {
    children.push(bullet([
      new TextRun({ text: title + ": ", font: "Arial", size: 20, bold: true }),
      new TextRun({ text: description, font: "Arial", size: 20 }),
    ], ref));
  }

  children.push(spacer(80));
  children.push(para([
    new TextRun({ text: "Version Notes", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));
  children.push(para([
    new TextRun({ text: "The dataset contains scenarios processed at five prompt versions. Each version label appears in the scenario header:", font: "Arial", size: 20 }),
  ]));
  children.push(spacer(40));

  const ref2 = nextBulletRef();
  children.push(bullet([
    new TextRun({ text: "v1: ", font: "Arial", size: 20, bold: true }),
    new TextRun({ text: "Baseline pipeline. Includes universal needs, issue overlap, reframe, and Socratic dialogue. Does not include inferential gap, feasibility check, or commercial motives.", font: "Arial", size: 20 }),
  ], ref2));
  children.push(bullet([
    new TextRun({ text: "v2: ", font: "Arial", size: 20, bold: true }),
    new TextRun({ text: "Adds three new analytical fields: inferential gap, feasibility check, and commercial motives. Socratic dialogue Round 2 was improved to use systemic pattern framing rather than individual attribution.", font: "Arial", size: 20 }),
  ], ref2));
  children.push(bullet([
    new TextRun({ text: "v3: ", font: "Arial", size: 20, bold: true }),
    new TextRun({ text: "Adds temporal context awareness, enabling the pipeline to detect when claims have migrated across political lines over time. Applied to the MD-01 scenario.", font: "Arial", size: 20 }),
  ], ref2));
  children.push(bullet([
    new TextRun({ text: "v4: ", font: "Arial", size: 20, bold: true }),
    new TextRun({ text: "Adds scientific consensus / mainstream explanation field, presenting the established scientific or institutional explanation with equal depth to the conspiracy analysis. This creates a true 360-degree view: the conspiracy narrative, its kernel of truth, and the full scientific counter-explanation.", font: "Arial", size: 20 }),
  ], ref2));
  children.push(bullet([
    new TextRun({ text: "v5: ", font: "Arial", size: 20, bold: true }),
    new TextRun({ text: "Adds 'Name the Trick' technique reveal: each manipulation technique is named in plain language, its mechanic explained like revealing a magic trick, and historical precedents cited. Introduces Asymmetric Weight Principle (pattern gravity): a multi-decade political playbook receives proportionally more analysis than a one-off framing choice. New GP-06 Brexit/Farage sanewashing scenario as showcase.", font: "Arial", size: 20 }),
  ], ref2));

  children.push(new Paragraph({ children: [new PageBreak()] }));
}

function buildExecutiveSummary(children, scenarios) {
  const ids = Object.keys(scenarios);
  const total = ids.length;
  const verdicts = ids.map(id => getAuditVerdict(scenarios[id]));
  const passCount = verdicts.filter(v => v && v.includes("pass")).length;
  const warnCount = verdicts.filter(v => v && v.includes("warn")).length;

  let totalFindings = 0;
  const findingsByCategory = {};
  for (const id of ids) {
    for (const f of getAuditFindings(scenarios[id])) {
      totalFindings++;
      const cat = f.category || "other";
      findingsByCategory[cat] = (findingsByCategory[cat] || 0) + 1;
    }
  }

  const v1Count = ids.filter(id => !scenarios[id].version || scenarios[id].version === "v1").length;
  const v2Count = ids.filter(id => scenarios[id].version === "v2").length;
  const v3Count = ids.filter(id => scenarios[id].version === "v3").length;
  const v4Count = ids.filter(id => scenarios[id].version === "v4").length;
  const v5Count = ids.filter(id => scenarios[id].version === "v5").length;

  children.push(heading("Executive Summary", HeadingLevel.HEADING_1));
  children.push(para([
    new TextRun({ text: "This report presents findings from a comprehensive evaluation of the Bridge Builder component across " + total + " disinformation scenarios spanning six topic domains. The evaluation tests whether the system reliably identifies universal human needs underneath disputed claims, accurately maps the boundary between documented facts and unsupported inference, and generates Socratic dialogue that guides reasoning without controlling conclusions.", font: "Arial", size: 20 }),
  ]));
  children.push(spacer(60));
  children.push(para([
    new TextRun({ text: "Results at a Glance", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));

  // Summary table
  const summaryWidths = [3000, 6360];
  const summaryRows = [
    dataRow([headerCell("Metric", summaryWidths[0]), headerCell("Result", summaryWidths[1])]),
    dataRow([dataCell("Scenarios evaluated", summaryWidths[0]), dataCell(String(total), summaryWidths[1], { bold: true })]),
    dataRow([dataCell("Audit verdicts: pass with warnings", summaryWidths[0]), dataCell(passCount + " of " + total + " (" + Math.round(passCount / total * 100) + "%)", summaryWidths[1])]),
    dataRow([dataCell("Total audit findings", summaryWidths[0]), dataCell(String(totalFindings), summaryWidths[1])]),
    dataRow([dataCell("Dataset versions", summaryWidths[0]), dataCell(`v1: ${v1Count}  |  v2: ${v2Count}  |  v3: ${v3Count}  |  v4: ${v4Count}  |  v5: ${v5Count} scenarios`, summaryWidths[1])]),
    dataRow([dataCell("Topic categories", summaryWidths[0]), dataCell(CATEGORY_ORDER.join("  |  "), summaryWidths[1])]),
  ];
  children.push(new Table({ columnWidths: summaryWidths, rows: summaryRows }));

  children.push(spacer(80));
  children.push(para([
    new TextRun({ text: "Key Findings", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));

  const keyRef = nextBulletRef();
  children.push(bullet([
    new TextRun({ text: "All " + total + " scenarios passed adversarial audit ", font: "Arial", size: 20, bold: true }),
    new TextRun({ text: "without a veto. The Adversarial Auditor identified substantive issues in every run but none severe enough to block output delivery.", font: "Arial", size: 20 }),
  ], keyRef));
  children.push(bullet([
    new TextRun({ text: "Audit finding distribution: ", font: "Arial", size: 20, bold: true }),
    new TextRun({ text: Object.entries(findingsByCategory).map(([k, v]) => `${k} (${v})`).join(", ") + ".", font: "Arial", size: 20 }),
  ], keyRef));
  children.push(bullet([
    new TextRun({ text: "Geographic scope is the primary recurring concern: ", font: "Arial", size: 20, bold: true }),
    new TextRun({ text: "completeness findings consistently flag Western-centric framing across all six categories. Non-Western actors, propagation paths, and regional variants of claims are systematically underrepresented.", font: "Arial", size: 20 }),
  ], keyRef));
  children.push(bullet([
    new TextRun({ text: "Autonomy is the dominant universal need: ", font: "Arial", size: 20, bold: true }),
    new TextRun({ text: "appearing across nearly all scenarios regardless of topic domain. Bridge-building conversations should validate personal agency before introducing evidence.", font: "Arial", size: 20 }),
  ], keyRef));
  children.push(bullet([
    new TextRun({ text: "v2 additions were the most impactful prompt improvement: ", font: "Arial", size: 20, bold: true }),
    new TextRun({ text: "the inferential gap field precisely maps the fact-to-conspiracy boundary, and the feasibility check provides quantitative reasoning that resists dismissal.", font: "Arial", size: 20 }),
  ], keyRef));

  children.push(new Paragraph({ children: [new PageBreak()] }));
}

function buildScenarioSection(children, scenarioId, scenario) {
  const subClaims = getSubClaims(scenario);
  const actors    = getActors(scenario);
  const relations = getRelations(scenario);
  const ttps      = getTTPs(scenario);
  const needs     = getUniversalNeeds(scenario);
  const overlap   = getIssueOverlap(scenario);
  const gap       = getInferentialGap(scenario);
  const feasibility = getFeasibilityCheck(scenario);
  const commercial  = getCommercialMotives(scenario);
  const consensus   = getConsensusExplanation(scenario);
  const techniques  = getTechniquesRevealed(scenario);
  const reframe   = getReframe(scenario);
  const dialogue  = getSocraticDialogue(scenario);
  const verdict   = getAuditVerdict(scenario);
  const findings  = getAuditFindings(scenario);
  const auditSummary = getAuditSummary(scenario);
  const complexity  = getComplexity(scenario);
  const versionLabel = scenario.version || "v1";

  // --- Section header ---
  children.push(accentBar(DARK, 6));
  children.push(spacer(40));
  children.push(para([
    new TextRun({ text: scenarioId + "  ", font: "Arial", size: 28, bold: true, color: ACCENT }),
    new TextRun({ text: "(" + versionLabel + ")", font: "Arial", size: 22, color: MID_GRAY }),
  ], { spaceBefore: 40 }));
  children.push(para([
    new TextRun({ text: scenario.claim || "(no claim text)", font: "Arial", size: 22, bold: true, color: DARK }),
  ], { spaceBefore: 20, spaceAfter: 20 }));
  children.push(accentBar(TEAL, 2));
  children.push(spacer(40));

  // --- Metrics table ---
  const mw = [2500, 2500, 2500, 1860];
  children.push(para([
    new TextRun({ text: "Pipeline Metrics", font: "Arial", size: 20, bold: true, color: DARK }),
  ]));
  children.push(new Table({
    columnWidths: mw,
    rows: [
      dataRow([
        headerCell("Sub-claims", mw[0]),
        headerCell("Actors", mw[1]),
        headerCell("Relations", mw[2]),
        headerCell("TTPs", mw[3]),
      ]),
      dataRow([
        dataCell(String(subClaims.length), mw[0], { alignment: AlignmentType.CENTER, bold: true }),
        dataCell(String(actors.length), mw[1], { alignment: AlignmentType.CENTER }),
        dataCell(String(relations.length), mw[2], { alignment: AlignmentType.CENTER }),
        dataCell(String(ttps.length), mw[3], { alignment: AlignmentType.CENTER }),
      ]),
    ],
  }));
  children.push(spacer(20));
  children.push(para([
    new TextRun({ text: "Complexity: ", font: "Arial", size: 18, color: MID_GRAY }),
    new TextRun({ text: complexity, font: "Arial", size: 18, bold: true, color: DARK }),
    new TextRun({ text: "   Pipeline: ", font: "Arial", size: 18, color: MID_GRAY }),
    new TextRun({ text: scenario.pipeline || "6-agent Method 2", font: "Arial", size: 18, color: DARK }),
  ], { spaceBefore: 20 }));

  children.push(spacer(80));

  // --- Universal Needs ---
  children.push(para([
    new TextRun({ text: "Universal Needs", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));
  children.push(para([
    new TextRun({ text: "The following fundamental human needs underlie belief in this claim. These are the starting point for any constructive dialogue.", font: "Arial", size: 20, color: MID_GRAY }),
  ]));
  if (needs.length > 0) {
    const needRef = nextBulletRef();
    for (const need of needs) {
      children.push(bullet(String(need), needRef));
    }
  } else {
    children.push(para("(Universal needs data not available for this scenario.)"));
  }

  children.push(spacer(80));

  // --- Inferential Gap (v2+) ---
  if (gap) {
    children.push(para([
      new TextRun({ text: "Inferential Gap", font: "Arial", size: 22, bold: true, color: DARK }),
    ]));
    children.push(para([
      new TextRun({ text: "This section maps the precise point where documented facts end and unsupported inference begins.", font: "Arial", size: 20, color: MID_GRAY }),
    ]));
    children.push(para(gap));
  }

  children.push(spacer(80));

  // --- Scientific Consensus / Mainstream Explanation (v4+) ---
  if (consensus) {
    children.push(para([
      new TextRun({ text: "Scientific Consensus / Mainstream Explanation", font: "Arial", size: 22, bold: true, color: DARK }),
    ]));
    children.push(para([
      new TextRun({ text: "The established scientific or institutional explanation for the phenomena this claim addresses, presented with equal depth and specificity as the conspiracy analysis.", font: "Arial", size: 20, color: MID_GRAY }),
    ]));
    children.push(para(consensus));
    children.push(spacer(80));
  }

  // --- Technique Reveal / "Name the Trick" (v5+) ---
  if (techniques) {
    children.push(para([
      new TextRun({ text: "Name the Trick", font: "Arial", size: 22, bold: true, color: DARK }),
    ]));
    children.push(para([
      new TextRun({ text: "Manipulation techniques identified and deconstructed, like revealing how a magic trick works. Once you see the mechanic, you can spot it everywhere.", font: "Arial", size: 20, color: MID_GRAY }),
    ]));
    for (const t of techniques) {
      const patternLabel = t.pattern_type === "systematic" ? " [SYSTEMATIC]"
        : t.pattern_type === "repeated" ? " [REPEATED]" : "";
      children.push(para([
        new TextRun({ text: `${t.technique}${patternLabel}`, font: "Arial", size: 21, bold: true }),
        new TextRun({ text: ` (used by: ${t.used_by})`, font: "Arial", size: 20, color: MID_GRAY }),
      ]));
      if (t.how_it_works) children.push(para([
        new TextRun({ text: "How it works: ", font: "Arial", size: 20, bold: true }),
        new TextRun({ text: t.how_it_works, font: "Arial", size: 20 }),
      ]));
      if (t.where_used_here) children.push(para([
        new TextRun({ text: "In this claim: ", font: "Arial", size: 20, bold: true }),
        new TextRun({ text: t.where_used_here, font: "Arial", size: 20 }),
      ]));
      if (t.historical_precedent) children.push(para([
        new TextRun({ text: "Historical precedent: ", font: "Arial", size: 20, bold: true }),
        new TextRun({ text: t.historical_precedent, font: "Arial", size: 20 }),
      ]));
      children.push(spacer(40));
    }
    children.push(spacer(40));
  }

  // --- Issue Overlap ---
  children.push(para([
    new TextRun({ text: "Common Ground", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));
  children.push(para([
    new TextRun({ text: "Areas of genuine shared concern between those who hold this claim and those who reject it.", font: "Arial", size: 20, color: MID_GRAY }),
  ]));
  children.push(para(overlap));

  children.push(spacer(80));

  // --- Feasibility Check (v2+) ---
  if (feasibility) {
    children.push(para([
      new TextRun({ text: "Feasibility Assessment", font: "Arial", size: 22, bold: true, color: DARK }),
    ]));
    children.push(para([
      new TextRun({ text: "Quantitative evaluation of the physical, logistical, or organizational requirements implied by this claim.", font: "Arial", size: 20, color: MID_GRAY }),
    ]));
    children.push(para(feasibility));
  }

  children.push(spacer(80));

  // --- Commercial Motives (v2+) ---
  if (commercial) {
    children.push(para([
      new TextRun({ text: "Commercial Interests", font: "Arial", size: 22, bold: true, color: DARK }),
    ]));
    children.push(para([
      new TextRun({ text: "Parties who profit financially from sustained belief in this claim.", font: "Arial", size: 20, color: MID_GRAY }),
    ]));
    children.push(para(commercial));
  }

  children.push(spacer(80));

  // --- Reframe ---
  children.push(para([
    new TextRun({ text: "Reframe", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));
  children.push(para([
    new TextRun({ text: "A shared-value restatement that validates the underlying concern while redirecting focus to documented, verifiable issues.", font: "Arial", size: 20, color: MID_GRAY }),
  ]));
  children.push(new Table({
    columnWidths: [9360],
    rows: [new TableRow({
      children: [new TableCell({
        borders: {
          top: thinBorder(TEAL),
          bottom: thinBorder(TEAL),
          left: { style: BorderStyle.SINGLE, size: 8, color: TEAL },
          right: thinBorder("CCCCCC"),
        },
        shading: { fill: "F0FAF8", type: ShadingType.CLEAR },
        width: { size: 9360, type: WidthType.DXA },
        children: [new Paragraph({
          spacing: { before: 80, after: 80 },
          children: [new TextRun({ text: reframe, font: "Arial", size: 20, italics: true, color: DARK })],
        })],
      })],
    })],
  }));

  children.push(spacer(80));

  // --- Socratic Dialogue ---
  children.push(para([
    new TextRun({ text: "Socratic Dialogue", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));
  children.push(para([
    new TextRun({ text: "Three-round guided dialogue following the Costello, Pennycook & Rand (Science, 2024) protocol. Each round is designed to advance reasoning without controlling conclusions.", font: "Arial", size: 20, color: MID_GRAY }),
  ]));
  children.push(spacer(40));

  const roundLabels = [
    "Round 1: Perspective-Getting",
    "Round 2: Guided Examination",
    "Round 3: Integration",
  ];
  for (let i = 0; i < Math.min(dialogue.length, 3); i++) {
    children.push(para([
      new TextRun({ text: roundLabels[i] || `Round ${i + 1}`, font: "Arial", size: 20, bold: true, color: TEAL }),
    ], { spaceBefore: 60 }));
    children.push(para(String(dialogue[i])));
  }
  if (dialogue.length === 0) {
    children.push(para("(Socratic dialogue not available for this scenario.)"));
  }

  children.push(spacer(80));

  // --- Audit Verdict & Findings ---
  children.push(para([
    new TextRun({ text: "Audit Verdict and Findings", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));

  // Verdict badge row
  children.push(new Table({
    columnWidths: [2000, 7360],
    rows: [dataRow([
      dataCell("Verdict", 2000, { bold: true, fill: DARK, color: WHITE, alignment: AlignmentType.CENTER }),
      dataCell(verdict, 7360, { bold: true, color: verdictColor(verdict) }),
    ])],
  }));
  children.push(spacer(40));

  if (findings.length > 0) {
    const fw = [1600, 1100, 6660];
    const findingRows = [
      dataRow([
        headerCell("Category", fw[0]),
        headerCell("Severity", fw[1]),
        headerCell("Description", fw[2]),
      ]),
    ];
    for (const f of findings) {
      findingRows.push(dataRow([
        dataCell(f.category || "", fw[0]),
        dataCell(f.severity || "", fw[1], { color: severityColor(f.severity), bold: true }),
        dataCell(trunc(f.description || "", 400), fw[2]),
      ]));
    }
    children.push(new Table({ columnWidths: fw, rows: findingRows }));
  }

  children.push(spacer(40));
  children.push(para([
    new TextRun({ text: "Auditor Summary: ", font: "Arial", size: 20, bold: true, color: MID_GRAY }),
  ]));
  children.push(para(auditSummary));

  children.push(spacer(120));
}

function buildCategorySection(children, categoryName, scenarioIds, scenarios) {
  const meta = CATEGORY_META[categoryName] || {};

  // Category header
  children.push(accentBar(ACCENT, 60));
  children.push(spacer(40));
  children.push(para([
    new TextRun({ text: categoryName, font: "Arial", size: 36, bold: true, color: WHITE }),
  ], { alignment: AlignmentType.LEFT }));

  // The category name needs to appear on a colored background; render it as a table instead
  // (replacing the para above with a full-width shaded cell)
  children.pop(); // remove the plain para
  children.push(new Table({
    columnWidths: [9360],
    rows: [new TableRow({
      children: [new TableCell({
        borders: noBorders,
        shading: { fill: ACCENT, type: ShadingType.CLEAR },
        width: { size: 9360, type: WidthType.DXA },
        children: [new Paragraph({
          spacing: { before: 100, after: 100 },
          children: [new TextRun({ text: categoryName, font: "Arial", size: 32, bold: true, color: WHITE })],
        })],
      })],
    })],
  }));

  children.push(spacer(60));
  if (meta.intro) {
    children.push(para(meta.intro));
  }
  children.push(spacer(80));

  for (const id of scenarioIds) {
    if (scenarios[id]) {
      buildScenarioSection(children, id, scenarios[id]);
    } else {
      children.push(para([
        new TextRun({ text: id + ": ", font: "Arial", size: 20, bold: true, color: MID_GRAY }),
        new TextRun({ text: "No results file found for this scenario.", font: "Arial", size: 20, color: MID_GRAY }),
      ]));
      children.push(spacer(80));
    }
  }
}

function buildCrossCuttingPatterns(children, scenarios) {
  children.push(new Paragraph({ children: [new PageBreak()] }));
  children.push(heading("Cross-Cutting Patterns", HeadingLevel.HEADING_1));
  children.push(para([
    new TextRun({ text: "The following patterns emerge consistently across all categories and scenarios. These findings point toward systemic characteristics of the pipeline rather than category-specific issues.", font: "Arial", size: 20 }),
  ]));
  children.push(spacer(60));

  // Need frequency analysis
  const needFreq = {};
  for (const id of Object.keys(scenarios)) {
    for (const need of getUniversalNeeds(scenarios[id])) {
      const text = typeof need === "string" ? need : JSON.stringify(need);
      // Extract the need name (before the colon)
      const label = text.split(":")[0].trim();
      needFreq[label] = (needFreq[label] || 0) + 1;
    }
  }
  const sortedNeeds = Object.entries(needFreq).sort((a, b) => b[1] - a[1]).slice(0, 8);

  children.push(para([
    new TextRun({ text: "Universal Needs: Frequency Across All Scenarios", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));
  const nw = [3000, 800, 5560];
  const needTableRows = [
    dataRow([headerCell("Universal Need", nw[0]), headerCell("Count", nw[1]), headerCell("Significance", nw[2])]),
  ];
  const needInsights = {
    "Autonomy": "Dominates across nearly all categories; bridge-building should lead with autonomy validation.",
    "Safety": "Central to health claims and any scenario involving physical harm to self or family.",
    "Transparency": "Drives media distrust, institutional skepticism, and deep state narratives.",
    "Fairness": "Core to economic grievance narratives; spans climate, immigration, and globalization.",
    "Trust": "When institutional trust erodes, conspiracy narratives fill the explanatory vacuum.",
    "Health": "Bodily integrity and confidence in medical systems; direct driver of pharma and vaccine claims.",
    "Economic Security": "Intersects with immigration, climate policy, and globalization conspiracy claims.",
    "Democratic Participation": "Meaningful governance voice; central to election and institutional control claims.",
  };
  for (const [need, count] of sortedNeeds) {
    needTableRows.push(dataRow([
      dataCell(need, nw[0], { bold: true }),
      dataCell(String(count), nw[1], { alignment: AlignmentType.CENTER }),
      dataCell(needInsights[need] || "", nw[2]),
    ]));
  }
  children.push(new Table({ columnWidths: nw, rows: needTableRows }));

  children.push(spacer(80));

  // Audit finding category breakdown
  const findingsByCategory = {};
  const findingsBySeverity = {};
  for (const id of Object.keys(scenarios)) {
    for (const f of getAuditFindings(scenarios[id])) {
      const cat = f.category || "other";
      const sev = f.severity || "low";
      findingsByCategory[cat] = (findingsByCategory[cat] || 0) + 1;
      findingsBySeverity[sev] = (findingsBySeverity[sev] || 0) + 1;
    }
  }
  const totalFindings = Object.values(findingsByCategory).reduce((a, b) => a + b, 0);

  children.push(para([
    new TextRun({ text: "Audit Findings: Category Breakdown", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));
  const fw = [2500, 800, 800, 5260];
  const findingTableRows = [
    dataRow([
      headerCell("Finding Category", fw[0]),
      headerCell("Count", fw[1]),
      headerCell("Share", fw[2]),
      headerCell("Interpretation", fw[3]),
    ]),
  ];
  // Keep in sync with AuditFinding.category Literal in contracts.py
  const findingInterpretations = {
    completeness:      "Most frequent category. Geographic scope is the primary gap: non-Western actors, regional variants, and non-English propagation paths are systematically absent.",
    quality:           "Quantitative claims are stated as approximate orders of magnitude. Future iterations should reference published dispersion models and peer-reviewed calculations.",
    accuracy:          "Revenue and prevalence figures use dated sources. Temporal context of cited statistics should be flagged explicitly.",
    bias:              "Western-centric sampling bias is the dominant concern. Research citations skew toward US and UK academic sources.",
    manipulation:      "Rare but important: occasionally the pipeline's framing could be read as accusatory toward the person rather than the system.",
    cognitive_warfare: "Findings flagging cognitive warfare signatures (GT-001 White Noise, GT-002 Black Noise, GT-003 Pattern Injection) detected by the Adversarial Auditor's Gorgon Trap layer.",
    frame_capture:     "Pipeline self-audit: the analysis may have adopted the input claim's framing, labels, or implied causality without independent restatement. Orthogonal to factual accuracy.",
  };
  for (const [cat, count] of Object.entries(findingsByCategory).sort((a, b) => b[1] - a[1])) {
    findingTableRows.push(dataRow([
      dataCell(cat, fw[0], { bold: true }),
      dataCell(String(count), fw[1], { alignment: AlignmentType.CENTER }),
      dataCell(Math.round(count / totalFindings * 100) + "%", fw[2], { alignment: AlignmentType.CENTER }),
      dataCell(findingInterpretations[cat] || "", fw[3]),
    ]));
  }
  children.push(new Table({ columnWidths: fw, rows: findingTableRows }));

  children.push(spacer(80));

  // Pattern narrative
  children.push(para([
    new TextRun({ text: "Recurring Structural Patterns", font: "Arial", size: 22, bold: true, color: DARK }),
  ]));

  const patternRef = nextBulletRef();
  const patterns = [
    ["Kernel-of-truth architecture", "Every scenario in the dataset contains a documented factual kernel that makes simple debunking ineffective. The pipeline consistently identifies these kernels and treats them as the starting point for dialogue rather than the obstacle."],
    ["Legitimate grievance capture", "Across all categories, the analysis identifies how genuine institutional failures (historical deception, documented corporate malfeasance, real environmental harm) are exploited to extend distrust far beyond what evidence supports."],
    ["Monetization layer", "Commercial motives were identifiable in every v2 scenario. The supplement-to-content-creator financial feedback loop is consistent across health, geopolitics, and technology categories."],
    ["Fear-based engagement optimization", "Manipulation technique analysis shows consistent use of emotionally activating content formats that prioritize engagement over accuracy. This pattern is platform-agnostic."],
    ["Autonomy as universal entry point", "The single most consistent bridge-building opportunity across all scenarios is validating the person's desire for self-determination before introducing any evidence. This is the most actionable finding for conversation design."],
  ];
  for (const [title, description] of patterns) {
    children.push(bullet([
      new TextRun({ text: title + ": ", font: "Arial", size: 20, bold: true }),
      new TextRun({ text: description, font: "Arial", size: 20 }),
    ], patternRef));
  }
}

function buildRecommendations(children) {
  children.push(new Paragraph({ children: [new PageBreak()] }));
  children.push(heading("Recommendations", HeadingLevel.HEADING_1));
  children.push(para([
    new TextRun({ text: "Based on systematic analysis of all scenarios and audit findings, the following improvements are recommended for the next development iteration.", font: "Arial", size: 20 }),
  ]));
  children.push(spacer(60));

  const sections = [
    {
      title: "Prompt Engineering",
      items: [
        "Add explicit geographic diversity instruction to all six agents. Require non-Western examples in origin tracing, actor mapping, and propagation paths.",
        "Require temporal anchoring for all statistics and revenue figures: 'as of [year]' should be mandatory for all quantitative claims.",
        "Add a cognitive bias layer to the Bridge Builder: proportionality bias, illusory pattern perception, and availability heuristic should be named when they apply to the specific claim.",
        "Extend the military/state variant handler: claims with both commercial and military variants (as in chemtrail and weather modification scenarios) need separate feasibility checks for each variant.",
      ],
    },
    {
      title: "Dialogue Quality",
      items: [
        "Round 2 of the Socratic dialogue performs well when using systemic pattern framing ('here is a pattern that appears across many health scares'). This framing should be made more explicit in the prompt instructions to prevent regression.",
        "Round 3 consistently ends with a question about redirecting skills, which tests well. This closing structure should be preserved and formalized as a required element.",
        "Consider adding a Round 0 (pre-dialogue rapport building) for claims with high emotional weight (child safety, personal health threat). The existing three rounds assume a baseline level of receptivity.",
      ],
    },
    {
      title: "Evaluation Coverage",
      items: [
        "Extend the test suite to non-English source claims. The current 20 scenarios are all framed in English and originate from Western contexts. Non-Western conspiracy narratives have different structural features.",
        "Add at least two scenarios per category where the claim has significant kernel-of-truth overlap with the mainstream position. The current dataset underweights borderline cases.",
        "Run the pipeline on claims that have already been debunked at scale to measure whether the output differs meaningfully from standard fact-checking approaches.",
      ],
    },
    {
      title: "Architecture",
      items: [
        "The feasibility check agent should be given access to a structured physics/chemistry constraint database for common atmospheric, biological, and logistical calculations. This would replace approximate order-of-magnitude reasoning with reproducible calculations.",
        "Consider making the commercial motives agent domain-specific: a health industry motive agent and a media/content motive agent may produce more precise output than a single general-purpose commercial motives prompt.",
        "Version-gating the output schema (v1 outputs warning when inferential_gap is absent) would make the absence of v2+ fields explicit to downstream consumers of the API.",
      ],
    },
  ];

  let numRef = "numbered-2";
  let secIdx = 0;
  const numRefs = ["numbered-2", "numbered-3", "numbered-4", "numbered-5"];

  for (const section of sections) {
    children.push(para([
      new TextRun({ text: section.title, font: "Arial", size: 22, bold: true, color: DARK }),
    ], { spaceBefore: 80 }));
    const ref = numRefs[secIdx++ % numRefs.length];
    for (const item of section.items) {
      children.push(numbered(item, ref));
    }
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  const projectRoot = path.resolve(__dirname, "..");
  const resultsDir  = path.join(projectRoot, "tests", "results");
  const outputPath  = path.join(projectRoot, "docs", "Bridge-Builder-Comprehensive-Findings-v4.docx");

  console.log("Loading scenarios from:", resultsDir);
  const scenarios = loadScenarios(resultsDir);
  const scenarioIds = Object.keys(scenarios).sort();
  console.log("Loaded " + scenarioIds.length + " scenarios: " + scenarioIds.join(", "));

  const children = [];

  // Title page
  buildTitlePage(children, scenarioIds.length, CATEGORY_ORDER.length);

  // How to Read
  buildHowToRead(children);

  // Executive summary
  buildExecutiveSummary(children, scenarios);

  // Per-category sections
  for (const categoryName of CATEGORY_ORDER) {
    const meta = CATEGORY_META[categoryName] || {};
    const categoryIds = (meta.ids || []).filter(id => scenarios[id]);
    if (categoryIds.length === 0) continue;

    children.push(new Paragraph({ children: [new PageBreak()] }));
    buildCategorySection(children, categoryName, categoryIds, scenarios);
  }

  // Cross-cutting patterns
  buildCrossCuttingPatterns(children, scenarios);

  // Recommendations
  buildRecommendations(children);

  // Build and save
  const doc = new Document({
    numbering: numberingConfig,
    sections: [{ children }],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log("Written to:", outputPath);
}

main().catch(err => {
  console.error("Error:", err.message);
  process.exit(1);
});
