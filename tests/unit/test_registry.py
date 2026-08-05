import pytest
from clearfx.core.registry import AnimationRegistry, AnimationInfo

def test_animation_info():
    info = AnimationInfo(
        slug="test-anim",
        name="Test Anim",
        author_name="John Doe",
        author_handle="johndoe",
        description="A test animation",
        source="builtin"
    )
    assert info.slug == "test-anim"
    assert info.source == "builtin"
    assert info.version == "1.0"
    assert info.supports_ascii is True

class DummyMeta:
    slug = "dummy"
    name = "Dummy"
    author_name = "Author"
    author_handle = "author"
    description = "desc"
    tags = ["tag1"]
    version = "1.0"
    min_width = 10
    min_height = 10
    recommended_duration_ms = 1000
    supports_ascii = True
    supports_monochrome = True

class DummyAnim:
    meta = DummyMeta()

def test_registry_discover_builtin(monkeypatch):
    registry = AnimationRegistry()
    registry._builtin = {"dummy": DummyAnim}
    registry._loaded = True
    
    assert registry.is_installed("dummy")
    assert registry.get_animation("dummy") == DummyAnim
    assert "dummy" not in registry._community

def test_list_animations(monkeypatch):
    registry = AnimationRegistry()
    registry._builtin = {"dummy": DummyAnim}
    registry._community = {"comm-anim": {"path": "/fake/path", "source": "community"}}
    registry._loaded = True
    
    all_anims = registry.list_animations()
    assert len(all_anims) == 2
    slugs = [a["slug"] for a in all_anims]
    assert "dummy" in slugs
    assert "comm-anim" in slugs

    builtin_anims = registry.list_animations(source="builtin")
    assert len(builtin_anims) == 1
    assert builtin_anims[0]["slug"] == "dummy"
    
def test_get_all_builtin_classes():
    registry = AnimationRegistry()
    registry._builtin = {"dummy": DummyAnim}
    registry._loaded = True
    classes = registry.get_all_builtin_classes()
    assert classes == [DummyAnim]
