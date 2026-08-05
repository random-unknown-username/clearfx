import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class OrigamiCraneAnimation(Animation):
    meta = AnimationMeta(
        id="origami_crane", slug="origami-crane", name="Origami Crane",
        author_name="Zero", author_handle="@zero",
        description="Angular line segments fold into a small crane silhouette and fly away.",
        tags=["origami", "crane", "fold"],
        min_width=20, min_height=10, recommended_duration_ms=5000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        pass

    def update(self, ctx: AnimationContext) -> None:
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        w, h = ctx.width, ctx.height
        cx, cy = w/2, h/2
        
        if ctx.progress > 0.7:
            cx += (ctx.progress - 0.7) * w
            cy -= (ctx.progress - 0.7) * h
            
        points = [
            (-5, 0), (0, -5), (5, 0), (0, 5), (-5, 0)
        ]
        
        fold = min(ctx.progress / 0.5, 1.0)
        color = None if ctx.monochrome else (255, 255, 200)
        char = "-" if ctx.ascii_only else "─"
        
        for i in range(len(points)-1):
            x1 = cx + points[i][0] * (2 - fold)
            y1 = cy + points[i][1] * fold
            x2 = cx + points[i+1][0] * (2 - fold)
            y2 = cy + points[i+1][1] * fold
            canvas.draw_line(int(x1), int(y1), int(x2), int(y2), char, fg=color, bg=None)
