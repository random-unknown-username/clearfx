import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class InkInWaterAnimation(Animation):
    meta = AnimationMeta(
        id="ink_in_water", slug="ink-in-water", name="Ink in Water",
        author_name="Pixel", author_handle="@pixel",
        description="Dark and light tendrils spread organically before fading.",
        tags=["ink", "organic", "fluid"],
        min_width=20, min_height=10, recommended_duration_ms=6000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.drops = []
        for _ in range(3):
            self.drops.append((self.rng.random() * ctx.width, self.rng.random() * ctx.height))

    def update(self, ctx: AnimationContext) -> None:
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        w, h = ctx.width, ctx.height
        radius = ctx.progress * max(w, h)
        fade = max(0, 1.0 - ctx.progress * 1.5)
        
        chars = [" ", ".", ":", "=", "#"] if ctx.ascii_only else [" ", "░", "▒", "▓", "█"]
        
        for y in range(h):
            for x in range(w):
                val = 0
                for dx, dy in self.drops:
                    dist = math.sqrt((x-dx)**2 + (y-dy)**2 * 4)
                    if dist < radius:
                        val += (radius - dist) / radius
                
                val *= fade
                c_idx = int(val * len(chars))
                if c_idx > 0:
                    c_idx = min(c_idx, len(chars)-1)
                    canvas.put_char(x, y, chars[c_idx], fg=None, bg=None)
