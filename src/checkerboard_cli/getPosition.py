import cv2
from pupil_apriltags import Detector
from checkerboard_cli.config.ChessMapping import ChessMapping, SymbolMapping
import logging
import numpy as np
import datetime


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Peices:
    def __init__(self, symbol : str, center : tuple):
        self.std_symol = SymbolMapping.get(symbol, symbol)
        
        self.center = center


def getFrame(cap):
    if not cap.isOpened():
        logger.error("Error: Could not open camera.")
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        logger.error("Error: Could not read frame from camera.")
        return None
    return frame


def detectAprilTags(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detector = Detector()
    tags = detector.detect(gray)
    return tags


def getChessboard(frame, boardCorners : dict):
    # use the top left and bottom right corner to get the rotation and draw the chessboard in a top down view
    
    # if the corners are not detected, return None
    if boardCorners["TL"] is None or boardCorners["BR"] is None:
        logger.warning("Cannot get chessboard: Missing corners. TL: {}, BR: {}".format(boardCorners["TL"], boardCorners["BR"]))
        return None
    
    # draw the chessboard in a top down view
    tl = boardCorners["TL"].center
    br = boardCorners["BR"].center
    width = int(br[0] - tl[0])
    height = int(br[1] - tl[1])
    if width <= 0 or height <= 0:
        logger.warning("Invalid chessboard corners: TL: {}, BR: {}".format(tl, br))
        return None
    
    offset = min(np.linalg.norm(boardCorners["TL"].corners[1] - boardCorners["TL"].corners[0]), np.linalg.norm(boardCorners["TL"].corners[2] - boardCorners["TL"].corners[1]), np.linalg.norm(boardCorners["TL"].corners[3] - boardCorners["TL"].corners[2]), np.linalg.norm(boardCorners["TL"].corners[0] - boardCorners["TL"].corners[3]))
    
    offset = offset / 2.0  # reduce the offset to avoid cutting off the corners of the chessboard
    chessboard = frame.copy()
    # chessboard = frame[int(tl[1] + offset):int(br[1] - offset), int(tl[0] + offset):int(br[0] - offset)]
    # chessboard = cv2.resize(chessboard, (400, 400))
    
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
    
    position = {} # the center position of each square, key is the square name, value is the center position in pixel
    # draw the chessboard grid and get the position of each square
    for i in range(8):
        for j in range(8):
            x1 = int(tl[0] + j * width / 8 + offset)
            y1 = int(tl[1] + i * height / 8 + offset)
            x2 = int(tl[0] + (j + 1) * width / 8 - offset)
            y2 = int(tl[1] + (i + 1) * height / 8 - offset)
            
            square_name = files[j] + ranks[7 - i]
            position[square_name] = ((x1 + x2) // 2, (y1 + y2) // 2)
    
    
        
    
    
    return chessboard, position
    
    


def getCapture(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    frame = getFrame(cap)
    if frame is None:
        return None
    tags = detectAprilTags(frame)
    if not tags:
        logger.warning("No AprilTags detected.")
    
    boardCorners = {"TL": None, "BR": None}
    peicesTags : list[Peices] = []

    for tag in tags:
        logger.debug(f"Detected tag ID: {tag.tag_id} at position: {tag.center}")
        # draw the tag on the frame
        corners = tag.corners.astype(int)
        symbol = ChessMapping.get(tag.tag_id, str(tag.tag_id))
        logger.debug(f"Mapping tag ID {tag.tag_id} to symbol: {symbol}")

        # if symbol is Upper case, draw and fill in White, else draw in Black
        fill_color = (255, 255, 255) if symbol.isupper() else (0, 0, 0)
        text_color = (0, 0, 0) if symbol.isupper() else (255, 255, 255)
        
        # if the symbol is a space, draw in red to indicate the corner
        if symbol in ["TL", "BR"]:
            fill_color = (0, 0, 255)
            text_color = (255, 255, 255)
            boardCorners[symbol] = tag
            continue
            
        # find two point distance or corners[1] and corners[0] to get the size of the tag
        shortest_distance = min(np.linalg.norm(corners[1] - corners[0]), np.linalg.norm(corners[2] - corners[1]), np.linalg.norm(corners[3] - corners[2]), np.linalg.norm(corners[0] - corners[3]))
        # fill the tag with the color
        # cv2.fillPoly(frame, [corners], fill_color)
        # draw a circle that cover the polygon
        cv2.circle(frame, (int(tag.center[0]), int(tag.center[1])), int(np.sqrt(2 * (shortest_distance ** 2)) / 1.95), fill_color, -1)  # diameter^2 = a^2 + b^2, a = b = shortest_distance, divide by 1.95 to avoid rounding error that cause the rectangle of the tag to be visible
        
        font_scale = shortest_distance / 50.0
        # draw the tag ID near the center
        cv2.putText(frame, symbol, (int(tag.center[0] - 10 * font_scale), int(tag.center[1] + 10 * font_scale)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, int(shortest_distance // 10))
        
        
        peicesTags.append(Peices(symbol=symbol, center=tag.center))

    frame, position = getChessboard(frame, boardCorners)
    
    # find the peices position on the chessboard
    piece_map = {}
    for peice in peicesTags:
        if peice.center is not None and position is not None:
            # draw a small circle at the center of the peice
            # cv2.circle(frame, (int(peice.center[0]), int(peice.center[1])), 5, (0, 255, 0), -1)
            # find
            closest_square = min(position.keys(), key=lambda square: np.linalg.norm(np.array(position[square]) - np.array(peice.center)))
            peice.position = closest_square
            piece_map[closest_square] = peice.std_symol
            logger.debug(f"Peice {peice.std_symol} at center {peice.center} mapped to square {closest_square}")
    
    if position:
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        datetime_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        std_output = f"""\n## Checkerboard {datetime_str}\n"""
        std_output += "┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐\n"
        # print(f"\n## Checkerboard {datetime_str}\n")
        # print("┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐")
        for i, rank in enumerate(ranks):
            row_cells = []
            for j, file in enumerate(files):
                square = file + rank
                symbol = piece_map.get(square, "")
                # cell = f" {symbol:^3} " if symbol else f" {square:^3} "
                row_cells.append(f" {symbol:^3} " if symbol else f" {square:^3} ")
            # print("│" + "│".join(row_cells) + "│" + " " + rank)
            std_output += "│" + "│".join(row_cells) + "│" + " " + rank + "\n"
            if i < 7:
                # print("├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤")
                std_output += "├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤\n"
        # print("└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘")
        # print("  a     b     c     d     e     f     g     h")
        
        std_output += "└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘\n"
        std_output += "  a     b     c     d     e     f     g     h\n"
        std_output += "\n## Symbols\n"
        # show white and black symbols
        # print("\n## Symbols\n")
        for symbol, unicode in SymbolMapping.items():
            # print(f"{symbol}: {unicode}")
            std_output += f"{symbol}: {unicode}\n"
    

    return frame, std_output


if __name__ == "__main__":
    # list cv2 video capture devices and detail
    frame, output= getCapture(1)
    cv2.imwrite("detected_tags.jpg", frame)
    logger.info("Saved detected tags image as detected_tags.jpg")
    
    print(output)