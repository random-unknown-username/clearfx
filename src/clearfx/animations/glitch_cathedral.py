import math
from typing import List, Dict, Any
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class GlitchCathedral(Animation):
    meta = AnimationMeta(
        id="glitch_cathedral",
        slug="glitch-cathedral",
        name="Glitch Cathedral",
        author_name="Mira",
        author_handle="@mira",
        description="Symmetrical columns build upward, glitch, then collapse.",
        tags=["architectural", "glitch", "symmetry"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=6000,
        supports_ascii=True,
        supports_monochrome=True
    )

    def setup(self, ctx: AnimationContext):
        self.rng = RandomSource(ctx.seed)
        self.columns = []
        offsets = [2, 6, 12, 18, 26, 36]
        for off in offsets:
            char_set = ["|", "!", ":", "."] if ctx.ascii_only else ["│", "║", "┃", "╫"]
            self.columns.append({
                'offset': off,
                'char': self.rng.choice(char_set),
                'color': (self.rng.randint(100, 255), self.rng.randint(100, 255), 255),
                'max_height': self.rng.uniform(0.6, 0.9)
            })

    def update(self, ctx: AnimationContext):
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas):
        cx = ctx.width // 2
        build_phase = min(1.0, ctx.progress * 2.0)
        glitch_phase = max(0.0, min(1.0, (ctx.progress - 0.5) * 4.0))
        collapse_phase = max(0.0, min(1.0, (ctx.progress - 0.75) * 4.0))
        
        for col in self.columns:
            off = col['offset']
            h = int(ctx.height * col['max_height'] * build_phase)
            h = max(0, h - int(ctx.height * collapse_phase))
            
            c_char = col['char']
            c_color = None if ctx.monochrome else col['color']
            
            for y in range(ctx.height - h, ctx.height):
                x_left = cx - off
                x_right = cx + off
                
                if glitch_phase > 0 and self.rng.random() < glitch_phase * 0.3:
                    x_left += self.rng.randint(-2, 2)
                    x_right += self.rng.randint(-2, 2)
                    if self.rng.random() < 0.5:
                        c_char = self.rng.choice(["@", "#", "%", "&", "X", "+"])
                    if not ctx.monochrome and self.rng.random() < 0.5:
                        c_color = (255, 0, 0)
                        
                canvas.put_char(x_left, y, c_char, fg=c_color)
                canvas.put_char(x_right, y, c_char, fg=c_color)
                
                c_char = col['char']
                c_color = None if ctx.monochrome else col['color']
