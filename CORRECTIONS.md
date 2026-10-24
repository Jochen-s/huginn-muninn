# Corrections

A tool that asks people to examine their sources has to correct its own errors in the open. This file explains how to report an error and records the corrections made.

## What counts

- a factual error in a gallery scenario, the methodology page or the research documents
- a citation that does not say what we say it says
- a description of a person, group or organisation that is inaccurate or unfair
- a claim that a feature exists when it does not

## How to report

Open a GitHub issue with "Correction:" at the start of the title. Say what is wrong, where it appears, and what the evidence is.

If the error concerns a named person and you would rather not discuss it in public, use the private report form instead (the **Security** tab, then **Report a vulnerability**) and say that it is a correction request.

## What happens next

Each report is checked against the evidence. If it holds, the content is corrected, the change is noted here and in the CHANGELOG, and the live site is republished. Corrections are not deleted silently, and a decision not to correct is explained in the issue.

## Log

| Published | What was wrong | What changed |
|---|---|---|
| 2026-10-24 (v0.17.0) | The public knowledge graph gave named actors, including living people, a numeric credibility score. This breached Charter Commitment 1. | Numeric scores removed; actors carry only a categorical basis for the assessment. A build-time test now fails on any numeric score on an actor. |
| 2026-10-24 (v0.17.0) | The methodology page stated a source-tier ladder (0.9 / 0.7 / 0.5 / 0.3) that differed from the one the code uses (0.95 / 0.80 / 0.50 / 0.20). | The page now states the values in use; a test derives the documented values from the code. |
| 2026-10-24 (v0.17.0) | RESEARCH.md attributed the 76,977-response persuasion-accuracy study to the wrong authors, and five further citations overstated or misdescribed their sources. | Attributions and descriptions corrected. One effect size (Meyer et al. 2024) is marked as unresolved until it is checked against the paper's figure. Costello et al. 2024 now carries its June 2026 Science Expression of Concern. |
| 2026-10-24 (v0.17.0) | README and RESEARCH.md said the framework "implements" fading and system-regulated access. The engine has no user model, so these do not exist. | RESEARCH.md now says "the design calls for"; the README marks one pillar as built and the other three as design commitments. |
| 2026-10-24 (v0.17.0) | REJECTIONS.md cited pilot testing and a count of replication failures that the record does not support. | Both reasons restated on their actual basis. |
| 2026-10-24 (v0.17.0) | The privacy statement said data never leaves your machine, while three optional settings send data out. | The statement now leads with the local default and names the three optional exits; the API logs which ones are enabled. |
