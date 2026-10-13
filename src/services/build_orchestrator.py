"""Build orchestrator.

Wraps `cmake` configure + build for a generated project. Never shells out
with `shell=True`; argv is passed as a list so user-supplied config cannot
inject commands.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

BUILD_DIR = "out"
DEFAULT_TIMEOUT_S = 900


@dataclass(frozen=True, slots=True)
class BuildResult:
    ok: bool
    exit_code: int
    summary: str
    artifact: Path | None


class BuildOrchestrator:
    def __init__(self, project: Path) -> None:
        self.project = project
        self.build_dir = project / BUILD_DIR

    def _cpu_count(self) -> int:
        return os.cpu_count() or 4

    def _run(self, argv: list[str]) -> tuple[int, str]:
        try:
            proc = subprocess.run(
                argv,
                cwd=self.project,
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT_S,
                check=False,
            )
        except FileNotFoundError as exc:
            return 127, f"tool missing: {exc}"
        except subprocess.TimeoutExpired:
            return 124, f"timeout after {DEFAULT_TIMEOUT_S}s"
        tail = (proc.stderr or proc.stdout).splitlines()[-12:]
        return proc.returncode, "\n".join(tail)

    def build(self, *, config: str, jobs: int = 0) -> BuildResult:
        self.build_dir.mkdir(parents=True, exist_ok=True)
        jobs = jobs or self._cpu_count()

        configure = [
            "cmake",
            "-S", ".",
            "-B", str(self.build_dir),
            "-G", "Ninja",
            f"-DCMAKE_BUILD_TYPE={config}",
        ]
        rc, out = self._run(configure)
        if rc != 0:
            return BuildResult(False, rc, f"configure failed:\n{out}", None)

        compile_argv = [
            "cmake", "--build", str(self.build_dir),
            "--config", config,
            "--parallel", str(jobs),
        ]
        rc, out = self._run(compile_argv)
        if rc != 0:
            return BuildResult(False, rc, f"compile failed:\n{out}", None)

        candidates = list(self.build_dir.rglob("*_game.exe")) or list(
            self.build_dir.rglob("*_game")
        )
        artifact = candidates[0] if candidates else None
        return BuildResult(True, 0, "ok", artifact)