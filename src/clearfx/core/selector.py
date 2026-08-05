import random
import json
from pathlib import Path
from typing import Any, List, Optional
from clearfx.core.config import ClearFXConfig, get_data_dir
from clearfx.core.registry import AnimationRegistry

class AnimationSelector:
    def __init__(self, config: ClearFXConfig, registry: AnimationRegistry):
        self.config = config
        self.registry = registry
        self.history_file = get_data_dir() / "history.json"
        
    def _load_history(self) -> List[str]:
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    data = json.load(f)
                    return data.get("history", [])
            except Exception:
                pass
        return []

    def _save_history(self, history: List[str]) -> None:
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.history_file, "w") as f:
                json.dump({"history": history}, f)
        except Exception:
            pass

    def select(self, seed: Optional[int] = None) -> Optional[Any]:
        if seed is not None:
            random.seed(seed)
            
        animations = self.registry.list_animations(source=self.config.source)
        if not animations:
            return None
            
        history = self._load_history()
        
        # Filter based on config (blocked, filters)
        candidates = []
        for anim in animations:
            if anim.slug in self.config.blocked:
                continue
            if self.config.tag_filters and not any(tag in self.config.tag_filters for tag in anim.tags):
                continue
            if self.config.creator_filters and anim.author not in self.config.creator_filters:
                continue
            if anim.slug in history:
                continue
            candidates.append(anim)
            
        if not candidates:
            candidates = animations
            
        # Weights
        weights = []
        for anim in candidates:
            w = 1.0
            if anim.slug in self.config.favorites:
                w *= self.config.weights.favorites
            if anim.source == "builtin":
                w *= self.config.weights.builtins
            elif anim.source == "community":
                w *= self.config.weights.community
            weights.append(w)
            
        if not candidates:
            return None
            
        selected = random.choices(candidates, weights=weights, k=1)[0]
        
        # Update history
        history.append(selected.slug)
        if len(history) > self.config.history_size:
            history = history[-self.config.history_size:]
        self._save_history(history)
        
        return self.registry.get_animation(selected.slug)
