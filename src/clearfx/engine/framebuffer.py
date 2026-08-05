from typing import List, Tuple
from .canvas import Canvas
from .cell import Cell

class FrameBuffer:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.front = Canvas(width, height)
        self.back = Canvas(width, height)
        # Initialize front with empty cells to ensure first diff is full
        self.front.fill(' ')

    def swap(self):
        self.front, self.back = self.back, self.front

    def diff(self) -> List[Tuple[int, int, Cell]]:
        changes = []
        width = self.width
        
        front_cells = self.front.cells
        back_cells = self.back.cells
        
        for i in range(len(back_cells)):
            fc = front_cells[i]
            bc = back_cells[i]
            
            # If the back cell is empty/None, treat as a default empty cell for rendering
            if bc is None:
                continue  # Or replace with EMPTY_CELL if we want to clear it explicitly
            
            # If front cell matches back cell, no change needed
            if fc != bc:
                y = i // width
                x = i % width
                changes.append((x, y, bc))
                
        return changes
