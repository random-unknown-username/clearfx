import pytest
from clearfx.engine.noise import Noise1D, Noise2D, noise1d, noise2d

def test_noise1d_consistency():
    n1 = Noise1D(seed=42)
    n2 = Noise1D(seed=42)
    assert n1.get(1.5) == n2.get(1.5)
    
    n3 = Noise1D(seed=10)
    assert n1.get(1.5) != n3.get(1.5)

def test_noise2d_consistency():
    n1 = Noise2D(seed=42)
    n2 = Noise2D(seed=42)
    assert n1.get(1.5, 2.5) == n2.get(1.5, 2.5)

def test_convenience_functions():
    val1 = noise1d(1.5, seed=42)
    val2 = noise1d(1.5, seed=42)
    assert val1 == val2
    
    val3 = noise2d(1.5, 2.5, seed=42)
    val4 = noise2d(1.5, 2.5, seed=42)
    assert val3 == val4

def test_noise1d_bounds():
    n = Noise1D(seed=0)
    for i in range(10):
        val = n.get(i * 0.1)
        assert 0.0 <= val <= 1.0
        
def test_noise2d_bounds():
    n = Noise2D(seed=0)
    for i in range(10):
        val = n.get(i * 0.1, i * 0.2)
        assert 0.0 <= val <= 1.0
