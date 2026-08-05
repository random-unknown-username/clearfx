import pytest
from clearfx.engine.canvas import Canvas
from clearfx.engine.cell import Cell

def test_canvas_initialization():
    canvas = Canvas(10, 20)
    assert canvas.width == 10
    assert canvas.height == 20
    assert len(canvas.cells) == 200

def test_canvas_in_bounds():
    canvas = Canvas(10, 10)
    assert canvas._in_bounds(5, 5) is True
    assert canvas._in_bounds(10, 10) is False
    assert canvas._in_bounds(-1, 0) is False

def test_canvas_clip_rect():
    canvas = Canvas(10, 10)
    canvas.set_clip(2, 2, 4, 4)
    assert canvas._in_bounds(3, 3) is True
    assert canvas._in_bounds(1, 1) is False
    assert canvas._in_bounds(6, 6) is False
    canvas.clear_clip()
    assert canvas._in_bounds(1, 1) is True

def test_canvas_clear():
    canvas = Canvas(10, 10)
    canvas.put_char(0, 0, 'A')
    assert canvas.get_cell(0, 0) is not None
    canvas.clear()
    assert canvas.get_cell(0, 0) is None

def test_canvas_fill():
    canvas = Canvas(10, 10)
    canvas.fill('X', (255, 0, 0), (0, 255, 0))
    cell = canvas.get_cell(5, 5)
    assert cell.char == 'X'
    assert cell.fg_color == (255, 0, 0)
    assert cell.bg_color == (0, 255, 0)

def test_canvas_put_char():
    canvas = Canvas(10, 10)
    canvas.put_char(1, 1, 'A', fg=(255, 255, 255), bold=True)
    cell = canvas.get_cell(1, 1)
    assert cell.char == 'A'
    assert cell.fg_color == (255, 255, 255)
    assert cell.bold is True

def test_canvas_put_text():
    canvas = Canvas(10, 10)
    canvas.put_text(0, 0, 'Hello')
    assert canvas.get_cell(0, 0).char == 'H'
    assert canvas.get_cell(1, 0).char == 'e'
    assert canvas.get_cell(4, 0).char == 'o'
    assert canvas.get_cell(5, 0) is None

def test_canvas_draw_line():
    canvas = Canvas(10, 10)
    canvas.draw_line(0, 0, 2, 2, 'X')
    assert canvas.get_cell(0, 0).char == 'X'
    assert canvas.get_cell(1, 1).char == 'X'
    assert canvas.get_cell(2, 2).char == 'X'

def test_canvas_draw_rect():
    canvas = Canvas(10, 10)
    canvas.draw_rect(0, 0, 3, 3, '#')
    assert canvas.get_cell(0, 0).char == '#'
    assert canvas.get_cell(2, 0).char == '#'
    assert canvas.get_cell(0, 2).char == '#'
    assert canvas.get_cell(1, 1) is None
    
def test_canvas_draw_rect_filled():
    canvas = Canvas(10, 10)
    canvas.draw_rect(0, 0, 3, 3, '#', filled=True)
    assert canvas.get_cell(1, 1).char == '#'

def test_canvas_draw_circle():
    canvas = Canvas(10, 10)
    canvas.draw_circle(5, 5, 2, 'O')
    assert canvas.get_cell(5, 3).char == 'O'
    assert canvas.get_cell(5, 7).char == 'O'
