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
];

const CATEGORY_BY_PREFIX = {
  HS: 'Health & Science',
  GP: 'Geopolitics',
  EN: 'Environment',
  EV: 'Events',
  TC: 'Technology',
  MD: 'Media',
};

const CATEGORY_INTROS = {
  'Health & Science': 'Medical and scientific claims that exploit real uncertainties to construct false certainty.',
  'Geopolitics': 'Claims about hidden power structures, covert operations, and political conspiracies.',
  'Environment': 'Environmental and climate claims that mix legitimate science with manufactured doubt.',
  'Events': 'Narratives about specific historical or political events that dispute the established record.',
  'Technology': 'Technology fears that blend genuine risks with unfounded surveillance and control claims.',
  'Media': 'Claims about information systems, media bias, and how narratives are shaped and controlled.',
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
  .finding-severity-high   { color: var(--red); font-size: 0.75rem; font-weight: 600; }
  .finding-description { font-size: 0.875rem; color: #2C3E50; }
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
  if (s === 'high') return 'finding-severity-high';
  if (s === 'medium') return 'finding-severity-medium';
  return 'finding-severity-low';
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
        <span class="finding-category">${esc(f.category || '')}</span>
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

  console.log();
  console.log(`Done. Generated index.html + ${written} scenario pages.`);
  console.log(`Open: ${path.join(DIST_DIR, 'index.html')}`);
}

main();
