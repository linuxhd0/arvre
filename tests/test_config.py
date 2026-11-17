from pathlib import Path

import pytest
from test_commands import make_session

from arvre import cli
from arvre.commands import resume_command
from arvre.config import DEFAULT_CLAUDE_DIR, claude_env, resolve_claude_dir
from arvre.config import projects_root as projects_dir


def test_default_is_dot_claude():
    assert resolve_claude_dir(None, {}) == DEFAULT_CLAUDE_DIR == Path.home() / ".claude"


def test_precedence_flag_then_arvre_env_then_claude_env():
    env = {"ARVRE_CLAUDE_DIR": "/a", "CLAUDE_CONFIG_DIR": "/b"}
    assert resolve_claude_dir("/flag", env) == Path("/flag")
    assert resolve_claude_dir(None, env) == Path("/a")
    assert resolve_claude_dir(None, {"CLAUDE_CONFIG_DIR": "/b"}) == Path("/b")


def test_tilde_is_expanded():
    assert resolve_claude_dir("~/.claudeultra", {}) == Path.home() / ".claudeultra"


def test_projects_root():
    assert projects_dir(Path("/x")) == Path("/x/projects")


def test_claude_env_only_for_non_default():
    assert claude_env(None) is None
    assert claude_env(DEFAULT_CLAUDE_DIR) is None
    assert claude_env(Path("/x"))["CLAUDE_CONFIG_DIR"] == "/x"


def test_resume_command_carries_non_default_dir():
    session = make_session()
    assert "CLAUDE_CONFIG_DIR" not in resume_command(session)
    assert "CLAUDE_CONFIG_DIR=/x/y claude --resume abc" in resume_command(session, Path("/x/y"))


def test_cli_reads_sessions_from_claude_dir(projects_root, tmp_path_factory, capsys, monkeypatch):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path_factory.mktemp("cache")))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path_factory.mktemp("data")))
    claude_dir = tmp_path_factory.mktemp("claudeultra")
    (claude_dir / "projects").symlink_to(projects_root)
    cli.main(["--claude-dir", str(claude_dir), "--print", "--no-cache", "--all-time", "--dir", "/Users/me/project"])
    assert "Auth refactor" in capsys.readouterr().out


def test_cli_rejects_missing_dir(tmp_path):
    with pytest.raises(SystemExit):
        cli.main(["--claude-dir", str(tmp_path / "nope"), "--print"])
