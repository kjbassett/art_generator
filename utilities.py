import random

def choose_points_on_sides(x, y, canvas_width, canvas_height):
    endpoints = []
    for direction in random.sample([0, 1, 2, 3], 2):
        # 0 = top, 1 = right, 2 = bottom, 3 = left
        if direction == 0:
            endpoints.extend([x, 0])
        elif direction == 1:
            endpoints.extend([canvas_width - 1, y])
        elif direction == 2:
            endpoints.extend([x, canvas_height - 1])
        else:
            endpoints.extend([0, y])
    x0, y0, x1, y1 = endpoints
    return x0, y0, x1, y1

def round_and_draw(canvas, x, y, color):
    x = round(x)
    y = round(y)
    if (0 <= y < canvas.shape[0]) and (0 <= x < canvas.shape[1]):
        canvas[y, x] = color
        return True
    else:
        return False