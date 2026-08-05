import re
import tomllib
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

@dataclass
class ManifestData:
    format_version: str
    id: str
    slug: str
    name: str
    version: str
    author_name: str
    author_handle: str
    description: str
    license: str = "MIT"
    entry_scene: str = "main"
    minimum_width: int = 40
    minimum_height: int = 20
    recommended_duration_ms: int = 5000
    supports_ascii: bool = True
    supports_monochrome: bool = True
    tags: List[str] = field(default_factory=list)

def validate_slug(slug: str) -> bool:
    return bool(re.match(r'^[a-z0-9-]+$', slug))

def validate_semver(version: str) -> bool:
    return bool(re.match(r'^\d+\.\d+\.\d+$', version))

def validate_id(id_str: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9_.-]+$', id_str))

def load_manifest(path: str | Path) -> ManifestData:
    with open(path, "rb") as f:
        data = tomllib.load(f)
    
    # validate
    if not validate_semver(data.get("version", "")):
        raise ValueError("Invalid version format")
    if not validate_slug(data.get("slug", "")):
        raise ValueError("Invalid slug format")
    if not validate_id(data.get("id", "")):
        raise ValueError("Invalid ID format")
        
    return ManifestData(**data)

def save_manifest(data: ManifestData, path: str | Path) -> None:
    # Not required to use tomllib for writing, just write simple string since we don't have tomli_w
    with open(path, "w") as f:
        f.write(f'format_version = "{data.format_version}"\n')
        f.write(f'id = "{data.id}"\n')
        f.write(f'slug = "{data.slug}"\n')
        f.write(f'name = "{data.name}"\n')
        f.write(f'version = "{data.version}"\n')
        f.write(f'author_name = "{data.author_name}"\n')
        f.write(f'author_handle = "{data.author_handle}"\n')
        f.write(f'description = "{data.description}"\n')
        f.write(f'license = "{data.license}"\n')
        f.write(f'entry_scene = "{data.entry_scene}"\n')
        f.write(f'minimum_width = {data.minimum_width}\n')
        f.write(f'minimum_height = {data.minimum_height}\n')
        f.write(f'recommended_duration_ms = {data.recommended_duration_ms}\n')
        f.write(f'supports_ascii = {"true" if data.supports_ascii else "false"}\n')
        f.write(f'supports_monochrome = {"true" if data.supports_monochrome else "false"}\n')
        f.write('tags = [')
        f.write(', '.join(f'"{t}"' for t in data.tags))
        f.write(']\n')
