import math
from typing import List, Tuple
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas

class LaserLoom(Animation):
    meta = AnimationMeta(
        id="laser_loom",
        slug="laser-loom",
        name="Laser Loom",
        author_name="Nova",
        author_handle="@nova",
        description="Fast laser beams weave a geometric fabric pattern.",
        tags=["laser", "grid", "geometric"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=5000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.h_beams: List[float] = [] # y coords
        self.v_beams: List[float] = [] # x coords
        self.fabric: set[Tuple[int, int]] = set()
        
    def update(self, ctx: AnimationContext) -> None:
        if ctx.reduced_motion:
            return
            
        t = ctx.progress
        
        if t < 0.8:
            # Weaving phase
            if ctx.frame_number % 3 == 0:
                self.h_beams.append(ctx.height * (ctx.frame_number % 20) / 20.0)
            if ctx.frame_number % 4 == 0:
                self.v_beams.append(ctx.width * (ctx.frame_number % 30) / 30.0)
                
            # Add to fabric
            for h in self.h_beams[-1:]:
                for v in self.v_beams:
                    self.fabric.add((int(v), int(h)))
        else:
            # Slicing phase
            self.h_beams.clear()
            self.v_beams.clear()
            # Remove from fabric
            cut_x = int(ctx.width * (t - 0.8) / 0.2)
            self.fabric = { (x, y) for x, y in self.fabric if x > cut_x }

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        
        # Draw fabric
        fabric_color = (150, 0, 255) if not ctx.monochrome else None
        char = '+'
        for x, y in self.fabric:
            canvas.put_char(x, y, char, fg=fabric_color)
            
        # Draw beams
        beam_color = (255, 50, 50) if not ctx.monochrome else None
        for y in self.h_beams:
            for x in range(ctx.width):
                canvas.put_char(x, int(y), '-', fg=beam_color, bold=True)
                
        beam_color_v = (255, 150, 50) if not ctx.monochrome else None
        for x in self.v_beams:
            for y in range(ctx.height):
                ix = int(x)
                existing = canvas.get_cell(ix, y)
                current_char = existing.char if existing else ' '
                if current_char == '-':
                    canvas.put_char(ix, y, '+', fg=(255, 255, 255) if not ctx.monochrome else None, bold=True)
                else:
                    canvas.put_char(ix, y, '|', fg=beam_color_v, bold=True)
