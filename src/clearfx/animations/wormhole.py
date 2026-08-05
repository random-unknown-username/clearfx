import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class WormholeAnimation(Animation):
    meta = AnimationMeta(
        id="wormhole", slug="wormhole", name="Wormhole",
        author_name="Luna", author_handle="@luna",
        description="Concentric distorted rings create forward movement through a tunnel.",
        tags=["tunnel", "rings", "space"],
        min_width=20, min_height=10, recommended_duration_ms=6000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        pass

    def update(self, ctx: AnimationContext) -> None:
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        w, h = ctx.width, ctx.height
        cx, cy = w/2, h/2
        time = (ctx.elapsed_ms / 1000.0) * (0.5 if ctx.reduced_motion else 1.0)
        
        chars = [".", "-", "=", "#"] if ctx.ascii_only else ["·", "─", "═", "█"]
        
        for i in range(10, 0, -1):
            r = (i * 5 + time * 10) % 50
            if r > 0:
                for theta in range(0, 360, 10):
                    rad = math.radians(theta)
                    distort = math.sin(rad * 3 + time) * 2
                    x = int(cx + (r + distort) * math.cos(rad) * 2)
                    y = int(cy + (r + distort) * math.sin(rad))
                    
                    c_idx = min(int(r / 15), len(chars)-1)
                    if 0 <= x < w and 0 <= y < h:
                        bright = int(255 * (r / 50))
                        color = None if ctx.monochrome else (bright, bright, 255)
                        canvas.put_char(x, y, chars[c_idx], fg=color, bg=None)
