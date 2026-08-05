from typing import Any, Tuple

class AttributionOverlay:
    """
    Renders subtle attribution text on canvas for an animation design.
    """

    def render(self, canvas: Any, meta: Any, position: str, progress: float) -> None:
        """
        Renders the attribution text onto the canvas based on the progress.
        It appears for the final 35% of the animation.
        """
        if progress < 0.65:
            return

        opacity = (progress - 0.65) / 0.35
        # Assuming meta is an object or dict with 'name' and 'author'/'handle'
        name = getattr(meta, 'name', '') or (meta.get('name', 'Unknown') if isinstance(meta, dict) else 'Unknown')
        handle = getattr(meta, 'author', '') or (meta.get('author', 'Unknown') if isinstance(meta, dict) else 'Unknown')
        
        text = f"◇ {name} · {handle}"
        
        # Position logic
        pos_y, pos_x = self._calculate_position(canvas, position, text)
        
        # Dim styling applied depending on canvas implementation
        if hasattr(canvas, "put_text"):
            canvas.put_text(pos_x, pos_y, text, style=f"dim;opacity={opacity:.2f}")

    def _calculate_position(self, canvas: Any, position: str, text: str) -> Tuple[int, int]:
        height = getattr(canvas, 'height', 24)
        width = getattr(canvas, 'width', 80)
        
        text_len = len(text)
        
        if position == "auto":
            position = "bottom-right"
            
        if position == "bottom-right":
            return height - 1, max(0, width - text_len - 1)
        elif position == "bottom-left":
            return height - 1, 1
        elif position == "top-right":
            return 0, max(0, width - text_len - 1)
        elif position == "top-left":
            return 0, 1
        return height - 1, max(0, width - text_len - 1)
