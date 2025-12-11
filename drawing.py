from abc import ABC, abstractmethod
import math
import random
from utilities import round_and_draw

class Drawing(ABC):
    def __init__(self, canvas_width, canvas_height):
        self.i = 0  # Current iteration AKA frame counter
        self.x = random.randint(0, canvas_width - 1)
        self.y = random.randint(0, canvas_height - 1)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.color = (
            random.random(),
            random.random(),
            random.random()
        )
        self.complete = False  # Flag for ArtGenerator to keep or remove drawing
        self.child_drawings = []
    

    def draw(self, canvas):
        self._draw(canvas)
        self.draw_children(canvas)
        self.remove_finished_children()
        self.i += 1
    
    def draw_children(self, canvas):
        for cd in self.child_drawings:
            cd.draw(canvas)

    def remove_finished_children(self):
        self.child_drawings = [cd for cd in self.child_drawings if not cd.complete]
    
    @abstractmethod
    def _draw(self, canvas):
        pass


class dot(Drawing):
    def _draw(self, canvas):
        canvas[self.y, self.x] = self.color
        self.complete = True


class line(Drawing):
    def __init__(self, canvas_width, canvas_height, x0: int=None, y0: int=None, x1: int=None, y1: int=None, duration: int=None):
        super().__init__(canvas_width, canvas_height)
        self.x0 = self.x if x0 is None else x0
        self.y0 = self.y if y0 is None else y0
        self.x1 = random.randint(0, canvas_width - 1) if x1 is None else x1
        self.y1 = random.randint(0, canvas_height - 1) if y1 is None else y1
        self.x = self.x0
        self.y = self.y0
        self.duration = random.randint(1, 20) if duration is None else duration
        self.step_x = (self.x1 - self.x0) / self.duration
        self.step_y = (self.y1 - self.y0) / self.duration

    def _draw(self, canvas):
        self.x += self.step_x
        self.y += self.step_y
        x = round(self.x)
        y = round(self.y)
        if x >= canvas.shape[1] or x < 0 or y >= canvas.shape[0] or y < 0:
            self.complete = True
            return
        canvas[y, x] = self.color
        if self.i > self.duration:
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


class firework(Drawing):
    def __init__(self, canvas_width, canvas_height):
        super().__init__(canvas_width, canvas_height)
        self.phase = 0  # 0 = fly up, 1 = explosion
        self.n_children = random.randint(100, 400)
        self.max_radius = random.randint(int(self.canvas_width * 0.05), int(self.canvas_width * 0.4))
        self.explosion_duration = random.randint(15, 100)

    def _draw(self, canvas):
        if self.phase == 0:
            y = canvas.shape[0] - 1 - self.i
            if y >= self.y:
                canvas[y, self.x] = [1, 1, 1]
            else:
                for n in range(self.n_children):
                    radius = random.random() * self.max_radius
                    angle = random.random() * 2 * math.pi
                    end_x = self.x + round(math.cos(angle) * radius)
                    end_y = self.y + round(math.sin(angle) * radius)
                    self.child_drawings.append(line(self.canvas_width, self.canvas_height, self.x, self.y, end_x, end_y, self.explosion_duration))
                self.phase = 1
        if self.phase == 1:
            if not self.child_drawings:
                self.complete = True


class vine(Drawing):
    def __init__(self, canvas_width, canvas_height):
        super().__init__(canvas_width, canvas_height)
        self.direction = random.choice([0, 0.5, 1, 1.5])  # right, up, left, down
        print(self.direction)
        if self.direction == 0:
            self.x = 0
        elif self.direction == 0.5:
            self.y = canvas_height-1
        elif self.direction == 1:
            self.x = canvas_width - 1
        else:
            self.y = 0
        self.direction *= math.pi
        self.color = (0, self.color[1], 0) # green

    def _draw(self, canvas):
        if not round_and_draw(canvas, self.x, self.y, self.color):
            self.complete = True
            return
        self.x += math.cos(self.direction)
        self.y -= math.sin(self.direction)
        self.direction += random.gauss() * 0.314 # 0.314 is 5% of of a full circle in radians
        
                 

# put your drawing class in this list if you want it to appear
drawing_choices = [spiral, dot, line, firework, vine]