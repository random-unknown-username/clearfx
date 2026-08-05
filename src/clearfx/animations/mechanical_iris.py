import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas

class MechanicalIris(Animation):
    meta = AnimationMeta(
        id="mechanical_iris",
        slug="mechanical-iris",
        name="Mechanical Iris",
        author_name="Iris",
        author_handle="@iris",
        description="Radial blades close like a camera aperture.",
        tags=["mechanical", "camera", "circle"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=3000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.num_blades = 6
        self.blade_chars = ['▓', '▒', '░'] if not ctx.ascii_only else ['#', '=', '-']
        
    def update(self, ctx: AnimationContext) -> None:
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        
        cx = ctx.width / 2
        cy = ctx.height / 2
        max_radius = max(ctx.width, ctx.height)
        
        # Aperture closing
        progress = ctx.progress
        if progress > 0.9:
            return # Clean screen at the end
            
        aperture_radius = max_radius * (1.0 - (progress / 0.9))
        rotation = progress * math.pi / 2
        
        for y in range(ctx.height):
            for x in range(ctx.width):
                dx = x - cx
                dy = (y - cy) * 2 # terminal aspect ratio correction
                
                dist = math.sqrt(dx**2 + dy**2)
                if dist > aperture_radius:
                    angle = math.atan2(dy, dx) + rotation
                    
                    # Determine which blade we are on
                    blade_idx = int((angle / (math.pi * 2)) * self.num_blades) % self.num_blades
                    
                    # Metallic sheen based on angle
                    sheen = (math.sin(angle * 3) + 1) / 2
                    char_idx = int(sheen * (len(self.blade_chars) - 1))
                    char = self.blade_chars[char_idx]
                    
                    color = (100 + int(100 * sheen), 100 + int(100 * sheen), 110 + int(100 * sheen)) if not ctx.monochrome else None
                    canvas.put_char(x, y, char, fg=color)
