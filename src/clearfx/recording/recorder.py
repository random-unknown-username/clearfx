from pathlib import Path
from ..engine.animation import Animation

class AnimationRecorder:
    def record_cast(self, animation: Animation, output_path: str | Path):
        pass
        
    def record_frames(self, animation: Animation, output_dir: str | Path):
        pass
        
    def record_svg(self, animation: Animation, output_path: str | Path):
        pass
        
    def record_gif(self, animation: Animation, output_path: str | Path):
        pass
