"""Command-line entry point for the sdl2-game-engine-starter tooling.

Exposes the `sdl2-starter` console script. Commands are thin wrappers around
the service layer; no business logic lives here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console

from src.bootstrap.preflight import run_preflight
from src.services.project_generator import ProjectGenerator
from src.services.build_orchestrator import BuildOrchestrator
from src.services.asset_pipeline import AssetPipeline

console = Console()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="sdl2-game-engine-starter")
def main() -> None:
    """sdl2-game-engine-starter: scaffold, build, and validate a C++/SDL2 engine."""


@main.command("new")
@click.argument("target", type=click.Path(path_type=Path))
@click.option("--template", default="default", show_default=True)
@click.option("--force", is_flag=True, help="Overwrite an existing target directory.")
def cmd_new(target: Path, template: str, force: bool) -> None:
    """Generate a new engine project at TARGET."""
    gen = ProjectGenerator(template=template)
    gen.generate(target, force=force)
    console.print(f"[green]scaffolded[/green] {target}")


@main.command("build")
@click.argument("project", type=click.Path(exists=True, path_type=Path))
@click.option("--config", "config_name", default="Release", show_default=True)
@click.option("--jobs", type=int, default=0, help="0 = auto-detect CPU count.")
def cmd_build(project: Path, config_name: str, jobs: int) -> None:
    """Configure and build the C++/SDL2 engine in PROJECT."""
    orch = BuildOrchestrator(project)
    result = orch.build(config=config_name, jobs=jobs)
    if not result.ok:
        console.print(f"[red]build failed[/red]: {result.summary}")
        sys.exit(result.exit_code)
    console.print(f"[green]built[/green] {result.artifact}")


@main.command("assets")
@click.argument("project", type=click.Path(exists=True, path_type=Path))
def cmd_assets(project: Path) -> None:
    """Validate and pack the asset manifest for PROJECT."""
    pipe = AssetPipeline(project)
    report = pipe.validate()
    console.print(report.render())


@main.command("doctor")
def cmd_doctor() -> None:
    """Check that the local toolchain can build the engine."""
    ok, lines = run_preflight()
    for line in lines:
        console.print(line)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()