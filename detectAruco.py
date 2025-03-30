import cv2
import numpy as np

# Load the predefined dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()

# Initialize the webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Set width to 1280
cap.set(4, 720)   # Set height to 720

# Define initial UI size and scale factor
base_ui_size = 200  # Initial size of the square
ui_scale_factor = 2.1  # Default scale multiplier

# Set a default size to avoid NameError
ui_size = int(base_ui_size * ui_scale_factor)  # Define a default size

# Transparency level (0.5 = 50% transparent initially)
ui_transparency = 0.5

# Load or generate a basic calculator UI as an overlay (dummy UI for now)
calculator_ui = np.ones((base_ui_size, base_ui_size, 3), dtype=np.uint8) * 255
cv2.putText(calculator_ui, "Calculator", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect ArUco markers
    corners, ids, rejected = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)

    if ids is not None:
        for i in range(len(ids)):
            if ids[i] == 0:  # Only overlay if the marker ID is 0
                corner_pts = corners[i][0].astype(np.float32)

                # Calculate the scaled UI size (fixed square with dynamic scaling)
                ui_size = int(base_ui_size * ui_scale_factor)

                # Resize the calculator UI to the new size (keeping it square)
                calculator_resized = cv2.resize(calculator_ui, (ui_size, ui_size))

                # Define source points from the resized UI (square shape)
                src_pts = np.array([
                    [0, 0],
                    [ui_size - 1, 0],
                    [ui_size - 1, ui_size - 1],
                    [0, ui_size - 1]
                ], dtype=np.float32)

                # Get the marker corner points
                top_left, top_right, bottom_right, bottom_left = corner_pts

                # Calculate offset to place UI to the right of the marker
                offset_vector = (top_right - top_left) / np.linalg.norm(top_right - top_left)  # Normalize vector
                vertical_offset_vector = (bottom_left - top_left) / np.linalg.norm(bottom_left - top_left)  # Normalize vector

                # Place the UI to the right side of the marker (fixed aspect ratio)
                dst_pts = np.array([
                    top_right,  # Top-left of UI aligned with top-right of marker
                    top_right + offset_vector * ui_size,  # Top-right of UI
                    bottom_right + offset_vector * ui_size + vertical_offset_vector * ui_size,  # Bottom-right of UI
                    bottom_right + vertical_offset_vector * ui_size  # Bottom-left of UI
                ], dtype=np.float32)

                # Calculate perspective transform matrix
                matrix, _ = cv2.findHomography(src_pts, dst_pts)

                # Warp the calculator UI onto the right side of the marker
                warped_ui = cv2.warpPerspective(calculator_resized, matrix, (frame.shape[1], frame.shape[0]))

                # Create a mask to overlay only the non-zero UI region
                mask = cv2.cvtColor(warped_ui, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)

                # Apply transparency blending
                for c in range(3):
                    frame[:, :, c] = np.where(
                        mask == 255,
                        cv2.addWeighted(frame[:, :, c], 1 - ui_transparency, warped_ui[:, :, c], ui_transparency, 0),
                        frame[:, :, c]
                    )

    # Display the result
    cv2.putText(frame, f"UI Size: {ui_size}px", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Transparency: {ui_transparency:.2f}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("ArUco Marker with Calculator UI on Right Side", frame)

    # Key press handling
    key = cv2.waitKey(1) & 0xFF

    # Press 's' to increase UI size
    if key == ord('s'):
        ui_scale_factor += 0.5
        print(f"UI size increased to: {ui_size}px")

    # Press 'a' to decrease size
    elif key == ord('a'):
        if ui_scale_factor > 0.5:
            ui_scale_factor -= 0.5
            print(f"UI size decreased to: {ui_size}px")
        else:
            print("Minimum UI size reached!")

    # Press 'w' to increase transparency
    elif key == ord('w'):
        if ui_transparency < 1.0:
            ui_transparency += 0.1
            print(f"Transparency increased to: {ui_transparency:.2f}")
        else:
            print("Maximum transparency reached!")

    # Press 'z' to decrease transparency
    elif key == ord('z'):
        if ui_transparency > 0.1:
            ui_transparency -= 0.1
            print(f"Transparency decreased to: {ui_transparency:.2f}")
        else:
            print("Minimum transparency reached!")

    # Press 'q' to quit
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
