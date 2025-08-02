import numpy as np
import cv2

class ArtGenerator:

    def __init__(self, width, height, max_drawings=0, background_color=(0, 0, 0)):
        self.background_color = background_color  #BGR 0-1
        self.canvas = np.zeros((height, width, 3))
        self.canvas[:,:] = self.background_color
        self.max_drawings = max_drawings

    def run(self):
        while not (cv2.waitKey(1) & 0xFF == ord('q')):
            cv2.imshow("RGB Array", self.canvas)

            
if __name__ == "__main__":
    art_gen = ArtGenerator(800, 450, background_color=(0, 0, 0))
    art_gen.run()
