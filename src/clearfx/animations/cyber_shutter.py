import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class CyberShutterAnimation(Animation):
    meta = AnimationMeta(
        id="cyber_shutter", slug="cyber-shutter", name="Cyber Shutter",
        author_name="Sage", author_handle="@sage",
        description="Mechanical panels close across the screen from edges with glowing seam lines.",
        tags=["cyber", "mechanical", "panels"],
        min_width=20, min_height=10, recommended_duration_ms=4000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        pass

    def update(self, ctx: AnimationContext) -> None:
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        w, h = ctx.width, ctx.height
        close_amt = min(ctx.progress * 1.5, 1.0)
        
        char = "#" if ctx.ascii_only else "█"
        color = None if ctx.monochrome else (50, 50, 60)
        glow_color = None if ctx.monochrome else (0, 255, 255)
        
        top_limit = int(h / 2 * close_amt)
        bottom_limit = h - int(h / 2 * close_amt)
        
        for y in range(h):
            if y < top_limit or y >= bottom_limit:
                canvas.draw_line(0, y, w-1, y, char, fg=color, bg=None)
                
        if top_limit > 0 and top_limit < h/2:
            canvas.draw_line(0, top_limit, w-1, top_limit, "-" if ctx.ascii_only else "═", fg=glow_color, bg=None)
        if bottom_limit < h and bottom_limit > h/2:
            canvas.draw_line(0, bottom_limit-1, w-1, bottom_limit-1, "-" if ctx.ascii_only else "═", fg=glow_color, bg=None)
