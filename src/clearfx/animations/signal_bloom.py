import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class SignalBloomAnimation(Animation):
    meta = AnimationMeta(
        id="signal_bloom", slug="signal-bloom", name="Signal Bloom",
        author_name="Volt", author_handle="@volt",
        description="Radio waves expand from several points and intersect into flower-like shapes.",
        tags=["waves", "signal", "bloom"],
        min_width=20, min_height=10, recommended_duration_ms=5000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.points = [(ctx.width/2, ctx.height/2), (ctx.width/3, ctx.height/3), (ctx.width*2/3, ctx.height*2/3)]

    def update(self, ctx: AnimationContext) -> None:
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        w, h = ctx.width, ctx.height
        time = (ctx.elapsed_ms / 1000.0) * (0.5 if ctx.reduced_motion else 1.0)
        color = None if ctx.monochrome else (0, 255, 255)
        chars = [" ", ".", "o", "O", "@"] if ctx.ascii_only else [" ", "·", "∘", "○", "◎"]
        
        for y in range(h):
            for x in range(w):
                intensity = 0
                for px, py in self.points:
                    dist = math.sqrt((x-px)**2 + (y-py)**2 * 4)
                    intensity += math.sin(dist - time * 5)
                
                if intensity > 1.5:
                    c_idx = min(int(intensity), len(chars)-1)
                    canvas.put_char(x, y, chars[c_idx], fg=color, bg=None)
