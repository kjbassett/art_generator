from abc import ABC, abstractmethod
import random

class Drawing(ABC):
    def __init__(self, canvas_width, canvas_height):
        self.x = random.randint(0, canvas_width - 1)
        self.y = random.randint(0, canvas_height - 1)
        self.color = (
            random.random(),
            random.random(),
            random.random()
        )
        self.complete = False
    
    @abstractmethod
    def draw(self, canvas):
        pass


class dot(Drawing):
    def draw(self, canvas):
        canvas[self.y, self.x] = self.color
        self.complete = True

class invert(Drawing):
    def draw(self, canvas):
        canvas[:] = 1 - canvas[:]

drawing_choices = [dot]