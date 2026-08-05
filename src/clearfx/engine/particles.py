import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
from .canvas import Canvas
from .cell import ColorType

@dataclass
class Particle:
    __slots__ = ['x', 'y', 'vx', 'vy', 'life', 'max_life', 'char', 'fg', 'bg', 'size']
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    char: str
    fg: ColorType
    bg: ColorType
    size: float

class ParticleEmitter:
    def __init__(self, x: float, y: float, rate: float):
        self.x = x
        self.y = y
        self.rate = rate  # particles per second
        self.velocity_range = ((-5.0, 5.0), (-5.0, 5.0))
        self.life_range = (1.0, 3.0)
        self.spread_angle = (0.0, math.pi * 2)
        self.char_set = ['*']
        self.color_range = [] # Should be list of colors if provided
        
        self._accumulator = 0.0

    def emit(self, dt: float, random_source) -> List[Particle]:
        particles = []
        self._accumulator += self.rate * dt
        
        while self._accumulator >= 1.0:
            self._accumulator -= 1.0
            
            angle = random_source.uniform(self.spread_angle[0], self.spread_angle[1])
            speed_x = random_source.uniform(self.velocity_range[0][0], self.velocity_range[0][1])
            speed_y = random_source.uniform(self.velocity_range[1][0], self.velocity_range[1][1])
            
            vx = math.cos(angle) * speed_x
            vy = math.sin(angle) * speed_y
            
            life = random_source.uniform(self.life_range[0], self.life_range[1])
            char = random_source.choice(self.char_set)
            
            fg = random_source.choice(self.color_range) if self.color_range else None
            
            p = Particle(
                x=self.x, y=self.y,
                vx=vx, vy=vy,
                life=life, max_life=life,
                char=char, fg=fg, bg=None, size=1.0
            )
            particles.append(p)
            
        return particles

class ParticleSystem:
    def __init__(self, max_particles: int = 1000):
        self.max_particles = max_particles
        self.particles: List[Particle] = []
        self.emitters: List[ParticleEmitter] = []
        
        self.gravity = (0.0, 0.0)
        self.drag = 0.0
        self.wind = (0.0, 0.0)

    def add_emitter(self, emitter: ParticleEmitter):
        self.emitters.append(emitter)

    def update(self, dt: float, random_source):
        # Update existing particles
        living_particles = []
        for p in self.particles:
            p.life -= dt
            if p.life > 0:
                p.vx += self.gravity[0] * dt + self.wind[0] * dt
                p.vy += self.gravity[1] * dt + self.wind[1] * dt
                
                # Apply drag
                p.vx *= (1.0 - self.drag * dt)
                p.vy *= (1.0 - self.drag * dt)
                
                p.x += p.vx * dt
                p.y += p.vy * dt
                
                living_particles.append(p)
                
        self.particles = living_particles
        
        # Emit new particles
        if len(self.particles) < self.max_particles:
            for emitter in self.emitters:
                new_particles = emitter.emit(dt, random_source)
                self.particles.extend(new_particles)
                
                if len(self.particles) >= self.max_particles:
                    self.particles = self.particles[:self.max_particles]
                    break

    def render(self, canvas: Canvas):
        for p in self.particles:
            if 0 <= int(p.x) < canvas.width and 0 <= int(p.y) < canvas.height:
                canvas.put_char(int(p.x), int(p.y), p.char, fg=p.fg, bg=p.bg)
