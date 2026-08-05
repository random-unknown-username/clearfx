import math
from typing import List
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class Drop:
    def __init__(self, x: int, y: float, speed: float, size: int):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.trail: List[float] = []

class RainWindow(Animation):
    meta = AnimationMeta(
        id="rain_on_window",
        slug="rain-on-window",
        name="Rain on Window",
        author_name="Luna",
        author_handle="@luna",
        description="Gentle rain drops sliding down a window pane.",
        tags=["rain", "ambient", "calm"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=6000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.drops: List[Drop] = []
        
    def update(self, ctx: AnimationContext) -> None:
        if ctx.reduced_motion:
            return
            
        # Add new drops
        if self.rng.random() < 0.2:
            self.drops.append(Drop(
                x=self.rng.randint(0, ctx.width - 1),
                y=0.0,
                speed=self.rng.uniform(0.1, 0.5),
                size=1
            ))
            
        # Update drops
        for d in self.drops:
            d.trail.append(d.y)
            if len(d.trail) > 10:
                d.trail.pop(0)
                
            d.y += d.speed
            
            # Chance to merge or slide
            if self.rng.random() < 0.05:
                d.x += self.rng.choice([-1, 1])
                
        # Merge logic (simplified)
        for i, d1 in enumerate(self.drops):
            for j, d2 in enumerate(self.drops):
                if i != j and d1.x == d2.x and abs(d1.y - d2.y) < 1.0:
                    if d1.size >= d2.size:
                        d1.size += 1
                        d1.speed += 0.1
                        d2.y = ctx.height + 10 # Send offscreen to remove
                        
        self.drops = [d for d in self.drops if d.y < ctx.height + 5]

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        
        drop_chars = ['•', '●', 'O'] if not ctx.ascii_only else ['.', 'o', 'O']
        trail_char = '│' if not ctx.ascii_only else '|'
        
        color = (150, 200, 255) if not ctx.monochrome else None
        trail_color = (80, 100, 130) if not ctx.monochrome else None
        
        for d in self.drops:
            # Draw trail
            for ty in d.trail:
                if 0 <= int(ty) < ctx.height:
                    canvas.put_char(d.x, int(ty), trail_char, fg=trail_color, dim=True)
            
            # Draw drop
            if 0 <= int(d.y) < ctx.height:
                size_idx = min(d.size - 1, len(drop_chars) - 1)
                canvas.put_char(d.x, int(d.y), drop_chars[size_idx], fg=color, bold=True)
