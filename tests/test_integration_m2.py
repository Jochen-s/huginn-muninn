"""Integration test for the full Method 2 pipeline."""
import json
from unittest.mock import MagicMock

from huginn_muninn.contracts import AnalysisReport
from huginn_muninn.llm import OllamaClient
from huginn_muninn.orchestrator import Orchestrator

MOCK_DECOMPOSER = json.dumps({
    "sub_claims": [
        {"text": "Immigration has increased in the US", "type": "factual", "verifiable": True},
        {"text": "Crime rates have risen in the US", "type": "factual", "verifiable": True},
        {"text": "Increased immigration causes increased crime", "type": "causal", "verifiable": True},
    ],
    "original_claim": "Immigration increases crime rates in the United States",
    "complexity": "moderate",
})

MOCK_TRACER = json.dumps({
    "origins": [
        {
            "sub_claim": "Immigration has increased in the US",
            "earliest_source": "census.gov",
            "earliest_date": "2024-09-01",
            "source_tier": 1,
            "propagation_path": ["census.gov", "reuters.com", "foxnews.com", "twitter.com"],
        },
        {
            "sub_claim": "Increased immigration causes increased crime",
            "earliest_source": "politicalcommentary.com/blog",
            "earliest_date": "2024-10-15",
            "source_tier": 4,
            "propagation_path": ["politicalcommentary.com", "facebook.com", "local news"],
        },
    ],
    "mutations": [
        {
            "original": "Net migration increased by 1.2 million in 2024",
            "mutated": "Millions of illegal immigrants flooding the border",
            "mutation_type": "amplification",
            "source": "twitter.com/political_commentator",
        }
    ],
})

MOCK_MAPPER = json.dumps({
    "actors": [
        {"name": "Census Bureau", "type": "organization", "motivation": "statistical reporting", "credibility": 0.95, "evidence": "Government statistics agency"},
        {"name": "Political commentators", "type": "influencer", "motivation": "audience engagement", "credibility": 0.3, "evidence": "Pattern of amplifying divisive narratives"},
        {"name": "Research institutions", "type": "organization", "motivation": "academic research", "credibility": 0.85, "evidence": "Peer-reviewed studies"},
    ],
    "relations": [
        {"source_actor": "Political commentators", "target_actor": "Census Bureau", "relation_type": "cites", "confidence": 0.6},
    ],
    "narrative_summary": "Statistical data from credible sources is selectively cited and amplified by political commentators to support a pre-existing narrative.",
})

MOCK_CLASSIFIER = json.dumps({
    "ttp_matches": [
        {"disarm_id": "T0023", "technique_name": "Distort facts", "confidence": 0.8, "evidence": "Census data reframed without context"},
        {"disarm_id": "T0056", "technique_name": "Amplify existing narratives", "confidence": 0.75, "evidence": "Organic concern about crime amplified"},
    ],
    "primary_tactic": "Execute",
})

MOCK_BRIDGE = json.dumps({
    "universal_needs": ["safety", "economic security", "belonging"],
    "issue_overlap": "Both pro- and anti-immigration voices cite community safety as their primary concern, with 78% agreement on wanting safer neighborhoods.",
    "narrative_deconstruction": "Actor A framed community safety as an immigration problem. Actor B framed it as a policing/poverty problem. Both framings serve electoral interests while hiding the shared concern.",
    "perception_gap": "Each side estimates 65% of opponents want completely open/closed borders; actual rates are 11% and 7%.",
    "moral_foundations": {"side_a": ["loyalty", "authority", "sanctity"], "side_b": ["care", "fairness"]},
    "reframe": "Rather than 'immigrants vs citizens', this is about 'how do we build safer communities for everyone who lives here?'",
    "socratic_dialogue": [
        "If I understand correctly, the concern is that your community feels less safe, and you're connecting that to changes in who lives there. Feeling safe where you live is fundamental. Is that a fair summary?",
        "Interestingly, the research consistently shows that immigrant communities have lower crime rates than native-born populations. But the narrative you've encountered uses a technique called 'distortion' -- taking real data about immigration numbers and linking it to crime without the actual crime statistics. What do you make of that disconnect?",
        "What's striking is that 78% of people on both sides of this debate say community safety is their top priority. If most people want the same thing, who benefits from making them think they're on opposite sides?",
    ],
})

MOCK_AUDITOR = json.dumps({
    "verdict": "pass_with_warnings",
    "findings": [
        {
            "category": "completeness",
            "severity": "medium",
            "description": "Analysis focuses on US context; claim may apply differently in other countries",
            "recommendation": "Note geographic scope limitation",
        }
    ],
    "confidence_adjustment": -0.05,
    "veto": False,
    "summary": "Analysis is well-supported with minor scope limitation noted.",
})


class TestMethodTwoPipeline:
    def test_full_pipeline(self):
        client = MagicMock(spec=OllamaClient)
        client.generate.side_effect = [
            MOCK_DECOMPOSER, MOCK_TRACER, MOCK_MAPPER,
            MOCK_CLASSIFIER, MOCK_BRIDGE, MOCK_AUDITOR,
        ]

        orch = Orchestrator(client)
        result = orch.run("Immigration increases crime rates in the United States")

        report = AnalysisReport(**result)
        assert report.claim == "Immigration increases crime rates in the United States"
        assert report.method == "method_2"
        assert not report.audit.veto
        assert len(report.decomposition.sub_claims) == 3
        assert len(report.origins.origins) == 2
        assert len(report.origins.mutations) == 1
        assert len(report.intelligence.actors) == 3
        assert len(report.ttps.ttp_matches) == 2
        assert "safety" in report.bridge.universal_needs
        assert len(report.bridge.socratic_dialogue) == 3
        assert report.overall_confidence > 0.5
        assert not report.degraded

    def test_pipeline_backcompat_legacy_decomposer_defaults_priority(self):
        """Sprint 2 P2-7 regression guard: the legacy MOCK_DECOMPOSER fixture
        predates verification_priority. The full integration pipeline must
        still succeed and every sub-claim must default to "low" -- this is
        the same backwards-compat discipline Sprint 1 shipped."""
        client = MagicMock(spec=OllamaClient)
        client.generate.side_effect = [
            MOCK_DECOMPOSER, MOCK_TRACER, MOCK_MAPPER,
            MOCK_CLASSIFIER, MOCK_BRIDGE, MOCK_AUDITOR,
        ]
        orch = Orchestrator(client)
        result = orch.run("Immigration increases crime rates in the United States")
        report = AnalysisReport(**result)
        for sc in report.decomposition.sub_claims:
            assert sc.verification_priority == "low"

    def test_pipeline_with_explicit_verification_priority_triage(self):
        """End-to-end integration: a realistic Decomposer output that
        triages three sub-claims at different priorities (critical for the
        causal death claim, high for a factual harm claim, low for opinion)
        must round-trip through the full pipeline intact and not be
        overwritten or downgraded by any downstream agent contract."""
        triaged_decomposer = json.dumps({
            "sub_claims": [
                {
                    "text": "Policy X caused 200 deaths",
                    "type": "causal",
                    "verifiable": True,
                    "verification_priority": "critical",
                },
                {
                    "text": "Policy X raised costs 15 percent",
                    "type": "factual",
                    "verifiable": True,
                    "verification_priority": "high",
                },
                {
                    "text": "Policy X is the worst of its kind",
                    "type": "opinion",
                    "verifiable": False,
                    "verification_priority": "low",
                },
            ],
            "original_claim": "Policy X caused 200 deaths, raised costs 15%, and is the worst",
            "complexity": "complex",
        })
        client = MagicMock(spec=OllamaClient)
        client.generate.side_effect = [
            triaged_decomposer, MOCK_TRACER, MOCK_MAPPER,
            MOCK_CLASSIFIER, MOCK_BRIDGE, MOCK_AUDITOR,
        ]
        orch = Orchestrator(client)
        result = orch.run("Policy X claim")
        report = AnalysisReport(**result)
        priorities = [sc.verification_priority for sc in report.decomposition.sub_claims]
        assert priorities == ["critical", "high", "low"]

    def test_pipeline_with_veto(self):
        veto_auditor = json.dumps({
            "verdict": "fail",
            "findings": [{"category": "bias", "severity": "critical", "description": "Systematic bias", "recommendation": "Redo"}],
            "confidence_adjustment": -0.4,
            "veto": True,
            "summary": "Critical bias -- veto",
        })
        client = MagicMock(spec=OllamaClient)
        client.generate.side_effect = [
            MOCK_DECOMPOSER, MOCK_TRACER, MOCK_MAPPER,
            MOCK_CLASSIFIER, MOCK_BRIDGE, veto_auditor,
        ]

        orch = Orchestrator(client)
        result = orch.run("Test claim")
        report = AnalysisReport(**result)
        assert report.degraded
        assert report.audit.veto
