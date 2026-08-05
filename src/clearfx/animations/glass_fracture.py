import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class GlassFracture(Animation):
    meta = AnimationMeta(
        id="glass_fracture",
        slug="glass-fracture",
        name="Glass Fracture",
        author_name="Ash",
        author_handle="@ash",
        description="Cracks spread from an impact, then shatter.",
        tags=["impact", "shatter", "glass"],
        recommended_duration_ms=5000
    )

    def setup(self, ctx: AnimationContext):
        self.rng = RandomSource(ctx.seed)
        self.cracks = []
        cx = self.rng.randint(ctx.width // 3, ctx.width * 2 // 3)
        cy = self.rng.randint(ctx.height // 3, ctx.height * 2 // 3)
        self.impact = (cx, cy)
        
        for _ in range(8):
            angle = self.rng.uniform(0, math.pi * 2)
            self.cracks.append({
                'x': cx, 'y': cy, 'angle': angle, 'active': True,
                'path': [(cx, cy)]
            })

    def update(self, ctx: AnimationContext):
        if ctx.progress > 0.6:
            return
            
        speed = max(0.1, 1.0 - (ctx.progress / 0.6)) * 2.0
        new_cracks = []
        
        for c in self.cracks:
            if not c['active']: continue
            
            c['x'] += math.cos(c['angle']) * speed * 2
            c['y'] += math.sin(c['angle']) * speed
            
            ix, iy = int(c['x']), int(c['y'])
            if (ix, iy) != c['path'][-1]:
                c['path'].append((ix, iy))
                
            if self.rng.random() < 0.1 and len(self.cracks) + len(new_cracks) < 30:
                new_angle = c['angle'] + self.rng.uniform(-0.5, 0.5)
                new_cracks.append({
                    'x': c['x'], 'y': c['y'], 'angle': new_angle, 'active': True,
                    'path': [(ix, iy)]
                })
                
            if c['x'] < 0 or c['x'] >= ctx.width or c['y'] < 0 or c['y'] >= ctx.height:
                c['active'] = False
                
        self.cracks.extend(new_cracks)

    def render(self, ctx: AnimationContext, canvas: Canvas):
        if ctx.progress < 0.05:
            # Flash
            for y in range(ctx.height):
                for x in range(ctx.width):
                    canvas.put_char(x, y, " ", bg=(255, 255, 255) if not ctx.monochrome else None)
            return
            
        shatter_phase = max(0.0, (ctx.progress - 0.7) / 0.3)
        
        for c in self.cracks:
            for i in range(1, len(c['path'])):
                x1, y1 = c['path'][i-1]
                x2, y2 = c['path'][i]
                
                # Falling shards logic could go here; simplified to disappearing
                if shatter_phase > 0 and self.rng.random() < shatter_phase:
                    continue
                    
                char = "/" if (x2 > x1 and y2 < y1) or (x2 < x1 and y2 > y1) else "\\"
                if x1 == x2: char = "|"
                if y1 == y2: char = "-"
                
                canvas.put_char(x2, y2, char, fg=(200, 200, 255) if not ctx.monochrome else None)
