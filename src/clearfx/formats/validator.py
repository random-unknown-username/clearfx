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
