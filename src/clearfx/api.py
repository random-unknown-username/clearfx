"""Public API for integrating ClearFX into other Python applications."""
from __future__ import annotations

from typing import Optional

def play(
    slug: Optional[str] = None, 
    clear_after: Optional[bool] = None,
    duration_ms: Optional[int] = None,
    fps: Optional[int] = None,
    fallback_on_error: bool = True
) -> bool:
    """Play a ClearFX terminal animation.
    
    This function is designed to be easily embedded into other Python CLIs,
    such as Typer or Click applications.
    
    Args:
        slug: The specific animation slug to play. If None, a random one is chosen.
        clear_after: Whether to clear the terminal completely after playback.
        duration_ms: Override the animation duration in milliseconds.
        fps: Override the target frames per second.
        fallback_on_error: If playback fails (e.g. terminal not supported), fallback to normal clear.
        
    Returns:
        True if the animation played successfully, False otherwise.
    """
    try:
        from clearfx.core.config import load_config
        from clearfx.core.registry import AnimationRegistry
        from clearfx.core.selector import AnimationSelector
        from clearfx.engine.terminal import TerminalSession
        from clearfx.engine.player import AnimationPlayer
        
        config = load_config()
        if clear_after is not None:
            config.clear_after = clear_after
        if duration_ms is not None:
            config.duration_ms = duration_ms
        if fps is not None:
            config.fps = fps
            
        registry = AnimationRegistry()
        
        if slug:
            anim_cls = registry.get_animation(slug)
            if not anim_cls:
                raise ValueError(f"Animation '{slug}' not found.")
        else:
            selector = AnimationSelector(registry, config)
            anim_cls = selector.select()
            
        if not anim_cls:
            raise RuntimeError("No animations available to play.")
            
        anim = anim_cls()
        with TerminalSession() as session:
            player = AnimationPlayer(anim, session, config)
            player.play()
            
        return True
    except Exception:
        if fallback_on_error:
            from clearfx.core.fallback import fallback_clear
            fallback_clear()
        return False


def clear() -> bool:
    """Drop-in programmatic replacement for clearing the terminal.
    
    Plays a random, stunning terminal animation, then clears the screen,
    leaving the user with a fresh prompt.
    """
    return play(clear_after=True)
