import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource
from clearfx.engine.noise import noise1d

class PaperBurn(Animation):
    meta = AnimationMeta(
        id="paper_burn",
        slug="paper-burn",
        name="Paper Burn",
        author_name="Flux",
        author_handle="@flux",
        description="A bright irregular burning edge moves across the screen.",
        tags=["fire", "burn", "organic"],
        recommended_duration_ms=6000
    )

    def setup(self, ctx: AnimationContext):
        self.rng = RandomSource(ctx.seed)
        self.ashes = []

    def update(self, ctx: AnimationContext):
        if self.rng.random() < 0.3:
            bx = int(ctx.progress * ctx.width * 1.5)
            self.ashes.append({
                'x': self.rng.randint(max(0, bx - 10), max(0, bx)),
                'y': self.rng.randint(0, ctx.height - 1),
                'vy': self.rng.uniform(0.1, 0.3),
                'life': 1.0
            })
            
        for a in self.ashes:
            a['y'] += a['vy']
            a['life'] -= 0.02
        self.ashes = [a for a in self.ashes if a['life'] > 0 and a['y'] < ctx.height]

    def render(self, ctx: AnimationContext, canvas: Canvas):
        burn_x_base = ctx.progress * (ctx.width + 20) - 10
        
        for y in range(ctx.height):
            noise_val = noise1d(y * 0.1, ctx.seed)
            burn_x = burn_x_base + noise_val * 8
            
            for x in range(ctx.width):
                if x > burn_x:
                    if x < burn_x + 3:
                        c = (255, 100, 0)
                        char = "#" if ctx.ascii_only else "▒"
                        canvas.put_char(x, y, char, fg=None if ctx.monochrome else c)
                    elif x < burn_x + 5:
                        c = (255, 200, 0)
                        char = "@" if ctx.ascii_only else "▓"
                        canvas.put_char(x, y, char, fg=None if ctx.monochrome else c)
                    elif self.rng.random() < 0.05:
                        canvas.put_char(x, y, ".", fg=(50, 50, 50) if not ctx.monochrome else None)
                        
        for a in self.ashes:
            ax, ay = int(a['x']), int(a['y'])
            if 0 <= ax < ctx.width and 0 <= ay < ctx.height:
                canvas.put_char(ax, ay, ".", fg=(80, 80, 80) if not ctx.monochrome else None)
