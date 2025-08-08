import numpy as np
import cv2
import random
from drawing import drawing_choices


class ArtGenerator:

    def __init__(
            self, 
            drawing_choices, 
            width, 
            height, 
            new_drawing_chance=0.05, max_drawings=0, background_color=(0, 0, 0)
            ):
        self.drawing_choices = drawing_choices
        self.background_color = np.array(background_color)  #BGR 0-1
        self.width = width
        self.height = height
        self.canvas = np.ones((height, width, 3)) * self.background_color
        self.new_drawing_chance = new_drawing_chance
        self.max_drawings = max_drawings
        self.drawings = []

    def run(self):
        cv2.namedWindow('Art Generator', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Art Generator', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        while not (cv2.waitKey(1) & 0xFF == ord('q')):
            self.fade_to_background()
            self.remove_old_drawings()
            self.generate_new_drawings()
            self.draw()
            cv2.imshow("Art Generator", self.canvas)
    
    def fade_to_background(self):
        self.canvas = self.canvas * 0.95 + self.background_color * 0.05


    def remove_old_drawings(self):
        self.drawings = [d for d in self.drawings if not d.complete]


    def generate_new_drawings(self):
        if len(self.drawings) >= self.max_drawings and self.max_drawings > 0:
            return
        if random.random() > self.new_drawing_chance:
            return
        drawing_class = random.choice(self.drawing_choices)
        new_drawing = drawing_class(self.width, self.height)
        self.drawings.append(new_drawing)
    
    def draw(self):
        for d in self.drawings:
            d.draw(self.canvas)

            
if __name__ == "__main__":
    art_gen = ArtGenerator(drawing_choices, 160, 90, new_drawing_chance=0.05)
    art_gen.run()
