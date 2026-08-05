import math
from typing import List
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas

class MosaicFlip(Animation):
    meta = AnimationMeta(
        id="mosaic_flip",
        slug="mosaic-flip",
        name="Mosaic Flip",
        author_name="Pixel",
        author_handle="@pixel",
        description="Tiles flip in coordinated waves.",
        tags=["geometry", "wave", "grid"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=4000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.cols = 4
        self.rows = 2
        
    def update(self, ctx: AnimationContext) -> None:
        pass

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        
        tile_w = ctx.width // self.cols
        tile_h = ctx.height // self.rows
        
        for r in range(self.rows):
            for c in range(self.cols):
                # Calculate wave delay based on position
                delay = (c * 0.1) + (r * 0.1)
                t = (ctx.progress * 2) - delay
                
                state = 0 # 0: flat, 1: edge, 2: empty
                if t < 0.2:
                    state = 0
                elif t < 0.4:
                    state = 1
                else:
                    state = 2
                    
                x = c * tile_w
                y = r * tile_h
                
                if state == 0:
                    color = (100, 150, 200) if not ctx.monochrome else None
                    char = '█' if not ctx.ascii_only else '#'
                    for dy in range(tile_h - 1):
                        canvas.put_text(x, y + dy, char * (tile_w - 1), fg=color)
                elif state == 1:
                    color = (255, 255, 255) if not ctx.monochrome else None
                    char = '|'
                    for dy in range(tile_h - 1):
                        canvas.put_char(x + (tile_w // 2), y + dy, char, fg=color, bold=True)
