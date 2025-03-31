import cv2
from cv2 import aruco
import numpy as np

# Load the predefined dictionary for ArUco markers
aruco_dict = aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

# Correctly create an instance of DetectorParameters for OpenCV 4.11.0+
aruco_params = aruco.DetectorParameters()

# Create an instance of ArucoDetector (only for OpenCV 4.7.0+)
aruco_detector = aruco.ArucoDetector(aruco_dict, aruco_params)

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Set width to 1280
cap.set(4, 720)   # Set height to 720

# Load the improved calculator UI with transparent background
calculator_ui = cv2.imread("calculator_ui_preview.png", cv2.IMREAD_UNCHANGED)

# Scale factor for UI size (default 2.1x of marker size)
ui_scale_factor = 2.1

# Convert RGBA to BGR for overlay
def get_bgr_ui(resized_ui):
    if resized_ui.shape[2] == 4:
        # Extract RGB and ignore alpha
        return cv2.cvtColor(resized_ui[:, :, :3], cv2.COLOR_RGBA2BGR)
    return resized_ui

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Use detectMarkers from ArucoDetector instance
    corners, ids, rejected = aruco_detector.detectMarkers(frame)

    if ids is not None:
        for i in range(len(ids)):
            if ids[i] == 0:  # Only overlay for marker ID 0
                corner_pts = corners[i][0].astype(np.float32)

                # Calculate marker size dynamically
                marker_size = np.linalg.norm(corner_pts[0] - corner_pts[1])  # Width of marker
                ui_size = int(marker_size * ui_scale_factor)  # Dynamic scale based on marker size

                # Resize improved calculator UI to the correct size
                resized_ui = cv2.resize(calculator_ui, (ui_size, ui_size))
                calculator_bgr = get_bgr_ui(resized_ui)

                # Define source points for perspective warp
                src_pts = np.array([
                    [0, 0],
                    [ui_size - 1, 0],
                    [ui_size - 1, ui_size - 1],
                    [0, ui_size - 1]
                ], dtype=np.float32)

                # Get corner points of the marker
                top_left, top_right, bottom_right, bottom_left = corner_pts

                # Place UI aligned to the right side of marker
                offset_vector = (top_right - top_left) / np.linalg.norm(top_right - top_left)
                vertical_offset_vector = (bottom_left - top_left) / np.linalg.norm(bottom_left - top_left)

                dst_pts = np.array([
                    top_right,  # Align top-left of UI to top-right of marker
                    top_right + offset_vector * ui_size,
                    bottom_right + offset_vector * ui_size + vertical_offset_vector * ui_size,
                    bottom_right + vertical_offset_vector * ui_size
                ], dtype=np.float32)

                # Calculate perspective transform
                matrix, _ = cv2.findHomography(src_pts, dst_pts)

                # Warp the improved UI onto the right side
                warped_ui = cv2.warpPerspective(calculator_bgr, matrix, (frame.shape[1], frame.shape[0]))

                # Create a mask to overlay only the UI region
                mask = cv2.cvtColor(warped_ui, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

                # Overlay the warped UI onto the frame
                for c in range(3):
                    frame[:, :, c] = np.where(mask == 255, warped_ui[:, :, c], frame[:, :, c])

    # Display result
    cv2.putText(frame, f"UI Size: {ui_scale_factor:.1f}x", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("ArUco Marker with Enhanced Calculator UI", frame)

    # Key press handling
    key = cv2.waitKey(1) & 0xFF

    # Press 's' to increase size by 0.5
    if key == ord('s'):
        ui_scale_factor += 0.5
        print(f"UI size increased to: {ui_scale_factor:.1f}x")

    # Press 'a' to decrease size by 0.5
    elif key == ord('a'):
        if ui_scale_factor > 0.5:
            ui_scale_factor -= 0.5
            print(f"UI size decreased to: {ui_scale_factor:.1f}x")
        else:
            print("UI size cannot be reduced further!")

    # Press 'q' to quit
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
