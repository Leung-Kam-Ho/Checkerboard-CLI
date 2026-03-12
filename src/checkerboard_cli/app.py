from checkerboard_cli.getPosition import getCapture
from checkerboard_cli.visualizeTool import ChessLive

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Detect chessboard and pieces using AprilTags.")
    parser.add_argument("camera_index", type=int, default=0, help="Index of the camera to use.")
    parser.add_argument("--live", action="store_true", help="Show live video feed with detected chessboard.")
    
    args = parser.parse_args()
    # list cv2 video capture devices and detail
    cameraIndex = args.camera_index
    if args.live:
        ChessLive.live(cameraIndex)
    else:
        result = getCapture(args.camera_index)
        if result is not None:
            frame, output = result
            print(output)

if __name__ == "__main__":
    main()