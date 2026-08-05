from typing import List, Tuple
from .cell import Cell
from .canvas import Canvas

class DiffRenderer:
    def __init__(self, color_mode: str = 'truecolor'):
        self.color_mode = color_mode
        self.current_fg = None
        self.current_bg = None
        self.current_x = -1
        self.current_y = -1

    def _format_color(self, color, is_bg: bool) -> str:
        if color is None:
            return '\033[49m' if is_bg else '\033[39m'
        
        prefix = '48' if is_bg else '38'
        
        if isinstance(color, int):
            if self.color_mode in ('truecolor', '256color'):
                return f'\033[{prefix};5;{color}m'
            else:
                # Fallback to nearest 16 color (simplified)
                code = 40 + (color % 8) if is_bg else 30 + (color % 8)
                if color > 7: code += 60 # bright
                return f'\033[{code}m'
        elif isinstance(color, tuple) and len(color) == 3:
            r, g, b = color
            if self.color_mode == 'truecolor':
                return f'\033[{prefix};2;{r};{g};{b}m'
            elif self.color_mode == '256color':
                # Simplified 24-bit to 256 color mapping
                if r == g == b:
                    if r < 8: idx = 16
                    elif r > 248: idx = 231
                    else: idx = round(((r - 8) / 247) * 24) + 232
                else:
                    idx = 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)
                return f'\033[{prefix};5;{idx}m'
            else:
                return f'\033[{40 if is_bg else 30}m' # Default fallback
        return ''

    def render_diff(self, changes: List[Tuple[int, int, Cell]]) -> bytes:
        if not changes:
            return b''

        output = []
        
        # Sort by y, then x to optimize cursor movement
        changes.sort(key=lambda c: (c[1], c[0]))
        
        for x, y, cell in changes:
            if x != self.current_x or y != self.current_y:
                output.append(f'\033[{y + 1};{x + 1}H')
                self.current_x = x
                self.current_y = y
                
            if cell.fg_color != self.current_fg:
                output.append(self._format_color(cell.fg_color, False))
                self.current_fg = cell.fg_color
                
            if cell.bg_color != self.current_bg:
                output.append(self._format_color(cell.bg_color, True))
                self.current_bg = cell.bg_color
                
            # Styles (simplified, normally we track these too)
            style_code = ''
            if cell.bold: style_code += '\033[1m'
            if cell.dim: style_code += '\033[2m'
            if cell.italic: style_code += '\033[3m'
            if cell.underline: style_code += '\033[4m'
            if style_code:
                output.append(style_code)
                
            output.append(cell.char)
            self.current_x += 1
            
            # Reset styles if any were applied
            if style_code:
                output.append('\033[22;23;24m') # Reset specific styles
                
        output.append('\033[0m') # Reset all at the end to be safe
        self.current_fg = None
        self.current_bg = None
        
        return "".join(output).encode('utf-8')

    def render_full(self, canvas: Canvas) -> bytes:
        changes = []
        for y in range(canvas.height):
            for x in range(canvas.width):
                cell = canvas.get_cell(x, y)
                if cell:
                    changes.append((x, y, cell))
        return self.render_diff(changes)
