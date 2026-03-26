const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, BorderStyle, WidthType, ShadingType,
  VerticalAlign, LevelFormat, HeadingLevel, PageBreak, PageNumber,
} = require("docx");

// Brand colors
const DARK = "1B2A4A";
const ACCENT = "C0392B";
const TEAL = "16A085";
const LIGHT_BG = "F0F4F8";
const MID_GRAY = "5D6D7E";
const WHITE = "FFFFFF";
const BLACK = "2C3E50";

const noBorder = { style: BorderStyle.NONE, size: 0 };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const thinBorder = (color) => ({ style: BorderStyle.SINGLE, size: 1, color });
const cellBorders = { top: thinBorder("DEE2E6"), bottom: thinBorder("DEE2E6"), left: thinBorder("DEE2E6"), right: thinBorder("DEE2E6") };

// --- Helpers ---

function spacer(before = 80, after = 0) {
  return new Paragraph({ spacing: { before, after }, children: [] });
}

function bodyText(texts, opts = {}) {
  const runs = texts.map(t => {
    if (typeof t === "string") return new TextRun({ text: t, font: "Arial", size: 22, color: BLACK });
    return new TextRun({ font: "Arial", size: 22, color: BLACK, ...t });
  });
  return new Paragraph({
    spacing: { before: opts.before || 80, after: opts.after || 80 },
    indent: opts.indent ? { left: opts.indent } : undefined,
    alignment: opts.align || AlignmentType.LEFT,
    children: runs,
  });
}

function quoteBlock(text) {
  return new Table({
    columnWidths: [120, 9240],
    rows: [new TableRow({
      children: [
        new TableCell({
          borders: noBorders,
          shading: { fill: TEAL, type: ShadingType.CLEAR },
          width: { size: 120, type: WidthType.DXA },
          children: [new Paragraph({ spacing: { before: 0, after: 0 }, children: [] })],
        }),
        new TableCell({
          borders: noBorders,
          shading: { fill: LIGHT_BG, type: ShadingType.CLEAR },
          width: { size: 9240, type: WidthType.DXA },
          margins: { top: 100, bottom: 100, left: 180, right: 180 },
          children: [new Paragraph({
            children: [new TextRun({ text, font: "Arial", size: 22, italics: true, color: DARK })],
          })],
        }),
      ],
    })],
  });
}

function slideRow(num, title, content, time, notes) {
  return new TableRow({
    children: [num, title, content, time, notes].map((text, i) =>
      new TableCell({
        borders: cellBorders,
        width: { size: [600, 1800, 3600, 800, 2560][i], type: WidthType.DXA },
        shading: { fill: WHITE, type: ShadingType.CLEAR },
        children: [new Paragraph({
          spacing: { before: 40, after: 40 },
          children: [new TextRun({ text, font: "Arial", size: 18, color: BLACK })],
        })],
      })
    ),
  });
}

function slideHeaderRow() {
  return new TableRow({
    tableHeader: true,
    children: ["#", "Slide Title", "Content", "Time", "Notes"].map((h, i) =>
      new TableCell({
        borders: cellBorders,
        shading: { fill: DARK, type: ShadingType.CLEAR },
        width: { size: [600, 1800, 3600, 800, 2560][i], type: WidthType.DXA },
        children: [new Paragraph({
          spacing: { before: 40, after: 40 },
          children: [new TextRun({ text: h, bold: true, font: "Arial", size: 18, color: WHITE })],
        })],
      })
    ),
  });
}

function researchRow(domain, finding, application, isAlt) {
  return new TableRow({
    children: [domain, finding, application].map((text, i) =>
      new TableCell({
        borders: cellBorders,
        width: { size: [2400, 3480, 3480][i], type: WidthType.DXA },
        shading: { fill: isAlt ? LIGHT_BG : WHITE, type: ShadingType.CLEAR },
        children: [new Paragraph({
          spacing: { before: 40, after: 40 },
          children: [new TextRun({ text, font: "Arial", size: 19, color: BLACK })],
        })],
      })
    ),
  });
}

function antiPatternRow(pattern, problem, isAlt) {
  return new TableRow({
    children: [pattern, problem].map((text, i) =>
      new TableCell({
        borders: cellBorders,
        width: { size: [3120, 6240][i], type: WidthType.DXA },
        shading: { fill: isAlt ? LIGHT_BG : WHITE, type: ShadingType.CLEAR },
        children: [new Paragraph({
          spacing: { before: 40, after: 40 },
          children: [new TextRun({ text, font: "Arial", size: 19, color: BLACK })],
        })],
      })
    ),
  });
}

// --- Document ---

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22, color: BLACK } } },
    paragraphStyles: [
      {
        id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: DARK, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER },
      },
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: DARK, font: "Arial" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: ACCENT, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: TEAL, font: "Arial" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "numbered-agents",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "numbered-slides",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
      {
        reference: "bullets-qa",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } },
        }],
      },
    ],
  },
  sections: [

    // ========================================
    // TITLE PAGE
    // ========================================
    {
      properties: {
        page: {
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      headers: {
        default: new Header({ children: [new Paragraph({ children: [] })] }),
      },
      footers: {
        default: new Footer({ children: [new Paragraph({ children: [] })] }),
      },
      children: [
        spacer(2400),

        // Title banner
        new Table({
          columnWidths: [9360],
          rows: [new TableRow({
            children: [new TableCell({
              borders: noBorders,
              shading: { fill: DARK, type: ShadingType.CLEAR },
              width: { size: 9360, type: WidthType.DXA },
              margins: { top: 400, bottom: 400, left: 400, right: 400 },
              verticalAlign: VerticalAlign.CENTER,
              children: [
                new Paragraph({
                  spacing: { before: 0, after: 120 },
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "HUGINN & MUNINN", bold: true, font: "Arial", size: 52, color: WHITE })],
                }),
                new Paragraph({
                  spacing: { before: 0, after: 80 },
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "The Fact-Checker That Finds Common Ground", font: "Arial", size: 28, color: "B0C4DE", italics: true })],
                }),
                // Accent bar
                new Table({
                  columnWidths: [9360],
                  rows: [new TableRow({
                    height: { value: 40, rule: "exact" },
                    children: [new TableCell({
                      borders: noBorders,
                      shading: { fill: ACCENT, type: ShadingType.CLEAR },
                      width: { size: 9360, type: WidthType.DXA },
                      children: [new Paragraph({ spacing: { before: 0, after: 0 }, children: [] })],
                    })],
                  })],
                }),
                new Paragraph({
                  spacing: { before: 120, after: 0 },
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "How AI Can Fight Disinformation by Revealing Shared Humanity", font: "Arial", size: 24, color: "D0D8E8" })],
                }),
              ],
            })],
          })],
        }),

        spacer(600),

        bodyText([
          { text: "Presentation Brief", bold: true, size: 28, color: DARK },
        ], { align: AlignmentType.CENTER }),
        bodyText([
          { text: "PKM Summit 2026  |  Utrecht  |  March 20\u201321, 2026", size: 24, color: MID_GRAY },
        ], { align: AlignmentType.CENTER }),
        spacer(200),
        bodyText([
          { text: "Jochen", size: 24, color: DARK },
        ], { align: AlignmentType.CENTER }),
      ],
    },

    // ========================================
    // PART 1: THE SUBSTANCE
    // ========================================
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
            children: [new TextRun({ text: "Huginn & Muninn \u2014 PKM Summit 2026 Brief", font: "Arial", size: 18, color: MID_GRAY, italics: true })],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "Page ", font: "Arial", size: 18, color: MID_GRAY }),
              new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 18, color: MID_GRAY }),
            ],
          })],
        }),
      },
      children: [

        // ----- PART 1 BANNER -----
        new Table({
          columnWidths: [9360],
          rows: [new TableRow({
            children: [new TableCell({
              borders: noBorders,
              shading: { fill: DARK, type: ShadingType.CLEAR },
              width: { size: 9360, type: WidthType.DXA },
              margins: { top: 160, bottom: 160, left: 300, right: 300 },
              children: [new Paragraph({
                spacing: { before: 0, after: 0 },
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: "PART 1: THE SUBSTANCE", bold: true, font: "Arial", size: 28, color: WHITE })],
              })],
            })],
          })],
        }),

        spacer(200),

        // ===========================
        // CHAPTER 1: THE PROBLEM
        // ===========================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Chapter 1: The Problem")],
        }),

        bodyText([
          "We are living through the golden age of disinformation. Not because lies are new, but because the infrastructure for spreading them has never been this efficient. Automated accounts, algorithmic amplification, and cross-platform virality have turned individual falsehoods into coordinated campaigns that reach millions within hours.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("The PKM Angle")],
        }),

        bodyText([
          "Knowledge workers build \"second brains\" \u2014 Obsidian vaults, Notion databases, Zettelkasten systems. These are powerful tools for collecting, connecting, and creating knowledge. But none of them have an immune system.",
        ]),

        bodyText([
          "When the information you are curating is manipulated, your PKM system does not protect you \u2014 it ",
          { text: "amplifies", italics: true },
          " the manipulation by giving it structure, permanence, and connections to your other thinking. The \"collect, connect, create\" cycle that PKM teaches becomes \"collect polluted data, connect it to clean data, create conclusions built on contaminated foundations.\"",
        ]),

        bodyText([
          "This is not a theoretical risk. Studies show that false information travels six times faster than accurate information on social media (Vosoughi et al., Science, 2018). By the time a correction reaches you, the false version has already been filed, tagged, linked, and integrated into your thinking.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("The Failure of Current Approaches")],
        }),

        bodyText([
          "Fact-checking is necessary but insufficient. Facebook/Meta's fact-checking labels reduce resharing by only 10\u201315%. More importantly: telling people they are wrong triggers ",
          { text: "psychological reactance", italics: true },
          " \u2014 the harder you push, the harder they push back. The goal should not be to win arguments but to build understanding.",
        ]),

        bodyText([
          "A crucial clarification: the \"backfire effect\" \u2014 the idea that corrections make beliefs ",
          { text: "stronger", italics: true },
          " \u2014 was once considered settled science but has largely failed replication (Wood & Porter, 2019 meta-analysis). Corrections ",
          { text: "do", italics: true },
          " work. The question is ",
          { text: "how", italics: true },
          ", not ",
          { text: "whether", italics: true },
          ". The research has moved from \"should we correct?\" to \"how do we correct without triggering defensiveness?\"",
        ]),

        quoteBlock("The goal is not to build a better lie detector. It is to build a tool that reminds us what we share \u2014 because most of the time, it is more than we think."),

        // ===========================
        // CHAPTER 2: THE INSIGHT
        // ===========================
        new Paragraph({ children: [new PageBreak()] }),

        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Chapter 2: The Insight")],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("The Research Breakthrough")],
        }),

        bodyText([
          "In September 2024, Costello, Pennycook, and Rand published a landmark study in ",
          { text: "Science", italics: true },
          ". They demonstrated that AI-driven Socratic dialogue produces a ",
          { text: "20% durable reduction", bold: true },
          " in conspiracy beliefs. Not temporary, not marginal \u2014 durable. Across thousands of participants. This is the largest measured effect of any single intervention on conspiracy beliefs ever published.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Why Socratic Works")],
        }),

        bodyText([
          "Instead of telling people they are wrong (which triggers reactance), you ask questions that let them discover inconsistencies themselves. The key: acknowledge the kernel of truth in their concern first. People become defensive when their core identity is threatened. Socratic dialogue sidesteps this by treating the person as a thinking partner, not an adversary.",
        ]),

        bodyText([
          "The inoculation approach (van der Linden, Cambridge; Google/Jigsaw) complements this: teaching people to recognize manipulation techniques is more durable than debunking individual claims. In a large-scale field study, 5.4 million YouTube users showed a 5\u201310% improvement in detecting manipulation after seeing prebunking videos. This is \"psychological vaccination\" \u2014 small doses of weakened misinformation that build cognitive immunity.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("The Perception Gap")],
        }),

        bodyText([
          "More in Common (2019) and Beyond Conflict found that Americans overestimate how extreme the other side is by a factor of 2x. But here is the surprising finding: people who consume the ",
          { text: "most", italics: true },
          " news have the ",
          { text: "most distorted", italics: true },
          " view of the other side \u2014 not the least. Knowledge alone does not fix this. ",
          { text: "The right kind", italics: true },
          " of knowledge does.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Moral Reframing")],
        }),

        bodyText([
          "Feinberg and Willer (Stanford/Toronto) demonstrated across six studies that arguments are more persuasive when presented in the audience's own moral language. Conservatives and progressives care about the same issues but through different moral foundations (Haidt's Moral Foundations Theory). An argument about environmental protection framed in terms of purity and sanctity resonates with conservatives. The same argument framed in terms of care and harm resonates with progressives. The underlying concern \u2014 a healthy planet \u2014 is identical.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("The Synthesis")],
        }),

        bodyText([
          { text: "What if you combined all of these \u2014 Socratic dialogue, inoculation, perception gap data, and moral reframing \u2014 into a single tool?", bold: true },
        ]),

        bodyText([
          "That is what Huginn & Muninn attempts. Not a better fact-checker, but a reconciliation engine that uses the best available research on how humans actually change their minds.",
        ]),

        // ===========================
        // CHAPTER 3: WHAT WE BUILT
        // ===========================
        new Paragraph({ children: [new PageBreak()] }),

        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Chapter 3: What We Built")],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("The Name")],
        }),

        bodyText([
          "Huginn and Muninn are Odin's two ravens in Norse mythology. Huginn means \"thought\" and Muninn means \"memory.\" Every day they fly across the world and return to whisper what they have seen. One scans for information; the other remembers and reflects. Together they report the truth. The tool carries this spirit: observe without judgment, remember without bias, report without agenda.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Two Methods of Analysis")],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("Method 1: Quick Check")],
        }),

        bodyText([
          "A single-prompt, two-pass verification system. Fast \u2014 approximately 10 seconds on consumer hardware. The first pass gathers evidence for and against the claim without rendering judgment. The second pass analyzes that evidence, produces a verdict with calibrated confidence, ",
          { text: "and", italics: true },
          " generates a Common Ground section.",
        ]),

        bodyText([
          "Every Quick Check output includes:",
        ]),

        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({ text: "Verdict", bold: true, font: "Arial", size: 22, color: BLACK }),
            new TextRun({ text: " \u2014 true, mostly true, mixed, mostly false, false, or insufficient evidence", font: "Arial", size: 22, color: BLACK }),
          ],
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({ text: "Calibrated confidence score", bold: true, font: "Arial", size: 22, color: BLACK }),
            new TextRun({ text: " (0.0 to 1.0) with explicit thresholds", font: "Arial", size: 22, color: BLACK }),
          ],
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({ text: "Evidence for and against", bold: true, font: "Arial", size: 22, color: BLACK }),
            new TextRun({ text: " with source URLs and source tier ratings", font: "Arial", size: 22, color: BLACK }),
          ],
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({ text: "Common Ground section", bold: true, font: "Arial", size: 22, color: BLACK }),
            new TextRun({ text: ": shared concern, named framing technique, technique explanation, and a Socratic reflection question", font: "Arial", size: 22, color: BLACK }),
          ],
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({ text: "Escalation score", bold: true, font: "Arial", size: 22, color: BLACK }),
            new TextRun({ text: " \u2014 auto-determines whether a deeper analysis is warranted", font: "Arial", size: 22, color: BLACK }),
          ],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("Method 2: Full Analysis (6-Agent Pipeline)")],
        }),

        bodyText([
          "For complex, multi-actor, or heavily polarized claims, Method 2 deploys a pipeline of six specialized AI agents. Each agent focuses on one aspect of the analysis, and the results are combined into a comprehensive report. The pipeline takes 30\u201390 seconds and produces a deep narrative deconstruction.",
        ]),

        bodyText([{ text: "The six agents:", bold: true }]),

        ...[
          ["Claim Decomposer", "Breaks complex claims into verifiable sub-claims, classifying each by type (factual, opinion, prediction) and verifiability."],
          ["Origin Tracer", "Tracks where the claim originated, how it has mutated as it spread, and identifies the earliest known source."],
          ["Network Mapper", "Maps the information flow: who is amplifying the claim, what are the relationships between actors, and what is the narrative structure."],
          ["TTP Classifier", "Identifies manipulation techniques using the DISARM framework (Tactics, Techniques, and Procedures used in information operations)."],
          ["Bridge Builder", "The core differentiator. Identifies universal human needs at stake, finds where opposing groups actually agree, deconstructs how the same concern was split into opposing narratives, and generates Socratic dialogue."],
          ["Adversarial Auditor", "Red-teams the entire analysis. Checks for confirmation bias, overreach, unfounded confidence, and potential misuse. Can veto the output."],
        ].map(([name, desc], i) =>
          new Paragraph({
            numbering: { reference: "numbered-agents", level: 0 },
            spacing: { before: 60, after: 60 },
            children: [
              new TextRun({ text: name + ": ", bold: true, font: "Arial", size: 22, color: DARK }),
              new TextRun({ text: desc, font: "Arial", size: 22, color: BLACK }),
            ],
          })
        ),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("The Common Humanity Layer")],
        }),

        bodyText([
          { text: "Three questions every output answers:", bold: true },
        ]),

        // Three questions as styled table
        new Table({
          columnWidths: [3120, 6240],
          margins: { top: 60, bottom: 60, left: 100, right: 100 },
          rows: [
            ["What is true?", "Evidence-based verification with source tiering and confidence calibration."],
            ["How are you being played?", "Names the manipulation technique so you recognize it next time."],
            ["What do we actually share?", "Surfaces the common ground that divisive framing hides."],
          ].map(([q, a], i) =>
            new TableRow({
              children: [
                new TableCell({
                  borders: cellBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: i % 2 === 0 ? LIGHT_BG : WHITE, type: ShadingType.CLEAR },
                  children: [new Paragraph({
                    spacing: { before: 60, after: 60 },
                    children: [new TextRun({ text: q, bold: true, font: "Arial", size: 22, color: DARK })],
                  })],
                }),
                new TableCell({
                  borders: cellBorders,
                  width: { size: 6240, type: WidthType.DXA },
                  shading: { fill: i % 2 === 0 ? LIGHT_BG : WHITE, type: ShadingType.CLEAR },
                  children: [new Paragraph({
                    spacing: { before: 60, after: 60 },
                    children: [new TextRun({ text: a, font: "Arial", size: 22, color: BLACK })],
                  })],
                }),
              ],
            })
          ),
        }),

        bodyText([
          "Every other fact-checking tool stops at column one. Huginn & Muninn delivers all three.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("The Three-Layer Depth Model")],
        }),

        bodyText([
          "The Bridge Builder agent operates at three levels of increasing depth:",
        ]),

        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({ text: "Universal Human Needs: ", bold: true, font: "Arial", size: 22, color: BLACK }),
            new TextRun({ text: "What do people on all sides of this issue genuinely care about? Safety, fairness, health, security, dignity.", font: "Arial", size: 22, color: BLACK }),
          ],
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({ text: "Issue-Specific Overlap: ", bold: true, font: "Arial", size: 22, color: BLACK }),
            new TextRun({ text: "Where do the specific positions of opposing groups actually converge? What do they agree on that the framing hides?", font: "Arial", size: 22, color: BLACK }),
          ],
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({ text: "Narrative Deconstruction: ", bold: true, font: "Arial", size: 22, color: BLACK }),
            new TextRun({ text: "How was a single shared concern split into two opposing narratives? What was the mechanism of division?", font: "Arial", size: 22, color: BLACK }),
          ],
        }),

        // ===========================
        // CHAPTER 4: DESIGN DECISIONS
        // ===========================
        new Paragraph({ children: [new PageBreak()] }),

        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Chapter 4: The Design Decisions")],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Why Local-First")],
        }),

        bodyText([
          "Your data never leaves your machine. No cloud dependency. No API keys required for base usage. Complete data sovereignty. If you are analyzing sensitive political claims, you should not have to trust a third party with that data. Huginn & Muninn runs entirely on your own hardware using open-source language models through Ollama.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Why Open Source")],
        }),

        bodyText([
          "Transparency is non-negotiable for a trust tool. The algorithms that decide what is \"true\" and what is \"manipulation\" must be inspectable. If you cannot read the code, you cannot trust the output. Open source is not a business model decision \u2014 it is an integrity requirement.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Why Socratic, Not Declarative")],
        }),

        bodyText([
          "The system never says \"this is false.\" It presents evidence and asks \"what do you make of this?\" Every output uses autonomy-supportive language only. No controlling phrases like \"experts agree,\" \"the truth is,\" or \"debunked.\" The research is clear: people change their minds when they feel their autonomy is respected, not when they feel lectured.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Why Common Ground Is Mandatory")],
        }),

        bodyText([
          "Every fact-check that does not address the underlying human concern is incomplete. The Bridge Builder runs on every analysis, not as an add-on. This is a deliberate architectural choice: the Common Ground section is not an optional feature you can disable. The research shows that addressing the emotional and moral dimensions of belief is essential for durable attitude change.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Why Inoculation Over Correction")],
        }),

        bodyText([
          "Teaching people to recognize scapegoating, false dichotomy, and emotional amplification is more durable than debunking individual claims. Name the technique, explain how it works, and let the user apply that knowledge going forward. A single inoculation against a manipulation technique protects against multiple future exposures.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("The Guardrails")],
        }),

        bodyText([
          "What the system refuses to do:",
        ]),

        ...[
          "Cannot manufacture false common ground. If positions are genuinely irreconcilable, it says so.",
          "Cannot be used as a persuasion engine. It reveals manipulation \u2014 it does not employ it.",
          "Acknowledges when moral positions are genuinely irreconcilable. Not every disagreement is manufactured.",
          "Profiles public narratives only \u2014 never surveils or profiles individuals.",
          "Verdicts are analysis aids, not automated censorship or takedown signals.",
        ].map(text =>
          new Paragraph({
            numbering: { reference: "bullets", level: 0 },
            spacing: { before: 40, after: 40 },
            children: [new TextRun({ text, font: "Arial", size: 22, color: BLACK })],
          })
        ),

        quoteBlock("Not every disagreement is manufactured. Some are real. But the ones that are manufactured deserve to be seen."),

        // ===========================
        // CHAPTER 5: WHAT WE'RE TRYING TO ACHIEVE
        // ===========================
        new Paragraph({ children: [new PageBreak()] }),

        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Chapter 5: What We Are Trying to Achieve")],
        }),

        bodyText([
          "Not a better fact-checker. A reconciliation engine.",
        ]),

        bodyText([
          "The vision: fight disinformation not by telling people they are wrong, but by helping them see what they share with the people they have been taught to fear.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Success Metrics from the Research")],
        }),

        ...[
          "15\u201320% reduction in conspiracy belief scores (Costello et al.)",
          "5\u201310% improvement in manipulation detection (Google/Jigsaw inoculation)",
          "Measurable perception gap reduction (More in Common framework)",
          "Less than 5% of users reporting feeling lectured or condescended to",
        ].map(text =>
          new Paragraph({
            numbering: { reference: "bullets", level: 0 },
            spacing: { before: 40, after: 40 },
            children: [new TextRun({ text, font: "Arial", size: 22, color: BLACK })],
          })
        ),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("The Broader Aspiration")],
        }),

        bodyText([
          "What if every news article, social media post, and viral claim could be accompanied not just by a fact-check, but by a reminder of what we share? Not to suppress disagreement \u2014 genuine disagreement is healthy \u2014 but to separate the real disagreements from the manufactured ones.",
        ]),

        bodyText([
          "The disinformation industry profits from division. The antidote is not more argument but more understanding. Huginn & Muninn is a small step in that direction: a tool that refuses to let you walk away from a fact-check feeling only anger at the other side. It always, without exception, shows you the common ground.",
        ]),

        // ===========================
        // CHAPTER 6: RESEARCH FOUNDATION
        // ===========================
        new Paragraph({ children: [new PageBreak()] }),

        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Chapter 6: Research Foundation")],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Six Research Domains")],
        }),

        bodyText([
          "Huginn & Muninn integrates findings from six distinct research domains. Each informs a specific component of the system.",
        ]),

        new Table({
          columnWidths: [2400, 3480, 3480],
          margins: { top: 60, bottom: 60, left: 100, right: 100 },
          rows: [
            new TableRow({
              tableHeader: true,
              children: ["Research Domain", "Key Finding", "How H&M Uses It"].map((h, i) =>
                new TableCell({
                  borders: cellBorders,
                  shading: { fill: DARK, type: ShadingType.CLEAR },
                  width: { size: [2400, 3480, 3480][i], type: WidthType.DXA },
                  children: [new Paragraph({
                    spacing: { before: 50, after: 50 },
                    children: [new TextRun({ text: h, bold: true, font: "Arial", size: 19, color: WHITE })],
                  })],
                })
              ),
            }),
            researchRow("Socratic AI Dialogue", "20% durable reduction in conspiracy beliefs (Costello, Pennycook & Rand, Science, 2024)", "3-round personalized Socratic dialogue in Bridge Builder output", false),
            researchRow("Inoculation / Prebunking", "5.4M users showed 5\u201310% improvement in detecting manipulation (van der Linden, Google/Jigsaw)", "Technique labeling in every output; names the manipulation method", true),
            researchRow("Perception Gap", "Americans overestimate opponent extremism by 2x; news consumers have most distorted view (More in Common, Beyond Conflict)", "Surfaces what the other side actually thinks; corrects exaggerated stereotypes", false),
            researchRow("Moral Reframing", "Arguments in audience's moral language are significantly more persuasive (Feinberg & Willer, 6 studies)", "Bridge Builder adapts framing to audience moral foundations", true),
            researchRow("Narrative Complexity", "False stories are structurally simpler than true ones; complexity correlates with accuracy (Tangherlini et al., 2020)", "Narrative deconstruction shows how oversimplification enables manipulation", false),
            researchRow("Redirect Method", "Counter-narrative ads reduce engagement with extremist content by 75% (Google/Jigsaw, Moonshot CVE)", "Reflective questions redirect attention to underlying concerns", true),
          ],
        }),

        spacer(200),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Anti-Patterns: What Does NOT Work")],
        }),

        bodyText([
          "The research is equally clear about approaches that backfire. Huginn & Muninn is deliberately designed to avoid these:",
        ]),

        new Table({
          columnWidths: [3120, 6240],
          margins: { top: 60, bottom: 60, left: 100, right: 100 },
          rows: [
            new TableRow({
              tableHeader: true,
              children: ["Anti-Pattern", "Why It Fails"].map((h, i) =>
                new TableCell({
                  borders: cellBorders,
                  shading: { fill: ACCENT, type: ShadingType.CLEAR },
                  width: { size: [3120, 6240][i], type: WidthType.DXA },
                  children: [new Paragraph({
                    spacing: { before: 50, after: 50 },
                    children: [new TextRun({ text: h, bold: true, font: "Arial", size: 19, color: WHITE })],
                  })],
                })
              ),
            }),
            antiPatternRow("Controlling language", "Phrases like \"experts agree\" or \"the truth is\" trigger psychological reactance. People push back harder.", false),
            antiPatternRow("Identity confrontation", "Attacking someone's group identity (\"conspiracy theorists believe...\") activates tribal defense. Belief hardens.", true),
            antiPatternRow("Generic counter-narratives", "One-size-fits-all rebuttals ignore the moral foundations that drive belief. They feel irrelevant.", false),
            antiPatternRow("Forced engagement", "Requiring people to read corrections or watch videos breeds resentment and reduces effectiveness.", true),
            antiPatternRow("Declarative correction", "Simply stating \"this is false\" without addressing the underlying concern leaves the emotional need unmet.", false),
          ],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("The Backfire Effect: A Myth Debunked")],
        }),

        bodyText([
          "For years, the \"backfire effect\" \u2014 the idea that corrections make false beliefs stronger \u2014 was treated as established fact. It influenced policy, journalism practice, and technology design. However, Wood and Porter's 2019 meta-analysis and subsequent replications have shown that this effect is far rarer than originally claimed. Corrections generally do work. The nuance is in the delivery: corrections that respect autonomy, acknowledge legitimate concerns, and present evidence without condescension are effective. Corrections delivered as authority pronouncements are not.",
        ]),

        bodyText([
          "Huginn & Muninn is designed around this updated understanding. It corrects, but it does so through questions, evidence presentation, and empathy \u2014 not declarations of truth.",
        ]),

        // ===========================
        // CHAPTER 7: OPEN QUESTIONS & FUTURE
        // ===========================
        new Paragraph({ children: [new PageBreak()] }),

        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Chapter 7: Open Questions and Future Directions")],
        }),

        bodyText([
          "Huginn & Muninn is v0.3.0 \u2014 functional and research-grounded, but far from complete. Several important challenges remain:",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Multilingual Support")],
        }),

        bodyText([
          "Moral foundations differ across cultures (Haidt's research is primarily Western). Socratic dialogue patterns vary by language and cultural context. The current system is English-focused. Extending it to other languages requires not just translation but cultural adaptation of the moral reframing and Socratic dialogue components.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("PKM Tool Integration")],
        }),

        bodyText([
          "The natural next step is integration with knowledge management tools. An Obsidian plugin that automatically runs incoming notes through a verification layer. A browser extension that adds a \"check this\" option to any text selection. Integration with note-taking workflows so that fact-checking becomes a seamless part of knowledge curation, not a separate step.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Community and Academic Partnerships")],
        }),

        bodyText([
          "The underlying research (Costello et al.) was conducted under controlled conditions. Our implementation applies these principles in a production tool, but it has not been independently validated. We are actively seeking academic partnerships to measure the tool's real-world effectiveness. The open-source model makes this possible: researchers can inspect, modify, and study the system.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Real-Time Source Verification")],
        }),

        bodyText([
          "The current system uses the language model's knowledge for evidence assessment. Adding real-time source verification \u2014 checking live URLs, verifying publication dates, cross-referencing fact-checking databases \u2014 would significantly improve accuracy and trustworthiness.",
        ]),

        // ========================================
        // PART 2: PRESENTATION GUIDE
        // ========================================
        new Paragraph({ children: [new PageBreak()] }),

        new Table({
          columnWidths: [9360],
          rows: [new TableRow({
            children: [new TableCell({
              borders: noBorders,
              shading: { fill: DARK, type: ShadingType.CLEAR },
              width: { size: 9360, type: WidthType.DXA },
              margins: { top: 160, bottom: 160, left: 300, right: 300 },
              children: [new Paragraph({
                spacing: { before: 0, after: 0 },
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: "PART 2: PRESENTATION GUIDE", bold: true, font: "Arial", size: 28, color: WHITE })],
              })],
            })],
          })],
        }),

        spacer(200),

        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Suggested Slide Deck")],
        }),

        bodyText([
          "20 slides for a 30-minute session. Each slide includes content guidance and speaker notes.",
        ]),

        new Table({
          columnWidths: [600, 1800, 3600, 800, 2560],
          margins: { top: 40, bottom: 40, left: 80, right: 80 },
          rows: [
            slideHeaderRow(),
            slideRow("1", "Title Slide", "\"The Fact-Checker That Finds Common Ground\"", "0:30", "Clean, no clutter."),
            slideRow("2", "The Golden Age of Disinformation", "Scale statistics. One powerful example the audience may have seen.", "1:30", "Hook: start with a real claim."),
            slideRow("3", "Your Second Brain Has No Immune System", "PKM collect-connect-create cycle + contamination risk.", "2:00", "This is the PKM-specific hook. Make it personal."),
            slideRow("4", "The Fact-Checking Paradox", "10\u201315% reshare reduction. Reactance theory.", "1:30", "\"Telling people they're wrong makes it worse.\""),
            slideRow("5", "Audience Interaction", "Poll: \"Have you ever changed someone's mind by proving them wrong?\"", "1:00", "Expected: almost nobody raises hand."),
            slideRow("6", "The Breakthrough", "Costello et al. \u2014 20% durable reduction via Socratic dialogue.", "2:00", "This is the \"aha\" moment. Let it land."),
            slideRow("7", "Why Socratic Works", "Acknowledge, question, don't declare.", "1:30", "Contrast with traditional fact-checking."),
            slideRow("8", "The Perception Gap", "2x overestimation. News consumers worst.", "1:30", "Surprising to most audiences."),
            slideRow("9", "Six Research Domains", "Quick overview table.", "1:00", "Reference slide. Don't dwell."),
            slideRow("10", "Three Questions", "What is true? How are you being played? What do we share?", "1:30", "Core framework. Let this land."),
            slideRow("11", "Introducing H&M", "Norse mythology. Odin's two ravens.", "1:00", "Brief origin story."),
            slideRow("12", "Method 1: Quick Check", "Demo or screenshot with Common Ground section visible.", "2:00", "Show real output."),
            slideRow("13", "Method 2: The Pipeline", "6-agent diagram.", "1:30", "Architecture for builders."),
            slideRow("14", "The Bridge Builder", "Common Humanity layer deep dive.", "2:00", "This is the differentiator."),
            slideRow("15", "Three-Layer Depth", "Universal Needs \u2192 Overlap \u2192 Narrative Deconstruction.", "1:30", "Visual diagram."),
            slideRow("16", "Design Decisions", "Local-first, Socratic, mandatory common ground.", "1:30", "Why these choices matter."),
            slideRow("17", "The Guardrails", "What the system refuses to do.", "1:00", "Builds trust."),
            slideRow("18", "Live Demo", "Run a current polarizing claim through the system.", "3:00", "Prepare backup output."),
            slideRow("19", "What's Next", "Open source, community, PKM integration.", "1:00", "Call to action."),
            slideRow("20", "Closing", "\"Not every disagreement is manufactured...\"", "1:00", "End with the quote. Then Q&A."),
          ],
        }),

        // ===========================
        // OPENING AND CLOSING
        // ===========================
        spacer(200),

        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Opening and Closing")],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Opening Hook")],
        }),

        quoteBlock("\"Show of hands \u2014 how many of you have an Obsidian vault, a Notion workspace, or some kind of second brain? [most hands go up] Great. Now \u2014 how many of you have ever checked whether the information you put INTO that system was manipulated before you connected it to everything else? [few hands] That is what I want to talk about today.\""),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Closing Line")],
        }),

        quoteBlock("\"The goal is not to build a better lie detector. It is to build a tool that reminds us what we share \u2014 because most of the time, it is more than we think.\""),

        // ===========================
        // Q&A PREPARATION
        // ===========================
        new Paragraph({ children: [new PageBreak()] }),

        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Q&A Preparation")],
        }),

        bodyText([
          "Likely questions and prepared responses:",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("\"Can this be weaponized?\"")],
        }),

        bodyText([
          "Yes, any analysis tool can be misused. That is why we have the Adversarial Auditor (which red-teams every output), anti-weaponization guardrails (the system cannot manufacture false common ground), and it is open source so anyone can inspect the logic. The system reveals manipulation \u2014 it does not employ it.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("\"Why local models instead of GPT-4 or Claude?\"")],
        }),

        bodyText([
          "Data sovereignty. If you are analyzing sensitive political claims, you should not trust a third party with that data. Additionally: no API costs, no rate limits, works offline. For users who want higher quality and are willing to use a cloud provider, the system also supports OpenAI-compatible APIs.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("\"Does this actually work?\"")],
        }),

        bodyText([
          "The underlying research does \u2014 Costello et al. in ",
          { text: "Science", italics: true },
          " is peer-reviewed and replicated. Our implementation applies these principles but has not been independently validated yet. That is part of why we are open-sourcing it \u2014 we want the research community to test and improve it.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("\"How does this relate to PKM?\"")],
        }),

        bodyText([
          "Your PKM system is only as good as the knowledge you put in it. Huginn & Muninn is the verification layer that PKM tools lack. Think of it as an immune system for your second brain. When you encounter a claim before filing it in your vault, you can run it through Huginn & Muninn to understand not just whether it is true, but how it was framed and what shared concern it touches.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("\"What about non-English content?\"")],
        }),

        bodyText([
          "Currently English-focused. The Socratic dialogue and moral reframing principles are culturally specific \u2014 they cannot simply be translated. Multilingual support is a key area for community contribution and academic collaboration.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("\"Isn't AI fact-checking just replacing one authority with another?\"")],
        }),

        bodyText([
          "Good question. That is exactly why the system never declares truth. It presents evidence, names techniques, and asks questions. You decide. The Socratic approach is designed to build your discernment, not create dependence on the tool. And because it is open source, you can verify exactly how it arrives at every output.",
        ]),

        // ===========================
        // TECHNICAL APPENDIX
        // ===========================
        new Paragraph({ children: [new PageBreak()] }),

        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("Technical Appendix")],
        }),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Architecture Overview")],
        }),

        bodyText([
          "Huginn & Muninn is a Python application (v0.3.0) built on FastAPI, using Pydantic for data validation and Ollama for local LLM inference. The web interface is a lightweight vanilla JavaScript frontend served as static files.",
        ]),

        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("Core Stack")],
        }),

        ...[
          "Python 3.12+ with FastAPI (REST API)",
          "Pydantic models for strict I/O contracts",
          "Ollama for local LLM inference (default: qwen3.5:9b)",
          "SQLite for caching, history, sessions, and feedback",
          "Docker support for one-command deployment",
          "Optional: OpenAI-compatible API support, Brave Search integration",
        ].map(text =>
          new Paragraph({
            numbering: { reference: "bullets", level: 0 },
            spacing: { before: 40, after: 40 },
            children: [new TextRun({ text, font: "Arial", size: 22, color: BLACK })],
          })
        ),

        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("API Endpoints")],
        }),

        new Table({
          columnWidths: [2800, 2200, 4360],
          margins: { top: 40, bottom: 40, left: 80, right: 80 },
          rows: [
            new TableRow({
              tableHeader: true,
              children: ["Endpoint", "Method", "Description"].map((h, i) =>
                new TableCell({
                  borders: cellBorders,
                  shading: { fill: DARK, type: ShadingType.CLEAR },
                  width: { size: [2800, 2200, 4360][i], type: WidthType.DXA },
                  children: [new Paragraph({
                    spacing: { before: 40, after: 40 },
                    children: [new TextRun({ text: h, bold: true, font: "Arial", size: 19, color: WHITE })],
                  })],
                })
              ),
            }),
            ...[
              ["/api/check", "POST", "Method 1: Quick check with common ground"],
              ["/api/analyze", "POST", "Method 2: Full 6-agent pipeline"],
              ["/api/check-and-escalate", "POST", "Auto-escalation from Method 1 to 2"],
              ["/api/jobs", "POST/GET", "Async job queue for batch processing"],
              ["/api/batch", "POST/GET", "Batch submission (up to 50 claims)"],
              ["/api/compare", "POST", "Cross-model comparison and reconciliation"],
              ["/api/sessions", "POST/GET", "Research session management"],
              ["/api/feedback", "POST", "User feedback collection"],
              ["/api/webhooks", "CRUD", "Webhook management for integrations"],
              ["/api/health", "GET", "LLM backend health check"],
            ].map(([endpoint, method, desc], i) =>
              new TableRow({
                children: [endpoint, method, desc].map((text, j) =>
                  new TableCell({
                    borders: cellBorders,
                    width: { size: [2800, 2200, 4360][j], type: WidthType.DXA },
                    shading: { fill: i % 2 === 0 ? LIGHT_BG : WHITE, type: ShadingType.CLEAR },
                    children: [new Paragraph({
                      spacing: { before: 30, after: 30 },
                      children: [new TextRun({ text, font: "Arial", size: 19, color: BLACK })],
                    })],
                  })
                ),
              })
            ),
          ],
        }),

        spacer(200),

        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("Quick Start")],
        }),

        // CLI quick start
        new Table({
          columnWidths: [9360],
          rows: [new TableRow({
            children: [new TableCell({
              borders: cellBorders,
              shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
              width: { size: 9360, type: WidthType.DXA },
              margins: { top: 100, bottom: 100, left: 180, right: 180 },
              children: [
                new Paragraph({ spacing: { before: 40, after: 40 }, children: [
                  new TextRun({ text: "# Prerequisites: Python 3.12+, Ollama with qwen3.5:9b", font: "Consolas", size: 20, color: MID_GRAY }),
                ]}),
                new Paragraph({ spacing: { before: 20, after: 20 }, children: [
                  new TextRun({ text: "pip install huginn-muninn", font: "Consolas", size: 20, color: BLACK }),
                ]}),
                new Paragraph({ spacing: { before: 20, after: 20 }, children: [
                  new TextRun({ text: "huginn check \"claim text here\"", font: "Consolas", size: 20, color: BLACK }),
                ]}),
                new Paragraph({ spacing: { before: 20, after: 20 }, children: [
                  new TextRun({ text: "huginn analyze \"claim text here\"", font: "Consolas", size: 20, color: BLACK }),
                ]}),
                new Paragraph({ spacing: { before: 20, after: 40 }, children: [
                  new TextRun({ text: "huginn analyze \"claim\" --auto-escalate", font: "Consolas", size: 20, color: BLACK }),
                ]}),
              ],
            })],
          })],
        }),

        spacer(200),

        // ===========================
        // FINAL CLOSING
        // ===========================
        new Table({
          columnWidths: [9360],
          rows: [new TableRow({
            children: [new TableCell({
              borders: noBorders,
              shading: { fill: DARK, type: ShadingType.CLEAR },
              width: { size: 9360, type: WidthType.DXA },
              margins: { top: 200, bottom: 200, left: 400, right: 400 },
              children: [
                new Paragraph({
                  spacing: { before: 0, after: 80 },
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "\"Not every disagreement is manufactured.", font: "Arial", size: 24, italics: true, color: "D0D8E8" })],
                }),
                new Paragraph({
                  spacing: { before: 0, after: 80 },
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "Some are real.", font: "Arial", size: 24, italics: true, color: "D0D8E8" })],
                }),
                new Paragraph({
                  spacing: { before: 0, after: 0 },
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "But the ones that are manufactured deserve to be seen.\"", font: "Arial", size: 24, italics: true, color: WHITE, bold: true })],
                }),
              ],
            })],
          })],
        }),

        spacer(100),

        bodyText([
          { text: "Huginn & Muninn v0.3.0  |  Open Source (MIT)  |  Local-First  |  DISARM-Compatible", size: 20, color: MID_GRAY },
        ], { align: AlignmentType.CENTER }),
      ],
    },
  ],
});

const outPath = "C:/LocalAgent/Products/huginn_muninn/docs/Huginn-Muninn-PKM-Summit-Brief.docx";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outPath, buffer);
  console.log("Created: " + outPath);
}).catch(err => {
  console.error("Error:", err);
  process.exit(1);
});
