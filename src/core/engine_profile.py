"""Engine profile: the resolved configuration for one engine project.

A profile is the single source of truth for what a project is: target
platform, C++ standard, SDL2 version floor, module list, and render backend.
It is built from `engine.toml` and validated before anything touches disk.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

VALID_BACKENDS = frozenset({"opengl", "vulkan", "software", "d3d11"})
VALID_PLATFORMS = frozenset({"windows", "linux", "macos"})


class ProfileError(ValueError):
    """Raised when engine.toml is malformed or violates a constraint."""


@dataclass(frozen=True, slots=True)
class EngineProfile:
    name: str
    platform: str
    cxx_standard: int
    sdl2_min: str
    render_backend: str
    modules: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if self.platform not in VALID_PLATFORMS:
            raise ProfileError(f"platform {self.platform!r} not in {sorted(VALID_PLATFORMS)}")
        if self.render_backend not in VALID_BACKENDS:
            raise ProfileError(f"backend {self.render_backend!r} not in {sorted(VALID_BACKENDS)}")
        if self.cxx_standard not in (14, 17, 20, 23):
            raise ProfileError(f"cxx_standard {self.cxx_standard} unsupported")
        if not self.modules:
            raise ProfileError("at least one engine module is required")

    @classmethod
    def load(cls, path: Path) -> "EngineProfile":
        try:
            raw = tomllib.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ProfileError(f"engine.toml not found at {path}") from exc
        except tomllib.TOMLDecodeError as exc:
            raise ProfileError(f"engine.toml is not valid TOML: {exc}") from exc

        engine = raw.get("engine", {})
        try:
            profile = cls(
                name=engine["name"],
                platform=engine["platform"],
                cxx_standard=int(engine.get("cxx_standard", 17)),
                sdl2_min=engine.get("sdl2_min", "2.28.0"),
                render_backend=engine.get("render_backend", "opengl"),
                modules=tuple(engine.get("modules", ["render", "input", "audio", "scene"])),
            )
        except KeyError as exc:
            raise ProfileError(f"engine.toml missing required key: {exc}") from exc
        profile.validate()
        return profile