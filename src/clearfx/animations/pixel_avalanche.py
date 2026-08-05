import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class PixelAvalancheAnimation(Animation):
    meta = AnimationMeta(
        id="pixel_avalanche", slug="pixel-avalanche", name="Pixel Avalanche",
        author_name="Flux", author_handle="@flux",
        description="The screen appears to break into blocks that fall downward.",
        tags=["blocks", "falling", "gravity"],
        min_width=20, min_height=10, recommended_duration_ms=4000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.blocks = []
        for y in range(0, ctx.height, 2):
            for x in range(0, ctx.width, 4):
                delay = self.rng.random() * 2.0
                self.blocks.append({"x": x, "y": y, "delay": delay, "vy": 0})

    def update(self, ctx: AnimationContext) -> None:
        time = ctx.elapsed_ms / 1000.0
        speed = 0.5 if ctx.reduced_motion else 1.0
        for b in self.blocks:
            if time > b["delay"]:
                b["vy"] += 9.8 * ctx.dt * speed
                b["y"] += b["vy"] * ctx.dt * speed

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        chars = ["#", "=", "-"] if ctx.ascii_only else ["█", "▄", "▀"]
        for b in self.blocks:
            bx, by = int(b["x"]), int(b["y"])
            if by < ctx.height:
                char = chars[int(b["x"] + b["y"]) % len(chars)]
                color = None if ctx.monochrome else (100, 150, 255)
                for dx in range(4):
                    if 0 <= bx+dx < ctx.width and 0 <= by < ctx.height:
                        canvas.put_char(bx+dx, by, char, fg=color, bg=None)
