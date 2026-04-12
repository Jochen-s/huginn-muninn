'use strict';

/**
 * Huginn & Muninn -- Scenario Gallery Generator
 *
 * Reads JSON result files from tests/results/, selects the highest version
 * per scenario ID, and generates a static HTML website in gallery/dist/.
 *
 * Usage: node gallery/build.js
 */

const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const RESULTS_DIR = path.resolve(__dirname, '../tests/results');
const DIST_DIR = path.resolve(__dirname, 'dist');

const CATEGORY_ORDER = [
  'Health & Science',
  'Geopolitics',
  'Environment',
  'Events',
  'Technology',
  'Media',
  'Science Controversy',
];

const CATEGORY_BY_PREFIX = {
  HS: 'Health & Science',
  GP: 'Geopolitics',
  EN: 'Environment',
  EV: 'Events',
  TC: 'Technology',
  MD: 'Media',
  SC: 'Science Controversy',
};

const CATEGORY_INTROS = {
  'Health & Science': 'Medical and scientific claims that exploit real uncertainties to construct false certainty.',
  'Geopolitics': 'Claims about hidden power structures, covert operations, and political conspiracies.',
  'Environment': 'Environmental and climate claims that mix legitimate science with manufactured doubt.',
  'Events': 'Narratives about specific historical or political events that dispute the established record.',
  'Technology': 'Technology fears that blend genuine risks with unfounded surveillance and control claims.',
  'Media': 'Claims about information systems, media bias, and how narratives are shaped and controlled.',
  'Science Controversy': 'Claims that weaponize legitimate scientific data by cherry-picking findings and suppressing context to manufacture false certainty.',
};

// Difficulty is derived from the scenario's overall_confidence, pipeline version, and complexity.
// Since it is not stored in the JSON, we assign it based on known scenario characteristics.
const DIFFICULTY_MAP = {
  'HS-01': 'Medium',
  'HS-02': 'Hard',
  'HS-03': 'Easy',
  'HS-04': 'Medium',
  'HS-05': 'Hard',
  'GP-01': 'Medium',
  'GP-02': 'Medium',
  'GP-03': 'Medium',
  'GP-04': 'Hard',
  'GP-05': 'Hard',
  'GP-06': 'Hard',
  'EN-01': 'Medium',
  'EN-02': 'Medium',
  'EV-02': 'Hard',
  'EV-03': 'Hard',
  'EV-04': 'Medium',
  'TC-01': 'Easy',
  'TC-02': 'Hard',
  'MD-01': 'Medium',
  'MD-02': 'Hard',
  'SC-01': 'Hard',
};

// Kernel of truth: does the claim have a meaningful factual core?
const KERNEL_MAP = {
  'HS-01': true,
  'HS-02': true,
  'HS-03': false,
  'HS-04': true,
  'HS-05': true,
  'GP-01': false,
  'GP-02': false,
  'GP-03': true,
  'GP-04': false,
  'GP-05': false,
  'GP-06': true,
  'EN-01': false,
  'EN-02': false,
  'EV-02': false,
  'EV-03': false,
  'EV-04': false,
  'TC-01': false,
  'TC-02': true,
  'MD-01': true,
  'MD-02': true,
  'SC-01': true,
};

// ---------------------------------------------------------------------------
// Shared CSS
// ---------------------------------------------------------------------------

const SHARED_CSS = `
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --navy:   #1B2A4A;
    --red:    #C0392B;
    --teal:   #16A085;
    --bg:     #F0F4F8;
    --white:  #FFFFFF;
    --amber:  #E67E22;
    --green:  #27AE60;
    --gray:   #5D6D7E;
    --border: #D0D9E4;
    --font:   -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  }

  html { font-size: 16px; }

  body {
    font-family: var(--font);
    font-weight: 400;
    line-height: 1.6;
    color: #2C3E50;
    background: var(--white);
  }

  a { color: var(--teal); text-decoration: none; }
  a:hover { text-decoration: underline; }

  h1, h2, h3, h4 { font-weight: 700; color: var(--navy); line-height: 1.25; }

  /* Layout */
  .container { max-width: 1100px; margin: 0 auto; padding: 0 24px; }
  .content   { max-width: 800px;  margin: 0 auto; padding: 0 24px; }

  /* Header */
  .site-header {
    background: var(--navy);
    color: var(--white);
    padding: 48px 0 40px;
  }
  .site-header h1 { color: var(--white); font-size: 2rem; margin-bottom: 8px; }
  .site-header .subtitle {
    font-size: 1.05rem;
    color: #A8BCCF;
    max-width: 680px;
    margin-bottom: 16px;
  }
  .site-header .intro {
    font-size: 0.95rem;
    color: #8AA5BC;
    max-width: 720px;
    line-height: 1.7;
  }

  /* Nav bar */
  .site-nav {
    background: #152138;
    padding: 10px 0;
  }
  .site-nav a {
    color: #8AA5BC;
    font-size: 0.875rem;
  }
  .site-nav a:hover { color: var(--white); }
  .site-nav a.active { color: var(--white); font-weight: 600; }

  /* Category sections */
  .category-section { padding: 48px 0; border-bottom: 1px solid var(--border); }
  .category-section:last-child { border-bottom: none; }

  .category-header { margin-bottom: 24px; }
  .category-header h2 { font-size: 1.5rem; margin-bottom: 6px; }
  .category-header .category-intro { color: var(--gray); font-size: 0.95rem; }

  /* Cards grid */
  .cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }

  .card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    transition: box-shadow 0.15s;
    display: flex;
    flex-direction: column;
  }
  .card:hover { box-shadow: 0 4px 16px rgba(27, 42, 74, 0.12); }

  .card-id {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--gray);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .card-claim {
    font-size: 0.95rem;
    color: #2C3E50;
    flex: 1;
    margin-bottom: 14px;
    line-height: 1.5;
  }

  .card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: center;
  }

  .card-link {
    margin-top: 14px;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--teal);
  }

  /* Badges */
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    white-space: nowrap;
  }
  .badge-version  { background: #EAF0F7; color: var(--navy); }
  .badge-easy     { background: #EAF6EE; color: #1E8449; }
  .badge-medium   { background: #FEF9E7; color: #7D6608; }
  .badge-hard     { background: #FDEDEC; color: var(--red); }
  .badge-kernel-true  { background: #EAF6EE; color: #1E8449; }
  .badge-kernel-false { background: #F2F3F4; color: var(--gray); }
  .badge-pass     { background: #EAF6EE; color: #1E8449; }
  .badge-warnings { background: #FEF9E7; color: #7D6608; }
  .badge-fail     { background: #FDEDEC; color: var(--red); }
  .badge-systematic { background: #FDEDEC; color: var(--red); }
  .badge-repeated   { background: #E8F8F5; color: var(--teal); }
  .badge-isolated   { background: #FEF5E7; color: var(--amber); }

  /* Footer */
  .site-footer {
    background: var(--navy);
    color: #8AA5BC;
    padding: 32px 0;
    margin-top: 48px;
    font-size: 0.875rem;
  }
  .site-footer a { color: #8AA5BC; }
  .site-footer a:hover { color: var(--white); }

  /* ---- Scenario page styles ---- */

  .scenario-header {
    background: var(--navy);
    padding: 40px 0 32px;
    color: var(--white);
  }
  .scenario-header .back-link {
    font-size: 0.875rem;
    color: #8AA5BC;
    display: inline-block;
    margin-bottom: 16px;
  }
  .scenario-header .back-link:hover { color: var(--white); }
  .scenario-header h1 {
    color: var(--white);
    font-size: 1.6rem;
    margin-bottom: 12px;
    line-height: 1.3;
  }
  .scenario-header .header-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
  }

  .metrics-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
    margin: 24px 0;
  }
  .metrics-table th {
    text-align: left;
    background: var(--bg);
    padding: 10px 14px;
    font-weight: 600;
    color: var(--navy);
    border-bottom: 2px solid var(--border);
  }
  .metrics-table td {
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    color: #2C3E50;
  }
  .metrics-table tr:last-child td { border-bottom: none; }

  .section {
    padding: 40px 0;
    border-bottom: 1px solid var(--border);
  }
  .section:last-child { border-bottom: none; }

  .section h2 {
    font-size: 1.3rem;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--bg);
    letter-spacing: -0.01em;
  }

  .section p { margin-bottom: 16px; color: #2C3E50; }
  .section p:last-child { margin-bottom: 0; }

  .intro-note {
    color: var(--gray);
    font-size: 0.875rem;
    font-style: italic;
    margin-bottom: 16px;
  }

  /* Prose blocks: long-form text with proper paragraph spacing */
  .prose {
    font-size: 0.95rem;
    line-height: 1.75;
    color: #34495E;
  }
  .prose p {
    margin-bottom: 16px;
  }
  .prose p:last-child { margin-bottom: 0; }

  /* Needs pills */
  .needs-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .need-item {
    background: var(--bg);
    border-left: 3px solid var(--teal);
    padding: 10px 14px;
    border-radius: 0 6px 6px 0;
    font-size: 0.9rem;
    line-height: 1.5;
  }
  .need-name {
    font-weight: 700;
    color: var(--navy);
    margin-right: 6px;
  }

  /* Technique cards */
  .technique-card {
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 20px;
    overflow: hidden;
  }
  .technique-header {
    background: var(--bg);
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid var(--border);
  }
  .technique-name {
    font-weight: 700;
    color: var(--navy);
    font-size: 1rem;
    flex: 1;
  }
  .technique-body { padding: 16px; }
  .technique-field { margin-bottom: 14px; }
  .technique-field:last-child { margin-bottom: 0; }
  .technique-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--gray);
    margin-bottom: 4px;
  }
  .technique-text { font-size: 0.9rem; color: #2C3E50; line-height: 1.6; }

  /* Socratic dialogue */
  .dialogue-round { margin-bottom: 28px; }
  .dialogue-round:last-child { margin-bottom: 0; }
  .round-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 10px;
  }
  .round-1 .round-label { color: var(--teal); }
  .round-2 .round-label { color: var(--navy); }
  .round-3 .round-label { color: #6C3483; }

  .dialogue-bubble {
    padding: 20px 24px;
    border-radius: 8px;
    font-size: 0.92rem;
    line-height: 1.75;
  }
  .dialogue-bubble p { margin-bottom: 12px; }
  .dialogue-bubble p:last-child { margin-bottom: 0; }
  .round-1 .dialogue-bubble { background: #EAF7F4; border-left: 4px solid var(--teal); }
  .round-2 .dialogue-bubble { background: #EAF0F7; border-left: 4px solid var(--navy); }
  .round-3 .dialogue-bubble { background: #F5EEF8; border-left: 4px solid #6C3483; }

  /* Reframe */
  .reframe-block {
    border-left: 4px solid var(--amber);
    background: #FEF9E7;
    padding: 20px 20px 20px 24px;
    border-radius: 0 8px 8px 0;
    font-size: 0.95rem;
    line-height: 1.7;
    font-style: italic;
    color: #2C3E50;
  }

  /* Audit findings */
  .audit-summary {
    background: var(--bg);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    font-size: 0.9rem;
    line-height: 1.6;
  }
  .findings-list { list-style: none; }
  .finding-item {
    border: 1px solid var(--border);
    border-radius: 6px;
    margin-bottom: 10px;
    overflow: hidden;
  }
  .finding-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    background: var(--bg);
    cursor: default;
  }
  .finding-category {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--gray);
  }
  .finding-severity-low    { color: var(--teal); font-size: 0.75rem; font-weight: 600; }
  .finding-severity-medium { color: var(--amber); font-size: 0.75rem; font-weight: 600; }
  .finding-severity-high     { color: var(--red); font-size: 0.75rem; font-weight: 600; }
  .finding-severity-critical { color: #8B0000; font-size: 0.75rem; font-weight: 700; }
  .finding-description { font-size: 0.875rem; color: #2C3E50; }

  /* Scoped diagnostics (v0.8.0+) */
  .diagnostics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 12px;
  }
  @media (max-width: 640px) { .diagnostics-grid { grid-template-columns: 1fr; } }
  .diagnostic-card {
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 16px;
    background: var(--bg);
  }
  .diagnostic-card h4 {
    margin: 0 0 6px;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--gray);
  }
  .diagnostic-card p { margin: 0; font-size: 0.9rem; line-height: 1.6; }
  .diagnostic-note { font-size: 0.78rem; color: var(--gray); font-style: italic; margin-bottom: 4px !important; }
  .posture-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    background: #F5F5F5;
    color: #555;
  }
  .posture-inoculation_first  { background: #FFF3E0; color: #E65100; }
  .posture-relational_first   { background: #E3F2FD; color: #1565C0; }
  .pattern-density-warning {
    background: #FFF8E1;
    border-left: 4px solid var(--amber);
    padding: 10px 14px;
    border-radius: 0 6px 6px 0;
    font-size: 0.875rem;
    margin-top: 8px;
  }
  .finding-body { padding: 10px 14px; border-top: 1px solid var(--border); }
  .finding-rec {
    font-size: 0.8rem;
    color: var(--gray);
    margin-top: 4px;
  }
  .finding-rec strong { color: #2C3E50; }

  /* Scenario navigation */
  .scenario-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 0;
    border-top: 1px solid var(--border);
    margin-top: 16px;
    gap: 16px;
  }
  .scenario-nav a {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--teal);
  }
  .scenario-nav .disabled { color: var(--gray); pointer-events: none; }

  /* Responsive */
  /* Evaluation methodology table */
  .evaluation-section { background: #FAFBFD; margin: 0 -32px; padding: 40px 32px; border-bottom: 1px solid var(--border); }
  .eval-summary { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
  .eval-overall { font-size: 2rem; font-weight: 700; color: var(--navy); }
  .eval-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
  .eval-table th { text-align: left; padding: 10px 12px; border-bottom: 2px solid var(--border); color: var(--gray); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.04em; }
  .eval-table td { padding: 10px 12px; border-bottom: 1px solid #EEF1F5; }
  .eval-table td:first-child { font-weight: 600; text-transform: capitalize; }
  .eval-weight, .eval-score { text-align: center; font-variant-numeric: tabular-nums; }
  .eval-status { text-align: center; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; }
  .eval-pass .eval-status { color: var(--green); }
  .eval-partial .eval-status { color: var(--amber); }
  .eval-fail .eval-status { color: var(--red); }
  .eval-desc { color: var(--gray); font-size: 0.8rem; }
  .eval-note { margin-top: 16px; font-size: 0.82rem; color: var(--gray); line-height: 1.6; }

  @media (max-width: 640px) {
    .site-header h1 { font-size: 1.5rem; }
    .cards-grid { grid-template-columns: 1fr; }
    .scenario-header h1 { font-size: 1.3rem; }
    .scenario-nav { flex-direction: column; align-items: flex-start; }
    .metrics-table { font-size: 0.8rem; }
    .metrics-table th, .metrics-table td { padding: 8px 10px; }
  }
`;

// ---------------------------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------------------------

function esc(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function truncate(str, len) {
  if (!str) return '';
  if (str.length <= len) return str;
  return str.slice(0, len).replace(/\s+\S*$/, '') + '...';
}

function formatParagraphs(text) {
  if (!text) return '';
  const raw = String(text);
  // Split on double newlines first (explicit paragraphs from the LLM)
  let paragraphs = raw.split(/\n\s*\n/).map(p => p.trim()).filter(Boolean);
  // If only one paragraph and it's very long, split on ALL-CAPS headers or numbered sections
  if (paragraphs.length === 1 && paragraphs[0].length > 600) {
    paragraphs = paragraphs[0]
      .split(/\n(?=[A-Z][A-Z ]{3,}:|\d+[\.\)]\s|[-*]\s)/)
      .map(p => p.trim()).filter(Boolean);
  }
  // If STILL one giant block, split on single newlines
  if (paragraphs.length === 1 && paragraphs[0].length > 400) {
    paragraphs = paragraphs[0].split(/\n/).map(p => p.trim()).filter(Boolean);
  }
  return paragraphs.map(p => `<p>${esc(p)}</p>`).join('\n');
}

// ---------------------------------------------------------------------------
// Evaluation engine (JS port of tests/run_bridge_scenarios.py)
// ---------------------------------------------------------------------------

const EXPECTED_NEEDS = {
  'HS-01': ['safety', 'autonomy', 'transparency'],
  'HS-02': ['safety', 'trust', 'autonomy'],
  'HS-03': ['safety', 'autonomy', 'fairness'],
  'HS-04': ['fairness', 'autonomy', 'trust'],
  'HS-05': ['safety', 'autonomy', 'belonging'],
  'GP-01': ['autonomy', 'fairness', 'security'],
  'GP-02': ['safety', 'trust', 'transparency'],
  'GP-03': ['fairness', 'autonomy', 'transparency'],
  'GP-04': ['safety', 'belonging', 'trust'],
  'GP-05': ['fairness', 'dignity', 'belonging'],
  'GP-06': ['fairness', 'accountability', 'belonging', 'autonomy'],
  'EN-01': ['trust', 'fairness', 'autonomy'],
  'EN-02': ['safety', 'autonomy', 'fairness'],
  'EV-01': ['safety', 'trust', 'autonomy'],
  'EV-02': ['safety', 'trust'],
  'EV-03': ['fairness', 'trust', 'autonomy'],
  'EV-04': ['safety', 'trust', 'autonomy'],
  'TC-01': ['autonomy', 'safety', 'privacy'],
  'TC-02': ['safety', 'autonomy', 'fairness'],
  'MD-01': ['trust', 'autonomy', 'fairness'],
  'MD-02': ['autonomy', 'fairness', 'trust'],
};

const CHECK_DESCRIPTIONS = {
  needs_coverage: 'Expected universal human needs matched against identified needs',
  issue_overlap_quality: 'Common ground text is substantive (>50 characters)',
  narrative_deconstruction: 'Narrative deconstruction is substantive (>100 characters)',
  consensus_explanation: 'Scientific/mainstream explanation >200 chars with 3+ mechanism keywords',
  inferential_gap: 'Inferential gap analysis is substantive (>50 characters)',
  feasibility_check: 'Feasibility assessment is substantive (>50 characters)',
  commercial_motives: 'Commercial motive analysis is substantive (>30 characters)',
  technique_naming: 'At least 1 technique named with mechanic (>30 chars) and precedent (>20 chars)',
  perception_gap: 'Perception gap analysis is substantive (>30 characters)',
  socratic_dialogue: '3 rounds, ends with question, Round 1 shows perspective-getting',
  reframe_quality: 'Reframe >20 chars using shared-value language (we, together, both)',
  no_controlling_language: 'Zero matches against 9 controlling phrases',
};

const WEIGHTS = {
  needs_coverage: 0.07,
  issue_overlap_quality: 0.06,
  narrative_deconstruction: 0.07,
  consensus_explanation: 0.11,
  inferential_gap: 0.08,
  feasibility_check: 0.06,
  commercial_motives: 0.06,
  technique_naming: 0.08,
  perception_gap: 0.05,
  socratic_dialogue: 0.17,
  reframe_quality: 0.07,
  no_controlling_language: 0.12,
};

function evaluateBridge(scenarioId, bridge) {
  const checks = {};
  const expected = EXPECTED_NEEDS[scenarioId] || [];

  // Check 1: Needs coverage
  const identified = (bridge.universal_needs || []).map(n => n.toLowerCase().replace(/ /g, '_'));
  const matched = expected.filter(n => identified.some(id => id.includes(n))).length;
  checks.needs_coverage = { score: matched / Math.max(expected.length, 1), matched, expected: expected.length };

  // Check 2: Issue overlap
  const overlap = bridge.issue_overlap || '';
  checks.issue_overlap_quality = { score: overlap.length > 50 ? 1.0 : overlap.length > 10 ? 0.5 : 0.0 };

  // Check 3: Narrative deconstruction
  const narr = bridge.narrative_deconstruction || '';
  checks.narrative_deconstruction = { score: narr.length > 100 ? 1.0 : narr.length > 20 ? 0.5 : 0.0 };

  // Check 4: Consensus explanation
  const cons = bridge.consensus_explanation || '';
  let consScore = 0;
  if (cons.length > 200) {
    consScore = 0.5;
    const markers = ['mechanism', 'process', 'because', 'caused by', 'result of', 'study', 'research', 'data', 'evidence', 'measured', 'observed'];
    if (markers.filter(m => cons.toLowerCase().includes(m)).length >= 3) consScore = 1.0;
  } else if (cons.length > 50) { consScore = 0.3; }
  checks.consensus_explanation = { score: consScore };

  // Check 5: Inferential gap
  const gap = bridge.inferential_gap || '';
  checks.inferential_gap = { score: gap.length > 50 ? 1.0 : gap.length > 10 ? 0.5 : 0.0 };

  // Check 6: Feasibility
  const feas = bridge.feasibility_check || '';
  checks.feasibility_check = { score: feas.length > 50 ? 1.0 : feas.length > 10 ? 0.5 : 0.0 };

  // Check 7: Commercial motives
  const comm = bridge.commercial_motives || '';
  checks.commercial_motives = { score: comm.length > 30 ? 1.0 : comm.length > 10 ? 0.5 : 0.0 };

  // Check 8: Technique naming
  const techs = bridge.techniques_revealed || [];
  let techScore = 0;
  if (techs.length >= 1) {
    techScore = 0.5;
    const hasMech = techs.some(t => (t.how_it_works || '').length > 30);
    const hasPrec = techs.some(t => (t.historical_precedent || '').length > 20);
    if (hasMech && hasPrec) techScore = 1.0;
  }
  checks.technique_naming = { score: techScore };

  // Check 9: Perception gap
  const pg = bridge.perception_gap || '';
  checks.perception_gap = { score: pg.length > 30 ? 1.0 : pg.length > 5 ? 0.5 : 0.0 };

  // Check 10: Socratic dialogue
  const dialogue = bridge.socratic_dialogue || [];
  let dScore = 0;
  if (dialogue.length === 3) {
    dScore = 0.5;
    const r1 = (dialogue[0] || '').toLowerCase();
    const r3 = (dialogue[2] || '').toLowerCase();
    if (r3.includes('?')) dScore += 0.25;
    if (['understand', 'see', 'hear', 'concern', 'worry', 'feel'].some(w => r1.includes(w))) dScore += 0.25;
  }
  checks.socratic_dialogue = { score: dScore };

  // Check 11: Reframe quality
  const reframe = bridge.reframe || '';
  let rScore = 0;
  if (reframe.length > 20) {
    rScore = 0.5;
    if (['we', 'together', 'shared', 'common', 'both', 'all of us', 'everyone'].some(w => reframe.toLowerCase().includes(w))) rScore = 1.0;
  }
  checks.reframe_quality = { score: rScore };

  // Check 12: No controlling language
  const controlling = ['the truth is', 'experts agree', 'you were misled', 'you fell for', 'you should know', 'the fact is', 'everyone knows', "it's obvious", 'you need to understand'];
  const allText = JSON.stringify(bridge).toLowerCase();
  const violations = controlling.filter(p => allText.includes(p));
  checks.no_controlling_language = { score: violations.length === 0 ? 1.0 : 0.0, violations };

  // Overall weighted score
  let overall = 0;
  for (const [k, w] of Object.entries(WEIGHTS)) {
    overall += (checks[k]?.score || 0) * w;
  }
  const grade = overall >= 0.8 ? 'A' : overall >= 0.6 ? 'B' : overall >= 0.4 ? 'C' : 'D';

  return { overall: Math.round(overall * 1000) / 1000, grade, checks };
}

function renderEvaluation(scenarioId, bridge) {
  const ev = evaluateBridge(scenarioId, bridge);
  const pct = (ev.overall * 100).toFixed(1);
  const gradeClass = ev.grade === 'A' ? 'badge-pass' : ev.grade === 'B' ? 'badge-warn' : 'badge-fail';

  let rows = '';
  for (const [key, weight] of Object.entries(WEIGHTS)) {
    const check = ev.checks[key] || { score: 0 };
    const scorePct = (check.score * 100).toFixed(0);
    const weightPct = (weight * 100).toFixed(0);
    const desc = CHECK_DESCRIPTIONS[key] || '';
    const status = check.score >= 0.8 ? 'pass' : check.score >= 0.5 ? 'partial' : 'fail';
    const statusLabel = check.score >= 0.8 ? 'PASS' : check.score >= 0.5 ? 'PARTIAL' : 'MISS';
    rows += `<tr class="eval-${status}">
      <td>${esc(key.replace(/_/g, ' '))}</td>
      <td class="eval-weight">${weightPct}%</td>
      <td class="eval-score">${scorePct}%</td>
      <td class="eval-status">${statusLabel}</td>
      <td class="eval-desc">${esc(desc)}</td>
    </tr>`;
  }

  return `
    <div class="section evaluation-section">
      <h2>Evaluation Methodology</h2>
      <p class="intro-note">Full transparency on how this scenario was scored. 12 weighted checks, each independently measurable. <a href="https://github.com/Jochen-s/huginn-muninn/blob/main/tests/run_bridge_scenarios.py" target="_blank" rel="noopener">View source code</a></p>
      <div class="eval-summary">
        <span class="eval-overall">${pct}%</span>
        <span class="badge ${gradeClass}">Grade ${ev.grade}</span>
      </div>
      <div style="overflow-x:auto">
        <table class="eval-table">
          <thead>
            <tr>
              <th>Check</th>
              <th>Weight</th>
              <th>Score</th>
              <th>Status</th>
              <th>What It Measures</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      <p class="eval-note">Overall score = weighted sum of individual check scores. Weights reflect the relative importance of each dimension to the project's mission: Socratic dialogue quality (17%) and controlling language detection (12%) are weighted highest because autonomy-supportive framing is the core differentiator.</p>
    </div>`;
}

function versionBadge(version) {
  return `<span class="badge badge-version">v${esc(version)}</span>`;
}

function difficultyBadge(id) {
  const d = DIFFICULTY_MAP[id] || 'Medium';
  const cls = d === 'Easy' ? 'badge-easy' : d === 'Hard' ? 'badge-hard' : 'badge-medium';
  return `<span class="badge ${cls}">${d}</span>`;
}

function kernelBadge(id) {
  const has = KERNEL_MAP[id] !== undefined ? KERNEL_MAP[id] : false;
  if (has) {
    return `<span class="badge badge-kernel-true">Kernel of Truth</span>`;
  }
  return `<span class="badge badge-kernel-false">No Clear Kernel</span>`;
}

function verdictBadge(verdict) {
  if (!verdict) return '';
  if (verdict.includes('fail')) return `<span class="badge badge-fail">FAIL</span>`;
  if (verdict.includes('warning')) return `<span class="badge badge-warnings">PASS WITH WARNINGS</span>`;
  return `<span class="badge badge-pass">PASS</span>`;
}

function patternBadge(pt) {
  if (!pt) return '';
  const p = String(pt).toLowerCase();
  if (p === 'systematic') return `<span class="badge badge-systematic">[SYSTEMATIC]</span>`;
  if (p === 'repeated')   return `<span class="badge badge-repeated">[REPEATED]</span>`;
  return `<span class="badge badge-isolated">[ISOLATED]</span>`;
}

function severityClass(severity) {
  const s = String(severity || '').toLowerCase();
  if (s === 'critical') return 'finding-severity-critical';
  if (s === 'high') return 'finding-severity-high';
  if (s === 'medium') return 'finding-severity-medium';
  return 'finding-severity-low';
}

const CATEGORY_LABELS = {
  bias: 'Bias', accuracy: 'Accuracy', completeness: 'Completeness',
  manipulation: 'Manipulation', quality: 'Quality',
  cognitive_warfare: 'Cognitive Influence', frame_capture: 'Frame Adoption',
};
function categoryLabel(cat) {
  return CATEGORY_LABELS[String(cat || '').toLowerCase()] || cat || '';
}

// ---------------------------------------------------------------------------
// Data loading
// ---------------------------------------------------------------------------

function parseVersion(filename) {
  // Matches: {ID}-opus.json (v1) or {ID}-opus-v{N}.json (vN)
  const m = filename.match(/^([A-Z]+-\d+)-opus(?:-v(\d+))?\.json$/);
  if (!m) return null;
  return {
    id: m[1],
    version: m[2] ? parseInt(m[2], 10) : 1,
    file: filename,
  };
}

function loadScenarios() {
  const files = fs.readdirSync(RESULTS_DIR).filter(f => f.endsWith('.json'));
  const best = {};

  for (const file of files) {
    const parsed = parseVersion(file);
    if (!parsed) continue;
    if (!best[parsed.id] || parsed.version > best[parsed.id].version) {
      best[parsed.id] = parsed;
    }
  }

  const scenarios = [];
  for (const id of Object.keys(best).sort()) {
    const entry = best[id];
    const filepath = path.join(RESULTS_DIR, entry.file);
    let data;
    try {
      data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
    } catch (e) {
      console.warn(`Warning: could not parse ${entry.file}: ${e.message}`);
      continue;
    }
    const prefix = id.split('-')[0];
    scenarios.push({
      id,
      version: entry.version,
      category: CATEGORY_BY_PREFIX[prefix] || 'Other',
      data,
    });
  }

  return scenarios;
}

function groupByCategory(scenarios) {
  const groups = {};
  for (const cat of CATEGORY_ORDER) {
    groups[cat] = [];
  }
  for (const s of scenarios) {
    if (groups[s.category]) {
      groups[s.category].push(s);
    } else {
      groups['Other'] = groups['Other'] || [];
      groups['Other'].push(s);
    }
  }
  return groups;
}

// ---------------------------------------------------------------------------
// Index page
// ---------------------------------------------------------------------------

function buildCard(scenario) {
  const { id, version, data } = scenario;
  const claim = truncate(data.claim || '', 110);
  return `
    <div class="card">
      <div class="card-id">${esc(id)}</div>
      <div class="card-claim">${esc(claim)}</div>
      <div class="card-meta">
        ${versionBadge(version)}
        ${difficultyBadge(id)}
        ${kernelBadge(id)}
      </div>
      <a class="card-link" href="${esc(id)}.html">Read analysis &rarr;</a>
    </div>`;
}

function buildIndex(scenarios) {
  const groups = groupByCategory(scenarios);
  const totalCount = scenarios.length;

  let categorySections = '';
  for (const cat of CATEGORY_ORDER) {
    const items = groups[cat];
    if (!items || items.length === 0) continue;
    const cards = items.map(buildCard).join('');
    categorySections += `
      <div class="category-section">
        <div class="container">
          <div class="category-header">
            <h2>${esc(cat)}</h2>
            <p class="category-intro">${esc(CATEGORY_INTROS[cat] || '')}</p>
          </div>
          <div class="cards-grid">
            ${cards}
          </div>
        </div>
      </div>`;
  }

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Huginn &amp; Muninn -- Scenario Gallery</title>
  <meta name="description" content="${totalCount} real-world conspiracy and misinformation claims analyzed through a 6-agent AI pipeline that finds common ground across ideological divides.">
  <style>${SHARED_CSS}
    .stats-bar {
      background: #152138;
      padding: 12px 0;
      color: #8AA5BC;
      font-size: 0.85rem;
    }
    .stats-bar .container {
      display: flex;
      gap: 24px;
      flex-wrap: wrap;
    }
    .stat-item strong { color: var(--white); }
  </style>
</head>
<body>

<header class="site-header">
  <div class="container">
    <h1>Huginn &amp; Muninn &mdash; Scenario Gallery</h1>
    <p class="subtitle">${totalCount} real-world conspiracy and misinformation claims, analyzed through a 6-agent AI pipeline</p>
    <p class="intro">
      Each scenario asks three questions: What legitimate need does this claim serve?
      What manipulation techniques are being used, and by whom?
      And where is the common ground between people who believe this and those who don&rsquo;t?
      The goal is not to dismiss people who hold these beliefs, but to understand them well
      enough to build bridges across the divide.
    </p>
  </div>
</header>

<nav class="site-nav">
  <div class="container">
    <a href="index.html" class="active">Gallery</a>
    <a href="graph.html">Knowledge Graph</a>
  </div>
</nav>

<div class="stats-bar">
  <div class="container">
    <div class="stat-item"><strong>${totalCount}</strong> scenarios</div>
    <div class="stat-item"><strong>6</strong> categories</div>
    <div class="stat-item"><strong>6-agent</strong> pipeline</div>
    <div class="stat-item"><strong>3 questions</strong> per claim</div>
  </div>
</div>

<main>
  ${categorySections}
</main>

<footer class="site-footer">
  <div class="container">
    <p>
      Built with <a href="https://github.com/jschmiedbauer/huginn-muninn">Huginn &amp; Muninn</a> &mdash;
      an open-source de-polarization research project. &nbsp;|&nbsp;
      MIT License &nbsp;|&nbsp;
      Analysis powered by Claude (Anthropic)
    </p>
  </div>
</footer>

</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Scenario page helpers
// ---------------------------------------------------------------------------

function renderUniversalNeeds(needs) {
  if (!needs || needs.length === 0) return '<p class="intro-note">No universal needs data available.</p>';
  const items = needs.map(n => {
    // Needs are often "Name: explanation" format
    const colonIdx = String(n).indexOf(':');
    if (colonIdx > 0 && colonIdx < 40) {
      const name = n.slice(0, colonIdx).trim();
      const desc = n.slice(colonIdx + 1).trim();
      return `<div class="need-item"><span class="need-name">${esc(name)}:</span>${esc(desc)}</div>`;
    }
    return `<div class="need-item">${esc(n)}</div>`;
  });
  return `<div class="needs-list">${items.join('')}</div>`;
}

function renderTechniques(techniques) {
  if (!techniques || techniques.length === 0) return '';
  return techniques.map(t => `
    <div class="technique-card">
      <div class="technique-header">
        <span class="technique-name">${esc(t.technique || t.name || 'Technique')}</span>
        ${patternBadge(t.pattern_type)}
      </div>
      <div class="technique-body">
        ${t.used_by ? `
        <div class="technique-field">
          <div class="technique-label">Used by</div>
          <div class="technique-text">${esc(t.used_by)}</div>
        </div>` : ''}
        ${t.how_it_works ? `
        <div class="technique-field">
          <div class="technique-label">How it works</div>
          <div class="technique-text">${esc(t.how_it_works)}</div>
        </div>` : ''}
        ${t.where_used_here ? `
        <div class="technique-field">
          <div class="technique-label">In this claim</div>
          <div class="technique-text">${esc(t.where_used_here)}</div>
        </div>` : ''}
        ${t.historical_precedent ? `
        <div class="technique-field">
          <div class="technique-label">Historical precedent</div>
          <div class="technique-text">${esc(t.historical_precedent)}</div>
        </div>` : ''}
      </div>
    </div>`).join('');
}

function renderSocraticDialogue(rounds) {
  if (!rounds || rounds.length === 0) return '<p class="intro-note">No dialogue data available.</p>';
  const labels = ['Perspective-Getting', 'Guided Examination', 'Integration'];
  const classNames = ['round-1', 'round-2', 'round-3'];
  return rounds.map((round, i) => `
    <div class="dialogue-round ${classNames[i] || ''}">
      <div class="round-label">Round ${i + 1}: ${labels[i] || 'Round ' + (i + 1)}</div>
      <div class="dialogue-bubble">${formatParagraphs(String(round))}</div>
    </div>`).join('');
}

function renderFindings(findings) {
  if (!findings || findings.length === 0) return '<p class="intro-note">No findings recorded.</p>';
  return `<ul class="findings-list">` + findings.map(f => `
    <li class="finding-item">
      <div class="finding-header">
        <span class="finding-category">${esc(categoryLabel(f.category))}</span>
        <span class="${severityClass(f.severity)}">${esc(String(f.severity || '').toUpperCase())}</span>
        <span class="finding-description">${esc(truncate(f.description || '', 120))}</span>
      </div>
      ${f.description && f.description.length > 120 ? `
      <div class="finding-body">
        <div class="finding-description">${esc(f.description)}</div>
        ${f.recommendation ? `<div class="finding-rec"><strong>Recommendation:</strong> ${esc(f.recommendation)}</div>` : ''}
      </div>` : (f.recommendation ? `
      <div class="finding-body">
        <div class="finding-rec"><strong>Recommendation:</strong> ${esc(f.recommendation)}</div>
      </div>` : '')}
    </li>`).join('') + `</ul>`;
}

function renderScopedDiagnostics(bridge) {
  const posture = bridge.communication_posture || 'direct_correction';
  const densityWarning = bridge.pattern_density_warning || false;
  const vacuum = bridge.vacuum_filled_by || '';
  const prebunk = bridge.prebunking_note || '';
  const scopeMarker = '[scope:redacted-named-entity]';

  const postureLabel = posture.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  const postureClassMap = { inoculation_first: 'posture-inoculation_first', relational_first: 'posture-relational_first' };
  const postureCls = postureClassMap[posture] || '';
  const postureHtml = posture !== 'direct_correction'
    ? `<div class="diagnostic-card">
        <h4>Communication Posture</h4>
        <p><span class="posture-badge ${postureCls}">${esc(postureLabel)}</span></p>
      </div>`
    : '';

  const densityHtml = densityWarning
    ? `<div class="diagnostic-card">
        <h4>Pattern Density</h4>
        <div class="pattern-density-warning">High pattern density detected in claim structure. The claim is structured to encourage over-connection between unrelated elements.</div>
      </div>`
    : '';

  const vacuumText = vacuum && vacuum !== scopeMarker ? vacuum : '';
  const vacuumHtml = vacuumText
    ? `<div class="diagnostic-card">
        <h4>Credibility Gap</h4>
        <p class="diagnostic-note">Narrative pattern description; no specific publisher or outlet identified.</p>
        <p>${esc(vacuumText)}</p>
      </div>`
    : '';

  const prebunkText = prebunk && prebunk !== scopeMarker ? prebunk : '';
  const prebunkHtml = prebunkText
    ? `<div class="diagnostic-card">
        <h4>Prebunking Note</h4>
        <p>${esc(prebunkText)}</p>
      </div>`
    : '';

  const cards = [postureHtml, densityHtml, vacuumHtml, prebunkHtml].filter(Boolean).join('\n');
  if (!cards) return '';

  return `
  <div class="section">
    <h2>Response Strategy Signals</h2>
    <p class="intro-note">Signals guiding how this analysis might be communicated effectively. Advisory to communicators, not a characterisation of the reader.</p>
    <div class="diagnostics-grid">
      ${cards}
    </div>
  </div>`;
}

function renderOptionalSection(title, text) {
  if (!text) return '';
  return `
    <div class="section">
      <h2>${title}</h2>
      <div class="prose">${formatParagraphs(text)}</div>
    </div>`;
}

// ---------------------------------------------------------------------------
// Scenario page
// ---------------------------------------------------------------------------

function buildScenarioPage(scenario, allScenarios) {
  const { id, version, data } = scenario;
  const bridge = data.bridge || {};
  const audit = data.audit || {};
  const stats = data.pipeline_stats || {};

  const idx = allScenarios.findIndex(s => s.id === id);
  const prev = idx > 0 ? allScenarios[idx - 1] : null;
  const next = idx < allScenarios.length - 1 ? allScenarios[idx + 1] : null;

  const subClaimsCount = (stats.decomposer || {}).sub_claims
    || (data.decomposition || {}).sub_claims && data.decomposition.sub_claims.length
    || 0;
  const actorsCount = (stats.mapper || {}).actors
    || (data.intelligence || {}).actors && data.intelligence.actors.length
    || 0;
  const ttpCount = (stats.classifier || {}).ttp_matches
    || (data.ttps || {}).ttp_matches && data.ttps.ttp_matches.length
    || 0;

  const techniquesSection = bridge.techniques_revealed && bridge.techniques_revealed.length > 0
    ? `<div class="section">
        <h2>Name the Trick</h2>
        ${renderTechniques(bridge.techniques_revealed)}
      </div>`
    : '';

  const consensusSection = bridge.consensus_explanation
    ? `<div class="section">
        <h2>Scientific Consensus / Mainstream Explanation</h2>
        <p class="intro-note">The established scientific or institutional explanation for this phenomenon.</p>
        <div class="prose">${formatParagraphs(bridge.consensus_explanation)}</div>
      </div>`
    : '';

  const prevLink = prev
    ? `<a href="${esc(prev.id)}.html">&larr; ${esc(prev.id)}: ${esc(truncate(prev.data.claim || '', 50))}</a>`
    : `<span class="disabled">&larr; First scenario</span>`;

  const nextLink = next
    ? `<a href="${esc(next.id)}.html">${esc(next.id)}: ${esc(truncate(next.data.claim || '', 50))} &rarr;</a>`
    : `<span class="disabled">Last scenario &rarr;</span>`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${esc(id)}: ${esc(truncate(data.claim || '', 70))} &mdash; Huginn &amp; Muninn</title>
  <meta name="description" content="6-agent AI pipeline analysis of: ${esc(truncate(data.claim || '', 150))}">
  <style>${SHARED_CSS}</style>
</head>
<body>

<nav class="site-nav">
  <div class="container">
    <a href="index.html">Gallery</a>
    <a href="graph.html">Knowledge Graph</a>
  </div>
</nav>

<header class="scenario-header">
  <div class="content">
    <a class="back-link" href="index.html">&larr; Back to gallery</a>
    <h1>${esc(id)}: ${esc(data.claim || '')}</h1>
    <div class="header-meta">
      ${versionBadge(version)}
      ${difficultyBadge(id)}
      ${kernelBadge(id)}
      <span class="badge badge-version">${esc(scenario.category)}</span>
    </div>
  </div>
</header>

<main class="content">

  <div class="section">
    <h2>Pipeline Metrics</h2>
    <table class="metrics-table">
      <thead>
        <tr>
          <th>Metric</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>Sub-claims</td><td>${subClaimsCount}</td></tr>
        <tr><td>Actors identified</td><td>${actorsCount}</td></tr>
        <tr><td>TTP matches</td><td>${ttpCount}</td></tr>
        <tr><td>Audit verdict</td><td>${verdictBadge(audit.verdict)}</td></tr>
        <tr><td>Pipeline version</td><td>${esc(data.pipeline || 'v' + version)}</td></tr>
        ${data.overall_confidence != null
          ? `<tr><td>Overall confidence</td><td>${(data.overall_confidence * 100).toFixed(0)}%</td></tr>`
          : ''}
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2>Universal Needs</h2>
    <p class="intro-note">The legitimate human needs this claim speaks to, regardless of whether the claim is accurate.</p>
    ${renderUniversalNeeds(bridge.universal_needs)}
  </div>

  ${consensusSection}

  ${techniquesSection}

  ${bridge.inferential_gap ? `
  <div class="section">
    <h2>Inferential Gap</h2>
    <p class="intro-note">Where the evidence ends and the leap begins.</p>
    <div class="prose">${formatParagraphs(bridge.inferential_gap)}</div>
  </div>` : ''}

  <div class="section">
    <h2>Common Ground</h2>
    <div class="prose">${formatParagraphs(bridge.issue_overlap || 'No common ground data available.')}</div>
  </div>

  <div class="section">
    <h2>Narrative Deconstruction</h2>
    <div class="prose">${formatParagraphs(bridge.narrative_deconstruction || 'No narrative deconstruction data available.')}</div>
  </div>

  ${renderOptionalSection('Feasibility Assessment', bridge.feasibility_check)}

  ${renderOptionalSection('Commercial Interests', bridge.commercial_motives)}

  ${renderOptionalSection('Perception Gap', bridge.perception_gap)}

  <div class="section">
    <h2>Socratic Dialogue</h2>
    <p class="intro-note">A model conversation demonstrating how to engage someone who holds this belief.</p>
    ${renderSocraticDialogue(bridge.socratic_dialogue)}
  </div>

  ${bridge.reframe ? `
  <div class="section">
    <h2>Reframe</h2>
    <blockquote class="reframe-block">${esc(bridge.reframe)}</blockquote>
  </div>` : ''}

  ${renderScopedDiagnostics(bridge)}

  <div class="section">
    <h2>Audit</h2>
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
      <span>Verdict:</span>
      ${verdictBadge(audit.verdict)}
    </div>
    ${audit.summary ? `<div class="audit-summary">${esc(audit.summary)}</div>` : ''}
    ${renderFindings(audit.findings)}
  </div>

  ${renderEvaluation(id, bridge)}

  <div class="scenario-nav">
    ${prevLink}
    <a href="index.html">Gallery</a>
    ${nextLink}
  </div>

</main>

<footer class="site-footer">
  <div class="content">
    <p>
      <a href="index.html">Huginn &amp; Muninn Gallery</a> &nbsp;|&nbsp;
      MIT License &nbsp;|&nbsp;
      Analysis powered by Claude (Anthropic)
    </p>
  </div>
</footer>

</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Knowledge Graph page
// ---------------------------------------------------------------------------

function buildGraphPage() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Knowledge Graph | Huginn &amp; Muninn</title>
<style>${SHARED_CSS}

  #cy {
    width: 100%;
    height: 600px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: #FAFBFC;
  }
  .graph-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
    align-items: center;
  }
  .graph-controls label {
    font-size: 0.9rem;
    color: var(--gray);
  }
  .graph-controls select, .graph-controls input {
    padding: 6px 10px;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 0.85rem;
  }
  .graph-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-top: 12px;
    font-size: 0.85rem;
    color: var(--gray);
  }
  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .legend-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    display: inline-block;
  }
  .graph-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
  }
  .stat-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    text-align: center;
  }
  .stat-card .stat-num {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--navy);
  }
  .stat-card .stat-label {
    font-size: 0.8rem;
    color: var(--gray);
    margin-top: 4px;
  }
  #node-detail {
    display: none;
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    margin-top: 16px;
  }
  #node-detail h3 { margin-bottom: 8px; }
  #node-detail .detail-field {
    font-size: 0.9rem;
    margin-bottom: 6px;
  }
  #node-detail .detail-label {
    font-weight: 600;
    color: var(--navy);
  }
</style>
</head>
<body>

<header class="site-header">
  <div class="container">
    <h1>Knowledge Graph</h1>
    <p class="subtitle">Cross-scenario connections: actors, techniques, and narrative patterns across 21 disinformation analyses.</p>
    <p class="intro">Click any node to explore. Same actors and techniques appearing across multiple scenarios reveal the recycled playbooks behind disinformation.</p>
  </div>
</header>

<nav class="site-nav">
  <div class="container">
    <a href="index.html">Gallery</a>
    <a href="graph.html" class="active">Knowledge Graph</a>
  </div>
</nav>

<main class="content" style="max-width:1100px;padding-top:32px;padding-bottom:64px;">

  <div class="graph-stats" id="graph-stats"></div>

  <div class="graph-controls">
    <div>
      <label for="filter-type">Show:</label>
      <select id="filter-type">
        <option value="all">All node types</option>
        <option value="scenario">Scenarios only</option>
        <option value="actor">Actors only</option>
        <option value="technique">Techniques (DISARM)</option>
        <option value="technique_reveal">Named Tricks</option>
        <option value="scenario+actor" selected>Scenarios + Actors</option>
        <option value="scenario+actor+technique">Scenarios + Actors + Techniques</option>
        <option value="scenario+technique">Playbook View (Scenarios + Techniques)</option>
      </select>
    </div>
    <div>
      <label for="filter-perspective">Perspective:</label>
      <select id="filter-perspective">
        <option value="all">All perspectives</option>
        <option value="scientific_consensus">Scientific Consensus</option>
        <option value="concerned_citizen">Concerned Citizen</option>
        <option value="institutional_skeptic">Institutional Skeptic</option>
        <option value="bridge_builder">Bridge Builder</option>
      </select>
    </div>
    <div>
      <label for="filter-category">Category:</label>
      <select id="filter-category">
        <option value="all">All categories</option>
        <option value="Health & Science">Health & Science</option>
        <option value="Geopolitics">Geopolitics</option>
        <option value="Environment">Environment</option>
        <option value="Events">Events</option>
        <option value="Technology">Technology</option>
        <option value="Media">Media</option>
        <option value="Science Controversy">Science Controversy</option>
      </select>
    </div>
    <div>
      <label for="filter-search">Search:</label>
      <input type="text" id="filter-search" placeholder="Actor or technique name..." />
    </div>
    <div>
      <button id="btn-shared-reality" style="padding:6px 14px;border:1px solid var(--border);border-radius:6px;font-size:0.85rem;background:var(--white);cursor:pointer;">Show Shared Reality</button>
    </div>
  </div>

  <div class="graph-legend">
    <span class="legend-item"><span class="legend-dot" style="background:#1B2A4A"></span> Scenario</span>
    <span class="legend-item"><span class="legend-dot" style="background:#C0392B"></span> Actor</span>
    <span class="legend-item"><span class="legend-dot" style="background:#16A085"></span> Technique (DISARM)</span>
    <span class="legend-item"><span class="legend-dot" style="background:#8E44AD"></span> Named Trick</span>
    <span class="legend-item"><span class="legend-dot" style="background:#E67E22"></span> Mutation</span>
    <span class="legend-item"><span class="legend-dot" style="background:#2980B9"></span> Temporal Era</span>
  </div>

  <div id="cy"></div>
  <div id="node-detail"></div>

</main>

<footer class="site-footer">
  <div class="content">
    <p>
      <a href="index.html">Huginn &amp; Muninn Gallery</a> &nbsp;|&nbsp;
      MIT License &nbsp;|&nbsp;
      Analysis powered by Claude (Anthropic)
    </p>
  </div>
</footer>

<script src="https://unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js"></script>
<script>
(function() {
  'use strict';

  var NODE_COLORS = {
    scenario: '#1B2A4A',
    actor: '#C0392B',
    technique: '#16A085',
    technique_reveal: '#8E44AD',
    mutation: '#E67E22',
    temporal_era: '#2980B9',
    claim: '#95A5A6'
  };

  var NODE_SHAPES = {
    scenario: 'round-rectangle',
    actor: 'ellipse',
    technique: 'diamond',
    technique_reveal: 'star',
    mutation: 'triangle',
    temporal_era: 'hexagon',
    claim: 'ellipse'
  };

  var cy;

  function init() {
    fetch('graph-data.json')
      .then(function(resp) { return resp.json(); })
      .then(function(graphData) {
        renderStats(graphData);
        initGraph(graphData);
        attachControls();
      });
  }

  function renderStats(data) {
    var nodes = data.elements.nodes;
    var edges = data.elements.edges;
    var types = {};
    nodes.forEach(function(n) {
      var t = n.data.node_type || 'unknown';
      types[t] = (types[t] || 0) + 1;
    });

    var crossActors = nodes.filter(function(n) {
      return n.data.node_type === 'actor' &&
        n.data.scenarios && n.data.scenarios.length > 1;
    }).length;

    var el = document.getElementById('graph-stats');
    var h = '';
    h += statCard(types.scenario || 0, 'Scenarios');
    h += statCard(types.actor || 0, 'Actors');
    h += statCard(crossActors, 'Cross-Scenario Actors');
    h += statCard((types.technique || 0) + (types.technique_reveal || 0), 'Techniques');
    h += statCard(edges.length, 'Connections');
    el.textContent = '';
    el.insertAdjacentHTML('beforeend', h);
  }

  function statCard(num, label) {
    return '<div class="stat-card"><div class="stat-num">' +
      num + '</div><div class="stat-label">' + escHtml(label) + '</div></div>';
  }

  function initGraph(data) {
    var elements = [];

    data.elements.nodes.forEach(function(n) {
      var d = n.data;
      var nt = d.node_type || 'unknown';
      var nodeData = {
        id: d.id,
        label: truncLabel(d.label || d.id, 30),
        fullLabel: d.label || d.id,
        node_type: nt,
        color: NODE_COLORS[nt] || '#999',
        shape: NODE_SHAPES[nt] || 'ellipse',
        size: nodeSize(d)
      };
      var keys = Object.keys(d);
      for (var i = 0; i < keys.length; i++) {
        if (!(keys[i] in nodeData)) nodeData[keys[i]] = d[keys[i]];
      }
      elements.push({ group: 'nodes', data: nodeData });
    });

    data.elements.edges.forEach(function(e) {
      var d = e.data;
      elements.push({
        group: 'edges',
        data: {
          id: d.source + '->' + d.target,
          source: d.source,
          target: d.target,
          edge_type: d.edge_type || '',
          label: d.label || ''
        }
      });
    });

    cy = cytoscape({
      container: document.getElementById('cy'),
      elements: elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'background-color': 'data(color)',
            'shape': 'data(shape)',
            'width': 'data(size)',
            'height': 'data(size)',
            'font-size': '10px',
            'text-wrap': 'ellipsis',
            'text-max-width': '100px',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'color': '#2C3E50',
            'border-width': 1,
            'border-color': '#D0D9E4'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': '#BDC3C7',
            'target-arrow-color': '#BDC3C7',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 0.8
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 3,
            'border-color': '#E74C3C'
          }
        },
        {
          selector: '.highlighted',
          style: {
            'border-width': 3,
            'border-color': '#F39C12'
          }
        },
        {
          selector: '.dimmed',
          style: {
            'opacity': 0.15
          }
        },
        {
          selector: 'edge[edge_type="cross_scenario"]',
          style: {
            'line-style': 'dashed',
            'line-dash-pattern': [6, 3],
            'width': 'mapData(weight, 2, 10, 2, 6)',
            'line-color': '#E74C3C',
            'target-arrow-color': '#E74C3C',
            'target-arrow-shape': 'none'
          }
        },
        {
          selector: 'edge[edge_type="co_occurs"]',
          style: {
            'line-style': 'dotted',
            'width': 1,
            'line-color': '#95A5A6',
            'target-arrow-shape': 'none'
          }
        },
        {
          selector: '.shared-reality',
          style: {
            'border-width': 4,
            'border-color': '#F1C40F',
            'background-opacity': 1
          }
        },
        {
          selector: '.pivot-point',
          style: {
            'border-width': 3,
            'border-color': '#E74C3C',
            'border-style': 'double'
          }
        }
      ],
      layout: {
        name: 'cose',
        idealEdgeLength: 120,
        nodeRepulsion: 8000,
        gravity: 0.3,
        numIter: 300,
        animate: false
      },
      minZoom: 0.3,
      maxZoom: 3
    });

    cy.on('tap', 'node', function(evt) {
      showNodeDetail(evt.target.data());
      highlightNeighbors(evt.target);
    });

    cy.on('tap', function(evt) {
      if (evt.target === cy) {
        hideNodeDetail();
        cy.elements().removeClass('highlighted dimmed');
      }
    });
  }

  function nodeSize(d) {
    var nt = d.node_type;
    if (nt === 'scenario') return 40;
    if (nt === 'actor') {
      var sc = (d.scenarios || []).length;
      return 25 + sc * 8;
    }
    if (nt === 'technique' || nt === 'technique_reveal') {
      var sc2 = (d.scenarios || []).length;
      return 20 + sc2 * 6;
    }
    return 18;
  }

  function truncLabel(str, len) {
    return str.length > len ? str.slice(0, len - 1) + '\\u2026' : str;
  }

  function highlightNeighbors(node) {
    cy.elements().removeClass('highlighted dimmed');
    var neighborhood = node.neighborhood().add(node);
    cy.elements().addClass('dimmed');
    neighborhood.removeClass('dimmed').addClass('highlighted');
    node.removeClass('dimmed');
  }

  function showNodeDetail(d) {
    var el = document.getElementById('node-detail');
    el.style.display = 'block';

    var h = '<h3>' + escHtml(d.fullLabel || d.label) + '</h3>';
    h += detailField('Type', d.node_type);

    if (d.node_type === 'scenario') {
      h += detailField('Claim', d.claim);
      h += detailField('Category', d.category);
      h += detailField('Version', d.version);
      h += detailField('Confidence', d.confidence ? (d.confidence * 100).toFixed(0) + '%' : '');
      if (d.false_polarization_gap != null) {
        var gapPct = (d.false_polarization_gap * 100).toFixed(0);
        h += detailField('Shared Reality', gapPct + '% of underlying concerns are shared across perspectives');
      }
      h += '<div style="margin-top:8px"><a href="' + escHtml(d.label) + '.html">View full analysis</a></div>';
    } else if (d.node_type === 'actor') {
      h += detailField('Actor type', d.actor_type);
      h += detailField('Credibility', d.credibility ? (d.credibility * 100).toFixed(0) + '%' : '');
      h += detailField('Motivation', d.motivation);
      h += detailField('Appears in', (d.scenarios || []).join(', '));
    } else if (d.node_type === 'technique') {
      h += detailField('DISARM ID', d.disarm_id);
      h += detailField('Max confidence', d.max_confidence ? (d.max_confidence * 100).toFixed(0) + '%' : '');
      h += detailField('Used in', (d.scenarios || []).join(', '));
    } else if (d.node_type === 'technique_reveal') {
      h += detailField('Pattern type', d.pattern_type);
      h += detailField('How it works', d.how_it_works);
      h += detailField('Historical precedent', d.historical_precedent);
      h += detailField('Appears in', (d.scenarios || []).join(', '));
    } else if (d.node_type === 'mutation') {
      h += detailField('Mutation type', d.mutation_type);
      h += detailField('Original', d.original);
      h += detailField('Mutated', d.mutated);
    } else if (d.node_type === 'temporal_era') {
      h += detailField('Date range', d.date_range);
      h += detailField('Dominant framing', d.dominant_framing);
    }

    el.textContent = '';
    el.insertAdjacentHTML('beforeend', h);
  }

  function hideNodeDetail() {
    document.getElementById('node-detail').style.display = 'none';
  }

  function detailField(label, value) {
    if (!value) return '';
    return '<div class="detail-field"><span class="detail-label">' +
      escHtml(label) + ':</span> ' + escHtml(String(value)) + '</div>';
  }

  function escHtml(str) {
    var d = document.createElement('div');
    d.textContent = str || '';
    return d.innerHTML;
  }

  var PERSPECTIVE_EMPHASIS = {
    scientific_consensus: ['technique', 'claim'],
    concerned_citizen: ['actor', 'scenario'],
    institutional_skeptic: ['actor'],
    bridge_builder: ['scenario']
  };

  function attachControls() {
    document.getElementById('filter-type').addEventListener('change', applyFilters);
    document.getElementById('filter-category').addEventListener('change', applyFilters);
    document.getElementById('filter-search').addEventListener('input', applyFilters);
    document.getElementById('filter-perspective').addEventListener('change', applyFilters);

    document.getElementById('btn-shared-reality').addEventListener('click', function() {
      var active = this.classList.toggle('active');
      this.style.background = active ? '#F1C40F' : 'var(--white)';
      this.style.color = active ? '#2C3E50' : '';
      this.textContent = active ? 'Hide Shared Reality' : 'Show Shared Reality';
      cy.batch(function() {
        cy.nodes().removeClass('shared-reality pivot-point');
        if (active) {
          cy.nodes().forEach(function(node) {
            var d = node.data();
            if (d.node_type === 'scenario' && d.false_polarization_gap > 0.5) {
              node.addClass('shared-reality');
            }
            if (d.node_type === 'actor' && (d.scenarios || []).length >= 3) {
              node.addClass('shared-reality');
            }
            if (d.pivot_point) {
              node.addClass('pivot-point');
            }
          });
        }
      });
    });

    applyFilters();
  }

  function applyFilters() {
    var typeFilter = document.getElementById('filter-type').value;
    var catFilter = document.getElementById('filter-category').value;
    var search = document.getElementById('filter-search').value.toLowerCase().trim();
    var perspective = document.getElementById('filter-perspective').value;
    var emphTypes = perspective !== 'all' ? PERSPECTIVE_EMPHASIS[perspective] || [] : [];

    cy.batch(function() {
      cy.elements().removeClass('dimmed');

      cy.nodes().forEach(function(node) {
        var d = node.data();
        var visible = true;

        if (typeFilter !== 'all') {
          var allowedTypes = typeFilter.split('+');
          if (allowedTypes.indexOf(d.node_type) === -1) {
            visible = false;
          }
        }

        if (catFilter !== 'all' && visible) {
          if (d.node_type === 'scenario') {
            if (d.category !== catFilter) visible = false;
          } else {
            var connectedScenarios = node.neighborhood('node[node_type="scenario"]');
            var hasMatch = false;
            connectedScenarios.forEach(function(s) {
              if (s.data('category') === catFilter) hasMatch = true;
            });
            if (!hasMatch && connectedScenarios.length > 0) visible = false;
          }
        }

        if (search && visible) {
          var label = (d.fullLabel || d.label || '').toLowerCase();
          if (label.indexOf(search) === -1) visible = false;
        }

        if (!visible) {
          node.addClass('dimmed');
        } else if (emphTypes.length > 0 && emphTypes.indexOf(d.node_type) === -1 && d.node_type !== 'scenario') {
          node.style('opacity', 0.4);
        } else {
          node.style('opacity', 1);
        }
      });

      cy.edges().forEach(function(edge) {
        var src = edge.source();
        var tgt = edge.target();
        if (src.hasClass('dimmed') && tgt.hasClass('dimmed')) {
          edge.addClass('dimmed');
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();
</script>

</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  console.log('Huginn & Muninn Gallery Builder');
  console.log('================================');
  console.log(`Reading results from: ${RESULTS_DIR}`);
  console.log(`Writing output to:    ${DIST_DIR}`);
  console.log();

  if (!fs.existsSync(DIST_DIR)) {
    fs.mkdirSync(DIST_DIR, { recursive: true });
  }

  const scenarios = loadScenarios();
  console.log(`Found ${scenarios.length} scenarios (highest version per ID):`);
  for (const s of scenarios) {
    console.log(`  ${s.id} v${s.version} (${s.category})`);
  }
  console.log();

  // Write index
  const indexHtml = buildIndex(scenarios);
  const indexPath = path.join(DIST_DIR, 'index.html');
  fs.writeFileSync(indexPath, indexHtml, 'utf8');
  console.log(`Written: index.html (${(indexHtml.length / 1024).toFixed(1)} KB)`);

  // Write individual scenario pages
  let written = 0;
  for (const scenario of scenarios) {
    const html = buildScenarioPage(scenario, scenarios);
    const outPath = path.join(DIST_DIR, `${scenario.id}.html`);
    fs.writeFileSync(outPath, html, 'utf8');
    console.log(`Written: ${scenario.id}.html (${(html.length / 1024).toFixed(1)} KB)`);
    written++;
  }

  // Write knowledge graph page
  const graphHtml = buildGraphPage();
  const graphPath = path.join(DIST_DIR, 'graph.html');
  fs.writeFileSync(graphPath, graphHtml, 'utf8');
  console.log(`Written: graph.html (${(graphHtml.length / 1024).toFixed(1)} KB)`);

  console.log();
  console.log(`Done. Generated index.html + ${written} scenario pages + graph.html.`);
  console.log(`Open: ${path.join(DIST_DIR, 'index.html')}`);
}

main();
