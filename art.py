import numpy as np
import cv2
import random
from drawing import drawing_choices
from ui import UIOverlay


class ArtGenerator:

    def __init__(self, width, height, new_drawing_chance=0.05, max_drawings=0, background_color=(0, 0, 0)):
        self.background_color = np.array(background_color)
        self.width   = width
        self.height  = height
        self.canvas  = np.ones((height, width, 3)) * self.background_color
        self.drawings = []
        self.paused   = False
        self.ui = UIOverlay(
            width, height, drawing_choices,
            new_drawing_chance=new_drawing_chance,
            max_drawings=max_drawings,
        )

    def run(self):
        cv2.namedWindow('Art Generator', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Art Generator', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback('Art Generator', self.ui.handle_mouse)

        while True:
            key = cv2.waitKey(1) & 0xFF

            consumed = self.ui.handle_key(key)
            if not consumed:
                if key == ord('q'):
                    break
                elif key == ord('h'):
                    self.ui.visible = not self.ui.visible
                elif key == ord('c'):
                    self.canvas[:] = self.background_color
                    self.drawings.clear()
                elif key == 32:   # spacebar
                    self.paused = not self.paused

            if self.paused:
                self.ui.draw(self.canvas)
                cv2.imshow('Art Generator', self.canvas)
                continue

            self.fade_to_background()
            self.remove_old_drawings()
            self.generate_new_drawings()
            self.draw()
            self.ui.draw(self.canvas)
            cv2.imshow('Art Generator', self.canvas)

    def fade_to_background(self):
        r = self.ui.fade_rate
        self.canvas = self.canvas * r + self.background_color * (1.0 - r)

    def remove_old_drawings(self):
        self.drawings = [d for d in self.drawings if not d.complete]

    def generate_new_drawings(self):
        if self.ui.max_drawings > 0 and len(self.drawings) >= self.ui.max_drawings:
            return
        if random.random() > self.ui.new_drawing_chance:
            return
        weights = self.ui.get_weights()
        active  = [(cls, w) for cls, w in zip(drawing_choices, weights) if w > 0]
        if not active:
            return
        classes, ws = zip(*active)
        cls = random.choices(classes, weights=ws, k=1)[0]
        self.drawings.append(cls(self.width, self.height))

    def draw(self):
        for d in self.drawings:
            d.draw(self.canvas)


if __name__ == "__main__":
    art_gen = ArtGenerator(800, 450, new_drawing_chance=0.1)
    art_gen.run()
