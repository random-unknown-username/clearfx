import pytest
from clearfx.engine.particles import Particle, ParticleEmitter, ParticleSystem
import random

class MockCanvas:
    def __init__(self):
        self.width = 100
        self.height = 100
        self.points = []
    
    def put_char(self, x, y, char, fg=None, bg=None):
        self.points.append((x, y, char, fg, bg))

def test_particle_creation():
    p = Particle(x=1.0, y=2.0, vx=0.1, vy=0.2, life=1.0, max_life=1.0, 
                 char='*', fg=(255,255,255), bg=None, size=1.0)
    assert p.x == 1.0
    assert p.y == 2.0
    assert p.char == '*'

def test_emitter():
    emitter = ParticleEmitter(x=10.0, y=10.0, rate=10.0)
    rand = random.Random(42)
    particles = emitter.emit(0.1, rand) # 10 * 0.1 = 1 particle
    assert len(particles) == 1
    assert particles[0].x == 10.0
    assert particles[0].y == 10.0

def test_particle_system_update():
    system = ParticleSystem(max_particles=10)
    emitter = ParticleEmitter(x=5.0, y=5.0, rate=100.0)
    system.add_emitter(emitter)
    
    rand = random.Random(42)
    system.update(0.05, rand) # Should create 5 particles
    assert len(system.particles) == 5
    
    # Update again to move particles
    initial_y = [p.y for p in system.particles]
    system.gravity = (0.0, 10.0)
    system.update(0.1, rand)
    
    # Particles should have moved
    for i, p in enumerate(system.particles[:5]):
        assert p.y != initial_y[i]

def test_particle_system_render():
    system = ParticleSystem()
    p = Particle(x=10.0, y=20.0, vx=0.0, vy=0.0, life=1.0, max_life=1.0, 
                 char='@', fg=None, bg=None, size=1.0)
    system.particles.append(p)
    
    canvas = MockCanvas()
    system.render(canvas)
    
    assert len(canvas.points) == 1
    assert canvas.points[0][:3] == (10, 20, '@')
