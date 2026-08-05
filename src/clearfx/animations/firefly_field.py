import math
from typing import List, Tuple
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource
from clearfx.engine.noise import noise2d

class Firefly:
    def __init__(self, x: float, y: float, phase: float):
        self.x = x
        self.y = y
        self.phase = phase

class FireflyField(Animation):
    meta = AnimationMeta(
        id="firefly_field",
        slug="firefly-field",
        name="Firefly Field",
        author_name="Sage",
        author_handle="@sage",
        description="Warm glowing points drift slowly and communicate.",
        tags=["nature", "ambient", "light"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=6000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.flies: List[Firefly] = []
        for _ in range(20):
            self.flies.append(Firefly(
                x=self.rng.uniform(0, ctx.width),
                y=self.rng.uniform(0, ctx.height),
                phase=self.rng.uniform(0, math.pi * 2)
            ))
        self.connections: List[Tuple[int, int, float]] = [] # i, j, life
            
    def update(self, ctx: AnimationContext) -> None:
        if ctx.reduced_motion:
            return
            
        t = ctx.elapsed_ms / 1000.0
        
        for i, f in enumerate(self.flies):
            # Slow drift using noise
            nx = noise2d(f.x * 0.1, t, ctx.seed) * 0.5
            ny = noise2d(f.y * 0.1, t + 10, ctx.seed) * 0.5
            f.x += nx
            f.y += ny
            
            # Form connections
            if self.rng.random() < 0.01:
                for j, other in enumerate(self.flies):
                    if i != j:
                        dist = math.sqrt((f.x - other.x)**2 + (f.y - other.y)**2)
                        if dist < 10:
                            self.connections.append((i, j, 1.0))
                            break
                            
        # Update connections
        new_conn = []
        for i, j, life in self.connections:
            if life > 0:
                new_conn.append((i, j, life - 0.05))
        self.connections = new_conn

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        
        t = ctx.elapsed_ms / 1000.0
        
        # Draw connections
        for i, j, life in self.connections:
            if i < len(self.flies) and j < len(self.flies):
                f1 = self.flies[i]
                f2 = self.flies[j]
                color = (255, 200, 50) if not ctx.monochrome else None
                # Simplified line drawing: just draw the endpoints
                # Real draw_line is available on canvas but might be blocky
                canvas.draw_line(int(f1.x), int(f1.y), int(f2.x), int(f2.y), char='·', fg=color)

        # Draw flies
        for f in self.flies:
            brightness = (math.sin(t * 3 + f.phase) + 1) / 2 # 0 to 1
            if brightness > 0.2:
                r = 255
                g = int(200 * brightness)
                b = 50
                color = (r, g, b) if not ctx.monochrome else None
                canvas.put_char(int(f.x), int(f.y), '*', fg=color, bold=True)
