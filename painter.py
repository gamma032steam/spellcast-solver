from game_board import Bound, GameBoard
from cv2 import arrowedLine, imwrite, addWeighted, addText, rectangle, FILLED

OUTPUT_PATH = 'solution.png'
TRANSPERENCY = 0.8
EVEN_LINE_COLOUR = (0, 200, 0)
ODD_LINE_COLOUR = (0, 0, 200)

def draw_solution(board: GameBoard, path: list):
    img = draw_swaps_on_image(board.image, path, board.tile_bounds)
    points = get_line_points(board.tile_bounds, path)
    img = draw_lines_on_image(img, points)
    imwrite(OUTPUT_PATH, img)
    print(f"Saved output image to '{OUTPUT_PATH}'")

def get_line_points(tile_bounds: list, path: list):
    points = []
    for letter in path:
        bound = tile_bounds[letter.tile_number]
        points.append(calculate_center(bound))
    return points

def calculate_center(bound: Bound):
    return ((bound.lo_x + bound.hi_x) // 2, (bound.lo_y + bound.hi_y) // 2)

def draw_lines_on_image(image, points: list):
    overlay = image.copy()
    for i in range(len(points) - 1):
        arrowedLine(overlay, points[i], points[i+1], EVEN_LINE_COLOUR if i % 2 == 0 else ODD_LINE_COLOUR, 4)
    return addWeighted(overlay, TRANSPERENCY, image, 1 - TRANSPERENCY, 0)

def draw_swaps_on_image(image, path: list, tile_bounds: list):
    '''Draw the swapped letters over the image'''
    for letter in path:
        if letter.swapped_letter:
            bound = tile_bounds[letter.tile_number]
            # colours are BGR
            #rectangle(image, (bound.lo_x, bound.lo_y), (bound.hi_x, bound.hi_y), color=(0, 100, 255), thickness=FILLED)
            # TODO: Deal with 
            # cv2.error: OpenCV(4.6.0) /Users/xperience/actions-runner/_work/opencv-python/opencv-python/opencv/modules/highgui/src/window.cpp:1185: error: (-213:The function/feature is not implemented) The library is compiled without QT support in function 'addText'
            #addText(image, letter.char, (bound.lo_x, bound.lo_y), nameFont="times new roman")
    return image
