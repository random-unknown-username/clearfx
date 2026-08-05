from typing import Any, List, Dict
from clearfx.engine.animation import Animation, AnimationContext, AnimationMeta
from clearfx.engine.canvas import Canvas

class CreatorAnimation(Animation):
    meta = AnimationMeta(
        id="io.clearfx.studio",
        slug="studio-preview",
        name="Studio Preview",
        author_name="Creator",
        author_handle="@creator",
        description="Studio preview animation.",
        tags=[],
        version="1.0",
        min_width=40,
        min_height=12,
        recommended_duration_ms=1200,
        supports_ascii=True,
        supports_monochrome=True,
    )
    
    def __init__(self):
        self.elements: List[Dict[str, Any]] = []
        self.keyframes: List[Dict[str, Any]] = []
        self.design()
        
    def design(self) -> None:
        """Override this to build the animation."""
        pass
        
    def add_text(self, text: str, x: Any, y: Any, fg: Any = None, bold: bool = False):
        self.elements.append({"type": "text", "text": text, "x": x, "y": y, "fg": fg, "bold": bold, "id": f"text_{len(self.elements)}"})
        
    def add_line(self, x1: Any, y1: Any, x2: Any, y2: Any):
        self.elements.append({"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2})
        
    def add_rect(self, x: Any, y: Any, w: Any, h: Any):
        pass
        
    def add_circle(self, cx: Any, cy: Any, r: Any):
        pass
        
    def add_particles(self):
        pass
        
    def add_sprite(self):
        pass
        
    def set_keyframe(self, target: str, property: str, time: float, value: Any):
        self.keyframes.append({"target": target, "property": property, "time": time, "value": value})
        
    def add_transition(self):
        pass
        
    def setup(self, ctx: AnimationContext) -> None:
        pass
        
    def update(self, ctx: AnimationContext) -> None:
        pass
        
    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        # Simple evaluation of expressions like "w/2"
        def eval_coord(expr, size):
            if isinstance(expr, int): return expr
            try:
                # Safe eval with w and h
                e = str(expr).replace("w", str(ctx.width)).replace("h", str(ctx.height))
                return int(eval(e))
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
                # Fade color to black based on opacity (simple hack)
                if opacity < 1.0 and isinstance(fg, tuple) and len(fg) == 3:
                    fg = (int(fg[0] * opacity), int(fg[1] * opacity), int(fg[2] * opacity))
                canvas.put_text(x, y, el["text"], fg=fg, bold=el.get("bold", False))

