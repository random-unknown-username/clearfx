from typing import Union, Tuple, Optional

ColorType = Union[None, int, Tuple[int, int, int]]

class Cell:
    __slots__ = ('char', 'fg_color', 'bg_color', 'bold', 'dim', 'italic', 'underline', 'blink', 'reverse', 'strikethrough')

    def __init__(self,
                 char: str = ' ',
                 fg_color: ColorType = None,
                 bg_color: ColorType = None,
                 bold: bool = False,
                 dim: bool = False,
                 italic: bool = False,
                 underline: bool = False,
                 blink: bool = False,
                 reverse: bool = False,
                 strikethrough: bool = False):
        self.char = char
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.bold = bold
        self.dim = dim
        self.italic = italic
        self.underline = underline
        self.blink = blink
        self.reverse = reverse
        self.strikethrough = strikethrough

    def __eq__(self, other):
        if not isinstance(other, Cell):
            return False
        return (self.char == other.char and
                self.fg_color == other.fg_color and
                self.bg_color == other.bg_color and
                self.bold == other.bold and
                self.dim == other.dim and
                self.italic == other.italic and
                self.underline == other.underline and
                self.blink == other.blink and
                self.reverse == other.reverse and
                self.strikethrough == other.strikethrough)

    def __hash__(self):
        return hash((self.char, self.fg_color, self.bg_color, self.bold, self.dim, self.italic,
                     self.underline, self.blink, self.reverse, self.strikethrough))

    def copy(self):
        return Cell(
            char=self.char,
            fg_color=self.fg_color,
            bg_color=self.bg_color,
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            underline=self.underline,
            blink=self.blink,
            reverse=self.reverse,
            strikethrough=self.strikethrough
        )

EMPTY_CELL = Cell()
