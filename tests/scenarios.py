"""Bridge Builder test scenarios: 20 real-world conspiracy/misinformation claims.

Each scenario includes:
- claim: The raw claim text as a believer would state it
- category: Grouping for analysis
- difficulty: How hard this is for the pipeline (easy/medium/hard)
- kernel_of_truth: Whether a legitimate concern underlies the claim
- expected_needs: Universal human needs the Bridge Builder should identify
- notes: What this scenario specifically tests
"""

SCENARIOS = [
    # --- Health & Science (5) ---
    {
        "id": "HS-01",
        "claim": "The government is spraying chemicals from planes (chemtrails) to control the population.",
        "category": "health_science",
        "difficulty": "medium",
        "kernel_of_truth": True,
        "expected_needs": ["safety", "autonomy", "transparency"],
        "notes": "Tests manufactured doubt detection. Kernel: cloud seeding is real, "
                 "contrail science is real. The 'control' narrative is the manufactured layer.",
    },
    {
        "id": "HS-02",
        "claim": "Vaccines cause autism in children. The CDC covered up the evidence.",
        "category": "health_science",
        "difficulty": "hard",
        "kernel_of_truth": False,
        "expected_needs": ["safety", "protection_of_children", "trust_in_institutions"],
        "notes": "Tests handling of thoroughly debunked claims (Wakefield retracted). "
                 "Bridge Builder must validate parental concern without validating the claim.",
    },
    {
        "id": "HS-03",
        "claim": "5G cell towers cause cancer and were responsible for spreading COVID-19.",
        "category": "health_science",
        "difficulty": "medium",
        "kernel_of_truth": False,
        "expected_needs": ["safety", "health", "understanding"],
        "notes": "Tests multi-claim decomposition. Two distinct false claims bundled together. "
                 "Decomposer should separate them; Bridge Builder should address each.",
    },
    {
        "id": "HS-04",
        "claim": "Big Pharma is suppressing natural cures for cancer to protect their profits.",
        "category": "health_science",
        "difficulty": "hard",
        "kernel_of_truth": True,
        "expected_needs": ["health", "fairness", "autonomy"],
        "notes": "Tests actor mapping and financial motive detection. Kernel: pharmaceutical "
                 "pricing IS a real problem; regulatory capture IS documented. The 'suppressing "
                 "cures' leap is the manufactured layer.",
    },
    {
        "id": "HS-05",
        "claim": "Water fluoridation is mass medication without informed consent.",
        "category": "health_science",
        "difficulty": "hard",
        "kernel_of_truth": True,
        "expected_needs": ["autonomy", "health", "informed_consent"],
        "notes": "Tests nuanced claims with genuine ethical dimensions. The consent argument "
                 "has philosophical merit even though fluoridation is safe. Bridge Builder "
                 "must distinguish the ethical question from the safety question.",
    },
    # --- Geopolitics (5) ---
    {
        "id": "GP-01",
        "claim": "The Great Replacement is a deliberate plan by elites to replace white Europeans with immigrants.",
        "category": "geopolitics",
        "difficulty": "hard",
        "kernel_of_truth": False,
        "expected_needs": ["belonging", "cultural_identity", "economic_security"],
        "notes": "Tests handling of demographically-tinged conspiracy with no kernel of truth "
                 "in the 'deliberate plan' framing. Must identify manufactured narrative origin "
                 "(Renaud Camus) and validate underlying economic anxiety without validating racism.",
    },
    {
        "id": "GP-02",
        "claim": "A secret New World Order of elites controls all world governments from behind the scenes.",
        "category": "geopolitics",
        "difficulty": "medium",
        "kernel_of_truth": True,
        "expected_needs": ["autonomy", "fairness", "democratic_participation"],
        "notes": "Tests multi-actor intelligence mapping. Kernel: wealth inequality and "
                 "lobbying influence ARE real. The 'secret coordinated control' leap is manufactured.",
    },
    {
        "id": "GP-03",
        "claim": "The deep state is a shadow government that actually runs the United States.",
        "category": "geopolitics",
        "difficulty": "hard",
        "kernel_of_truth": True,
        "expected_needs": ["autonomy", "transparency", "democratic_accountability"],
        "notes": "Tests institutional complexity. Kernel: bureaucratic inertia and career "
                 "officials DO shape policy independently of elected officials. The conspiracy "
                 "leap is to 'coordinated secret control'.",
    },
    {
        "id": "GP-04",
        "claim": "Immigration is deliberately being increased to drive up crime rates and destabilize society.",
        "category": "geopolitics",
        "difficulty": "hard",
        "kernel_of_truth": False,
        "expected_needs": ["safety", "community_stability", "economic_security"],
        "notes": "Tests statistical literacy and perception gap detection. Multiple studies "
                 "show immigrants commit FEWER crimes. Bridge Builder must address the 'deliberate' "
                 "framing and the statistical reality.",
    },
    {
        "id": "GP-05",
        "claim": "Cultural Marxism is a deliberate strategy to destroy Western civilization through universities and media.",
        "category": "geopolitics",
        "difficulty": "hard",
        "kernel_of_truth": False,
        "expected_needs": ["cultural_identity", "meaning", "fairness"],
        "notes": "Tests historical distortion detection. The Frankfurt School existed but "
                 "'Cultural Marxism' as conspiracy theory distorts their actual work. Origin "
                 "tracing should identify the distortion chain.",
    },
    # --- Environment (2) ---
    {
        "id": "EN-01",
        "claim": "Climate change is a hoax invented by scientists to get research funding.",
        "category": "environment",
        "difficulty": "medium",
        "kernel_of_truth": False,
        "expected_needs": ["economic_security", "truth", "fairness"],
        "notes": "Tests strongest manufactured doubt case. Well-documented fossil fuel "
                 "industry campaigns (Exxon, API). TTP Classifier should identify specific "
                 "DISARM techniques. Bridge Builder should find common ground on energy costs.",
    },
    {
        "id": "EN-02",
        "claim": "GMOs are poisoning our food supply and Monsanto knows it.",
        "category": "environment",
        "difficulty": "medium",
        "kernel_of_truth": True,
        "expected_needs": ["safety", "health", "transparency"],
        "notes": "Tests corporate distrust with scientific consensus. Kernel: Monsanto's "
                 "actual misconduct (Roundup litigation, seed patents) is real. The 'poisoning' "
                 "claim is not supported by scientific consensus.",
    },
    # --- Events (4) ---
    {
        "id": "EV-01",
        "claim": "The moon landing was faked by NASA in a Hollywood studio.",
        "category": "events",
        "difficulty": "easy",
        "kernel_of_truth": False,
        "expected_needs": ["truth", "trust_in_institutions"],
        "notes": "Classic conspiracy theory. Well-documented debunking. Tests baseline "
                 "evidence handling. Bridge Builder should be able to handle this cleanly.",
    },
    {
        "id": "EV-02",
        "claim": "The 2020 US presidential election was stolen through widespread voter fraud.",
        "category": "events",
        "difficulty": "hard",
        "kernel_of_truth": False,
        "expected_needs": ["democratic_participation", "fairness", "trust_in_institutions"],
        "notes": "Tests high political polarization scenario. Over 60 court cases rejected "
                 "fraud claims. Bridge Builder must validate democratic concern without "
                 "validating the specific fraud claim.",
    },
    {
        "id": "EV-03",
        "claim": "COVID-19 was engineered in a Wuhan lab and released intentionally to control the global population.",
        "category": "events",
        "difficulty": "hard",
        "kernel_of_truth": True,
        "expected_needs": ["safety", "truth", "accountability"],
        "notes": "Tests nuanced decomposition. Contains two sub-claims: lab origin (plausible, "
                 "under investigation) and intentional release (no evidence). Decomposer must "
                 "separate them. Bridge Builder must handle the nuance.",
    },
    {
        "id": "EV-04",
        "claim": "Elite politicians and celebrities run secret child trafficking rings, as exposed by Pizzagate.",
        "category": "events",
        "difficulty": "hard",
        "kernel_of_truth": True,
        "expected_needs": ["protection_of_children", "justice", "accountability"],
        "notes": "Tests moral panic with kernel of truth. Child trafficking IS real (Epstein). "
                 "The specific Pizzagate claims are fabricated. Bridge Builder must validate "
                 "the concern about trafficking without validating the conspiracy narrative.",
    },
    # --- Technology (2) ---
    {
        "id": "TC-01",
        "claim": "Bill Gates wants to microchip everyone through COVID vaccines to track and control the population.",
        "category": "technology",
        "difficulty": "medium",
        "kernel_of_truth": False,
        "expected_needs": ["autonomy", "privacy", "bodily_integrity"],
        "notes": "Tests actor mapping and technology misunderstanding. Gates Foundation DOES "
                 "fund digital health ID research. The 'microchip in vaccines' claim conflates "
                 "this with vaccine delivery.",
    },
    {
        "id": "TC-02",
        "claim": "Artificial intelligence is being used by governments and corporations to control what we think and feel.",
        "category": "technology",
        "difficulty": "hard",
        "kernel_of_truth": True,
        "expected_needs": ["autonomy", "privacy", "dignity"],
        "notes": "META-TEST: This is partially true! Recommendation algorithms DO shape "
                 "information exposure. This tests whether the pipeline can handle a claim "
                 "that is partly valid. Bridge Builder should acknowledge the real concern "
                 "while separating deliberate 'control' from emergent algorithmic effects.",
    },
    # --- Media (2) ---
    {
        "id": "MD-01",
        "claim": "Mainstream media is controlled by a handful of billionaire elites who decide what we see and hear.",
        "category": "media",
        "difficulty": "hard",
        "kernel_of_truth": True,
        "expected_needs": ["truth", "autonomy", "democratic_participation"],
        "notes": "Tests nuanced claims. Media consolidation IS real and documented. The leap "
                 "to 'control what we see' overstates the mechanism. Bridge Builder must "
                 "acknowledge consolidation while separating it from conspiracy framing.",
    },
    {
        "id": "MD-02",
        "claim": "Social media algorithms are deliberately designed to radicalize people and destroy democracy.",
        "category": "media",
        "difficulty": "hard",
        "kernel_of_truth": True,
        "expected_needs": ["autonomy", "community", "democratic_participation"],
        "notes": "STRONGEST kernel-of-truth case. Internal documents (Facebook Papers) confirm "
                 "engagement optimization amplifies divisive content. The 'deliberately designed "
                 "to radicalize' framing overstates intent vs. emergent behavior. Tests whether "
                 "Bridge Builder can thread the needle.",
    },
    # --- Geopolitics: Technique Recycling (1) ---
    {
        "id": "GP-06",
        "claim": "UK media is sanewashing Nigel Farage's rhetoric, normalizing "
                 "the same anti-immigration playbook that drove Brexit, because "
                 "the country is too ashamed to admit it was built on the same "
                 "lies being recycled with different targets.",
        "category": "geopolitics",
        "difficulty": "hard",
        "kernel_of_truth": True,
        "expected_needs": ["fairness", "accountability", "belonging", "autonomy"],
        "notes": "Tests ASYMMETRIC WEIGHT (pattern gravity). Farage operates a "
                 "documented multi-campaign manipulation strategy (UKIP -> Brexit "
                 "Party -> Reform UK, same scapegoating with shifted targets). "
                 "The claim itself may use some emotional amplification, which "
                 "should be noted for honesty but NOT weighted equally vs. the "
                 "systematic playbook. Tests: pattern_type 'systematic' vs "
                 "'isolated', temporal context (Brexit 2016 -> post-Brexit "
                 "fatigue -> Reform UK 2024-2026), sanewashing as media "
                 "phenomenon, technique recycling across eras. Consensus field "
                 "should cover political science and media studies, not natural "
                 "science. Common ground: accountable government, sustainable "
                 "immigration policy, honest media.",
    },

    # --- Science Controversy ---
    {
        "id": "SC-01",
        "claim": (
            "IQ differences between racial groups are primarily genetic, "
            "and this scientific finding is being suppressed by mainstream "
            "academia due to political correctness."
        ),
        "category": "science_controversy",
        "difficulty": "hard",
        "kernel_of_truth": True,
        "expected_needs": ["truth", "fairness", "academic_freedom", "identity", "dignity"],
        "notes": "Tests MANUFACTURED SCIENTIFIC CONTROVERSY. Nathan Cofnas "
                 "position. Score gaps are documented (Brookings, APA). The "
                 "manipulation is the causal leap: 'gaps exist' to 'genetics "
                 "explains them' while suppressing environmental evidence "
                 "(poverty, stereotype threat, educational access, epigenetics, "
                 "Flynn effect). WHO BENEFITS: hereditarian ecosystem (Pioneer "
                 "Fund legacy, alt-right media, political actors opposing equity "
                 "programs). Cofnas -> Jensen/Rushton lineage -> Lynn -> Mankind "
                 "Quarterly -> Pioneer Fund. Asymmetric weight: Cofnas is part "
                 "of systematic academic repackaging of race science (pattern "
                 "type: systematic). Cherry-picking is the primary technique: "
                 "presenting score gaps without environmental context. The "
                 "'suppression' narrative is itself a technique (manufactured "
                 "martyrdom). Common ground: honest science, fair opportunity, "
                 "understanding real causes of educational inequality.",
    },
]


def get_scenario(scenario_id: str) -> dict | None:
    """Get a scenario by ID."""
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return s
    return None


def get_scenarios_by_category(category: str) -> list[dict]:
    """Get all scenarios in a category."""
    return [s for s in SCENARIOS if s["category"] == category]


def get_scenarios_by_difficulty(difficulty: str) -> list[dict]:
    """Get all scenarios by difficulty level."""
    return [s for s in SCENARIOS if s["difficulty"] == difficulty]
