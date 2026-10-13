"""Toolchain preflight for the sdl2-game-engine-starter.

Checks that cmake, a C++17 compiler, and SDL2 development headers are
reachable from PATH. Returns (ok, lines) where lines is rich-markup text.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolCheck:
    name: str
    binary: str
    version_args: list[str]


CHECKS: tuple[ToolCheck, ...] = (
    ToolCheck("cmake", "cmake", ["--version"]),
    ToolCheck("ninja", "ninja", ["--version"]),
    ToolCheck("c++ compiler", "c++", ["--version"]),
)


def _probe(tool: ToolCheck) -> tuple[bool, str]:
    path = shutil.which(tool.binary)
    if path is None:
        return False, f"[red]missing[/red] {tool.name} ({tool.binary})"
    try:
        out = subprocess.run(
            [path, *tool.version_args],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"[yellow]unusable[/yellow] {tool.name}: {exc}"
    first = (out.stdout or out.stderr).splitlines()
    head = first[0] if first else "(no version output)"
    return True, f"[green]ok[/green] {tool.name}: {head}"


def run_preflight() -> tuple[bool, list[str]]:
    """Run every tool check. Returns (all_ok, rendered lines)."""
    lines: list[str] = []
    ok = True
    for tool in CHECKS:
        passed, line = _probe(tool)
        ok = ok and passed
        lines.append(line)
    return ok, lines