import math
from typing import List, Tuple
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource
from clearfx.engine.noise import noise1d

class DataSerpent(Animation):
    meta = AnimationMeta(
        id="data_serpent",
        slug="data-serpent",
        name="Data Serpent",
        author_name="Flux",
        author_handle="@flux",
        description="A segmented serpent of hex values slithers.",
        tags=["data", "snake", "matrix"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=5000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.path: List[Tuple[float, float]] = []
        self.length = 15
        self.chars = "0123456789ABCDEF"
        self.segments: List[str] = [self.rng.choice(self.chars) for _ in range(self.length)]
        
    def update(self, ctx: AnimationContext) -> None:
        if ctx.reduced_motion:
            return
            
        t = ctx.elapsed_ms / 1000.0
        
        # Head position using noise
        hx = (ctx.width / 2) + noise1d(t, ctx.seed) * (ctx.width / 2.5)
        hy = (ctx.height / 2) + noise1d(t + 10, ctx.seed) * (ctx.height / 2.5)
        
        self.path.insert(0, (hx, hy))
        if len(self.path) > 100:
            self.path.pop()
            
        # Randomly change some segments
        if self.rng.random() < 0.3:
            idx = self.rng.randint(0, self.length - 1)
            self.segments[idx] = self.rng.choice(self.chars)

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        
        spacing = 3
        
        for i in range(min(self.length, len(self.path) // spacing)):
            pos_idx = i * spacing
            if pos_idx >= len(self.path):
                break
                
            x, y = self.path[pos_idx]
            char = self.segments[i]
            
            intensity = 1.0 - (i / self.length)
            g = int(255 * intensity)
            color = (0, g, 0) if not ctx.monochrome else None
            
            canvas.put_text(int(x), int(y), f"0x{char}", fg=color, bold=(i==0))
            
        # Draw fading trail
        if len(self.path) > self.length * spacing:
            for i in range(self.length * spacing, len(self.path), spacing):
                x, y = self.path[i]
                fade = 1.0 - (i / len(self.path))
                color = (0, int(50 * fade), 0) if not ctx.monochrome else None
                canvas.put_char(int(x), int(y), '.', fg=color, dim=True)
