import pytest
from clearfx.engine.easing import (
    linear, ease_in_quad, ease_in_out_quad,
    get_easing, ease_in_bounce
)

def test_linear():
    assert linear(0.0) == 0.0
    assert linear(0.5) == 0.5
    assert linear(1.0) == 1.0

def test_ease_in_quad():
    assert ease_in_quad(0.0) == 0.0
    assert ease_in_quad(0.5) == 0.25
    assert ease_in_quad(1.0) == 1.0

def test_get_easing():
    assert get_easing('linear') == linear
    assert get_easing('ease_in_quad') == ease_in_quad
    # default fallback
    assert get_easing('non_existent') == linear

@pytest.mark.parametrize("t, expected", [
    (0.0, 0.0),
    (0.5, 0.5),
    (1.0, 1.0)
])
def test_ease_in_out_quad(t, expected):
    assert ease_in_out_quad(t) == expected

def test_ease_boundaries():
    easings = ['ease_in_quad', 'ease_out_quad', 'ease_in_sine', 'ease_in_expo', 'ease_in_bounce']
    for name in easings:
        func = get_easing(name)
        assert func(0.0) == pytest.approx(0.0, abs=1e-5)
        assert func(1.0) == pytest.approx(1.0, abs=1e-5)
