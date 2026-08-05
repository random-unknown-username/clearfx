"""Animation registry — discovers and manages built-in and community animations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type


@dataclass
class AnimationInfo:
    """Lightweight info about a registered animation."""
    slug: str
    name: str
    author_name: str
    author_handle: str
    description: str
    source: str  # "builtin" or "community"
    tags: list[str] = field(default_factory=list)
    version: str = "1.0"
    min_width: int = 40
    min_height: int = 12
    recommended_duration_ms: int = 1200
    supports_ascii: bool = True
    supports_monochrome: bool = True


class AnimationRegistry:
    """Discovers and manages built-in and installed community animations."""

    def __init__(self) -> None:
        self._builtin: dict[str, type] = {}
        self._community: dict[str, Any] = {}
        self._loaded = False

    def _discover(self) -> None:
        """Load built-in animations from the animations package."""
        if self._loaded:
            return

        try:
            from clearfx.animations import BUILTIN_ANIMATIONS
            for anim_cls in BUILTIN_ANIMATIONS:
                meta = anim_cls.meta
                self._builtin[meta.slug] = anim_cls
        except ImportError:
            pass

        # Discover installed community packages
        self._discover_community()
        self._loaded = True

    def _discover_community(self) -> None:
        """Discover installed community .clearfx packages."""
        try:
            from clearfx.core.config import get_data_dir
            designs_dir = get_data_dir() / "designs"
            if designs_dir.exists():
                for pkg_dir in designs_dir.iterdir():
                    if pkg_dir.is_dir():
                        manifest_path = pkg_dir / "manifest.toml"
                        if manifest_path.exists():
                            self._community[pkg_dir.name] = {
                                "path": pkg_dir,
                                "source": "community",
                            }
        except Exception:
            pass

    def get_animation(self, slug: str) -> Optional[type]:
        """Get an animation class by slug.

        Returns the animation class or None if not found.
        """
        self._discover()

        # Try built-in first
        if slug in self._builtin:
            return self._builtin[slug]

        # Try community
        if slug in self._community:
            try:
                from clearfx.formats.interpreter import DesignInterpreter
                pkg_path = self._community[slug]["path"]
                interpreter = DesignInterpreter()
                return interpreter.load(pkg_path)
            except Exception:
                return None

        return None

    def list_animations(self, source: str | None = None) -> list[dict[str, Any]]:
        """List all available animations as dicts.

        Args:
            source: Filter by 'builtin', 'community', or None/all for both.
        """
        self._discover()
        results: list[dict[str, Any]] = []

        if source in (None, "all", "builtin"):
            for slug, anim_cls in self._builtin.items():
                meta = anim_cls.meta
                results.append({
                    "slug": meta.slug,
                    "name": meta.name,
                    "author_name": meta.author_name,
                    "author_handle": meta.author_handle,
                    "description": meta.description,
                    "tags": meta.tags,
                    "version": meta.version,
                    "source": "builtin",
                    "min_width": meta.min_width,
                    "min_height": meta.min_height,
                    "recommended_duration_ms": meta.recommended_duration_ms,
                    "supports_ascii": meta.supports_ascii,
                    "supports_monochrome": meta.supports_monochrome,
                })

        if source in (None, "all", "community"):
            for slug, info in self._community.items():
                results.append({
                    "slug": slug,
                    "name": slug.replace("-", " ").title(),
                    "author_handle": "community",
                    "description": "",
                    "tags": [],
                    "source": "community",
                })

        return results

    def is_installed(self, slug: str) -> bool:
        """Check if an animation is available (built-in or installed)."""
        self._discover()
        return slug in self._builtin or slug in self._community

    def get_all_builtin_classes(self) -> list[type]:
        """Get all built-in animation classes."""
        self._discover()
        return list(self._builtin.values())
