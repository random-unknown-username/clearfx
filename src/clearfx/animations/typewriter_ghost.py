import math
from typing import List, Dict
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class GhostWord:
    def __init__(self, text: str, x: int, y: float):
        self.text = text
        self.x = x
        self.y = y
        self.typed = 0
        self.done_typing = False
        self.drift_speed = 0.2

class TypewriterGhost(Animation):
    meta = AnimationMeta(
        id="typewriter_ghost",
        slug="typewriter-ghost",
        name="Typewriter Ghost",
        author_name="Reed",
        author_handle="@reed",
        description="Ghostly words type themselves and fade.",
        tags=["text", "spooky", "words"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=8000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.words = ["whisper", "echo", "fade", "memory", "silence", "shadow", "drift", "lost"]
        self.active: List[GhostWord] = []
        
    def update(self, ctx: AnimationContext) -> None:
        if ctx.reduced_motion:
            return
            
        if ctx.progress < 0.7 and self.rng.random() < 0.1 and len(self.active) < 5:
            word = self.rng.choice(self.words)
            x = self.rng.randint(5, ctx.width - len(word) - 5)
            y = self.rng.uniform(5, ctx.height - 5)
            self.active.append(GhostWord(word, x, y))
            
        for w in self.active:
            if not w.done_typing:
                if self.rng.random() < 0.3:
                    w.typed += 1
                    if w.typed >= len(w.text):
                        w.done_typing = True
            else:
                w.y -= w.drift_speed
                
        self.active = [w for w in self.active if w.y > 0]

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        
        for w in self.active:
            text_to_draw = w.text[:w.typed]
            if w.done_typing:
                fade = min(1.0, max(0.0, w.y / 10.0))
                color = (int(255 * fade), int(255 * fade), int(255 * fade)) if not ctx.monochrome else None
                canvas.put_text(w.x, int(w.y), text_to_draw, fg=color, dim=True)
            else:
                color = (200, 200, 200) if not ctx.monochrome else None
                canvas.put_text(w.x, int(w.y), text_to_draw, fg=color, bold=True)
                # Cursor
                if ctx.frame_number % 10 < 5:
                    canvas.put_char(w.x + w.typed, int(w.y), '_', fg=color)
