import math
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas

class PortalDoor(Animation):
    meta = AnimationMeta(
        id="portal_door",
        slug="portal-door",
        name="Portal Door",
        author_name="Pixel",
        author_handle="@pixel",
        description="A rectangular portal opens, shows depth, then closes.",
        tags=["portal", "depth", "magic"],
        recommended_duration_ms=6000
    )

    def setup(self, ctx: AnimationContext):
        pass

    def update(self, ctx: AnimationContext):
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas):
        cx = ctx.width // 2
        cy = ctx.height // 2
        
        # Open and close phase
        if ctx.progress < 0.3:
            p = ctx.progress / 0.3
        elif ctx.progress < 0.7:
            p = 1.0
        else:
            p = 1.0 - (ctx.progress - 0.7) / 0.3
            
        max_w = int(ctx.width * 0.4)
        max_h = int(ctx.height * 0.6)
        
        w = int(max_w * p)
        h = int(max_h * p)
        
        if w < 1 or h < 1:
            return
            
        # Draw receding rectangles for depth
        depth_factor = (ctx.elapsed_ms / 1000.0) % 1.0
        
        for i in range(5, 0, -1):
            scale = (i - depth_factor) / 5.0
            if scale <= 0: continue
            
            dw = int(w * scale)
            dh = int(h * scale)
            if dw < 1 or dh < 1: continue
            
            c = (int(100 * scale), int(50 * scale), int(255 * scale))
            char = "#" if ctx.ascii_only else "█"
            
            canvas.draw_rect(cx - dw, cy - dh, dw * 2, dh * 2, char, 
                             fg=None if ctx.monochrome else c)
                             
        # Portal outline
        canvas.draw_rect(cx - w, cy - h, w * 2, h * 2, "+" if ctx.ascii_only else "╬",
                         fg=None if ctx.monochrome else (255, 255, 255))
