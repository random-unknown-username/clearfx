import json
import os
from typing import Dict, Any, List
from ..engine.animation import Animation, AnimationContext, AnimationMeta
from ..engine.canvas import Canvas

class DesignInterpreter(Animation):
    def __init__(self):
        self.design: Dict[str, Any] = {}
        self.elements: List[Dict[str, Any]] = []
        self.keyframes: List[Dict[str, Any]] = []
        # Fallback meta if not set by load()
        self.__class__.meta = AnimationMeta(
            id="io.clearfx.interpreter", slug="interpreter", name="Interpreter",
            author_name="Unknown", author_handle="@unknown", description="Loaded from JSON",
            tags=[], version="1.0", min_width=40, min_height=12, recommended_duration_ms=1000,
            supports_ascii=True, supports_monochrome=True
        )

    def load(self, package_dir: str) -> type:
        design_path = os.path.join(package_dir, "design.json")
        manifest_path = os.path.join(package_dir, "manifest.json")
        
        # We return a dynamic subclass of DesignInterpreter bound to this specific data
        with open(design_path, "r", encoding="utf-8") as f:
            design_data = json.load(f)
            
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            
        class BoundInterpreter(DesignInterpreter):
            meta = AnimationMeta(
                id=manifest.get("id", "unknown"),
                slug=manifest.get("slug", "unknown"),
                name=manifest.get("name", "unknown"),
                author_name=manifest.get("author_name", "unknown"),
                author_handle=manifest.get("author_handle", "unknown"),
                description=manifest.get("description", ""),
                tags=manifest.get("tags", []),
                version=manifest.get("version", "1.0"),
                min_width=manifest.get("minimum_width", 40),
                min_height=manifest.get("minimum_height", 12),
                recommended_duration_ms=manifest.get("recommended_duration_ms", 1000),
                supports_ascii=manifest.get("supports_ascii", True),
                supports_monochrome=manifest.get("supports_monochrome", True)
            )
            
            def __init__(self):
                super().__init__()
                self.elements = design_data.get("elements", [])
                self.keyframes = design_data.get("keyframes", [])
                
        return BoundInterpreter
        
    def setup(self, ctx: AnimationContext) -> None:
        pass
        
    def update(self, ctx: AnimationContext) -> None:
        pass
        
    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        # Simple evaluation of expressions like "w/2"
        def eval_coord(expr, size):
            if isinstance(expr, int) or isinstance(expr, float): return int(expr)
            try:
                # Safe eval with w and h
                e = str(expr).replace("w", str(ctx.width)).replace("h", str(ctx.height))
                return int(eval(e, {"__builtins__": None}, {}))
            except:
                return 0

        # Render elements
        for el in self.elements:
            # Figure out opacity from keyframes
            opacity = 1.0
            relevant_kf = [kf for kf in self.keyframes if kf["target"] == el.get("id") and kf["property"] == "opacity"]
            if relevant_kf:
                # Sort by time
                relevant_kf.sort(key=lambda k: k["time"])
                if ctx.progress <= relevant_kf[0]["time"]:
                    opacity = relevant_kf[0]["value"]
                elif ctx.progress >= relevant_kf[-1]["time"]:
                    opacity = relevant_kf[-1]["value"]
                else:
                    for i in range(len(relevant_kf) - 1):
                        k1, k2 = relevant_kf[i], relevant_kf[i+1]
                        if k1["time"] <= ctx.progress <= k2["time"]:
                            t_range = k2["time"] - k1["time"]
                            p = (ctx.progress - k1["time"]) / t_range if t_range > 0 else 0
                            opacity = k1["value"] + (k2["value"] - k1["value"]) * p
                            break

            # If invisible, skip
            if opacity <= 0.01:
                continue

            if el["type"] == "text":
                x = eval_coord(el["x"], ctx.width)
                y = eval_coord(el["y"], ctx.height)
                fg = el.get("fg", (255, 255, 255))
                # Convert color lists [255, 255, 255] to tuples
                if isinstance(fg, list): fg = tuple(fg)
                
                # Fade color to black based on opacity (simple hack)
                if opacity < 1.0 and isinstance(fg, tuple) and len(fg) == 3:
                    fg = (int(fg[0] * opacity), int(fg[1] * opacity), int(fg[2] * opacity))
                    
                canvas.put_text(x, y, el["text"], fg=fg, bold=el.get("bold", False))

