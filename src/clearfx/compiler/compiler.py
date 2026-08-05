import json
import importlib.util
import inspect
from pathlib import Path
from typing import Any
import sys
import tomllib as toml
from ..formats.package import PackageBuilder
from ..formats.manifest import ManifestData

class AnimationCompiler:
    def __init__(self):
        pass

    def pack(self, directory: str | Path) -> str:
        d = Path(directory)
        manifest_path = d / "manifest.toml"
        design_path = d / "src" / "design.py"
        
        if not manifest_path.exists():
            raise FileNotFoundError(f"Missing {manifest_path}")
        if not design_path.exists():
            design_path = d / "design.py"
            if not design_path.exists():
                raise FileNotFoundError(f"Missing design.py in {d}")
                
        # Parse manifest
        from ..formats.manifest import load_manifest
        manifest_data = load_manifest(manifest_path)
        
        slug = manifest_data.slug
        out_file = d / f"{slug}.clearfx"
        
        # Load design dynamically to extract elements
        spec = importlib.util.spec_from_file_location("dynamic_pack", str(design_path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        from ..engine.animation import Animation
        anim_class = None
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if issubclass(obj, Animation) and obj is not Animation and obj.__name__ != 'CreatorAnimation':
                anim_class = obj
                break
                
        if anim_class is None:
            raise ValueError("No Animation subclass found in design.py")
            
        # Instantiate to get the declarative elements
        anim_instance = anim_class()
        elements = getattr(anim_instance, "elements", [])
        keyframes = getattr(anim_instance, "keyframes", [])
        
        design_data = {
            "elements": elements,
            "keyframes": keyframes
        }
        
        builder = PackageBuilder()
        builder.add_manifest(manifest_data)
        builder.add_design(design_data)
        
        # Add assets
        assets_dir = d / "assets"
        if assets_dir.exists():
            for p in assets_dir.glob("**/*"):
                if p.is_file():
                    arcname = f"assets/{p.relative_to(assets_dir)}"
                    with open(p, "rb") as f:
                        builder.add_asset(arcname, f.read())
                        
        builder.build(out_file)
        return str(out_file)

