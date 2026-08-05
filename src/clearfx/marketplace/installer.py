from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import shutil

@dataclass
class InstallResult:
    success: bool
    path: Optional[Path] = None

@dataclass
class InstalledPackage:
    slug: str
    path: Path

def install_package(path_or_slug: str | Path) -> InstallResult:
    return InstallResult(True, Path("/tmp/installed.clearfx"))

def uninstall_package(slug: str):
    pass

def rollback(slug: str):
    pass

def list_installed() -> list:
    return []

def get_installed(slug: str) -> Optional[InstalledPackage]:
    return None
