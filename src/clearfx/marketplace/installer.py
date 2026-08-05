from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
import shutil
import zipfile

from clearfx.marketplace.client import MarketplaceClient
from clearfx.core.config import get_data_dir

@dataclass
class InstallResult:
    success: bool
    slug: str
    version: str
    error: Optional[str] = None
    path: Optional[Path] = None

@dataclass
class InstalledPackage:
    slug: str
    path: Path

def install_package(slug: str) -> InstallResult:
    """Install a package. Since marketplace is local, this just checks availability."""
    from clearfx.core.registry import AnimationRegistry
    registry = AnimationRegistry()
    
    anim_cls = registry.get_animation(slug)
    if not anim_cls:
        return InstallResult(False, slug, "0.0.0", f"Package '{slug}' not found in catalog.")
        
    meta = anim_cls.meta
    source = "builtin"
    # Check if community
    if hasattr(anim_cls, "__module__") and "interpreter" in anim_cls.__module__:
        source = "community"
        
    if source == "builtin" or getattr(meta, "id", "").startswith("io.clearfx.builtin"):
        return InstallResult(True, slug, meta.version, f"'{slug}' is a built-in animation and does not need installation.", None)
        
    return InstallResult(True, slug, meta.version, f"'{slug}' is already installed locally.", get_data_dir() / "designs" / slug)

def uninstall_package(slug: str):
    """Remove an installed package."""
    pkg_dir = get_data_dir() / "designs" / slug
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    else:
        raise ValueError(f"Package '{slug}' is not installed.")

def list_installed() -> List[InstalledPackage]:
    """List all installed community packages."""
    designs_dir = get_data_dir() / "designs"
    installed = []
    if designs_dir.exists():
        for pkg_dir in designs_dir.iterdir():
            if pkg_dir.is_dir() and (pkg_dir / "manifest.toml").exists():
                installed.append(InstalledPackage(slug=pkg_dir.name, path=pkg_dir))
    return installed

def get_installed(slug: str) -> Optional[InstalledPackage]:
    """Get info about an installed package."""
    pkg_dir = get_data_dir() / "designs" / slug
    if pkg_dir.exists() and (pkg_dir / "manifest.toml").exists():
        return InstalledPackage(slug=slug, path=pkg_dir)
    return None
