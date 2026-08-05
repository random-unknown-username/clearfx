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
    """Download and install a package from the marketplace."""
    client = MarketplaceClient()
    
    try:
        # Download the package .clearfx file (zip) to a temp location
        temp_zip_path = client.download(slug)
    except Exception as e:
        return InstallResult(False, slug, "0.0.0", str(e))
        
    try:
        designs_dir = get_data_dir() / "designs"
        pkg_dir = designs_dir / slug
        
        # Remove old version if exists
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)
            
        pkg_dir.mkdir(parents=True, exist_ok=True)
        
        # Unpack the downloaded zip
        with zipfile.ZipFile(temp_zip_path, 'r') as zf:
            zf.extractall(pkg_dir)
            
        # Try to read version from manifest.toml
        version = "1.0.0"
        manifest_path = pkg_dir / "manifest.toml"
        if manifest_path.exists():
            import tomllib
            manifest = tomllib.loads(manifest_path.read_text())
            version = manifest.get("version", "1.0.0")
            
        return InstallResult(True, slug, version, None, pkg_dir)
    except Exception as e:
        return InstallResult(False, slug, "0.0.0", f"Extraction failed: {e}")
    finally:
        if temp_zip_path.exists():
            temp_zip_path.unlink()

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
