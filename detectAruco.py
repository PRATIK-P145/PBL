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

# Load the improved calculator UI with transparent background
calculator_ui = cv2.imread("calculator_ui_preview.png", cv2.IMREAD_UNCHANGED)

if calculator_ui.shape[2] == 3:  # BGR to RGB if 3 channels (no alpha)
    calculator_ui = cv2.cvtColor(calculator_ui, cv2.COLOR_BGR2RGB)
elif calculator_ui.shape[2] == 4:  # BGRA to RGBA if 4 channels (with alpha)
    calculator_ui = cv2.cvtColor(calculator_ui, cv2.COLOR_BGRA2RGBA)

# Scale factor for UI size (default 2.1x of marker size)
ui_scale_factor = 2.1

# Calculator grid size
rows, cols = 4, 4  # 4 rows and 4 columns for standard calculator layout

# Define button actions
button_actions = {
    (0, 0): "7", (0, 1): "8", (0, 2): "9", (0, 3): "/",
    (1, 0): "4", (1, 1): "5", (1, 2): "6", (1, 3): "*",
    (2, 0): "1", (2, 1): "2", (2, 2): "3", (2, 3): "-",
    (3, 0): "0", (3, 1): "C", (3, 2): "=", (3, 3): "+"
}

# Convert RGBA to BGR for overlay
def get_bgr_ui(resized_ui):
    if resized_ui.shape[2] == 4:
        # Extract RGB and ignore alpha
        return cv2.cvtColor(resized_ui[:, :, :3], cv2.COLOR_RGBA2BGR)
    return resized_ui


# Function to calculate button coordinates dynamically
def get_button_coordinates(resized_ui, display_height_ratio=0.25):
    h, w = resized_ui.shape[:2]

    # Skip display area - calculate height offset
    display_height = int(h * display_height_ratio)
    button_height_area = h - display_height

    button_width = w // cols
    button_height = button_height_area // rows

    button_coords = {}

    for row in range(rows):
        for col in range(cols):
            x1, y1 = col * button_width, display_height + row * button_height
            x2, y2 = (col + 1) * button_width, display_height + (row + 1) * button_height
            button_coords[(row, col)] = (x1, y1, x2, y2)

    return button_coords


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

                # Resize improved calculator UI to the correct size
                h, w = calculator_ui.shape[:2]
                aspect_ratio = w / h

                # Calculate new size while maintaining aspect ratio
                if w >= h:
                    new_w = ui_size
                    new_h = int(new_w / aspect_ratio)
                else:
                    new_h = ui_size
                    new_w = int(new_h * aspect_ratio)

                # Resize UI while maintaining aspect ratio
                resized_ui = cv2.resize(calculator_ui, (new_w, new_h))
                calculator_bgr = get_bgr_ui(resized_ui)

                # Get button coordinates dynamically after resizing UI
                button_coords = get_button_coordinates(resized_ui)

                # Update source points based on new UI size
                src_pts = np.array([
                    [0, 0],
                    [new_w - 1, 0],
                    [new_w - 1, new_h - 1],
                    [0, new_h - 1]
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
                alpha = 0.7  # Transparency level
                for c in range(3):
                    frame[:, :, c] = np.where(
                        mask == 255,
                        cv2.addWeighted(warped_ui[:, :, c], alpha, frame[:, :, c], 1 - alpha, 0),
                        frame[:, :, c]
                    )

                # Draw button boundaries for visualization
                for (row, col), (x1, y1, x2, y2) in button_coords.items():
                    warped_button_pts = np.array([
                        [x1, y1],
                        [x2, y1],
                        [x2, y2],
                        [x1, y2]
                    ], dtype=np.float32)

                    # Transform button coordinates to frame coordinates
                    transformed_pts = cv2.perspectiveTransform(warped_button_pts.reshape(-1, 1, 2), matrix)
                    transformed_pts = np.int32(transformed_pts.reshape(-1, 2))

                    # Draw button rectangle for debugging
                    cv2.polylines(frame, [transformed_pts], isClosed=True, color=(0, 255, 0), thickness=2)

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
