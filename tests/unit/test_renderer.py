import pytest
from clearfx.engine.renderer import DiffRenderer
from clearfx.engine.cell import Cell
from clearfx.engine.canvas import Canvas

def test_renderer_initialization():
    r = DiffRenderer(color_mode='truecolor')
    assert r.color_mode == 'truecolor'

def test_renderer_format_color():
    r = DiffRenderer(color_mode='truecolor')
    # fg
    assert r._format_color((255, 0, 0), False) == '\033[38;2;255;0;0m'
    # bg
    assert r._format_color((0, 255, 0), True) == '\033[48;2;0;255;0m'
    
    r2 = DiffRenderer(color_mode='256color')
    assert r2._format_color(15, False) == '\033[38;5;15m'
    
def test_render_diff():
    r = DiffRenderer()
    c1 = Cell(char='A', fg_color=(255, 0, 0))
    c2 = Cell(char='B', bold=True)
    changes = [
        (0, 0, c1),
        (1, 0, c2)
    ]
    out = r.render_diff(changes)
    assert b'\033[1;1H' in out
    assert b'A' in out
    assert b'\033[1m' in out
    assert b'B' in out
    assert b'\033[0m' in out

def test_render_full():
    r = DiffRenderer()
    canvas = Canvas(2, 2)
    canvas.put_char(0, 0, 'X')
    canvas.put_char(1, 1, 'Y')
    out = r.render_full(canvas)
    assert b'X' in out
    assert b'Y' in out
