import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


root = tk.Tk()
root.title("Hand Tracking GUI")
root.geometry("800x600")


video_label = tk.Label(root)
video_label.pack()


coord_label = tk.Label(root, text="Index Finger: (x, y)", font=("Arial", 16))
coord_label.pack()

def update_frame():
    """Capture video frame, process hand tracking, and update the GUI."""
    ret, frame = cap.read()
    if not ret:
        return
    
    frame = cv2.flip(frame, 1) 
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    index_finger_x, index_finger_y = 0, 0  

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            index_finger_x = int(hand_landmarks.landmark[8].x * frame.shape[1])
            index_finger_y = int(hand_landmarks.landmark[8].y * frame.shape[0])

    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)

 
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    coord_label.config(text=f"Index Finger: ({index_finger_x}, {index_finger_y})")

    root.after(10, update_frame)


update_frame()


root.mainloop()


cap.release()
cv2.destroyAllWindows()
