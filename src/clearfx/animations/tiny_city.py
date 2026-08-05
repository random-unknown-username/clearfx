import math
from typing import List
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class Building:
    def __init__(self, x: int, width: int, height: int):
        self.x = x
        self.width = width
        self.height = height
        self.windows: List[List[bool]] = [[True for _ in range(width - 2)] for _ in range(height - 1)]

class TinyCity(Animation):
    meta = AnimationMeta(
        id="tiny_city",
        slug="tiny-city",
        name="Tiny City Shutdown",
        author_name="Mira",
        author_handle="@mira",
        description="A miniature city turns off its lights and sinks.",
        tags=["city", "night", "cozy"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=6000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.buildings: List[Building] = []
        
        x = 2
        while x < ctx.width - 5:
            w = self.rng.randint(4, 10)
            h = self.rng.randint(5, 15)
            self.buildings.append(Building(x, w, h))
            x += w + self.rng.randint(1, 3)
            
    def update(self, ctx: AnimationContext) -> None:
        if ctx.reduced_motion:
            return
            
        if ctx.progress < 0.7:
            # Turn off windows randomly
            if self.rng.random() < 0.3:
                b = self.rng.choice(self.buildings)
                if b.windows:
                    ry = self.rng.randint(0, len(b.windows) - 1)
                    rx = self.rng.randint(0, len(b.windows[ry]) - 1)
                    b.windows[ry][rx] = False

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        
        # Sinking effect at the end
        y_offset = 0
        if ctx.progress > 0.7:
            y_offset = int(((ctx.progress - 0.7) / 0.3) * 20)
            
        # Draw stars
        if ctx.progress > 0.3:
            star_color = (200, 200, 255) if not ctx.monochrome else None
            for _ in range(10):
                sx = self.rng.randint(0, ctx.width - 1)
                sy = self.rng.randint(0, ctx.height // 2)
                if self.rng.random() > 0.5:
                    canvas.put_char(sx, sy, '.', fg=star_color, dim=True)

        window_on = '■' if not ctx.ascii_only else '#'
        window_off = '□' if not ctx.ascii_only else '.'
        
        for b in self.buildings:
            base_y = ctx.height - b.height + y_offset
            for dy in range(b.height):
                for dx in range(b.width):
                    y = base_y + dy
                    x = b.x + dx
                    
                    if 0 <= y < ctx.height:
                        if dx == 0 or dx == b.width - 1 or dy == 0:
                            # Wall
                            canvas.put_char(x, y, '█' if not ctx.ascii_only else '|', fg=(50, 50, 60) if not ctx.monochrome else None)
                        else:
                            # Window
                            w_y = dy - 1
                            w_x = dx - 1
                            is_on = b.windows[w_y][w_x] if w_y < len(b.windows) and w_x < len(b.windows[w_y]) else False
                            
                            if is_on:
                                canvas.put_char(x, y, window_on, fg=(255, 255, 100) if not ctx.monochrome else None, bold=True)
                            else:
                                canvas.put_char(x, y, window_off, fg=(30, 30, 40) if not ctx.monochrome else None, dim=True)
