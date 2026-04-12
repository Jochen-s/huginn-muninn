# Huginn & Muninn Roadmap

What's coming next. This is a directional guide, not a commitment schedule.

---

## Recently Shipped

**v0.11.0 "Auditor Exfiltration Guard"**
- Audit text scrubbing closes a channel where suppressed field content could leak through Auditor findings
- `audit_redacted` disclosure flag on all API responses

**v0.10.0 "First-Class Audit Categories"**
- `cognitive_warfare` and `frame_capture` as first-class audit finding categories
- Gallery rendering for Bridge diagnostic fields (communication posture, pattern density, credibility gaps, prebunking notes)

**v0.9.0 "External Surface Hardening"**
- Regulated API envelope at all external boundaries
- Operator field suppression with startup validation
- OpenAPI advisory descriptions for regulated fields

---

## Next Up

### Activate Existing Infrastructure

Several shipped schema fields are not yet wired into the confidence computation or downstream routing. Activating them improves result quality at zero additional LLM cost.

- Source tier integration into confidence scoring
- Cleaner separation between pipeline errors and epistemic vetoes
- Formalized convergence gates

### Structured Claim Analysis

Evolve the Decomposer's flat sub-claim list toward richer structural representation.

- Sub-claim dependency tracking (which sub-claims depend on which)
- Circular reasoning detection as a first-class signal (disinformation often relies on self-reinforcing narrative loops)
- Cross-leaf recombination awareness in the Auditor

### Source Quality and Usage

Expand the evidence model to distinguish between a source's inherent quality and how it is used in context. A peer-reviewed paper cited out of context is not the same as one cited faithfully.

- Expanded source tier system
- Usage confidence as a companion signal
- Context-aware citation handling

### Audit Trail

Full pipeline event logging for reproducibility and auditability.

- Immutable event log per analysis run
- Privacy-preserving design (no personally identifiable data in logs)
- Foundation for future batch processing and cross-claim analysis

---

## Under Consideration (Quality-Gated)

These features require measurement data before adoption decisions.

- Structured adversarial review within the pipeline (internal agent debates)
- Bounded iteration with convergence detection
- Narrative frame preservation through the decomposition stage

---

## Not Planned

Some patterns were evaluated and explicitly rejected. Each rejection includes conditions under which the decision would be revisited.

- **Automatic claim deferral**: dismissing claims as "low value" is a judgment about the person's concern, not just the claim's verifiability. Conflicts with the Anti-Weaponization Charter.
- **Forced acyclic claim structure**: circular reasoning in disinformation narratives is a detection signal, not an error to be removed.
- **Bridge Builder as optional**: the common humanity layer is the mission, not an add-on.

---

## Contributing

If any of these directions interest you, open an issue to discuss. We welcome contributions across all areas, especially cross-cultural validation, multilingual support, and manufactured doubt detection for non-Western contexts.

---

*This roadmap reflects the project's direction as of April 2026. Priorities may shift as research evidence evolves.*
