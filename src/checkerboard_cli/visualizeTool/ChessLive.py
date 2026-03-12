from checkerboard_cli.getPosition import getCapture
from pupil_apriltags import Detector
import datetime
import time
import cv2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def live(camera_index=2):
    cap = cv2.VideoCapture(camera_index)
    detector = Detector(families="tag36h11")
    while True:
        try:
            frame, output = getCapture(cap, detector, camera_index)
            print(output)
        except Exception as e:
            print(f"Error capturing frame: {e}")
            continue
        if frame is not None:
            # Put the current date and time on the frame, with white text and black background
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            
            
            # draw background for text
            text_size, _ = cv2.getTextSize(timestamp, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            text_width, text_height = text_size
            cv2.rectangle(frame, (5, 5), (10 + text_width, 35), (0, 0, 0), -1)
            # draw text
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            
            cv2.imshow("Chess Live", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        else:
            print("Failed to capture frame.")
        # time.sleep(1/10)  # Add a small delay to reduce CPU usage
    cv2.destroyAllWindows()


if __name__ == "__main__":
    live(2)