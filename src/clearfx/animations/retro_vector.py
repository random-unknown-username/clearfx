import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas

class RetroVector(Animation):
    meta = AnimationMeta(
        id="retro_vector",
        slug="retro-vector",
        name="Retro Vector Horizon",
        author_name="Volt",
        author_handle="@volt",
        description="A perspective grid moves toward the viewer with a neon horizon.",
        tags=["retro", "synthwave", "perspective"],
        recommended_duration_ms=6000
    )

    def setup(self, ctx: AnimationContext):
        pass

    def update(self, ctx: AnimationContext):
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas):
        cx = ctx.width // 2
        horizon_y = int(ctx.height * 0.4)
        
        # Sun
        sun_r = int(ctx.height * 0.2)
        for y in range(horizon_y - sun_r, horizon_y):
            for x in range(cx - sun_r, cx + sun_r):
                if (x - cx)**2 + (y - (horizon_y - sun_r))**2 < sun_r**2:
                    if y % 2 == 0 or y < horizon_y - sun_r // 2:
                        canvas.put_char(x, y, "@" if ctx.ascii_only else "█", 
                                        fg=None if ctx.monochrome else (255, 100, 200))
                                        
        # Grid
        offset = (ctx.progress * 10) % 1.0
        
        # Horizontal lines
        for i in range(1, 10):
            y = horizon_y + int(math.pow(i + offset, 1.5))
            if y < ctx.height:
                for x in range(ctx.width):
                    canvas.put_char(x, y, "-" if ctx.ascii_only else "─", 
                                    fg=None if ctx.monochrome else (0, 255, 255))
                                    
        # Vertical lines
        for i in range(-10, 11):
            x_bottom = cx + i * int(ctx.width / 10)
            canvas.draw_line(cx, horizon_y, x_bottom, ctx.height - 1, 
                             "/" if i < 0 else "\\" if i > 0 else "|",
                             fg=None if ctx.monochrome else (0, 200, 255))
                             
        # Horizon line
        for x in range(ctx.width):
            canvas.put_char(x, horizon_y, "=" if ctx.ascii_only else "═", 
                            fg=None if ctx.monochrome else (255, 0, 255), bold=True)
