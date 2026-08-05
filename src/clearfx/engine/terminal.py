"""Terminal session management with bulletproof state restoration.

Handles alternate screen, cursor visibility, signal handlers,
and terminal mode settings. Always restores state on exit.
"""
from __future__ import annotations

import os
import sys
import signal
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TerminalCapabilities:
    """Detected terminal capabilities."""
    width: int
    height: int
    colors: str  # "truecolor", "256color", "16color", "mono", "ascii"
    unicode_support: bool
    alternate_screen_support: bool
    title_support: bool
    os_name: str


def detect_capabilities() -> TerminalCapabilities:
    """Detect terminal capabilities from environment."""
    width, height = 80, 24
    try:
        size = os.get_terminal_size()
        width, height = size.columns, size.lines
    except OSError:
        pass

    # Color detection
    colorterm = os.environ.get("COLORTERM", "")
    term = os.environ.get("TERM", "")
    no_color = os.environ.get("NO_COLOR")

    if no_color is not None:
        colors = "mono"
    elif "truecolor" in colorterm or "24bit" in colorterm:
        colors = "truecolor"
    elif "256" in term:
        colors = "256color"
    elif term in ("xterm", "screen", "tmux", "rxvt", "linux"):
        colors = "16color"
    elif term == "dumb":
        colors = "ascii"
    else:
        # Default to 256color for most modern terminals
        colors = "256color" if term else "mono"

    # Unicode support
    lang = os.environ.get("LANG", "") + os.environ.get("LC_ALL", "")
    unicode_support = "UTF-8" in lang.upper() or "UTF8" in lang.upper()

    return TerminalCapabilities(
        width=width,
        height=height,
        colors=colors,
        unicode_support=unicode_support,
        alternate_screen_support=True,
        title_support=True,
        os_name=sys.platform,
    )


class TerminalSession:
    """Context manager for safe terminal animation sessions.

    Enters alternate screen, hides cursor, sets cbreak mode.
    Always restores everything on exit — even after signals or exceptions.

    Args:
        capabilities: Pre-detected capabilities (auto-detected if None).
    """

    def __init__(self, capabilities: Optional[TerminalCapabilities] = None, keep_screen: bool = False) -> None:
        self._capabilities = capabilities or detect_capabilities()
        self._keep_screen = keep_screen
        self._original_settings: Any = None
        self._original_flags: Optional[int] = None
        self._old_sigint: Any = None
        self._old_sigterm: Any = None
        self._old_sigwinch: Any = None
        self._cleaned_up = False

    @property
    def capabilities(self) -> TerminalCapabilities:
        """Current terminal capabilities."""
        return self._capabilities

    def get_size(self) -> tuple[int, int]:
        """Get current terminal size."""
        try:
            size = os.get_terminal_size()
            return size.columns, size.lines
        except OSError:
            return self._capabilities.width, self._capabilities.height

    def write(self, data: bytes) -> None:
        """Write bytes to terminal."""
        try:
            sys.stdout.buffer.write(data)
        except (IOError, OSError):
            pass

    def flush(self) -> None:
        """Flush terminal output."""
        try:
            sys.stdout.buffer.flush()
        except (IOError, OSError):
            pass

    def __enter__(self) -> TerminalSession:
        """Enter the terminal session."""
        # Save and set terminal mode (Unix only)
        if sys.platform != "win32":
            try:
                import termios
                import tty
                fd = sys.stdin.fileno()
                self._original_settings = termios.tcgetattr(fd)
                tty.setcbreak(fd)
            except (termios.error, ValueError, OSError):
                pass

            # Make stdin non-blocking for keypress detection
            try:
                import fcntl
                fd = sys.stdin.fileno()
                self._original_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, self._original_flags | os.O_NONBLOCK)
            except (OSError, ValueError):
                pass

        # Enter alternate screen + hide cursor
        self.write(b"\033[?1049h\033[?25l")
        self.flush()

        # Set up signal handlers
        try:
            self._old_sigint = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, self._handle_interrupt)
        except (OSError, ValueError):
            pass

        try:
            self._old_sigterm = signal.getsignal(signal.SIGTERM)
            signal.signal(signal.SIGTERM, self._handle_terminate)
        except (OSError, ValueError):
            pass

        # Handle terminal resize
        if hasattr(signal, "SIGWINCH"):
            try:
                self._old_sigwinch = signal.getsignal(signal.SIGWINCH)
                signal.signal(signal.SIGWINCH, self._handle_resize)
            except (OSError, ValueError):
                pass

        return self

    def _handle_interrupt(self, signum: int, frame: Any) -> None:
        """Handle Ctrl+C — clean up and re-raise."""
        self._cleanup()
        raise KeyboardInterrupt()

    def _handle_terminate(self, signum: int, frame: Any) -> None:
        """Handle SIGTERM — clean up and exit."""
        self._cleanup()
        sys.exit(128 + signum)

    def _handle_resize(self, signum: int, frame: Any) -> None:
        """Handle terminal resize."""
        try:
            size = os.get_terminal_size()
            self._capabilities.width = size.columns
            self._capabilities.height = size.lines
        except OSError:
            pass

    def _cleanup(self) -> None:
        """Restore all terminal state. Safe to call multiple times."""
        if self._cleaned_up:
            return
        self._cleaned_up = True

        # Restore terminal mode (Unix only)
        if sys.platform != "win32":
            if self._original_settings is not None:
                try:
                    import termios
                    fd = sys.stdin.fileno()
                    termios.tcsetattr(fd, termios.TCSADRAIN, self._original_settings)
                except (Exception,):
                    pass

            if self._original_flags is not None:
                try:
                    import fcntl
                    fd = sys.stdin.fileno()
                    fcntl.fcntl(fd, fcntl.F_SETFL, self._original_flags)
                except (Exception,):
                    pass

        # Show cursor + exit alternate screen + reset colors + enable line wrap
        if self._keep_screen:
            self.write(b"\033[?25h\033[0m\033[?7h")
        else:
            self.write(b"\033[?25h\033[?1049l\033[0m\033[?7h")
        self.flush()

        # Restore signal handlers
        try:
            if self._old_sigint is not None:
                signal.signal(signal.SIGINT, self._old_sigint)
        except (OSError, ValueError):
            pass

        try:
            if self._old_sigterm is not None:
                signal.signal(signal.SIGTERM, self._old_sigterm)
        except (OSError, ValueError):
            pass

        if hasattr(signal, "SIGWINCH"):
            try:
                if self._old_sigwinch is not None:
                    signal.signal(signal.SIGWINCH, self._old_sigwinch)
            except (OSError, ValueError):
                pass

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the terminal session — always clean up."""
        self._cleanup()
