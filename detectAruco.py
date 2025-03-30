import cv2
import numpy as np

# Load the predefined dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()

# Initialize the webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Set width to 1280
cap.set(4, 720)   # Set height to 720

# Define calculator UI size (same as marker size)
ui_size = 200

# Load or generate a basic calculator UI as an overlay (dummy UI for now)
calculator_ui = np.ones((ui_size, ui_size, 3), dtype=np.uint8) * 255
cv2.putText(calculator_ui, "Calculator", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect ArUco markers
    corners, ids, rejected = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)

    if ids is not None:
        for i in range(len(ids)):
            # Get marker corner points
            corner_pts = corners[i][0].astype(np.float32)

            # Define destination points for the overlay (same size as marker)
            dst_pts = np.array([[0, 0], [ui_size - 1, 0], [ui_size - 1, ui_size - 1], [0, ui_size - 1]], dtype=np.float32)

            # Get perspective transform matrix
            matrix, _ = cv2.findHomography(dst_pts, corner_pts)

            # Warp and overlay the calculator UI onto the detected marker
            warped_ui = cv2.warpPerspective(calculator_ui, matrix, (frame.shape[1], frame.shape[0]))

            # Create a mask to overlay the warped UI
            mask = (warped_ui > 0).astype(np.uint8) * 255
            frame = cv2.addWeighted(frame, 1, warped_ui, 0.7, 0)

    # Display the result
    cv2.imshow("ArUco Marker with Calculator UI", frame)

    # Exit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
