from abc import ABC, abstractmethod
import math
import random

class Drawing(ABC):
    def __init__(self, canvas_width, canvas_height):
        self.i = 0  # Current iteration AKA frame counter
        self.x = random.randint(0, canvas_width - 1)
        self.y = random.randint(0, canvas_height - 1)
        self.color = (
            random.random(),
            random.random(),
            random.random()
        )
        self.complete = False  # Flag for ArtGenerator to keep or remove drawing
    

    def draw(self, canvas):
        self._draw(canvas)
        self.i += 1
    
    @abstractmethod
    def _draw(self, canvas):
        pass


class dot(Drawing):
    def _draw(self, canvas):
        canvas[self.y, self.x] = self.color
        self.complete = True


class invert(Drawing):
    def _draw(self, canvas):
        canvas[:] = 1 - canvas[:]
        self.complete = True


class parabola(Drawing):
    def __init__(self, canvas_width, canvas_height):
        super().__init__(canvas_width, canvas_height)
        self.direction = random.choice(['vertical', 'horizontal'])
        self.coeff = random.random() * 0.1 - 0.05  # random number between -1 and 1
    
    def _draw(self, canvas):
        # start from the middle and draw outwards in both directions at the same time
        # in this case, both x and y are functions of i
        # determine next x positions
        x1 = self.x + self.i
        x2 = self.x - self.i
        # determine next y positions
        y1 = self.coeff * self.i ** 2 + self.y
        y1 = round(y1)  # can't use floats to index canvas
        y2 = y1

        # switch x and y if horizontal
        if self.direction == 'horizontal':
            x1, x2, y1, y2 = y1, y2, x1, x2

        
        # if points are off the window, end the drawing
        if x1 >= canvas.shape[1] or x1 < 0:
            self.complete = True
            return
        if x2 >= canvas.shape[1] or x2 < 0:
            self.complete = True
            return
        if y1 >= canvas.shape[0] or y1 < 0:
            self.complete = True
            return
        if y2 >= canvas.shape[0] or y2 < 0:
            self.complete = True
            return

        canvas[y1, x1] = self.color
        canvas[y2, x2] = self.color


class spiral(Drawing):
    def __init__(self, canvas_width, canvas_height):
        super().__init__(canvas_width, canvas_height)
        self.delta_radius = random.random() * 2
        self.delta_angle = random.random() * math.pi # 0-180 degrees
        self.max_iterations = random.random() * max(canvas_height, canvas_width) / self.delta_angle

    def _draw(self, canvas):
        r = self.delta_radius * self.i
        a = self.delta_angle * self.i
        x = round(self.x + r * math.cos(a))
        y = round(self.y + r * math.sin(a))
        if x >= canvas.shape[1] or x < 0:
            self.complete = True
            return
        if y >= canvas.shape[0] or y < 0:
            self.complete = True
            return
        canvas[y, x] = self.color

        if self.i >= self.max_iterations:
            self.complete = True


# put your drawing class in this list if you want it to appear
drawing_choices = [dot, parabola, spiral]