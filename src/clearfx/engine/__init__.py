from .cell import Cell, ColorType, EMPTY_CELL
from .canvas import Canvas
from .framebuffer import FrameBuffer
from .renderer import DiffRenderer
from .terminal import TerminalSession, TerminalCapabilities, detect_capabilities
from .timeline import FrameClock, Timeline
from .scene import Layer, Scene
from .animation import Animation, AnimationMeta, AnimationContext
from .easing import get_easing
from .particles import Particle, ParticleEmitter, ParticleSystem
from .palette import Color, Palette, PALETTES, lerp_color, hsv_to_rgb, rgb_to_hsv, color_to_256, color_to_16
from .sprite import Sprite
from .noise import Noise1D, Noise2D
from .random_source import RandomSource
from .player import AnimationPlayer

# Expose ease functions by importing all of them in easing, or simply exposing `get_easing`.
# Here we export the modules/classes as requested.
__all__ = [
    'Cell', 'ColorType', 'EMPTY_CELL',
    'Canvas',
    'FrameBuffer',
    'DiffRenderer',
    'TerminalSession', 'TerminalCapabilities', 'detect_capabilities',
    'FrameClock', 'Timeline',
    'Layer', 'Scene',
    'Animation', 'AnimationMeta', 'AnimationContext',
    'get_easing',
    'Particle', 'ParticleEmitter', 'ParticleSystem',
    'Color', 'Palette', 'PALETTES', 'lerp_color', 'hsv_to_rgb', 'rgb_to_hsv', 'color_to_256', 'color_to_16',
    'Sprite',
    'Noise1D', 'Noise2D',
    'RandomSource',
    'AnimationPlayer'
]
