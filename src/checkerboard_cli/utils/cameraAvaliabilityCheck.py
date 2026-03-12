# loop through camera index 1 ~ 5, if ret, capture a frame and save it to a file, then break the loop
import cv2


def getFrame(cap):
    if not cap.isOpened():
        print(f"Cannot open camera {cap}")
        return None
    ret, frame = cap.read()
    if not ret:
        print(f"Cannot read frame from camera {cap}")
        return None
    return frame


def getCapture(camera_index):
    cap = cv2.VideoCapture(camera_index)
    frame = getFrame(cap)
    if frame is not None:
        return frame, "Camera {} is available.".format(camera_index)
    else:
        return None


if __name__ == "__main__":
    for i in range(1, 6):
        result = getCapture(i)
        if result is not None:
            frame, output = result
            print(output)
            cv2.imwrite("camera_{}.jpg".format(i), frame)
            # break
