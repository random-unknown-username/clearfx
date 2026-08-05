import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class ConstellationWeaverAnimation(Animation):
    meta = AnimationMeta(
        id="constellation_weaver", slug="constellation-weaver", name="Constellation Weaver",
        author_name="Iris", author_handle="@iris",
        description="Stars appear one by one, connect into constellation lines, then dissolve.",
        tags=["stars", "constellation", "lines"],
        min_width=20, min_height=10, recommended_duration_ms=7000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.stars = []
        for _ in range(15 if not ctx.reduced_motion else 8):
            x = self.rng.random() * ctx.width
            y = self.rng.random() * ctx.height
            appear_time = self.rng.random() * 0.5
            self.stars.append({"x": x, "y": y, "t": appear_time})

    def update(self, ctx: AnimationContext) -> None:
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        time = ctx.progress
        color = None if ctx.monochrome else (200, 220, 255)
        
        active_stars = [s for s in self.stars if time > s["t"]]
        
        for s in active_stars:
            ix, iy = int(s["x"]), int(s["y"])
            if 0 <= ix < ctx.width and 0 <= iy < ctx.height:
                canvas.put_char(ix, iy, "*", fg=color, bg=None)
                
        if time > 0.5:
            for i, s1 in enumerate(active_stars):
                for s2 in active_stars[i+1:]:
                    dist = math.sqrt((s1["x"]-s2["x"])**2 + (s1["y"]-s2["y"])**2)
                    if dist < ctx.width / 3:
                        canvas.draw_line(int(s1["x"]), int(s1["y"]), int(s2["x"]), int(s2["y"]), "." if ctx.ascii_only else "·", fg=color, bg=None)
