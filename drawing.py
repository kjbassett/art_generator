from abc import ABC, abstractmethod
import math
import random
from utilities import round_and_draw
import numpy as np
import cv2

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
        success1 = round_and_draw(canvas, x1, y1, self.color)
        success2 = round_and_draw(canvas, x2, y2, self.color)
        if not success1 and not success2:
            self.complete = True
            return


class spiral(Drawing):
    def __init__(self, canvas_width, canvas_height):
        super().__init__(canvas_width, canvas_height)
        self.delta_radius = random.random() * 2
        self.delta_angle = random.random() * math.pi # 0-180 degrees
        self.max_iterations = random.random() * max(canvas_height, canvas_width) / self.delta_radius

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
        if self.direction == 0:
            self.x = 0
        elif self.direction == 0.5:
            self.y = canvas_height-1
        elif self.direction == 1:
            self.x = canvas_width - 1
        else:
            self.y = 0
        self.direction *= math.pi
        self.direction_change = 0
        self.previous_direction_change = 0
        self.color = (0, self.color[1], 0) # green
        self.canvas_width = self.canvas_width
        self.canvas_height = self.canvas_height

    def _draw(self, canvas):
        if not round_and_draw(canvas, self.x, self.y, self.color):
            self.complete = True
            return
        self.x += math.cos(self.direction)
        self.y -= math.sin(self.direction)
        # smooth direction changes out with weighted average of previous change and new change (90% old, 10% new)
        self.direction_change = self.previous_direction_change * 0.9 + random.gauss() * 0.314 * 0.1 # 0.314 is 5% of of a full circle in radians
        self.previous_direction_change = self.direction_change
        self.direction += self.direction_change

        # spawn new branch occasionally
        if random.random() <= 0.005 and len(self.child_drawings) <= 3:
            branch = vine(self.canvas_width, self.canvas_height)
            branch.x = self.x
            branch.y = self.y
            branch.direction = self.direction
            self.child_drawings.append(branch)
        
                 

class lissajous(Drawing):
    # Ken promised Pixel that he wouldn't touch it without Pixel's permission
    # Two signals at different frequencies, tracing the shape of their meeting.
    # The ratio decides everything; the canvas shows what the math feels like.
    _PAIRS = [(1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5), (2, 5)]

    def __init__(self, canvas_width, canvas_height):
        super().__init__(canvas_width, canvas_height)
        self.x  = random.randint(canvas_width  // 3, 2 * canvas_width  // 3)
        self.y  = random.randint(canvas_height // 3, 2 * canvas_height // 3)
        self.rx = random.randint(canvas_width  // 6, canvas_width  // 3)
        self.ry = random.randint(canvas_height // 6, canvas_height // 3)
        self.fx, self.fy = random.choice(self._PAIRS)
        self.phase    = random.uniform(0, math.pi / 2)
        self.speed    = random.uniform(0.015, 0.04)
        self.duration = int(2 * math.pi / self.speed * 2)   # two full cycles

    def _draw(self, canvas):
        t = self.i * self.speed
        x = round(self.x + self.rx * math.sin(self.fx * t + self.phase))
        y = round(self.y + self.ry * math.sin(self.fy * t))
        if 0 <= x < canvas.shape[1] and 0 <= y < canvas.shape[0]:
            canvas[y, x] = self.color
        if self.i >= self.duration:
            self.complete = True
    

class circle_pattern_wave(Drawing):
    def __init__(self, canvas_width, canvas_height):
        super().__init__(canvas_width, canvas_height)
        self.radius_delta = random.random() * 2
        self.max_i = max(
            [
                self.x**2 + self.y**2,
                self.x**2 + (canvas_height - self.y)**2,
                (canvas_width - self.x)**2 + self.y**2,
                (canvas_width - self.x)**2 + (canvas_height - self.y)**2
            ]
        ) ** 0.5
        self.max_i /= self.radius_delta
        self.ogrid = np.ogrid[:canvas_height, :canvas_width]
    
    def _draw(self, canvas):
        radius = self.i * self.radius_delta
        y, x = self.ogrid
        mask = np.round((x - self.x)**2 + (y - self.y)**2) == round(radius**2)
        canvas[mask] = self.color
        if self.i >= self.max_i:
            self.complete = True


class battery(Drawing):
    # A small lithium coin cell, like the ones that power watches and key fobs.
    BODY_COLOR = (0.72, 0.72, 0.76)   # brushed nickel/silver
    RIM_COLOR  = (0.40, 0.40, 0.44)
    TEXT_COLOR = (0.05, 0.05, 0.05)
    PLUS_COLOR = (0.20, 0.45, 0.72)   # copper-ish (BGR), for the positive terminal mark

    def __init__(self, canvas_width, canvas_height):
        super().__init__(canvas_width, canvas_height)
        self.radius = random.randint(35, 55)
        self.x = random.randint(self.radius + 5, max(self.radius + 6, canvas_width - self.radius - 5))
        self.y = random.randint(self.radius + 5, max(self.radius + 6, canvas_height - self.radius - 5))
        self.color = self.BODY_COLOR
        self.grow_duration = self.radius
        self.hold_duration = 90

        font = cv2.FONT_HERSHEY_SIMPLEX
        (base_w, _), _ = cv2.getTextSize("Duracell", font, 1.0, 1)
        self.text_scale = (self.radius * 1.5) / base_w
        (self.text_w, self.text_h), _ = cv2.getTextSize("Duracell", font, self.text_scale, 1)

    def _draw_body(self, canvas, radius):
        cv2.circle(canvas, (self.x, self.y), radius, self.BODY_COLOR, -1, cv2.LINE_AA)
        cv2.circle(canvas, (self.x, self.y), radius, self.RIM_COLOR, 2, cv2.LINE_AA)

    def _draw(self, canvas):
        if self.i <= self.grow_duration:
            radius = max(1, round(self.radius * self.i / self.grow_duration))
            self._draw_body(canvas, radius)
        elif self.i == self.grow_duration + 1:
            self._draw_body(canvas, self.radius)
            cv2.circle(canvas, (self.x, self.y), round(self.radius * 0.75), self.RIM_COLOR, 1, cv2.LINE_AA)

            font = cv2.FONT_HERSHEY_SIMPLEX
            tx = round(self.x - self.text_w / 2)
            ty = round(self.y + self.text_h / 2)
            cv2.putText(canvas, "Duracell", (tx, ty), font, self.text_scale, self.TEXT_COLOR, 1, cv2.LINE_AA)

            plus_y = round(self.y - self.radius * 0.55)
            plus_len = max(2, round(self.radius * 0.12))
            cv2.line(canvas, (self.x - plus_len, plus_y), (self.x + plus_len, plus_y), self.PLUS_COLOR, 1, cv2.LINE_AA)
            cv2.line(canvas, (self.x, plus_y - plus_len), (self.x, plus_y + plus_len), self.PLUS_COLOR, 1, cv2.LINE_AA)

        if self.i >= self.grow_duration + self.hold_duration:
            self.complete = True


drawing_choices = [cls for cls in Drawing.__subclasses__() if not getattr(cls, '__abstractmethods__', None)]