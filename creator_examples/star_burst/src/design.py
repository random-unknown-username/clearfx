from clearfx.compiler.creator_sdk import CreatorAnimation

class StarBurst(CreatorAnimation):
    def __init__(self):
        super().__init__()
        self.add_circle(40, 12, 10)
