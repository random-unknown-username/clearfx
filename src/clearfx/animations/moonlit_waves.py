import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource
from clearfx.engine.noise import noise2d

class MoonlitWaves(Animation):
    meta = AnimationMeta(
        id="moonlit_waves",
        slug="moonlit-waves",
        name="Moonlit Waves",
        author_name="Iris",
        author_handle="@iris",
        description="Layered ocean waves move with parallax under moonlight.",
        tags=["ambient", "water", "parallax"],
        recommended_duration_ms=10000
    )

    def setup(self, ctx: AnimationContext):
        pass

    def update(self, ctx: AnimationContext):
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas):
        moon_x = ctx.width // 2
        moon_y = int(ctx.height * 0.2)
        
        # Draw moon
        if moon_y >= 0:
            moon_char = "O" if ctx.ascii_only else "○"
            canvas.put_char(moon_x, moon_y, moon_char, fg=(255, 255, 200) if not ctx.monochrome else None, bold=True)
            
        horizon = int(ctx.height * 0.4)
        
        for y in range(horizon, ctx.height):
            depth = (y - horizon) / (ctx.height - horizon)
            speed = 1.0 + depth * 3.0
            x_offset = ctx.progress * speed * 20.0
            
            for x in range(ctx.width):
                n = noise2d(x * 0.05 + x_offset, y * 0.2, ctx.seed)
                
                if n > 0.5:
                    is_reflection = abs(x - moon_x) < (2 + depth * 5) and (x + y) % 2 == 0
                    c = (200, 220, 255) if is_reflection else (50, 100 + int(depth * 100), 200)
                    
                    chars = ["~", "-", "="] if ctx.ascii_only else ["∼", "≈", "≡"]
                    char_idx = int(depth * len(chars))
                    char = chars[min(char_idx, len(chars)-1)]
                    
                    canvas.put_char(x, y, char, fg=None if ctx.monochrome else c, bold=is_reflection)
