import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class RainGardenAnimation(Animation):
    meta = AnimationMeta(
        id="rain_garden", slug="rain-garden", name="Terminal Rain Garden",
        author_name="Ash", author_handle="@ash",
        description="Sparse falling glyphs strike an invisible ground line and grow tiny plant shapes.",
        tags=["rain", "garden", "growth"],
        min_width=20, min_height=10, recommended_duration_ms=8000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.drops = []
        self.plants = []
        for _ in range(20 if not ctx.reduced_motion else 10):
            self.drops.append({"x": int(self.rng.random() * ctx.width), "y": -self.rng.random() * ctx.height})

    def update(self, ctx: AnimationContext) -> None:
        speed = 10.0 * ctx.dt * (0.5 if ctx.reduced_motion else 1.0)
        ground = ctx.height - 2
        for d in self.drops:
            d["y"] += speed
            if d["y"] >= ground and d["x"] not in [p["x"] for p in self.plants]:
                self.plants.append({"x": d["x"], "height": 0})
                d["y"] = -self.rng.random() * ctx.height
                d["x"] = int(self.rng.random() * ctx.width)
                
        for p in self.plants:
            p["height"] = min(p["height"] + ctx.dt * 2, 3)

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        rain_color = None if ctx.monochrome else (100, 100, 255)
        plant_color = None if ctx.monochrome else (100, 255, 100)
        rain_char = "|" if ctx.ascii_only else "│"
        plant_chars = ["|", "Y", "*"] if ctx.ascii_only else ["│", "╰", "╯"]
        
        for d in self.drops:
            if d["y"] > 0:
                canvas.put_char(d["x"], int(d["y"]), rain_char, fg=rain_color, bg=None)
                
        ground = ctx.height - 2
        for p in self.plants:
            h = int(p["height"])
            for i in range(h):
                canvas.put_char(p["x"], ground - i, plant_chars[i % len(plant_chars)], fg=plant_color, bg=None)
