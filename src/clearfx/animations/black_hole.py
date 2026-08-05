import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class BlackHoleAnimation(Animation):
    meta = AnimationMeta(
        id="black_hole", slug="black-hole", name="Black Hole Terminal",
        author_name="Echo", author_handle="@echo",
        description="Characters and particles orbit a central void before collapsing into it.",
        tags=["space", "particles", "gravity"],
        min_width=20, min_height=10, recommended_duration_ms=6000,
        supports_ascii=True, supports_monochrome=True, version="1.0.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.particles = []
        for _ in range(50 if not ctx.reduced_motion else 20):
            r = self.rng.random() * max(ctx.width, ctx.height) / 2
            theta = self.rng.random() * math.pi * 2
            self.particles.append([r, theta, self.rng.random() * 2 + 1])

    def update(self, ctx: AnimationContext) -> None:
        speed = 0.5 if ctx.reduced_motion else 1.0
        for p in self.particles:
            p[0] -= p[2] * speed * 0.5
            p[1] += (5.0 / max(p[0], 1.0)) * speed
            if p[0] <= 2.0:
                p[0] = max(ctx.width, ctx.height) / 2
                p[1] = self.rng.random() * math.pi * 2

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        cx, cy = ctx.width // 2, ctx.height // 2
        void_radius = 2 + ctx.progress * 8
        
        for p in self.particles:
            r, theta, _ = p
            if r > void_radius:
                x = int(cx + r * math.cos(theta) * 2)
                y = int(cy + r * math.sin(theta))
                if 0 <= x < ctx.width and 0 <= y < ctx.height:
                    char = "*" if ctx.ascii_only else "●"
                    color = None if ctx.monochrome else (200, 200, 255)
                    canvas.put_char(x, y, char, fg=color, bg=None)
