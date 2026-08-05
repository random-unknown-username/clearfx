import math
from typing import List
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class WaterParticle:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.life = 1.0

class TidalVortex(Animation):
    meta = AnimationMeta(
        id="tidal_vortex",
        slug="tidal-vortex",
        name="Tidal Vortex",
        author_name="Volt",
        author_handle="@volt",
        description="Two opposing whirlpools create an S-shaped flow.",
        tags=["water", "vortex", "flow"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=6000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.particles: List[WaterParticle] = []
        self.chars = ['~', '≈', '∼'] if not ctx.ascii_only else ['~', '-', '=']
        
    def update(self, ctx: AnimationContext) -> None:
        if ctx.reduced_motion:
            return
            
        # Emit particles
        for _ in range(5):
            self.particles.append(WaterParticle(
                x=self.rng.uniform(0, ctx.width),
                y=self.rng.uniform(0, ctx.height)
            ))
            
        cx1 = ctx.width * 0.3
        cy1 = ctx.height * 0.5
        cx2 = ctx.width * 0.7
        cy2 = ctx.height * 0.5
        
        for p in self.particles:
            dx1 = cx1 - p.x
            dy1 = cy1 - p.y
            dist1 = max(1.0, math.sqrt(dx1**2 + dy1**2))
            
            dx2 = cx2 - p.x
            dy2 = cy2 - p.y
            dist2 = max(1.0, math.sqrt(dx2**2 + dy2**2))
            
            # Vortex 1 (clockwise)
            fx1 = (dy1 / dist1) * (10.0 / dist1)
            fy1 = (-dx1 / dist1) * (10.0 / dist1)
            
            # Vortex 2 (counter-clockwise)
            fx2 = (-dy2 / dist2) * (10.0 / dist2)
            fy2 = (dx2 / dist2) * (10.0 / dist2)
            
            # Pull towards centers
            fx1 += (dx1 / dist1) * 0.5
            fy1 += (dy1 / dist1) * 0.5
            
            fx2 += (dx2 / dist2) * 0.5
            fy2 += (dy2 / dist2) * 0.5
            
            p.x += (fx1 + fx2)
            p.y += (fy1 + fy2)
            p.life -= 0.02
            
        self.particles = [p for p in self.particles if p.life > 0]

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        
        for p in self.particles:
            if 0 <= int(p.x) < ctx.width and 0 <= int(p.y) < ctx.height:
                char = self.rng.choice(self.chars)
                color = (0, 150 + int(p.life * 100), 255) if not ctx.monochrome else None
                canvas.put_char(int(p.x), int(p.y), char, fg=color, dim=(p.life < 0.5))
