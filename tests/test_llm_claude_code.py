"""Tests for ClaudeCodeClient: runs prompts through the headless Claude Code CLI (subprocess mocked)."""
from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace

import pytest

from huginn_muninn import llm
from huginn_muninn.llm import ClaudeCodeClient, LLMClient, create_client


def _ok(result="hello", cost=0.01, is_error=False):
    out = json.dumps({"type": "result", "is_error": is_error, "result": result, "total_cost_usd": cost})
    return SimpleNamespace(returncode=0, stdout=out, stderr="")


@pytest.fixture
def runs(monkeypatch):
    calls: list[dict] = []
    replies: list = []

    def fake_run(cmd, **kwargs):
        calls.append({"cmd": cmd, **kwargs})
        return replies.pop(0) if replies else _ok()

    monkeypatch.setattr(llm.subprocess, "run", fake_run)
    monkeypatch.setattr(llm.shutil, "which", lambda name: "/usr/bin/claude")
    return SimpleNamespace(calls=calls, replies=replies)


class TestClaudeCodeClient:
    def test_satisfies_protocol(self, runs):
        assert isinstance(ClaudeCodeClient(), LLMClient)

    def test_factory_builds_it(self, runs):
        c = create_client("claude-code", "", "claude-opus-5-5", effort="medium")
        assert isinstance(c, ClaudeCodeClient) and c.effort == "medium"

    def test_prompt_sent_on_stdin(self, runs):
        ClaudeCodeClient().generate("the claim")
        assert runs.calls[0]["input"] == "the claim"

    def test_model_and_effort_flags(self, runs):
        ClaudeCodeClient(model="claude-opus-5-5", effort="medium").generate("x")
        cmd = runs.calls[0]["cmd"]
        assert cmd[cmd.index("--model") + 1] == "claude-opus-5-5"
        assert cmd[cmd.index("--effort") + 1] == "medium"

    def test_isolation_flags_present(self, runs):
        ClaudeCodeClient().generate("x")
        cmd = runs.calls[0]["cmd"]
        for flag in ("-p", "--strict-mcp-config", "--no-session-persistence", "--disable-slash-commands"):
            assert flag in cmd
        assert cmd[cmd.index("--setting-sources") + 1] == ""
        assert cmd[cmd.index("--tools") + 1] == ""
        assert cmd[cmd.index("--output-format") + 1] == "json"

    def test_runs_outside_the_repo(self, runs):
        ClaudeCodeClient().generate("x")
        assert "huginn-claude-code" in str(runs.calls[0]["cwd"])

    def test_returns_result_text(self, runs):
        runs.replies.append(_ok(result='{"verdict": "false"}'))
        assert ClaudeCodeClient().generate("x") == '{"verdict": "false"}'

    def test_cost_accumulates(self, runs):
        runs.replies.extend([_ok(cost=0.25), _ok(cost=0.5)])
        c = ClaudeCodeClient()
        c.generate("a")
        c.generate("b")
        assert c.total_cost_usd == pytest.approx(0.75)

    def test_is_error_raises(self, runs):
        runs.replies.append(_ok(result="Credit balance too low", is_error=True))
        with pytest.raises(RuntimeError, match="Credit balance"):
            ClaudeCodeClient().generate("x")

    def test_nonzero_exit_raises(self, runs):
        runs.replies.append(SimpleNamespace(returncode=1, stdout="", stderr="boom"))
        with pytest.raises(RuntimeError, match="boom"):
            ClaudeCodeClient().generate("x")

    def test_timeout_raises_runtime_error(self, monkeypatch):
        monkeypatch.setattr(llm.shutil, "which", lambda name: "/usr/bin/claude")

        def slow(cmd, **kwargs):
            raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout"))

        monkeypatch.setattr(llm.subprocess, "run", slow)
        with pytest.raises(RuntimeError, match="timed out"):
            ClaudeCodeClient(timeout=1).generate("x")

    def test_check_available_false_without_cli(self, monkeypatch):
        monkeypatch.setattr(llm.shutil, "which", lambda name: None)
        assert ClaudeCodeClient().check_available() is False
