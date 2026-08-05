import json
import urllib.request
import urllib.parse
from dataclasses import dataclass
from typing import List, Optional, Dict
from pathlib import Path
import tempfile
import base64
import zipfile
import importlib.util
import inspect
from clearfx.engine.animation import Animation

@dataclass
class DesignInfo:
    slug: str
    name: str
    version: str
    description: str
    author: str
    upvotes: int

class MarketplaceClient:
    def __init__(self, project_id: str = "clearfx-29744"):
        self.project_id = project_id
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"
        
    def _parse_document(self, doc: Dict) -> DesignInfo:
        fields = doc.get("fields", {})
        
        # Firestore REST API represents strings as {"stringValue": "..."}
        # and ints as {"integerValue": "..."}
        slug = doc.get("name", "").split("/")[-1]
        name = fields.get("name", {}).get("stringValue", slug)
        version = fields.get("version", {}).get("stringValue", "1.0.0")
        desc = fields.get("description", {}).get("stringValue", "")
        author = fields.get("author_handle", {}).get("stringValue", "unknown")
        upvotes = int(fields.get("upvotes_count", {}).get("integerValue", "0"))
        
        return DesignInfo(
            slug=slug,
            name=name,
            version=version,
            description=desc,
            author=author,
            upvotes=upvotes
        )

    def search(self, query: str = None, tags: List[str] = None, creator: str = None) -> List[DesignInfo]:
        """Fetch all designs from Firestore (no complex querying in MVP)."""
        url = f"{self.base_url}/designs"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            docs = data.get("documents", [])
            designs = [self._parse_document(doc) for doc in docs]
            
            # Simple client-side filtering for MVP
            if query:
                designs = [d for d in designs if query.lower() in d.name.lower() or query.lower() in d.slug.lower()]
            if creator:
                designs = [d for d in designs if creator.lower() == d.author.lower()]
                
            # Sort by upvotes descending
            designs.sort(key=lambda x: x.upvotes, reverse=True)
            return designs
            
        except Exception as e:
            print(f"Error fetching catalog from Firestore: {e}")
            return []
            
    def get_info(self, slug: str) -> Optional[DesignInfo]:
        url = f"{self.base_url}/designs/{slug}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            return self._parse_document(data)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            print(f"HTTP error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching design '{slug}': {e}")
            return None
            
    def download(self, slug: str, version: Optional[str] = None) -> Path:
        """Download the .clearfx package payload from Firestore and reconstruct it."""
        url = f"{self.base_url}/designs/{slug}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            fields = data.get("fields", {})
            package_b64 = fields.get("package_b64", {}).get("stringValue")
            code = fields.get("code", {}).get("stringValue")
            
            out_path = Path(tempfile.gettempdir()) / f"{slug}.clearfx"
            
            if package_b64:
                package_bytes = base64.b64decode(package_b64)
                out_path.write_bytes(package_bytes)
                return out_path
                
            elif code:
                # Compile the raw Python code into a .clearfx zip
                temp_dir = Path(tempfile.mkdtemp())
                design_py = temp_dir / "design.py"
                design_py.write_text(code)
                
                manifest_content = f"""format_version = 1
id = "io.clearfx.community.{slug}"
slug = "{slug}"
name = "{fields.get("name", {}).get("stringValue", slug)}"
version = "{fields.get("version", {}).get("stringValue", "1.0.0")}"
author_name = "Community Creator"
author_handle = "{fields.get("author_handle", {}).get("stringValue", "@unknown")}"
description = "{fields.get("description", {}).get("stringValue", "")}"
entry_scene = "main"
recommended_duration_ms = 3000
"""
                manifest_path = temp_dir / "manifest.toml"
                manifest_path.write_text(manifest_content)
                
                # Execute to get AST
                spec = importlib.util.spec_from_file_location("dynamic_compile", str(design_py))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                anim_class = None
                for name, obj in inspect.getmembers(mod, inspect.isclass):
                    if issubclass(obj, Animation) and obj is not Animation and obj.__name__ != 'CreatorAnimation':
                        anim_class = obj
                        break
                
                if not anim_class:
                    raise RuntimeError("No Animation class found in the provided code.")
                    
                anim_instance = anim_class()
                design_data = {
                    "elements": getattr(anim_instance, "elements", []),
                    "keyframes": getattr(anim_instance, "keyframes", [])
                }
                
                design_json = temp_dir / "design.json"
                with open(design_json, "w") as f:
                    json.dump(design_data, f)
                    
                # Zip it up
                with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.write(manifest_path, "manifest.toml")
                    zf.write(design_json, "design.json")
                    
                return out_path

            else:
                raise ValueError(f"Design '{slug}' has no package data or code.")
                
        except Exception as e:
            raise RuntimeError(f"Failed to download package '{slug}': {e}")
            
    def sync_index(self):
        # Firestore always pulls fresh data, no local sync index needed for MVP
        pass
