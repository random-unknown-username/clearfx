import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource
from clearfx.engine.noise import noise2d

class MagneticSand(Animation):
    meta = AnimationMeta(
        id="magnetic_sand",
        slug="magnetic-sand",
        name="Magnetic Sand",
        author_name="Sage",
        author_handle="@sage",
        description="Particles organize along rotating field lines.",
        tags=["physics", "particles", "field"],
        recommended_duration_ms=8000
    )

    def setup(self, ctx: AnimationContext):
        self.rng = RandomSource(ctx.seed)
        self.particles = []
        for _ in range(300):
            self.particles.append({
                'x': self.rng.uniform(0, ctx.width),
                'y': self.rng.uniform(0, ctx.height)
            })

    def update(self, ctx: AnimationContext):
        t = ctx.progress * math.pi * 2
        cx1 = ctx.width / 2 + math.cos(t) * ctx.width * 0.2
        cy1 = ctx.height / 2 + math.sin(t) * ctx.height * 0.2
        cx2 = ctx.width / 2 - math.cos(t) * ctx.width * 0.2
        cy2 = ctx.height / 2 - math.sin(t) * ctx.height * 0.2
        
        dispersion = 1.0 if ctx.progress < 0.8 else max(0.0, (1.0 - ctx.progress) * 5.0)
        
        for p in self.particles:
            if dispersion < 1.0:
                p['x'] += self.rng.uniform(-2, 2) * (1.0 - dispersion)
                p['y'] += self.rng.uniform(-1, 1) * (1.0 - dispersion)
            else:
                d1 = math.sqrt((p['x'] - cx1)**2 + (p['y'] - cy1)**2) + 0.1
                d2 = math.sqrt((p['x'] - cx2)**2 + (p['y'] - cy2)**2) + 0.1
                
                dx = (cx1 - p['x']) / d1 + (cx2 - p['x']) / d2
                dy = (cy1 - p['y']) / d1 + (cy2 - p['y']) / d2
                
                # Flow along perpendicular
                p['x'] += -dy * 0.5 + dx * 0.1
                p['y'] += dx * 0.5 + dy * 0.1

    def render(self, ctx: AnimationContext, canvas: Canvas):
        char = "." if ctx.ascii_only else "·"
        for p in self.particles:
            px, py = int(p['x']), int(p['y'])
            if 0 <= px < ctx.width and 0 <= py < ctx.height:
                canvas.put_char(px, py, char, fg=(150, 150, 150) if not ctx.monochrome else None)
