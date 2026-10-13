"""Asset pipeline.

Validates `assets/manifest.toml` — every declared asset must exist on disk,
have a recognized extension, and not collide with another entry's logical
name. Packs validated assets into a flat `assets.pak` staging directory.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

KNOWN_EXT = frozenset({".png", ".jpg", ".bmp", ".wav", ".ogg", ".ttf", ".json", ".tmx"})


@dataclass(frozen=True, slots=True)
class AssetEntry:
    logical: str
    path: Path
    kind: str


@dataclass(frozen=True, slots=True)
class AssetReport:
    ok: bool
    entries: tuple[AssetEntry, ...]
    problems: tuple[str, ...]

    def render(self) -> str:
        if self.ok:
            return f"[green]assets ok[/green] — {len(self.entries)} entries validated"
        return "[red]asset problems[/red]:\n" + "\n".join(f"  - {p}" for p in self.problems)


class AssetPipeline:
    def __init__(self, project: Path) -> None:
        self.project = project
        self.manifest = project / "assets" / "manifest.toml"

    def _load(self) -> list[AssetEntry]:
        if not self.manifest.exists():
            return []
        raw = tomllib.loads(self.manifest.read_text(encoding="utf-8"))
        out: list[AssetEntry] = []
        for item in raw.get("asset", []):
            out.append(
                AssetEntry(
                    logical=item["name"],
                    path=self.project / "assets" / item["file"],
                    kind=item.get("kind", "unknown"),
                )
            )
        return out

    def validate(self) -> AssetReport:
        entries = self._load()
        problems: list[str] = []
        seen: dict[str, str] = {}
        for entry in