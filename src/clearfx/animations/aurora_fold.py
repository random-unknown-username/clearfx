import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class AuroraFoldAnimation(Animation):
    meta = AnimationMeta(
        id="aurora_fold", slug="aurora-fold", name="Aurora Fold",
        author_name="Mira", author_handle="@mira",
        description="Smooth ribbons fold inward from the edges like northern lights.",
        tags=["aurora", "wave", "ribbon"],
        min_width=20, min_height=10, recommended_duration_ms=5000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)

    def update(self, ctx: AnimationContext) -> None:
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        w, h = ctx.width, ctx.height
        speed = 0.5 if ctx.reduced_motion else 2.0
        time = (ctx.elapsed_ms / 1000.0) * speed

        for y in range(h):
            for x in range(w):
                nx = x / w
                ny = y / h
                wave1 = math.sin(nx * 5.0 + time) * math.cos(ny * 3.0 - time * 0.5)
                wave2 = math.sin(ny * 4.0 - time * 1.2) * math.cos(nx * 6.0 + time * 0.8)
                val = (wave1 + wave2) / 2.0
                
                char = " "
                if val > 0.6: char = "#" if ctx.ascii_only else "█"
                elif val > 0.2: char = "=" if ctx.ascii_only else "▒"
                elif val > -0.2: char = "-" if ctx.ascii_only else "░"
                
                if char != " ":
                    r = int(128 + 127 * math.sin(time + nx * 2))
                    g = int(128 + 127 * math.cos(time + ny * 2))
                    b = 255
                    color = None if ctx.monochrome else (r, g, b)
                    canvas.put_char(x, y, char, fg=color, bg=None)
