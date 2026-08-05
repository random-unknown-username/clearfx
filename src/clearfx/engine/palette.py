from typing import Tuple, List, Dict
import math

class Color:
    @staticmethod
    def rgb(r: int, g: int, b: int) -> Tuple[int, int, int]:
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

def lerp_color(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    if s == 0.0:
        return (int(v * 255), int(v * 255), int(v * 255))
    
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
        
    return (int(r * 255), int(g * 255), int(b * 255))

def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
    r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
    cmax = max(r_norm, g_norm, b_norm)
    cmin = min(r_norm, g_norm, b_norm)
    diff = cmax - cmin
    
    if cmax == cmin:
        h = 0.0
    elif cmax == r_norm:
        h = (60.0 * ((g_norm - b_norm) / diff) + 360.0) % 360.0
    elif cmax == g_norm:
        h = (60.0 * ((b_norm - r_norm) / diff) + 120.0) % 360.0
    else:
        h = (60.0 * ((r_norm - g_norm) / diff) + 240.0) % 360.0
        
    s = 0.0 if cmax == 0 else (diff / cmax)
    v = cmax
    
    return (h / 360.0, s, v)

def color_to_256(r: int, g: int, b: int) -> int:
    if r == g == b:
        if r < 8: return 16
        if r > 248: return 231
        return round(((r - 8) / 247) * 24) + 232
    return 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)

def color_to_16(r: int, g: int, b: int) -> int:
    # Very basic 16 color approximation
    r_bit = 1 if r > 127 else 0
    g_bit = 1 if g > 127 else 0
    b_bit = 1 if b > 127 else 0
    bright = 8 if (r > 192 or g > 192 or b > 192) else 0
    
    return bright + (r_bit) + (g_bit << 1) + (b_bit << 2)

class Palette:
    def __init__(self, colors: List[Tuple[int, int, int]]):
        self.colors = colors
        
    def get(self, index: int) -> Tuple[int, int, int]:
        return self.colors[index % len(self.colors)]
        
    def get_interpolated(self, t: float) -> Tuple[int, int, int]:
        if not self.colors:
            return (0, 0, 0)
        t = max(0.0, min(1.0, t))
        idx = t * (len(self.colors) - 1)
        i = int(idx)
        f = idx - i
        if i >= len(self.colors) - 1:
            return self.colors[-1]
        return lerp_color(self.colors[i], self.colors[i+1], f)

PALETTES = {
    'ocean': Palette([(0, 119, 190), (0, 168, 204), (20, 186, 201), (60, 219, 211)]),
    'sunset': Palette([(255, 94, 77), (255, 140, 66), (255, 204, 92), (242, 235, 217)]),
    'forest': Palette([(46, 125, 50), (104, 159, 56), (156, 204, 101), (210, 235, 171)]),
    'neon': Palette([(255, 0, 255), (0, 255, 255), (0, 255, 0), (255, 255, 0)]),
    'monochrome': Palette([(30, 30, 30), (100, 100, 100), (180, 180, 180), (240, 240, 240)]),
    'pastel': Palette([(255, 179, 186), (255, 223, 186), (255, 255, 186), (186, 255, 201), (186, 225, 255)]),
    'fire': Palette([(255, 0, 0), (255, 90, 0), (255, 154, 0), (255, 206, 0), (255, 232, 8)]),
    'ice': Palette([(196, 235, 255), (145, 215, 255), (94, 194, 255), (43, 174, 255)]),
    'cyber': Palette([(11, 232, 129), (52, 231, 228), (255, 63, 52), (255, 221, 89)])
}
