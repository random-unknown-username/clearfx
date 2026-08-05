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
