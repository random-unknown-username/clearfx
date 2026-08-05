import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas

class ClockworkReset(Animation):
    meta = AnimationMeta(
        id="clockwork_reset",
        slug="clockwork-reset",
        name="Clockwork Reset",
        author_name="Luna",
        author_handle="@luna",
        description="Interlocking gears pull screen content inward.",
        tags=["mechanical", "gears", "reset"],
        recommended_duration_ms=7000
    )

    def setup(self, ctx: AnimationContext):
        pass

    def update(self, ctx: AnimationContext):
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas):
        cx = ctx.width // 2
        cy = ctx.height // 2
        
        angle_offset = ctx.progress * math.pi * 4
        
        gears = [
            (cx, cy, 10, angle_offset, (200, 150, 50)),
            (cx - 20, cy - 5, 8, -angle_offset * 1.25, (150, 100, 50)),
            (cx + 18, cy + 8, 6, -angle_offset * 1.66, (220, 180, 100))
        ]
        
        for (gx, gy, r, ang, color) in gears:
            for i in range(r * 4):
                a = ang + (i / (r * 4)) * math.pi * 2
                x = int(gx + math.cos(a) * r * 2)
                y = int(gy + math.sin(a) * r)
                
                if 0 <= x < ctx.width and 0 <= y < ctx.height:
                    is_tooth = i % 2 == 0
                    char = "O" if not is_tooth else "T"
                    if not ctx.ascii_only:
                        char = "⚙" if is_tooth else "●"
                        
                    canvas.put_char(x, y, char, fg=None if ctx.monochrome else color)
