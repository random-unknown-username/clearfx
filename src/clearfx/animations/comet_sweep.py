import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class CometSweep(Animation):
    meta = AnimationMeta(
        id="comet_sweep",
        slug="comet-sweep",
        name="Comet Sweep",
        author_name="Echo",
        author_handle="@echo",
        description="A bright comet sweeps across, wiping the terminal.",
        tags=["space", "wipe", "fast"],
        recommended_duration_ms=4000
    )

    def setup(self, ctx: AnimationContext):
        self.rng = RandomSource(ctx.seed)
        self.particles = []

    def update(self, ctx: AnimationContext):
        t = ctx.progress
        cx = int(t * (ctx.width + 40) - 20)
        cy = int(t * (ctx.height + 20) - 10)
        
        if t < 0.95:
            for _ in range(8):
                self.particles.append({
                    'x': cx + self.rng.uniform(-3, 3),
                    'y': cy + self.rng.uniform(-2, 2),
                    'vx': self.rng.uniform(-0.8, -0.1),
                    'vy': self.rng.uniform(-0.4, 0.1),
                    'life': 1.0
                })
                
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 0.04
            
        self.particles = [p for p in self.particles if p['life'] > 0]

    def render(self, ctx: AnimationContext, canvas: Canvas):
        t = ctx.progress
        cx = int(t * (ctx.width + 40) - 20)
        cy = int(t * (ctx.height + 20) - 10)
        
        if t < 0.5:
            for _ in range(40):
                x = self.rng.randint(0, ctx.width - 1)
                y = self.rng.randint(0, ctx.height - 1)
                if y > cy - 5 or x > cx - 5:
                    canvas.put_char(x, y, ".", fg=(100, 100, 100) if not ctx.monochrome else None)
        
        chars = ["*", ".", "x", "+"] if ctx.ascii_only else ["★", "✶", "⋆", "·"]
        
        for p in self.particles:
            px, py = int(p['x']), int(p['y'])
            if 0 <= px < ctx.width and 0 <= py < ctx.height:
                c = int(255 * p['life'])
                canvas.put_char(px, py, self.rng.choice(chars), fg=(c, c, int(c*0.8)) if not ctx.monochrome else None)
                
        if 0 <= cx < ctx.width and 0 <= cy < ctx.height:
            canvas.put_char(cx, cy, chars[0], fg=(255, 255, 255) if not ctx.monochrome else None, bold=True)
