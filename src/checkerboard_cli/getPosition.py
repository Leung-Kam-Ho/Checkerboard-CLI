import cv2
from pupil_apriltags import Detector
from checkerboard_cli.config.ChessMapping import ChessMapping
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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


def getCapture(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    frame = getFrame(cap)
    if frame is None:
        return None
    tags = detectAprilTags(frame)
    if not tags:
        logger.warning("No AprilTags detected.")
    
    shortest_distance = float('inf')

    for tag in tags:
        logger.debug(f"Detected tag ID: {tag.tag_id} at position: {tag.center}")
        # draw the tag on the frame
        corners = tag.corners.astype(int)
        symbol = ChessMapping.get(tag.tag_id, str(tag.tag_id))
        logger.debug(f"Mapping tag ID {tag.tag_id} to symbol: {symbol}")

        # if symbol is Upper case, draw and fill in White, else draw in Black
        fill_color = (255, 255, 255) if symbol.isupper() else (0, 0, 0)
        text_color = (0, 0, 0) if symbol.isupper() else (255, 255, 255)
        for i in range(4):
            # cv2.line(frame, tuple(corners[i]), tuple(corners[(i + 1) % 4]), (255, 0, 255), 2)
            if corners[i][1] < shortest_distance:
                shortest_distance = corners[i][1]
        # fill the tag with the color
        cv2.fillPoly(frame, [corners], fill_color)
        
        font_scale = shortest_distance / 200.0
        # draw the tag ID near the center
        cv2.putText(frame, symbol, (int(tag.center[0] - 10 * font_scale), int(tag.center[1] + 10 * font_scale)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 5)

    return frame


if __name__ == "__main__":
    # list cv2 video capture devices and detail
    frame = getCapture(1)
    cv2.imwrite("detected_tags.jpg", frame)