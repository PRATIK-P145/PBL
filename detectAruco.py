import cv2
from cv2 import aruco
import numpy as np

# Load the predefined dictionary for ArUco markers
aruco_dict = aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

# Correctly create an instance of DetectorParameters for OpenCV 4.11.0+
aruco_params = aruco.DetectorParameters()

# Create an instance of ArucoDetector (for OpenCV 4.7.0+)
aruco_detector = aruco.ArucoDetector(aruco_dict, aruco_params)

# Initialize webcam
cap = cv2.VideoCapture(0)

# Set resolution to 1280x720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Scale factor for UI size (default 2.1x of marker size)
ui_scale_factor = 2.1

# Define button size and spacing
button_width, button_height = 40, 40  # Default button size
button_spacing_x, button_spacing_y = 5, 5  # Spacing between buttons

# Define button labels and positions dynamically
button_labels = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"]
]

button_coords = []

# Get button boundaries dynamically after UI placement
def get_button_coords(ui_top_left, button_width, button_height, button_spacing_x, button_spacing_y):
    coords = []
    for row_idx, row in enumerate(button_labels):
        for col_idx, label in enumerate(row):
            x1 = int(ui_top_left[0] + col_idx * (button_width + button_spacing_x))
            y1 = int(ui_top_left[1] + row_idx * (button_height + button_spacing_y))
            x2 = x1 + button_width
            y2 = y1 + button_height
            coords.append({"label": label, "x1": x1, "y1": y1, "x2": x2, "y2": y2})
    return coords

# Dummy function to get fingertip position (for now we'll use the center of the frame)
def get_fingertip_position(frame):
    h, w, _ = frame.shape
    return (w // 2, h // 2)

# Detect button press based on fingertip position
def detect_button_press(fingertip_pos, button_coords):
    for button in button_coords:
        if button["x1"] <= fingertip_pos[0] <= button["x2"] and button["y1"] <= fingertip_pos[1] <= button["y2"]:
            return button["label"]
    return None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Verify camera resolution
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Check if the captured frame has the correct dimensions
    if frame.shape[1] != width or frame.shape[0] != height:
        print(f"Warning: Captured frame size ({frame.shape[1]}x{frame.shape[0]}) does not match requested resolution ({width}x{height}).")

    # Set window to correct resolution
    cv2.namedWindow("ArUco Marker with Enhanced Calculator UI", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ArUco Marker with Enhanced Calculator UI", width, height)

    # Use detectMarkers from ArucoDetector instance
    corners, ids, rejected = aruco_detector.detectMarkers(frame)

    if ids is not None:
        for i in range(len(ids)):
            if ids[i] == 0 or ids[i] == 8:  # Only overlay for marker ID 0 or 8
                corner_pts = corners[i][0].astype(np.float32)

                # Calculate marker size dynamically
                marker_size = np.linalg.norm(corner_pts[0] - corner_pts[1])  # Width of marker
                ui_size = int(marker_size * ui_scale_factor)  # Dynamic scale based on marker size

                top_left, top_right, bottom_right, bottom_left = corner_pts
                offset_vector = (top_right - top_left) / np.linalg.norm(top_right - top_left)
                vertical_offset_vector = (bottom_left - top_left) / np.linalg.norm(bottom_left - top_left)

                dst_pts = np.array([
                    top_right,
                    top_right + offset_vector * ui_size,
                    bottom_right + offset_vector * ui_size + vertical_offset_vector * ui_size,
                    bottom_right + vertical_offset_vector * ui_size
                ], dtype=np.float32)

                # Get button coordinates dynamically after placing UI
                button_coords = get_button_coords(top_right, button_width, button_height, button_spacing_x, button_spacing_y)

                # Draw button boundaries for visualization
                for button in button_coords:
                    cv2.rectangle(frame, (button["x1"], button["y1"]), (button["x2"], button["y2"]), (0, 255, 0), 2)
                    cv2.putText(frame, button["label"], (button["x1"] + 10, button["y1"] + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Detect fingertip position (for now, center of frame)
                fingertip_pos = get_fingertip_position(frame)
                cv2.circle(frame, fingertip_pos, 10, (0, 0, 255), -1)

                # Detect button press and print result
                button_pressed = detect_button_press(fingertip_pos, button_coords)
                if button_pressed:
                    print(f"Button Pressed: {button_pressed}")

    cv2.putText(frame, f"UI Size: {ui_scale_factor:.1f}x", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("ArUco Marker with Enhanced Calculator UI", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        ui_scale_factor += 0.5
        print(f"UI size increased to: {ui_scale_factor:.1f}x")
    elif key == ord('a'):
        if ui_scale_factor > 0.5:
            ui_scale_factor -= 0.5
            print(f"UI size decreased to: {ui_scale_factor:.1f}x")
        else:
            print("UI size cannot be reduced further!")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
