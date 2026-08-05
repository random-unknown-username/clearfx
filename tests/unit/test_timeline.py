import pytest
from unittest.mock import patch
from clearfx.engine.timeline import FrameClock, Timeline

def test_frame_clock():
    clock = FrameClock(target_fps=30)
    assert clock.target_fps == 30
    assert clock.target_frame_time == pytest.approx(1.0 / 30)
    
    with patch("time.monotonic", side_effect=[0.0, 0.05, 0.05, 0.1]):
        clock.last_time = 0.0
        dt = clock.tick()
        assert dt == pytest.approx(0.05)

def test_frame_clock_sleep():
    clock = FrameClock(target_fps=30)
    
    with patch("time.monotonic", side_effect=[0.01, 0.03333333333333333]), patch("time.sleep") as mock_sleep:
        clock.last_time = 0.0
        dt = clock.tick()
        mock_sleep.assert_called_once()
        assert dt == pytest.approx(0.03333333333333333)

def test_timeline():
    timeline = Timeline(duration_ms=1000.0)
    assert timeline.duration_ms == 1000.0
    assert timeline.progress == 0.0
    assert not timeline.is_complete
    
    timeline.tick(0.5)
    assert timeline.elapsed_ms == 500.0
    assert timeline.progress == 0.5
    assert not timeline.is_complete
    
    timeline.tick(0.6)
    assert timeline.elapsed_ms == 1100.0
    assert timeline.progress == 1.0
    assert timeline.is_complete

def test_timeline_zero_duration():
    timeline = Timeline(duration_ms=0.0)
    assert timeline.progress == 0.0
    assert not timeline.is_complete
    timeline.tick(0.5)
    assert timeline.progress == 0.0
    assert not timeline.is_complete
