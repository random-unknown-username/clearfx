import pytest
from clearfx.engine.palette import (
    Color, lerp_color, hsv_to_rgb, rgb_to_hsv,
    color_to_256, color_to_16, Palette, PALETTES
)

def test_rgb_clamping():
    assert Color.rgb(-10, 128, 300) == (0, 128, 255)

def test_lerp_color():
    c1 = (0, 0, 0)
    c2 = (255, 255, 255)
    assert lerp_color(c1, c2, 0.0) == (0, 0, 0)
    assert lerp_color(c1, c2, 0.5) == (127, 127, 127)
    assert lerp_color(c1, c2, 1.0) == (255, 255, 255)
    assert lerp_color(c1, c2, 1.5) == (255, 255, 255)

def test_hsv_to_rgb():
    assert hsv_to_rgb(0.0, 1.0, 1.0) == (255, 0, 0)
    assert hsv_to_rgb(1/3, 1.0, 1.0) == (0, 255, 0)

def test_rgb_to_hsv():
    assert rgb_to_hsv(255, 0, 0) == (0.0, 1.0, 1.0)
    h, s, v = rgb_to_hsv(0, 255, 0)
    assert pytest.approx(h) == 1/3
    assert s == 1.0
    assert v == 1.0

def test_color_to_256():
    assert color_to_256(0, 0, 0) == 16
    assert color_to_256(255, 255, 255) == 231

def test_color_to_16():
    assert color_to_16(0, 0, 0) == 0
    assert color_to_16(255, 255, 255) == 15

def test_palette():
    p = Palette([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    assert p.get(0) == (255, 0, 0)
    assert p.get(3) == (255, 0, 0)
    
    assert p.get_interpolated(0.0) == (255, 0, 0)
    assert p.get_interpolated(0.5) == (0, 255, 0)
    assert p.get_interpolated(1.0) == (0, 0, 255)

def test_palettes_exist():
    assert 'ocean' in PALETTES
    assert 'neon' in PALETTES
