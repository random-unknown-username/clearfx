import pytest

from clearfx.animations import BUILTIN_ANIMATIONS
from clearfx.engine.animation import Animation, AnimationMeta

def test_builtin_animations_count():
    """Test that exactly 36 built-in animations are registered."""
    assert len(BUILTIN_ANIMATIONS) == 36

def test_animations_are_valid_subclasses():
    """Test that all built-in animations subclass Animation and have valid meta."""
    for anim_cls in BUILTIN_ANIMATIONS:
        assert issubclass(anim_cls, Animation), f"{anim_cls} must subclass Animation"
        assert hasattr(anim_cls, "meta"), f"{anim_cls} must have a meta attribute"
        assert isinstance(anim_cls.meta, AnimationMeta), f"{anim_cls}.meta must be AnimationMeta"
        
        # Check required meta fields
        meta = anim_cls.meta
        assert meta.id, f"{anim_cls} missing id"
        assert meta.slug, f"{anim_cls} missing slug"
        assert meta.name, f"{anim_cls} missing name"
        assert meta.author_name, f"{anim_cls} missing author_name"
        assert meta.author_handle, f"{anim_cls} missing author_handle"
