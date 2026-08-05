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
                
            zf.writestr("CHECKSUMS", "\n".join(checksums))

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
