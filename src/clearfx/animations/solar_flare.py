import math
from typing import List
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource
from clearfx.engine.easing import ease_out_quad, ease_in_quad

class Flare:
    def __init__(self, x: float, y: float, vx: float, vy: float, life: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.gravity = 0.05

class SolarFlare(Animation):
    meta = AnimationMeta(
        id="solar_flare",
        slug="solar-flare",
        name="Solar Flare",
        author_name="Ash",
        author_handle="@ash",
        description="A blazing sun emits sweeping flares before exploding.",
        tags=["fire", "space", "sun"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=4000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.flares: List[Flare] = []
        self.heat_chars = ['·', '░', '▒', '▓', '█'] if not ctx.ascii_only else ['.', ',', ':', ';', '#', '@']
        self.sun_radius = 0.0
        
    def update(self, ctx: AnimationContext) -> None:
        if ctx.reduced_motion:
            return
            
        cx = ctx.width / 2
        cy = ctx.height - 5
        
        # Sun pulses and grows
        pulse = math.sin(ctx.elapsed_ms / 200) * 0.5
        target_radius = 4 + (ctx.progress * 8) + pulse
        if ctx.progress > 0.8:
            target_radius += (ctx.progress - 0.8) * 100 # Explode
            
        self.sun_radius = target_radius
        
        # Emit flares
        if ctx.progress < 0.8 and self.rng.random() < 0.4:
            angle = math.pi + (self.rng.random() * math.pi) # Upwards half circle
            speed = self.rng.uniform(1.0, 3.0) + ctx.progress * 2
            self.flares.append(Flare(
                x=cx + math.cos(angle) * self.sun_radius,
                y=cy + math.sin(angle) * self.sun_radius,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=self.rng.uniform(20.0, 40.0)
            ))
            
        # Update flares
        for f in self.flares:
            f.x += f.vx
            f.y += f.vy
            f.vy += f.gravity # Curve downwards
            f.life -= 1.0
            
        self.flares = [f for f in self.flares if f.life > 0]

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        cx = int(ctx.width / 2)
        cy = int(ctx.height - 5)
        
        # Draw flares
        for f in self.flares:
            life_ratio = f.life / f.max_life
            char_idx = int(life_ratio * (len(self.heat_chars) - 1))
            c = self.heat_chars[char_idx]
            
            fg = (255, int(150 * life_ratio), 0) if not ctx.monochrome else None
            canvas.put_char(int(f.x), int(f.y), c, fg=fg, bold=True)
            
        # Draw sun
        r = int(self.sun_radius)
        sun_color = (255, 200, 0) if not ctx.monochrome else None
        
        # Simple circle drawing
        for y in range(-r, r+1):
            for x in range(-r*2, r*2+1):
                if (x/2)**2 + y**2 <= r**2:
                    dist = math.sqrt((x/2)**2 + y**2)
                    intensity = 1.0 - (dist / (r if r > 0 else 1))
                    c = self.heat_chars[int(intensity * (len(self.heat_chars) - 1))]
                    if ctx.progress > 0.8:
                        c = self.heat_chars[-1]
                        sun_color = (255, 255, 255) if not ctx.monochrome else None
                    canvas.put_char(cx + x, cy + y, c, fg=sun_color, bold=True)
