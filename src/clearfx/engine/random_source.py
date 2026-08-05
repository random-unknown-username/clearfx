import random
from typing import Sequence, Any, Optional

class RandomSource:
    def __init__(self, seed: Optional[int] = None):
        self._rnd = random.Random(seed)

    def random(self) -> float:
        return self._rnd.random()

    def randint(self, a: int, b: int) -> int:
        return self._rnd.randint(a, b)

    def choice(self, seq: Sequence[Any]) -> Any:
        return self._rnd.choice(seq)

    def uniform(self, a: float, b: float) -> float:
        return self._rnd.uniform(a, b)

    def gauss(self, mu: float, sigma: float) -> float:
        return self._rnd.gauss(mu, sigma)

    def shuffle(self, x: list) -> None:
        self._rnd.shuffle(x)
