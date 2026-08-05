import time

class FrameClock:
    def __init__(self, target_fps: int):
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps
        self.last_time = time.monotonic()
        self.dt = 0.0

    def tick(self) -> float:
        current_time = time.monotonic()
        self.dt = current_time - self.last_time
        
        # Sleep to hit target FPS if needed
        sleep_time = self.target_frame_time - self.dt
        if sleep_time > 0:
            time.sleep(sleep_time)
            current_time = time.monotonic()
            self.dt = current_time - self.last_time
            
        self.last_time = current_time
        return self.dt

class Timeline:
    def __init__(self, duration_ms: float):
        self.duration_ms = duration_ms
        self.elapsed_ms = 0.0
        self.progress = 0.0

    def tick(self, dt: float):
        self.elapsed_ms += dt * 1000.0
        if self.duration_ms > 0:
            self.progress = min(1.0, self.elapsed_ms / self.duration_ms)
        else:
            self.progress = 0.0

    @property
    def is_complete(self) -> bool:
        return self.duration_ms > 0 and self.elapsed_ms >= self.duration_ms
