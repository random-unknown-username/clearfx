import math
from typing import List, Tuple
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class Snowflake:
    def __init__(self, x: float, y: float, size: int):
        self.x = x
        self.y = y
        self.size = size
        self.angle = 0.0
        self.settled = False

class SnowGlobe(Animation):
    meta = AnimationMeta(
        id="snow_globe",
        slug="snow-globe",
        name="Snow Globe",
        author_name="Mira",
        author_handle="@mira",
        description="A magical snow globe swirls and settles.",
        tags=["winter", "snow", "magic"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=6000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.flakes: List[Snowflake] = []
        self.chars = ['*', '·', '•', '❄'] if not ctx.ascii_only else ['*', '.', '+', 'x']
        
        for _ in range(50):
            self.flakes.append(Snowflake(
                x=ctx.width/2 + self.rng.uniform(-10, 10),
                y=ctx.height/2 + self.rng.uniform(-10, 10),
                size=self.rng.randint(0, len(self.chars) - 1)
            ))
            
    def update(self, ctx: AnimationContext) -> None:
        if ctx.reduced_motion:
            return
            
        cx = ctx.width / 2
        cy = ctx.height / 2
        radius = 12
        
        for f in self.flakes:
            if f.settled:
                continue
                
            # Swirl force
            dx = f.x - cx
            dy = f.y - cy
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist < radius - 1:
                angle = math.atan2(dy, dx)
                force = max(0.0, 1.0 - ctx.progress) * 2.0
                f.x += math.cos(angle + math.pi/2) * force
                f.y += math.sin(angle + math.pi/2) * force
                f.y += 0.5 # gravity
                
            if (f.x - cx)**2 + (f.y - cy)**2 >= (radius - 1)**2 and f.y > cy:
                f.settled = True

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        
        # Shrink and move up at the end
        cx = int(ctx.width / 2)
        cy = int(ctx.height / 2 - (ctx.progress**3 * 10))
        radius = max(0, int(12 * (1.0 - ctx.progress**5)))
        
        if radius > 0:
            color = (200, 230, 255) if not ctx.monochrome else None
            canvas.draw_circle(cx, cy, radius, char='-', fg=color)
            
            for f in self.flakes:
                dist_sq = (f.x - ctx.width/2)**2 + (f.y - ctx.height/2)**2
                if dist_sq < radius**2:
                    char = self.chars[f.size]
                    canvas.put_char(int(f.x), int(f.y - (ctx.height/2 - cy)), char, fg=(255, 255, 255) if not ctx.monochrome else None)
