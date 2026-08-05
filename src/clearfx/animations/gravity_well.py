import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class GravityWellAnimation(Animation):
    meta = AnimationMeta(
        id="gravity_well", slug="gravity-well", name="Gravity Well",
        author_name="Reed", author_handle="@reed",
        description="A coordinate grid bends toward a moving point and snaps back.",
        tags=["grid", "gravity", "warp"],
        min_width=20, min_height=10, recommended_duration_ms=6000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        pass

    def update(self, ctx: AnimationContext) -> None:
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        w, h = ctx.width, ctx.height
        time = (ctx.elapsed_ms / 1000.0) * (0.5 if ctx.reduced_motion else 1.0)
        px = w/2 + math.sin(time) * w/3
        py = h/2 + math.cos(time * 1.3) * h/3
        
        char = "+" if ctx.ascii_only else "·"
        color = None if ctx.monochrome else (100, 255, 150)
        
        for y in range(0, h, 2):
            for x in range(0, w, 4):
                dx = px - x
                dy = py - y
                dist = math.sqrt(dx*dx + dy*dy * 4) + 1
                pull = 20.0 / dist
                
                nx = x + dx * pull / dist
                ny = y + dy * pull / dist
                
                ix, iy = int(nx), int(ny)
                if 0 <= ix < w and 0 <= iy < h:
                    canvas.put_char(ix, iy, char, fg=color, bg=None)
        
        if 0 <= int(px) < w and 0 <= int(py) < h:
            canvas.put_char(int(px), int(py), "O", fg=(255,255,255) if not ctx.monochrome else None, bg=None)
