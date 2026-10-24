# Rejection Log

Every feature considered for Huginn & Muninn has a documented rejection pathway: if the evidence changes, the rejection can be revisited under the falsification criterion stated here. Features without a revisit path are marked permanent and tied to a specific commitment from the [Anti-Weaponization Charter](ANTI-WEAPONIZATION-CHARTER.md).

A rejection is a load-bearing design decision. Writing them down keeps the tool honest about what it refused to become.

## Permanent rejections

These will not be revisited. Each is bound to a charter commitment, and reversing them would require changing the commitment itself.

### "Victim of cognitive warfare" framing

**What was proposed:** A labeling layer that would characterize people holding manipulated beliefs as casualties of an adversarial information environment.

**Why it was rejected:** Removes agency from the user. A tool that treats people as victims cannot also treat them as autonomous adults. The framing also invites a rescuer-victim dynamic that the Common Humanity layer is specifically designed to avoid.

**Commitment:** 6 (autonomy-preserving).

**Revisit path:** None. This is a philosophical commitment, not an empirical one.

### Self-Poisoning Triad detection

**What was proposed:** An analytic pipeline that would build detailed actor dossiers by combining open-source intelligence, linguistic fingerprinting, and behavioral pattern matching to identify coordinated influence operators.

**Why it was rejected:** Would require constructing the exact dossier-assembly capability that Commitment 1 (anti-surveillance) forbids. A tool cannot prevent surveillance of named individuals if it is built on top of infrastructure that enables that surveillance.

**Commitment:** 1 (public narratives, not individuals).

**Revisit path:** None.

## Conditional rejections

These are rejected on current evidence. Each includes a falsification criterion: a specific empirical result that would license revisiting the decision.

### Timing suspicion field

**What was proposed:** A metadata field that would flag claims arriving in suspicious temporal clusters as likely coordinated.

**Why it was rejected:** A six-faction design review plus a cross-model check (Sprint 2, recorded in the CHANGELOG under P2-8) converged on the judgement that an LLM-generated timing flag would create structural false-positive exposure on legitimate journalism (breaking news naturally clusters in time) and grassroots protest coordination. No pilot was run and the field was never implemented; the basis is a predicted exposure, not a measured rate. Flagging either as suspect would violate Commitment 3 (evidence-first actor analysis).

**Commitment:** 3 (evidence-first actor analysis).

**Revisit path:** A labeled corpus with a documented 0% false-positive rate on journalism-timing patterns and protest-coordination patterns. A method that cannot distinguish organic temporal clustering from coordinated inauthentic behavior is not ready.

### Moral reframing as a primary de-polarization mechanism

**What was proposed:** Adopting Feinberg and Willer's moral reframing technique as a core component of the Bridge Builder's output.

**Why it was rejected:** Five preregistered replication attempts listed in the RESEARCH.md bibliography failed to reproduce the original effect, two of them unpublished manuscripts. Building on a replication-failed foundation would undermine the research integrity commitment (Commitment 8, open methodology).

**Commitment:** 8 (open methodology).

**Revisit path:** A successful preregistered large-N replication demonstrating the effect. Until then, moral reframing stays experimental and does not gate core pipeline decisions.

### The Redirect Method as a measurement of belief change

**What was proposed:** Using Moonshot's Redirect Method as evidence that the pipeline changes beliefs.

**Why it was rejected:** The Redirect Method measures engagement, not belief change. Treating an engagement metric as a belief-change metric would misrepresent what the pipeline is doing.

**Commitment:** 8 (open methodology), 5 (transparent uncertainty).

**Revisit path:** An evaluation protocol that measures post-intervention belief shift with preregistered analysis. Engagement can return as a complementary signal at that point, never as the primary mechanism.

## How this log is maintained

- New rejections are added when a feature is proposed, evaluated, and declined.
- Rejections move between conditional and permanent only if the underlying commitment changes. Charter amendments require the same bar as charter commitments themselves.
- The full log lives here, not in the charter. The charter states what the tool is committed to. This file records what the tool considered and refused.

If you are considering contributing a feature that appears here, read the falsification criterion first. The rejection can be revisited if the criterion is met. Presenting new evidence is welcome. Presenting the same idea without new evidence is not.
