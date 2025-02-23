import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Initialize Tkinter window
root = tk.Tk()
root.title("Webcam with GUI Overlay")

# Set the window size
WIDTH, HEIGHT = 800, 600
root.geometry(f"{WIDTH}x{HEIGHT}")

# OpenCV Video Capture
cap = cv2.VideoCapture(0)  # 0 for default webcam

# Create a Frame for the Video
video_frame = tk.Frame(root, width=WIDTH, height=HEIGHT)
video_frame.grid(row=0, column=0, columnspan=4)  # Span across columns for overlay

# Create a Label to Display Video
video_label = tk.Label(video_frame)
video_label.pack(fill="both", expand=True)

def update_frame():
    """Captures frame, converts it, and updates the GUI."""
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (WIDTH, HEIGHT))  # Resize to fit the window
        
        # Convert frame to ImageTk format
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        
        # Update label with the new image
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    
    root.after(10, update_frame)  # Refresh every 10ms

# Create a Frame for Calculator Buttons
button_frame = tk.Frame(root, bg="white")
button_frame.grid(row=0, column=0, padx=20, pady=20)  # Overlay on top of video

buttons = [
    ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
    ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
    ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
    ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
    ("C", 5, 0), ("Back", 5, 1)
]

# Create buttons and add them to the grid inside the button_frame
for (text, row, col) in buttons:
    if text == "=":
        button = tk.Button(button_frame, text=text, font=("Arial", 18), bd=5, height=2, width=5, relief="raised", bg="#4CAF50", fg="white")
    elif text == "C":
        button = tk.Button(button_frame, text=text, font=("Arial", 18), bd=5, height=2, width=5, relief="raised", bg="#f44336", fg="white")
    elif text == "Back":
        button = tk.Button(button_frame, text=text, font=("Arial", 18), bd=5, height=2, width=5, relief="raised", bg="#ff9800", fg="white")
    else:
        button = tk.Button(button_frame, text=text, font=("Arial", 18), bd=5, height=2, width=5, relief="raised", bg="#008CBA", fg="white")
    
    button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

# Close the webcam properly when the window is closed
def on_closing():
    cap.release()
    cv2.destroyAllWindows()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Start updating the frames
update_frame()

# Run Tkinter event loop
root.mainloop()
