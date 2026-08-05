"""Animation player — orchestrates the animation loop.

Ties together the animation, terminal session, rendering engine, and timing.
"""
from __future__ import annotations

import sys
import time
import select
from typing import Any, Optional

from .terminal import TerminalSession, TerminalCapabilities
from .animation import Animation, AnimationContext
from .framebuffer import FrameBuffer
from .renderer import DiffRenderer
from .timeline import FrameClock, Timeline


class AnimationPlayer:
    """Plays an animation in a terminal session.

    Args:
        animation: The animation instance to play.
        session: The terminal session (optional — will create one if not given).
        config: ClearFXConfig or dict with settings.
        seed: Random seed for deterministic playback.
    """

    def __init__(
        self,
        animation: Animation,
        session: Optional[TerminalSession] = None,
        config: Any = None,
        seed: Optional[int] = None,
        loop: bool = False,
    ) -> None:
        self.animation = animation
        self._external_session = session
        self._config = config
        self.loop = loop

        # Extract settings from config (supports both dict and dataclass)
        if config is None:
            cfg: dict[str, Any] = {}
        elif isinstance(config, dict):
            cfg = config
        else:
            # Assume dataclass with attributes
            cfg = {
                "fps": getattr(config, "fps", 30),
                "duration_ms": getattr(config, "duration_ms", None),
                "reduced_motion": getattr(config, "reduced_motion", False),
                "ascii_only": getattr(config, "ascii_only", False),
                "monochrome": getattr(config, "monochrome", False),
                "clear_after": getattr(config, "clear_after", True),
                "skip_on_keypress": getattr(config, "skip_on_keypress", True),
                "attribution_position": getattr(config, "attribution_position", "auto"),
            }

        self.fps = cfg.get("fps", 30)
        self.duration_ms = cfg.get("duration_ms") or animation.meta.recommended_duration_ms
        # Clamp duration to 150ms - 5000ms
        self.duration_ms = max(150, min(5000, self.duration_ms))
        self.seed = seed if seed is not None else int(time.time() * 1000) % (2**31)
        self.reduced_motion = cfg.get("reduced_motion", False)
        self.ascii_only = cfg.get("ascii_only", False)
        self.monochrome = cfg.get("monochrome", False)
        self.clear_after = cfg.get("clear_after", True)
        self.skip_on_keypress = cfg.get("skip_on_keypress", True)
        self.attribution_position = cfg.get("attribution_position", "auto")

    def _check_keypress(self) -> bool:
        """Check if a key was pressed without blocking."""
        if not self.skip_on_keypress:
            return False
        try:
            if sys.platform == "win32":
                import msvcrt  # type: ignore[import]
                if msvcrt.kbhit():
                    msvcrt.getch()
                    return True
                return False
            else:
                r, _, _ = select.select([sys.stdin], [], [], 0)
                if r:
                    sys.stdin.read(1)
                    return True
                return False
        except (IOError, OSError, ValueError):
            return False

    def play(self) -> None:
        """Run the animation loop."""
        anim = self.animation

        # Use reduced motion fallback if available
        if self.reduced_motion:
            fallback = anim.get_reduced_motion_fallback()
            if fallback is not None:
                anim = fallback

        if self._external_session is not None:
            self._play_in_session(anim, self._external_session)
        else:
            with TerminalSession() as session:
                self._play_in_session(anim, session)

    def _play_in_session(self, anim: Animation, session: TerminalSession) -> None:
        """Run the animation inside a terminal session."""
        caps = session.capabilities
        width = caps.width
        height = caps.height

        # Determine color mode
        if self.ascii_only:
            color_mode = "ascii"
        elif self.monochrome:
            color_mode = "monochrome"
        else:
            color_mode = caps.colors

        framebuffer = FrameBuffer(width, height)
        renderer = DiffRenderer(color_mode=color_mode)
        clock = FrameClock(target_fps=self.fps)
        timeline = Timeline(duration_ms=self.duration_ms)

        ctx = AnimationContext(
            width=width,
            height=height,
            capabilities=caps,
            duration_ms=self.duration_ms,
            fps=self.fps,
            seed=self.seed,
            reduced_motion=self.reduced_motion,
            ascii_only=self.ascii_only,
            monochrome=self.monochrome,
            progress=0.0,
            elapsed_ms=0.0,
            dt=0.0,
            frame_number=0,
        )

        # Clear screen
        session.write(b"\033[2J\033[H")
        session.flush()

        try:
            anim.setup(ctx)

            # First frame - full render
            anim.update(ctx)
            anim.render(ctx, framebuffer.back)

            # Render attribution on the back buffer
            self._render_attribution(framebuffer.back, anim, ctx.progress)

            initial_bytes = renderer.render_full(framebuffer.back)
            session.write(initial_bytes)
            session.flush()
            framebuffer.swap()

            # Animation loop
            while True:
                if self._check_keypress():
                    break

                dt = clock.tick()
                timeline.tick(dt)

                if timeline.is_complete:
                    if self.loop:
                        # Reset for next loop
                        timeline = Timeline(duration_ms=self.duration_ms)
                        # Re-seed or keep context flowing? Better to let context frame_number continue
                        # but elapsed_ms resets.
                    else:
                        break

                # Update context
                ctx = AnimationContext(
                    width=width,
                    height=height,
                    capabilities=caps,
                    duration_ms=self.duration_ms,
                    fps=self.fps,
                    seed=self.seed,
                    reduced_motion=self.reduced_motion,
                    ascii_only=self.ascii_only,
                    monochrome=self.monochrome,
                    progress=timeline.progress,
                    elapsed_ms=timeline.elapsed_ms,
                    dt=dt,
                    frame_number=ctx.frame_number + 1,
                )

                # Clear back buffer and render new frame
                framebuffer.back.clear()
                anim.update(ctx)
                anim.render(ctx, framebuffer.back)

                # Attribution overlay (show for final 35%)
                if ctx.progress >= 0.65:
                    self._render_attribution(framebuffer.back, anim, ctx.progress)

                # Diff render
                changes = framebuffer.diff()
                if changes:
                    diff_bytes = renderer.render_diff(changes)
                    session.write(diff_bytes)
                    session.flush()

                framebuffer.swap()

        except KeyboardInterrupt:
            pass
        finally:
            anim.cleanup()
            if self.clear_after:
                session.write(b"\033[2J\033[H")
                session.flush()

    def _render_attribution(
        self, canvas: Any, anim: Animation, progress: float
    ) -> None:
        """Render the attribution overlay on the canvas."""
        meta = anim.meta
        text = f"◇ {meta.name} · {meta.author_handle}"
        if self.ascii_only:
            text = f"* {meta.name} - {meta.author_handle}"

        # Truncate for narrow terminals
        max_len = canvas.width - 2
        if len(text) > max_len:
            text = text[:max_len - 1] + "…"

        if canvas.width < 20 or canvas.height < 5:
            return

        # Position: bottom-right by default
        x = canvas.width - len(text) - 1
        y = canvas.height - 1

        # Fade in effect: compute alpha based on how far into the attribution phase
        # Attribution appears from 65% to 100% of timeline
        attr_progress = max(0.0, (progress - 0.65) / 0.35)

        # Draw with dim style
        fg = (120, 120, 120) if not self.monochrome else None
        canvas.put_text(x, y, text, fg=fg, dim=True)
