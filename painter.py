from game_board import Bound, GameBoard, BOARD_SIDE_LEN
from cv2 import arrowedLine, imwrite, addWeighted

OUTPUT_PATH = 'solution.png'
TRANSPERENCY = 0.8
EVEN_LINE_COLOUR = (0, 200, 0)
ODD_LINE_COLOUR = (0, 0, 200)

def draw_solution(board: GameBoard, path: list):
    points = get_line_points(board.tile_bounds, path)
    img = draw_lines_on_image(board.image, points)
    imwrite(OUTPUT_PATH, img)
    print(f"Saved output image to '{OUTPUT_PATH}'")

def get_line_points(tile_bounds: list, path: list):
    points = []
    for letter in path:
        col, row = letter.position
        tile_number = row * BOARD_SIDE_LEN + col
        bound = tile_bounds[tile_number]
        points.append(calculate_center(bound))
    return points

def calculate_center(bound: Bound):
    return ((bound.lo_x + bound.hi_x) // 2, (bound.lo_y + bound.hi_y) // 2)

def draw_lines_on_image(image, points: list):
    overlay = image.copy()
    for i in range(len(points) - 1):
        arrowedLine(overlay, points[i], points[i+1], EVEN_LINE_COLOUR if i % 2 == 0 else ODD_LINE_COLOUR, 4)
    return addWeighted(overlay, TRANSPERENCY, image, 1 - TRANSPERENCY, 0)
