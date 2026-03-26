const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign,
  LevelFormat, TabStopType, TabStopPosition,
} = require("docx");

// Brand colors
const DARK = "1B2A4A";    // Deep navy
const ACCENT = "C0392B";  // Warm red
const TEAL = "16A085";    // Teal green for differentiator
const LIGHT_BG = "F0F4F8"; // Light blue-gray background
const MID_GRAY = "5D6D7E";
const WHITE = "FFFFFF";
const BLACK = "000000";

const noBorder = { style: BorderStyle.NONE, size: 0 };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };
const thinBorder = (color) => ({ style: BorderStyle.SINGLE, size: 1, color });

// Helper: accent bar (colored table row used as a visual divider)
function accentBar(color, height = 60) {
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

// Helper: section heading with left accent bar
function sectionHeading(text) {
  return new Table({
    columnWidths: [120, 9240],
    rows: [new TableRow({
      children: [
        new TableCell({
          borders: noBorders,
          shading: { fill: ACCENT, type: ShadingType.CLEAR },
          width: { size: 120, type: WidthType.DXA },
          children: [new Paragraph({ spacing: { before: 0, after: 0 }, children: [] })],
        }),
        new TableCell({
          borders: noBorders,
          width: { size: 9240, type: WidthType.DXA },
          children: [new Paragraph({
            spacing: { before: 40, after: 40 },
            indent: { left: 120 },
            children: [new TextRun({ text, bold: true, font: "Arial", size: 24, color: DARK })],
          })],
        }),
      ],
    })],
  });
}

// Helper: icon card (3-column layout for key features)
function iconCard(icon, title, body) {
  return new TableCell({
    borders: noBorders,
    shading: { fill: LIGHT_BG, type: ShadingType.CLEAR },
    width: { size: 3120, type: WidthType.DXA },
    margins: { top: 100, bottom: 100, left: 140, right: 140 },
    children: [
      new Paragraph({
        spacing: { before: 0, after: 60 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: icon, font: "Segoe UI Emoji", size: 32 })],
      }),
      new Paragraph({
        spacing: { before: 0, after: 40 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: title, bold: true, font: "Arial", size: 20, color: DARK })],
      }),
      new Paragraph({
        spacing: { before: 0, after: 0 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: body, font: "Arial", size: 17, color: MID_GRAY })],
      }),
    ],
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 20, color: BLACK } } },
  },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 540, hanging: 260 } } },
      }],
    }],
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 720, right: 720, bottom: 720, left: 720 },
      },
    },
    children: [

      // === HEADER BAR ===
      new Table({
        columnWidths: [9360],
        rows: [new TableRow({
          children: [new TableCell({
            borders: noBorders,
            shading: { fill: DARK, type: ShadingType.CLEAR },
            width: { size: 9360, type: WidthType.DXA },
            margins: { top: 200, bottom: 200, left: 300, right: 300 },
            verticalAlign: VerticalAlign.CENTER,
            children: [
              new Paragraph({
                spacing: { before: 0, after: 60 },
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "HUGINN & MUNINN", bold: true, font: "Arial", size: 40, color: WHITE }),
                ],
              }),
              new Paragraph({
                spacing: { before: 0, after: 40 },
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "Disinformation Analysis with a Reconciliation Engine", font: "Arial", size: 22, color: "B0C4DE", italics: true }),
                ],
              }),
              accentBar(ACCENT, 4),
              new Paragraph({
                spacing: { before: 80, after: 0 },
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "Not just what is false  \u2014  but why we were divided, and what we still share.", font: "Arial", size: 18, color: "D0D8E8" }),
                ],
              }),
            ],
          })],
        })],
      }),

      new Paragraph({ spacing: { before: 160, after: 0 }, children: [] }),

      // === THE PROBLEM ===
      sectionHeading("THE PROBLEM"),
      new Paragraph({
        spacing: { before: 80, after: 60 },
        indent: { left: 240 },
        children: [
          new TextRun({ text: "Fact-checkers tell people they are wrong. People stop listening. ", font: "Arial", size: 19, color: MID_GRAY }),
          new TextRun({ text: "Disinformation wins not by convincing people of lies, but by making them believe they have nothing in common with the people on the other side.", font: "Arial", size: 19, color: DARK, bold: true }),
          new TextRun({ text: " Current tools detect falsehoods but never address the fracture underneath.", font: "Arial", size: 19, color: MID_GRAY }),
        ],
      }),

      new Paragraph({ spacing: { before: 120, after: 0 }, children: [] }),

      // === WHAT MAKES THIS DIFFERENT ===
      sectionHeading("WHAT MAKES THIS DIFFERENT"),
      new Paragraph({ spacing: { before: 60, after: 60 }, children: [] }),

      // Three cards row
      new Table({
        columnWidths: [3120, 3120, 3120],
        rows: [new TableRow({
          children: [
            iconCard("\uD83D\uDD0D", "What is true?", "Evidence-based verification with source tiering and confidence calibration."),
            iconCard("\u26A0\uFE0F", "How are you being played?", "Names the manipulation technique so you recognize it next time."),
            iconCard("\uD83E\uDD1D", "What do we share?", "Surfaces the common ground that divisive framing hides."),
          ],
        })],
      }),

      new Paragraph({ spacing: { before: 60, after: 40 }, indent: { left: 240 }, children: [
        new TextRun({ text: "Every other tool stops at column one. Huginn & Muninn delivers all three.", font: "Arial", size: 18, color: ACCENT, bold: true, italics: true }),
      ]}),

      new Paragraph({ spacing: { before: 100, after: 0 }, children: [] }),

      // === THE COMMON HUMANITY LAYER ===
      sectionHeading("THE COMMON HUMANITY LAYER"),
      new Paragraph({
        spacing: { before: 60, after: 40 },
        indent: { left: 240 },
        children: [
          new TextRun({ text: "The core innovation. ", font: "Arial", size: 19, color: DARK, bold: true }),
          new TextRun({ text: "Grounded in peer-reviewed research across six domains, every output includes a reconciliation layer that identifies shared human needs, reveals where opposing groups actually agree, and deconstructs how the same concern was split into opposing narratives.", font: "Arial", size: 19, color: MID_GRAY }),
        ],
      }),

      // Research foundation compact table
      new Table({
        columnWidths: [2800, 3280, 3280],
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ["Research Domain", "Key Evidence", "Application"].map(h =>
              new TableCell({
                borders: { top: noBorder, bottom: thinBorder(DARK), left: noBorder, right: noBorder },
                shading: { fill: DARK, type: ShadingType.CLEAR },
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({
                  spacing: { before: 40, after: 40 },
                  children: [new TextRun({ text: h, bold: true, font: "Arial", size: 16, color: WHITE })],
                })],
              })
            ),
          }),
          ...[
            ["Socratic AI Dialogue", "20% durable reduction in conspiracy beliefs (Science, 2024)", "3-round personalized dialogue"],
            ["Inoculation / Prebunking", "5.4M users, 5-10% improvement (Google/Jigsaw)", "Technique labeling in every output"],
            ["Perception Gap", "Americans overestimate opponent extremism by 2x", "Surface what the other side actually thinks"],
            ["Moral Reframing", "6 studies: arguments in audience's moral language persuade", "Bridge Builder adapts framing"],
          ].map(([domain, evidence, app], i) =>
            new TableRow({
              children: [domain, evidence, app].map(text =>
                new TableCell({
                  borders: { top: noBorder, bottom: thinBorder("DEE2E6"), left: noBorder, right: noBorder },
                  shading: { fill: i % 2 === 0 ? LIGHT_BG : WHITE, type: ShadingType.CLEAR },
                  width: { size: 3120, type: WidthType.DXA },
                  children: [new Paragraph({
                    spacing: { before: 30, after: 30 },
                    children: [new TextRun({ text, font: "Arial", size: 16, color: DARK })],
                  })],
                })
              ),
            })
          ),
        ],
      }),

      new Paragraph({ spacing: { before: 100, after: 0 }, children: [] }),

      // === HOW IT WORKS ===
      sectionHeading("HOW IT WORKS"),

      // Two-method layout
      new Table({
        columnWidths: [4680, 4680],
        rows: [new TableRow({
          children: [
            // Method 1
            new TableCell({
              borders: { top: noBorder, bottom: noBorder, left: noBorder, right: thinBorder("DEE2E6") },
              width: { size: 4680, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 100, right: 200 },
              children: [
                new Paragraph({ spacing: { before: 0, after: 40 }, children: [
                  new TextRun({ text: "Method 1 \u2014 Quick Check", bold: true, font: "Arial", size: 20, color: DARK }),
                ]}),
                new Paragraph({ spacing: { before: 0, after: 20 }, children: [
                  new TextRun({ text: "Fast, single-pass verification (2-5 sec). Runs fully local on consumer hardware. Every verdict includes a Common Ground section with shared concern, named manipulation technique, and a Socratic reflection question.", font: "Arial", size: 16, color: MID_GRAY }),
                ]}),
                new Paragraph({ spacing: { before: 0, after: 0 }, children: [
                  new TextRun({ text: "Cost: $0.02/query (cloud) or free (local)", font: "Arial", size: 15, color: TEAL, italics: true }),
                ]}),
              ],
            }),
            // Method 2
            new TableCell({
              borders: noBorders,
              width: { size: 4680, type: WidthType.DXA },
              margins: { top: 60, bottom: 60, left: 200, right: 100 },
              children: [
                new Paragraph({ spacing: { before: 0, after: 40 }, children: [
                  new TextRun({ text: "Method 2 \u2014 Deep Analysis", bold: true, font: "Arial", size: 20, color: DARK }),
                ]}),
                new Paragraph({ spacing: { before: 0, after: 20 }, children: [
                  new TextRun({ text: "Multi-agent pipeline: Decomposer, Tracer, Mapper, TTP Classifier, Bridge Builder, and Adversarial Auditor. Full narrative deconstruction with opt-in 3-round Socratic dialogue.", font: "Arial", size: 16, color: MID_GRAY }),
                ]}),
                new Paragraph({ spacing: { before: 0, after: 0 }, children: [
                  new TextRun({ text: "80% of claims resolve at Method 1 = 72% cost savings", font: "Arial", size: 15, color: TEAL, italics: true }),
                ]}),
              ],
            }),
          ],
        })],
      }),

      new Paragraph({ spacing: { before: 100, after: 0 }, children: [] }),

      // === ANTI-WEAPONIZATION ===
      sectionHeading("BUILT-IN SAFEGUARDS"),
      new Paragraph({ spacing: { before: 60, after: 20 }, indent: { left: 240 }, children: [
        new TextRun({ text: "The capability to analyze disinformation is itself a dual-use capability. Non-negotiable commitments:", font: "Arial", size: 18, color: MID_GRAY }),
      ]}),

      // Safeguards as compact bullets
      ...[
        ["Public narratives only", " \u2014 never profiles or surveils individuals."],
        ["No automated censorship", " \u2014 verdicts are analysis aids, not takedown signals."],
        ["Reconciliation, not suppression", " \u2014 finds shared ground, never manufactures false consensus."],
        ["Autonomy-preserving", " \u2014 presents evidence and asks questions; never lectures or labels."],
      ].map(([bold, rest]) =>
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          spacing: { before: 20, after: 20 },
          children: [
            new TextRun({ text: bold, bold: true, font: "Arial", size: 17, color: DARK }),
            new TextRun({ text: rest, font: "Arial", size: 17, color: MID_GRAY }),
          ],
        })
      ),

      new Paragraph({ spacing: { before: 100, after: 0 }, children: [] }),

      // === TALK PROPOSAL ===
      new Table({
        columnWidths: [9360],
        rows: [new TableRow({
          children: [new TableCell({
            borders: noBorders,
            shading: { fill: DARK, type: ShadingType.CLEAR },
            width: { size: 9360, type: WidthType.DXA },
            margins: { top: 160, bottom: 160, left: 300, right: 300 },
            children: [
              new Paragraph({
                spacing: { before: 0, after: 60 },
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "TALK PROPOSAL", bold: true, font: "Arial", size: 22, color: WHITE }),
                ],
              }),
              new Paragraph({
                spacing: { before: 0, after: 60 },
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "\"Beyond Fact-Checking: Building AI That Heals Division\"", font: "Arial", size: 22, color: "B0C4DE", italics: true }),
                ],
              }),
              new Paragraph({
                spacing: { before: 0, after: 40 },
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "A 30-minute session with live demo showing how Huginn & Muninn analyzes a real disinformation narrative \u2014 not just debunking it, but revealing the shared human concern underneath, naming the manipulation technique, and opening a Socratic dialogue that reduces polarization rather than deepening it.", font: "Arial", size: 17, color: "D0D8E8" }),
                ],
              }),
              accentBar(ACCENT, 3),
              new Paragraph({
                spacing: { before: 60, after: 0 },
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "Audiences walk away with: a new mental model for fighting disinformation, practical inoculation techniques they can use immediately, and evidence that most people share far more than they think.", font: "Arial", size: 17, color: "D0D8E8" }),
                ],
              }),
            ],
          })],
        })],
      }),

      new Paragraph({ spacing: { before: 120, after: 0 }, children: [] }),

      // === FOOTER ===
      new Table({
        columnWidths: [9360],
        rows: [new TableRow({
          children: [new TableCell({
            borders: { top: thinBorder("DEE2E6"), bottom: noBorder, left: noBorder, right: noBorder },
            width: { size: 9360, type: WidthType.DXA },
            children: [
              new Paragraph({
                spacing: { before: 80, after: 20 },
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "\"Not every disagreement is manufactured. Some are real. But the ones that are manufactured deserve to be seen.\"", font: "Arial", size: 17, italics: true, color: MID_GRAY }),
                ],
              }),
              new Paragraph({
                spacing: { before: 20, after: 0 },
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: "Open-source  \u2022  Local-first  \u2022  DISARM-compatible  \u2022  Anti-weaponization charter", font: "Arial", size: 16, color: TEAL }),
                ],
              }),
            ],
          })],
        })],
      }),

    ],
  }],
});

const outPath = "C:/LocalAgent/Products/huginn_muninn/docs/Huginn-Muninn-One-Pager.docx";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outPath, buffer);
  console.log("Created: " + outPath);
});
