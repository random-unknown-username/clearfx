import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class NeonKoiAnimation(Animation):
    meta = AnimationMeta(
        id="neon_koi", slug="neon-koi", name="Neon Koi",
        author_name="Nova", author_handle="@nova",
        description="Two abstract fish made from glowing terminal strokes circle each other.",
        tags=["fish", "neon", "trails"],
        min_width=20, min_height=10, recommended_duration_ms=8000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)

    def update(self, ctx: AnimationContext) -> None:
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        w, h = ctx.width, ctx.height
        cx, cy = w / 2, h / 2
        time = (ctx.elapsed_ms / 1000.0) * (0.5 if ctx.reduced_motion else 1.0)
        
        chars = ["/", "\\", "|", "-"] if ctx.ascii_only else ["╭", "╮", "╰", "╯"]
        colors = [(255, 100, 50), (50, 150, 255)]
        
        for i in range(2):
            offset = i * math.pi
            color = None if ctx.monochrome else colors[i]
            for j in range(10): # trail
                t = time - j * 0.1
                x = cx + math.sin(t + offset) * (w / 4) * math.sin(t * 0.5)
                y = cy + math.cos(t + offset) * (h / 3)
                char = chars[(int(x) + int(y)) % len(chars)]
                ix, iy = int(x), int(y)
                if 0 <= ix < w and 0 <= iy < h:
                    canvas.put_char(ix, iy, char, fg=color, bg=None)
