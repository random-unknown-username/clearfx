import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class FractalBranch(Animation):
    meta = AnimationMeta(
        id="fractal_branch",
        slug="fractal-branch",
        name="Fractal Branch",
        author_name="Zero",
        author_handle="@zero",
        description="A recursive branching tree grows rapidly and retracts.",
        tags=["nature", "fractal", "recursive"],
        recommended_duration_ms=6000
    )

    def setup(self, ctx: AnimationContext):
        self.rng = RandomSource(ctx.seed)

    def draw_branch(self, canvas, x, y, length, angle, depth, progress, ctx):
        if depth == 0 or length < 1:
            if progress > 0.5:
                # Leaves
                if self.rng.random() < progress:
                    c = (50, 200, 50)
                    char = "*" if ctx.ascii_only else "•"
                    canvas.put_char(int(x), int(y), char, fg=None if ctx.monochrome else c)
            return

        end_x = x + math.cos(angle) * length * progress
        end_y = y + math.sin(angle) * length * progress
        
        canvas.draw_line(int(x), int(y), int(end_x), int(end_y), 
                         "|" if ctx.ascii_only else "│", 
                         fg=(139, 69, 19) if not ctx.monochrome else None)
                         
        if progress > 0.8:
            sub_prog = (progress - 0.8) * 5.0
            self.draw_branch(canvas, end_x, end_y, length * 0.7, angle - 0.5, depth - 1, sub_prog, ctx)
            self.draw_branch(canvas, end_x, end_y, length * 0.7, angle + 0.5, depth - 1, sub_prog, ctx)

    def update(self, ctx: AnimationContext):
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas):
        self.rng = RandomSource(ctx.seed) # Reset RNG for deterministic frame
        
        # Growth and retract phase
        if ctx.progress < 0.4:
            p = ctx.progress / 0.4
        elif ctx.progress < 0.8:
            p = 1.0
        else:
            p = 1.0 - (ctx.progress - 0.8) / 0.2
            
        self.draw_branch(canvas, ctx.width // 2, ctx.height, ctx.height * 0.3, -math.pi/2, 5, p, ctx)
