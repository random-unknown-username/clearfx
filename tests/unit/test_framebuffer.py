import pytest
from clearfx.engine.framebuffer import FrameBuffer
from clearfx.engine.cell import Cell

def test_framebuffer_initialization():
    fb = FrameBuffer(10, 10)
    assert fb.width == 10
    assert fb.height == 10
    assert fb.front.width == 10
    assert fb.back.width == 10

def test_framebuffer_swap():
    fb = FrameBuffer(10, 10)
    fb.back.put_char(0, 0, 'A')
    fb.swap()
    assert fb.front.get_cell(0, 0).char == 'A'
    assert fb.back.get_cell(0, 0).char == ' '

def test_framebuffer_diff():
    fb = FrameBuffer(10, 10)
    # The front is initialized with ' ' fill
    # The back is initialized with None
    
    # Fill back with ' ' so it matches front
    fb.back.fill(' ')
    changes = fb.diff()
    assert len(changes) == 0
    
    fb.back.put_char(0, 0, 'A')
    fb.back.put_char(1, 0, 'B')
    changes = fb.diff()
    assert len(changes) == 2
    assert changes[0][0] == 0
    assert changes[0][1] == 0
    assert changes[0][2].char == 'A'
    
    assert changes[1][0] == 1
    assert changes[1][1] == 0
    assert changes[1][2].char == 'B'
