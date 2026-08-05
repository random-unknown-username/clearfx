from dataclasses import dataclass
from typing import List, Tuple, Optional
import math
from .cell import Cell, ColorType

try:
    from wcwidth import wcwidth
except ImportError:
    def wcwidth(c):
        return 1 if c else 0

class Canvas:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cells: List[Optional[Cell]] = [None] * (width * height)
        self.clip_rect: Optional[Tuple[int, int, int, int]] = None

    def set_clip(self, x: int, y: int, w: int, h: int):
        self.clip_rect = (max(0, x), max(0, y), min(self.width, x + w), min(self.height, y + h))

    def clear_clip(self):
        self.clip_rect = None

    def _in_bounds(self, x: int, y: int) -> bool:
        if self.clip_rect:
            cx, cy, cw, ch = self.clip_rect
            if not (cx <= x < cw and cy <= y < ch):
                return False
        return 0 <= x < self.width and 0 <= y < self.height

    def clear(self):
        self.cells = [None] * (self.width * self.height)

    def fill(self, char: str = ' ', fg: ColorType = None, bg: ColorType = None):
        cell = Cell(char=char, fg_color=fg, bg_color=bg)
        for i in range(len(self.cells)):
            self.cells[i] = cell.copy()

    def put_char(
        self, x: int, y: int, char: str,
        fg: ColorType = None, bg: ColorType = None,
        style: dict | None = None,
        bold: bool = False, dim: bool = False, italic: bool = False,
        underline: bool = False, reverse: bool = False, strikethrough: bool = False,
        blink: bool = False,
        **_kwargs: object,
    ) -> None:
        if not self._in_bounds(x, y):
            return
        
        idx = y * self.width + x
        if not self.cells[idx]:
            self.cells[idx] = Cell()
        
        cell = self.cells[idx]
        cell.char = char
        if fg is not None: cell.fg_color = fg
        if bg is not None: cell.bg_color = bg
        if bold: cell.bold = True
        if dim: cell.dim = True
        if italic: cell.italic = True
        if underline: cell.underline = True
        if reverse: cell.reverse = True
        if strikethrough: cell.strikethrough = True
        if blink: cell.blink = True
        if style:
            for k, v in style.items():
                setattr(cell, k, v)
        
        w = wcwidth(char)
        if w > 1 and x + 1 < self.width:
            self.cells[idx + 1] = Cell(char='')

    def put_text(
        self, x: int, y: int, text: str,
        fg: ColorType = None, bg: ColorType = None,
        style: dict | None = None,
        bold: bool = False, dim: bool = False, italic: bool = False,
        underline: bool = False, reverse: bool = False, strikethrough: bool = False,
        blink: bool = False,
        **_kwargs: object,
    ) -> None:
        cx = x
        for char in text:
            w = wcwidth(char)
            if w < 0:
                continue
            self.put_char(
                cx, y, char, fg, bg, style,
                bold=bold, dim=dim, italic=italic,
                underline=underline, reverse=reverse,
                strikethrough=strikethrough, blink=blink,
            )
            cx += w

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, char: str, fg: ColorType = None, bg: ColorType = None):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            self.put_char(x1, y1, char, fg, bg)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def draw_rect(self, x: int, y: int, w: int, h: int, char: str, fg: ColorType = None, bg: ColorType = None, filled: bool = False):
        if filled:
            for cy in range(y, y + h):
                for cx in range(x, x + w):
                    self.put_char(cx, cy, char, fg, bg)
        else:
            for cx in range(x, x + w):
                self.put_char(cx, y, char, fg, bg)
                self.put_char(cx, y + h - 1, char, fg, bg)
            for cy in range(y + 1, y + h - 1):
                self.put_char(x, cy, char, fg, bg)
                self.put_char(x + w - 1, cy, char, fg, bg)

    def draw_circle(self, cx: int, cy: int, r: int, char: str, fg: ColorType = None, bg: ColorType = None):
        x = r
        y = 0
        err = 0

        while x >= y:
            self.put_char(cx + x, cy + y, char, fg, bg)
            self.put_char(cx + y, cy + x, char, fg, bg)
            self.put_char(cx - y, cy + x, char, fg, bg)
            self.put_char(cx - x, cy + y, char, fg, bg)
            self.put_char(cx - x, cy - y, char, fg, bg)
            self.put_char(cx - y, cy - x, char, fg, bg)
            self.put_char(cx + y, cy - x, char, fg, bg)
            self.put_char(cx + x, cy - y, char, fg, bg)

            y += 1
            err += 1 + 2 * y
            if 2 * (err - x) + 1 > 0:
                x -= 1
                err += 1 - 2 * x

    def draw_arc(self, cx: int, cy: int, r: int, start_angle: float, end_angle: float, char: str, fg: ColorType = None, bg: ColorType = None):
        # A simple naive implementation for arcs
        steps = max(10, int(r * abs(end_angle - start_angle)))
        for i in range(steps):
            angle = start_angle + (end_angle - start_angle) * (i / steps)
            px = cx + int(r * math.cos(angle))
            py = cy + int(r * math.sin(angle))
            self.put_char(px, py, char, fg, bg)

    def draw_wave(self, y_center: int, amplitude: float, frequency: float, phase: float, width: int, char: str, fg: ColorType = None, bg: ColorType = None):
        for x in range(width):
            y = y_center + int(amplitude * math.sin(frequency * x + phase))
            self.put_char(x, y, char, fg, bg)

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y * self.width + x]
        return None
