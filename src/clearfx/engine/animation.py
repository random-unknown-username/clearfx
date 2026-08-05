from dataclasses import dataclass, field
from typing import List, Optional, Any
from abc import ABC, abstractmethod
from .terminal import TerminalCapabilities
from .canvas import Canvas

@dataclass
class AnimationMeta:
    id: str
    slug: str
    name: str
    author_name: str
    author_handle: str
    description: str
    tags: List[str] = field(default_factory=list)
    min_width: int = 40
    min_height: int = 20
    recommended_duration_ms: int = 5000
    supports_ascii: bool = True
    supports_monochrome: bool = True
    version: str = "1.0.0"

@dataclass
class AnimationContext:
    width: int
    height: int
    capabilities: TerminalCapabilities
    duration_ms: int
    fps: int
    seed: int
    reduced_motion: bool
    ascii_only: bool
    monochrome: bool
    progress: float
    elapsed_ms: float
    dt: float
    frame_number: int

class Animation(ABC):
    meta: AnimationMeta

    @abstractmethod
    def setup(self, ctx: AnimationContext):
        pass

    @abstractmethod
    def update(self, ctx: AnimationContext):
        pass

    @abstractmethod
    def render(self, ctx: AnimationContext, canvas: Canvas):
        pass

    def cleanup(self):
        pass

    def get_reduced_motion_fallback(self) -> Optional['Animation']:
        return None
