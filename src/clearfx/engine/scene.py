from typing import List
from .canvas import Canvas

class Layer:
    def __init__(self, width: int, height: int, z_order: int = 0):
        self.canvas = Canvas(width, height)
        self.z_order = z_order
        self.visible = True
        self.opacity = 1.0 # Logical opacity

    def clear(self):
        self.canvas.clear()

class Scene:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.layers: List[Layer] = []

    def add_layer(self, z_order: int = 0) -> Layer:
        layer = Layer(self.width, self.height, z_order)
        self.layers.append(layer)
        self.layers.sort(key=lambda l: l.z_order)
        return layer

    def compose(self, final_canvas: Canvas):
        final_canvas.clear()
        
        for layer in self.layers:
            if not layer.visible:
                continue
                
            layer_cells = layer.canvas.cells
            final_cells = final_canvas.cells
            
            for i, cell in enumerate(layer_cells):
                if cell is not None and cell.char != '':
                    # Simple alpha compositing: if cell is not empty, it overwrites
                    # (In a more complex engine, we might blend colors here)
                    if final_cells[i] is None:
                        final_cells[i] = cell.copy()
                    else:
                        final_cells[i] = cell.copy()
