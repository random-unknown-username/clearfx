from typing import List, Tuple, Optional
from .canvas import Canvas
from .cell import ColorType

class Sprite:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # Stored as lines of characters
        self.lines: List[str] = [' ' * width for _ in range(height)]
        # Optional parallel structure for colors
        self.fg_colors: List[List[Optional[ColorType]]] = [[None for _ in range(width)] for _ in range(height)]
        self.bg_colors: List[List[Optional[ColorType]]] = [[None for _ in range(width)] for _ in range(height)]

    @classmethod
    def from_string(cls, ascii_art: str) -> 'Sprite':
        raw_lines = ascii_art.strip('\n').split('\n')
        if not raw_lines:
            return cls(0, 0)
            
        height = len(raw_lines)
        width = max(len(line) for line in raw_lines)
        
        sprite = cls(width, height)
        for y, line in enumerate(raw_lines):
            # Pad line to match width
            padded = line.ljust(width, ' ')
            sprite.lines[y] = padded
            
        return sprite

    def set_color(self, x: int, y: int, fg: ColorType = None, bg: ColorType = None):
        if 0 <= x < self.width and 0 <= y < self.height:
            if fg is not None:
                self.fg_colors[y][x] = fg
            if bg is not None:
                self.bg_colors[y][x] = bg

    def render(self, canvas: Canvas, x: int, y: int, ignore_spaces: bool = True):
        for cy in range(self.height):
            canvas_y = y + cy
            if canvas_y < 0 or canvas_y >= canvas.height:
                continue
                
            line = self.lines[cy]
            for cx in range(self.width):
                canvas_x = x + cx
                if canvas_x < 0 or canvas_x >= canvas.width:
                    continue
                    
                char = line[cx]
                if ignore_spaces and char == ' ':
                    continue
                    
                fg = self.fg_colors[cy][cx]
                bg = self.bg_colors[cy][cx]
                
                canvas.put_char(canvas_x, canvas_y, char, fg=fg, bg=bg)
