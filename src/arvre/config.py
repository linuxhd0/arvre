"""Where Claude Code keeps its data (~/.claude by default)."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_CLAUDE_DIR = Path.home() / ".claude"


def resolve_claude_dir(explicit: str | None = None, environ: dict[str, str] | None = None) -> Path:
    """Pick the Claude config directory.

    Precedence: the --claude-dir flag, $ARVRE_CLAUDE_DIR, $CLAUDE_CONFIG_DIR
    (the variable Claude Code itself honours), then ~/.claude.
    """
    env = os.environ if environ is None else environ
    chosen = explicit or env.get("ARVRE_CLAUDE_DIR") or env.get("CLAUDE_CONFIG_DIR")
    return Path(chosen).expanduser() if chosen else DEFAULT_CLAUDE_DIR


def projects_root(claude_dir: Path) -> Path:
    return claude_dir / "projects"


def claude_env(claude_dir: Path | None) -> dict[str, str] | None:
    """Environment for a spawned `claude` so it reads the same directory arvre does.

    None (inherit as-is) when arvre is using the default location.
    """
    if claude_dir is None or claude_dir == DEFAULT_CLAUDE_DIR:
        return None
    return {**os.environ, "CLAUDE_CONFIG_DIR": str(claude_dir)}
