import cv2
import mediapipe as mp
import numpy as np
import math

# Initialize Mediapipe Hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame for a natural view
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hands
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks, hand_info in zip(result.multi_hand_landmarks, result.multi_handedness):
            label = hand_info.classification[0].label

            if label == "Left":  # Check for left hand
                # Get wrist (landmark[0]) and middle finger base (landmark[9]) positions
                x0, y0 = int(hand_landmarks.landmark[0].x * w), int(hand_landmarks.landmark[0].y * h)
                x9, y9 = int(hand_landmarks.landmark[9].x * w), int(hand_landmarks.landmark[9].y * h)

                # Calculate palm size based on Euclidean distance
                palm_size = int(math.sqrt((x9 - x0) ** 2 + (y9 - y0) ** 2)) * 2

                # Define calculator size based on palm size
                calc_size = palm_size

                # Calculate top-left corner for centered UI
                calc_x, calc_y = x0 - calc_size // 2, y0 - calc_size // 2

                # Draw Calculator UI over palm (Dynamic size)
                cv2.rectangle(frame, (calc_x, calc_y), (calc_x + calc_size, calc_y + calc_size), (0, 255, 0), 2)
                cv2.putText(frame, "Calculator UI", (calc_x + 10, calc_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow("Virtual Calculator", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
