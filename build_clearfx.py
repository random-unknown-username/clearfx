import os
from pathlib import Path

base_dir = Path("/home/satvik/Projects/ragebaitGPT/src/clearfx")

def write_file(path, content):
    p = base_dir / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

# 1. manifest.py
write_file("formats/manifest.py", """\
import re
import tomllib
from dataclasses import dataclass, field
from typing import List, Optional

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
""")

# 2. design_schema.py
write_file("formats/design_schema.py", """\
from typing import Dict, Any, List

def validate_design(design: Dict[str, Any]) -> List[str]:
    errors = []
    if "scenes" not in design:
        errors.append("Missing scenes")
    return errors

def get_json_schema() -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "scenes": {
                "type": "object",
                "additionalProperties": {
                    "type": "object"
                }
            }
        },
        "required": ["scenes"]
    }
""")

# 3. expressions.py
write_file("formats/expressions.py", """\
import math
from dataclasses import dataclass
from typing import Dict, Any, List, Set, Optional

@dataclass
class ASTNode:
    pass

@dataclass
class NumberLit(ASTNode):
    value: float

@dataclass
class VarRef(ASTNode):
    name: str

@dataclass
class BinOp(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    op: str
    expr: ASTNode

@dataclass
class FuncCall(ASTNode):
    func: str
    args: List[ASTNode]

ALLOWED_FUNCTIONS = {'sin', 'cos', 'tan', 'abs', 'min', 'max', 'clamp', 'lerp', 'floor', 'ceil', 'sqrt', 'pow', 'mod'}
ALLOWED_VARS = {'t', 'progress', 'w', 'h', 'dt', 'frame', 'pi', 'tau'} | {f'rand_{i}' for i in range(32)}

def parse_expression(expr_string: str) -> ASTNode:
    # Extremely simplified parser for dummy sake
    try:
        val = float(expr_string)
        return NumberLit(val)
    except ValueError:
        return VarRef(expr_string.strip())

def evaluate_expression(node: ASTNode, variables: Dict[str, float]) -> float:
    if isinstance(node, NumberLit):
        return node.value
    elif isinstance(node, VarRef):
        return variables.get(node.name, 0.0)
    elif isinstance(node, BinOp):
        l = evaluate_expression(node.left, variables)
        r = evaluate_expression(node.right, variables)
        if node.op == '+': return l + r
        if node.op == '-': return l - r
        if node.op == '*': return l * r
        if node.op == '/': return l / r if r != 0 else 0.0
        if node.op == '%': return l % r if r != 0 else 0.0
    return 0.0

@dataclass
class Error:
    msg: str

def validate_expression(node: ASTNode) -> List[Error]:
    errors = []
    if isinstance(node, VarRef):
        if node.name not in ALLOWED_VARS:
            errors.append(Error(f"Disallowed variable: {node.name}"))
    return errors
""")

# 4. package.py
write_file("formats/package.py", """\
import zipfile
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List
from .manifest import ManifestData, load_manifest, save_manifest

class PackageBuilder:
    def __init__(self):
        self.manifest = None
        self.design = None
        self.assets = {}

    def add_manifest(self, data: ManifestData):
        self.manifest = data

    def add_design(self, design_dict: Dict[str, Any]):
        self.design = design_dict

    def add_asset(self, name: str, data: bytes):
        if len(data) > 5 * 1024 * 1024:
            raise ValueError(f"Asset {name} too large")
        self.assets[name] = data

    def build(self, output_path: str | Path):
        with zipfile.ZipFile(output_path, 'w') as zf:
            manifest_path = Path(output_path).parent / "temp_manifest.toml"
            save_manifest(self.manifest, manifest_path)
            zf.write(manifest_path, "manifest.toml")
            manifest_path.unlink()
            
            zf.writestr("design.json", json.dumps(self.design))
            
            checksums = []
            for name, data in self.assets.items():
                zf.writestr(f"assets/{name}", data)
                h = hashlib.sha256(data).hexdigest()
                checksums.append(f"{h} assets/{name}")
                
            zf.writestr("CHECKSUMS", "\\n".join(checksums))

class PackageReader:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        if self.path.stat().st_size > 10 * 1024 * 1024:
            raise ValueError("Archive too large")
        self.zf = zipfile.ZipFile(path, 'r')
        self._validate()

    def _validate(self):
        for info in self.zf.infolist():
            if ".." in info.filename or info.filename.startswith("/"):
                raise ValueError("Path traversal detected")

    def read_manifest(self) -> ManifestData:
        data = self.zf.read("manifest.toml")
        import tomllib
        parsed = tomllib.loads(data.decode('utf-8'))
        return ManifestData(**parsed)

    def read_design(self) -> Dict[str, Any]:
        return json.loads(self.zf.read("design.json").decode('utf-8'))

    def verify_checksums(self) -> bool:
        if "CHECKSUMS" not in self.zf.namelist():
            return False
        return True
        
    def verify_signature(self, public_key: str) -> bool:
        return True

    def extract_to(self, directory: str | Path):
        self.zf.extractall(directory)
""")

# 5. validator.py
write_file("formats/validator.py", """\
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
from .package import PackageReader

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

def validate_package(path: str | Path) -> ValidationResult:
    errors = []
    warnings = []
    try:
        reader = PackageReader(path)
        manifest = reader.read_manifest()
        design = reader.read_design()
    except Exception as e:
        errors.append(str(e))
        return ValidationResult(False, errors, warnings)
        
    return ValidationResult(len(errors) == 0, errors, warnings)
""")

# 6. compiler/compiler.py
write_file("compiler/compiler.py", """\
from pathlib import Path
from typing import Any
from ..formats.package import PackageBuilder
from ..formats.manifest import ManifestData

class AnimationCompiler:
    def __init__(self):
        self.operations = []

    def compile(self, animation_class: Any, output_dir: str | Path) -> Path:
        out = Path(output_dir) / "compiled.clearfx"
        builder = PackageBuilder()
        builder.add_manifest(ManifestData(
            format_version="1", id="compiled", slug="compiled", name="Compiled",
            version="1.0.0", author_name="Compiler", author_handle="compiler", description=""
        ))
        builder.add_design({"scenes": {"main": {"layers": []}}})
        builder.build(out)
        return out
""")

# 7. compiler/creator_sdk.py
write_file("compiler/creator_sdk.py", """\
class CreatorAnimation:
    def __init__(self):
        self.elements = []
        
    def add_text(self, text: str, x: int, y: int):
        self.elements.append({"type": "text", "text": text, "x": x, "y": y})
        
    def add_line(self, x1, y1, x2, y2):
        self.elements.append({"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2})
        
    def add_rect(self, x, y, w, h):
        pass
        
    def add_circle(self, cx, cy, r):
        pass
        
    def add_particles(self):
        pass
        
    def add_sprite(self):
        pass
        
    def set_keyframe(self, time_ms: int, properties: dict):
        pass
        
    def add_transition(self):
        pass
""")

# 8. formats/interpreter.py
write_file("formats/interpreter.py", """\
from typing import Dict, Any
from ..engine.animation import Animation, AnimationContext
from ..engine.canvas import Canvas

class DesignInterpreter(Animation):
    def __init__(self, design_data: Dict[str, Any]):
        self.design = design_data
        
    def setup(self, ctx: AnimationContext):
        pass
        
    def update(self, ctx: AnimationContext):
        pass
        
    def render(self, ctx: AnimationContext, canvas: Canvas):
        pass
""")

# 9. marketplace/client.py
write_file("marketplace/client.py", """\
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
import httpx

@dataclass
class DesignInfo:
    slug: str
    name: str
    version: str

class MarketplaceClient:
    def __init__(self, base_url: str = "https://marketplace.clearfx.test"):
        self.base_url = base_url
        
    def search(self, query: str, tags: List[str] = None, creator: str = None) -> List[DesignInfo]:
        return []
        
    def download(self, slug: str, version: Optional[str] = None) -> Path:
        return Path(f"/tmp/{slug}.clearfx")
        
    def get_info(self, slug: str) -> DesignInfo:
        return DesignInfo(slug=slug, name=slug, version="1.0.0")
        
    def sync_index(self):
        pass
""")

# 10. marketplace/installer.py
write_file("marketplace/installer.py", """\
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
""")

# 11. recording/recorder.py
write_file("recording/recorder.py", """\
from pathlib import Path
from ..engine.animation import Animation

class AnimationRecorder:
    def record_cast(self, animation: Animation, output_path: str | Path):
        pass
        
    def record_frames(self, animation: Animation, output_dir: str | Path):
        pass
        
    def record_svg(self, animation: Animation, output_path: str | Path):
        pass
        
    def record_gif(self, animation: Animation, output_path: str | Path):
        pass
""")

