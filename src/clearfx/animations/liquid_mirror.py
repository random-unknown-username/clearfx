import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas

class LiquidMirror(Animation):
    meta = AnimationMeta(
        id="liquid_mirror",
        slug="liquid-mirror",
        name="Liquid Mirror",
        author_name="Nova",
        author_handle="@nova",
        description="Horizontal wave distortion of a reflected pattern.",
        tags=["water", "mirror", "distortion"],
        recommended_duration_ms=7000
    )

    def setup(self, ctx: AnimationContext):
        pass

    def update(self, ctx: AnimationContext):
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas):
        mid_y = ctx.height // 2
        dampening = max(0.0, 1.0 - ctx.progress)
        
        for y in range(mid_y):
            # Base pattern top half
            for x in range(ctx.width):
                if (x + y) % 4 == 0:
                    c = (100, 200, 255)
                    char = "=" if ctx.ascii_only else "≡"
                    canvas.put_char(x, y, char, fg=None if ctx.monochrome else c)
                    
        for y in range(mid_y, ctx.height):
            dy = y - mid_y
            wave_offset = math.sin(dy * 0.5 + ctx.progress * 20.0) * 4.0 * dampening
            
            src_y = mid_y - dy - 1
            if src_y < 0:
                continue
                
            for x in range(ctx.width):
                src_x = int(x + wave_offset)
                if 0 <= src_x < ctx.width:
                    if (src_x + src_y) % 4 == 0:
                        c = (50, 100, 150)
                        char = "~" if ctx.ascii_only else "≈"
                        canvas.put_char(x, y, char, fg=None if ctx.monochrome else c)
