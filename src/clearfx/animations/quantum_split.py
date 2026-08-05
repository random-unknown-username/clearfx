import math
from typing import List, Tuple
from clearfx.engine.animation import Animation, AnimationMeta, AnimationContext
from clearfx.engine.canvas import Canvas
from clearfx.engine.random_source import RandomSource

class QuantumObject:
    def __init__(self, x: float, y: float, char: str):
        self.x = x
        self.y = y
        self.char = char
        self.states: List[Tuple[float, float]] = []

class QuantumSplit(Animation):
    meta = AnimationMeta(
        id="quantum_split",
        slug="quantum-split",
        name="Quantum Split",
        author_name="Zero",
        author_handle="@zero",
        description="Objects split into multiple probability states before collapsing.",
        tags=["quantum", "glitch", "geometry"],
        min_width=40,
        min_height=20,
        recommended_duration_ms=4000,
        supports_ascii=True,
        supports_monochrome=True,
        version="1.0"
    )

    def setup(self, ctx: AnimationContext) -> None:
        self.rng = RandomSource(ctx.seed)
        self.objects: List[QuantumObject] = []
        chars = ['▲', '■', '●', '◆'] if not ctx.ascii_only else ['A', '#', 'O', '+']
        
        for _ in range(10):
            self.objects.append(QuantumObject(
                x=self.rng.uniform(5, ctx.width - 5),
                y=self.rng.uniform(2, ctx.height - 2),
                char=self.rng.choice(chars)
            ))
            
    def update(self, ctx: AnimationContext) -> None:
        if ctx.reduced_motion:
            return
            
        phase = ctx.progress
        
        for obj in self.objects:
            obj.states = []
            
            if 0.2 < phase < 0.8:
                num_states = 3
                spread = math.sin((phase - 0.2) / 0.6 * math.pi) * 5
                
                for i in range(num_states):
                    angle = (i / num_states) * math.pi * 2 + (ctx.elapsed_ms / 500)
                    sx = obj.x + math.cos(angle) * spread
                    sy = obj.y + math.sin(angle) * spread
                    
                    # Vibration
                    sx += self.rng.uniform(-0.5, 0.5)
                    sy += self.rng.uniform(-0.5, 0.5)
                    
                    obj.states.append((sx, sy))

    def render(self, ctx: AnimationContext, canvas: Canvas) -> None:
        canvas.clear()
        
        color1 = (0, 255, 255) if not ctx.monochrome else None
        color2 = (255, 0, 255) if not ctx.monochrome else None
        
        for obj in self.objects:
            if not obj.states:
                canvas.put_char(int(obj.x), int(obj.y), obj.char, bold=True)
            else:
                for i, (sx, sy) in enumerate(obj.states):
                    c = color1 if i % 2 == 0 else color2
                    if ctx.monochrome: c = None
                    canvas.put_char(int(sx), int(sy), obj.char, fg=c, dim=True)
