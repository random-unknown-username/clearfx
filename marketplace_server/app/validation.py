import json
import zipfile
import io
from typing import Tuple

def validate_package(package_bytes: bytes) -> Tuple[bool, list, list]:
    errors = []
    warnings = []
    
    if len(package_bytes) > 10 * 1024 * 1024:
        errors.append("Package size exceeds 10MB limit.")
        return False, errors, warnings
        
    try:
        with zipfile.ZipFile(io.BytesIO(package_bytes)) as zf:
            files = zf.namelist()
            if "manifest.json" not in files:
                errors.append("Missing manifest.json in package.")
                return False, errors, warnings
                
            manifest_bytes = zf.read("manifest.json")
            try:
                manifest = json.loads(manifest_bytes.decode('utf-8'))
            except json.JSONDecodeError:
                errors.append("Invalid JSON in manifest.json.")
                return False, errors, warnings
                
            required_keys = ["id", "name", "version", "author"]
            for key in required_keys:
                if key not in manifest:
                    errors.append(f"Missing required key in manifest: {key}")
                    
    except zipfile.BadZipFile:
        errors.append("Invalid zip file format.")
        
    return len(errors) == 0, errors, warnings
