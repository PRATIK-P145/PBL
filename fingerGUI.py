import cv2
import numpy as np
import mediapipe as mp

# Initialize Mediapipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Initialize webcam for main video feed
cap = cv2.VideoCapture(0)

# Open the second video (replace with a video file path or use another camera)
video_path = 'Naruto.mp4'  # Path to video file
overlay_cap = cv2.VideoCapture(video_path)

# Default distance factor to maintain a minimum size
min_distance = 50
max_distance = 300
min_ui_size = 100
max_ui_size = 300

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for natural interaction
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Read the next frame from the overlay video
    ret_overlay, overlay_frame = overlay_cap.read()
    if not ret_overlay:
        overlay_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video if it ends
        ret_overlay, overlay_frame = overlay_cap.read()

    # Detect hand landmarks
    results = hands.process(rgb_frame)

    # Store index finger tips
    index_fingers = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get index finger tip coordinates
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_x, index_y = int(index_tip.x * frame.shape[1]), int(index_tip.y * frame.shape[0])

            # Draw circle on the index finger tip
            cv2.circle(frame, (index_x, index_y), 10, (0, 255, 0), -1)

            # Add index finger coordinates to the list
            index_fingers.append((index_x, index_y))

        # Proceed only if both hands are detected (2 index fingers)
        if len(index_fingers) == 2:
            # Get coordinates of both index fingers
            index1_x, index1_y = index_fingers[0]
            index2_x, index2_y = index_fingers[1]

            # Calculate distance between the two index fingers
            distance = np.sqrt((index1_x - index2_x) ** 2 + (index1_y - index2_y) ** 2)

            # Normalize distance to dynamically resize the overlay UI
            distance = np.clip(distance, min_distance, max_distance)
            ui_scaled_size = int(min_ui_size + (distance - min_distance) / (max_distance - min_distance) * (max_ui_size - min_ui_size))

            # Resize the overlay video to match the calculated size
            overlay_resized = cv2.resize(overlay_frame, (ui_scaled_size, ui_scaled_size))

            # Define corner points of the resized overlay
            height, width, _ = overlay_resized.shape
            src_pts = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)

            # Define destination points based on index finger positions (top corners on index fingers)
            dst_pts = np.array([
                [index1_x, index1_y],  # Top-left
                [index2_x, index2_y],  # Top-right
                [index2_x, index2_y + ui_scaled_size],  # Bottom-right
                [index1_x, index1_y + ui_scaled_size]  # Bottom-left
            ], dtype=np.float32)

            # Get perspective transform matrix
            matrix, _ = cv2.findHomography(src_pts, dst_pts)

            # Warp and overlay the resized video onto the frame
            warped_overlay = cv2.warpPerspective(overlay_resized, matrix, (frame.shape[1], frame.shape[0]))

            # Create a mask to blend only the overlay region with transparency
            mask = (warped_overlay > 0).astype(np.uint8)
            
            # Apply transparency and overlay onto the frame
            alpha = 0.7  # Transparency level
            frame[mask == 1] = cv2.addWeighted(frame, 1 - alpha, warped_overlay, alpha, 0)[mask == 1]

    # Display the result
    cv2.imshow("Hand-Tracking Live Video Overlay", frame)

    # Exit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
overlay_cap.release()
cv2.destroyAllWindows()
