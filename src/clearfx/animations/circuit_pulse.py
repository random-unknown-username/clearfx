import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class CircuitPulse(Animation):
    meta = AnimationMeta(
        id="circuit_pulse",
        slug="circuit-pulse",
        name="Circuit Pulse",
        author_name="Reed",
        author_handle="@reed",
        description="Circuit-like paths grow through the screen.",
        tags=["tech", "circuit", "growth"],
        recommended_duration_ms=8000
    )

    def setup(self, ctx: AnimationContext):
        self.rng = RandomSource(ctx.seed)
        self.paths = []
        self.grid = {}
        # Start a few paths
        for _ in range(5):
            self.paths.append({
                'x': self.rng.randint(0, ctx.width - 1),
                'y': self.rng.choice([0, ctx.height - 1]),
                'dx': 0,
                'dy': 1 if self.rng.random() < 0.5 else -1,
                'length': 0,
                'max_length': self.rng.randint(10, 40)
            })

    def update(self, ctx: AnimationContext):
        if ctx.progress > 0.8:
            return
            
        new_paths = []
        for p in self.paths:
            if p['length'] >= p['max_length']:
                continue
                
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['length'] += 1
            
            self.grid[(p['x'], p['y'])] = True
            
            if self.rng.random() < 0.2:
                # Turn
                if p['dx'] != 0:
                    p['dx'] = 0
                    p['dy'] = self.rng.choice([-1, 1])
                else:
                    p['dy'] = 0
                    p['dx'] = self.rng.choice([-1, 1])
                    
            if self.rng.random() < 0.05 and len(self.paths) + len(new_paths) < 30:
                # Branch
                new_paths.append({
                    'x': p['x'],
                    'y': p['y'],
                    'dx': p['dy'],
                    'dy': p['dx'],
                    'length': 0,
                    'max_length': self.rng.randint(5, 20)
                })
                
        self.paths.extend(new_paths)

    def render(self, ctx: AnimationContext, canvas: Canvas):
        pulse = (ctx.progress * 10) % 1.0
        
        char = "+" if ctx.ascii_only else "┼"
        for (x, y) in self.grid:
            if 0 <= x < ctx.width and 0 <= y < ctx.height:
                dist = math.sqrt((x - ctx.width/2)**2 + (y - ctx.height/2)**2)
                is_pulse = abs((dist / 10.0) % 1.0 - pulse) < 0.1
                c = (0, 255, 255) if is_pulse else (0, 100, 100)
                canvas.put_char(x, y, char, fg=None if ctx.monochrome else c, bold=is_pulse)
