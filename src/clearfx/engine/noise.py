class Noise1D:
    def __init__(self, seed: int = 0):
        self.seed = seed

    def _hash(self, x: int) -> float:
        # Simple integer hash
        x = ((x >> 16) ^ x) * 0x45d9f3b
        x = ((x >> 16) ^ x) * 0x45d9f3b
        x = (x >> 16) ^ x
        return (x & 0xfffffff) / 0xfffffff

    def get(self, x: float) -> float:
        i = int(x)
        f = x - i
        # smoothstep
        u = f * f * (3.0 - 2.0 * f)
        
        a = self._hash(i + self.seed)
        b = self._hash(i + 1 + self.seed)
        
        return a + u * (b - a)

class Noise2D:
    def __init__(self, seed: int = 0):
        self.seed = seed

    def _hash(self, x: int, y: int) -> float:
        h = self.seed + x * 374761393 + y * 668265263
        h = (h ^ (h >> 13)) * 1274126177
        return (h & 0xfffffff) / 0xfffffff

    def get(self, x: float, y: float) -> float:
        ix = int(x)
        iy = int(y)
        fx = x - ix
        fy = y - iy

        ux = fx * fx * (3.0 - 2.0 * fx)
        uy = fy * fy * (3.0 - 2.0 * fy)

        v00 = self._hash(ix, iy)
        v10 = self._hash(ix + 1, iy)
        v01 = self._hash(ix, iy + 1)
        v11 = self._hash(ix + 1, iy + 1)

        v0 = v00 + ux * (v10 - v00)
        v1 = v01 + ux * (v11 - v01)

        return v0 + uy * (v1 - v0)


# Module-level convenience caches for common seed values
_noise1d_cache: dict[int, Noise1D] = {}
_noise2d_cache: dict[int, Noise2D] = {}


def noise1d(x: float, seed: int = 0) -> float:
    """Convenience function for 1D value noise.

    Caches Noise1D instances by seed for reuse.
    """
    if seed not in _noise1d_cache:
        _noise1d_cache[seed] = Noise1D(seed)
    return _noise1d_cache[seed].get(x)


def noise2d(x: float, y: float, seed: int = 0) -> float:
    """Convenience function for 2D value noise.

    Caches Noise2D instances by seed for reuse.
    """
    if seed not in _noise2d_cache:
        _noise2d_cache[seed] = Noise2D(seed)
    return _noise2d_cache[seed].get(x, y)
