"""The cache answers only for the model that produced the result (2026-10-25:
results from qwen3.5:9b, qwen3.8:27b and Opus were served to each other)."""
import sqlite3
from types import SimpleNamespace

from huginn_muninn.db import HuginnDB
from huginn_muninn.llm import cache_key, client_cache_key

QWEN = "ollama/qwen3.5:9b"
OPUS = "claude-code/claude-opus-5-5@medium"


class TestCacheKey:
    def test_local_model_key(self):
        assert cache_key("ollama", "qwen3.5:9b") == QWEN

    def test_effort_is_part_of_a_claude_key(self):
        assert cache_key("claude-code", "claude-opus-5-5", "medium") == OPUS

    def test_effort_is_ignored_for_local_models(self):
        assert cache_key("ollama", "qwen3.5:9b", "high") == QWEN

    def test_client_key_matches_the_resolved_key(self):
        client = SimpleNamespace(provider="claude-code", model="claude-opus-5-5", effort="medium")
        assert client_cache_key(client) == OPUS

    def test_client_without_provider_gets_no_key(self):
        assert client_cache_key(SimpleNamespace(model="m")) is None


class TestKeyedVerdicts:
    def test_hit_for_the_same_model(self, tmp_path):
        db = HuginnDB(tmp_path / "h.db")
        db.store_verdict("c", {"verdict": "false"}, model_key=QWEN)
        assert db.get_cached_verdict("c", model_key=QWEN) == {"verdict": "false"}

    def test_miss_for_another_model(self, tmp_path):
        db = HuginnDB(tmp_path / "h.db")
        db.store_verdict("c", {"verdict": "false"}, model_key=QWEN)
        assert db.get_cached_verdict("c", model_key=OPUS) is None

    def test_with_id_respects_the_key(self, tmp_path):
        db = HuginnDB(tmp_path / "h.db")
        db.store_verdict("c", {"verdict": "false"}, model_key=QWEN)
        assert db.get_cached_verdict_with_id("c", model_key=OPUS) is None

    def test_unkeyed_lookup_still_sees_any_model(self, tmp_path):
        db = HuginnDB(tmp_path / "h.db")
        db.store_verdict("c", {"verdict": "false"}, model_key=QWEN)
        assert db.get_cached_verdict("c") == {"verdict": "false"}


class TestKeyedAnalyses:
    def test_miss_for_another_model(self, tmp_path):
        db = HuginnDB(tmp_path / "h.db")
        db.store_analysis("c", {"claim": "c"}, model_key=QWEN)
        assert db.get_cached_analysis("c", model_key=OPUS) is None

    def test_with_id_hit_for_the_same_model(self, tmp_path):
        db = HuginnDB(tmp_path / "h.db")
        row_id = db.store_analysis("c", {"claim": "c"}, model_key=QWEN)
        assert db.get_cached_analysis_with_id("c", model_key=QWEN)[1] == row_id


class TestLegacyDatabase:
    def _legacy(self, path):
        conn = sqlite3.connect(path)
        conn.executescript("""
            CREATE TABLE verdicts (id INTEGER PRIMARY KEY, claim TEXT NOT NULL,
                verdict_json TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE analyses (id INTEGER PRIMARY KEY, claim TEXT NOT NULL,
                analysis_json TEXT NOT NULL, created_at TEXT NOT NULL);
            INSERT INTO verdicts (claim, verdict_json, created_at)
                VALUES ('c', '{"verdict": "true"}', '2026-01-01T00:00:00+00:00');
        """)
        conn.commit()
        conn.close()

    def test_old_database_gains_the_column(self, tmp_path):
        path = tmp_path / "old.db"
        self._legacy(path)
        db = HuginnDB(path)
        db.store_verdict("c", {"verdict": "false"}, model_key=QWEN)
        assert db.get_cached_verdict("c", model_key=QWEN) == {"verdict": "false"}

    def test_rows_without_a_model_are_not_served_to_a_keyed_lookup(self, tmp_path):
        path = tmp_path / "old.db"
        self._legacy(path)
        assert HuginnDB(path).get_cached_verdict("c", model_key=QWEN) is None

    def test_opening_twice_does_not_fail(self, tmp_path):
        path = tmp_path / "old.db"
        self._legacy(path)
        HuginnDB(path).close()
        HuginnDB(path).close()


class TestCallersPassTheKey:
    def test_cli_analyze_looks_up_its_own_model(self):
        from unittest.mock import MagicMock, patch

        from click.testing import CliRunner

        from huginn_muninn.cli import main

        mock_db = MagicMock()
        mock_db.get_cached_analysis.return_value = {"overall_confidence": 0.5}
        with patch("huginn_muninn.cli.HuginnDB") as mock_db_cls:
            mock_db_cls.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_db_cls.return_value.__exit__ = MagicMock(return_value=False)
            CliRunner().invoke(main, ["analyze", "--json-output", "--model", "qwen3.8:27b", "some claim"],
                               env={"HUGINN_LLM_PROVIDER": None})
        assert mock_db.get_cached_analysis.call_args.kwargs["model_key"] == "ollama/qwen3.8:27b"

    def test_cli_check_with_claude_provider_includes_effort(self):
        from unittest.mock import MagicMock, patch

        from click.testing import CliRunner

        from huginn_muninn.cli import main

        mock_db = MagicMock()
        mock_db.get_cached_verdict.return_value = {"verdict": "false"}
        with patch("huginn_muninn.cli.HuginnDB") as mock_db_cls:
            mock_db_cls.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_db_cls.return_value.__exit__ = MagicMock(return_value=False)
            CliRunner().invoke(main, ["check", "--json-output", "--provider", "claude-code",
                                      "--effort", "medium", "some claim"],
                               env={"HUGINN_LLM_PROVIDER": None})
        assert mock_db.get_cached_verdict.call_args.kwargs["model_key"] == OPUS

    def test_api_method2_uses_the_client_key(self):
        from unittest.mock import MagicMock

        from huginn_muninn import api

        api.app.state.db = MagicMock()
        api.app.state.db.get_cached_analysis_with_id.return_value = ({"claim": "c"}, 7)
        api.app.state.client = SimpleNamespace(provider="ollama", model="qwen3.5:9b")
        assert api._run_method2("c") == ({"claim": "c"}, 7)
        assert api.app.state.db.get_cached_analysis_with_id.call_args.kwargs["model_key"] == QWEN


class TestReviewFindings:
    """Independent Station 2 review, 2026-10-25."""

    def test_read_only_legacy_database_opens_and_serves_nothing_keyed(self, tmp_path):
        import os
        import stat

        path = tmp_path / "old.db"
        db = HuginnDB(path)  # full schema, then strip the new column to mimic an old database
        db.store_verdict("c", {"verdict": "true"})
        db.close()
        conn = sqlite3.connect(path)
        for table in ("verdicts", "analyses"):
            conn.execute(f"DROP INDEX idx_{table}_claim_model")
            conn.execute(f"ALTER TABLE {table} DROP COLUMN model_key")
        conn.commit()
        conn.close()
        os.chmod(path, stat.S_IREAD)
        try:
            db = HuginnDB(path)
            assert db.get_cached_verdict("c", model_key=QWEN) is None
            assert db.get_cached_verdict("c") == {"verdict": "true"}
            db.close()
        finally:
            os.chmod(path, stat.S_IREAD | stat.S_IWRITE)

    def test_history_names_the_model(self, tmp_path):
        db = HuginnDB(tmp_path / "h.db")
        db.store_analysis("c", {"claim": "c"}, model_key=QWEN)
        assert db.get_recent_analyses()[0]["model_key"] == QWEN

    def test_cli_anthropic_key_matches_the_client_it_opens(self):
        from unittest.mock import MagicMock, patch

        from click.testing import CliRunner

        from huginn_muninn.cli import main
        from huginn_muninn.llm import AnthropicClient

        mock_db = MagicMock()
        mock_db.get_cached_verdict.return_value = {"verdict": "false"}
        with patch("huginn_muninn.cli.HuginnDB") as mock_db_cls:
            mock_db_cls.return_value.__enter__ = MagicMock(return_value=mock_db)
            mock_db_cls.return_value.__exit__ = MagicMock(return_value=False)
            CliRunner().invoke(main, ["check", "--json-output", "--provider", "anthropic",
                                      "--effort", "high", "some claim"],
                               env={"HUGINN_LLM_PROVIDER": None})
        client = SimpleNamespace(provider=AnthropicClient.provider, model="claude-opus-5-5", effort="high")
        assert mock_db.get_cached_verdict.call_args.kwargs["model_key"] == client_cache_key(client)

    def test_one_effort_provider_list(self):
        from huginn_muninn import cli, llm

        assert cli.CLAUDE_PROVIDERS is llm.EFFORT_PROVIDERS
