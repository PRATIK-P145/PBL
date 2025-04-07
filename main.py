import cv2
import numpy as np
from cv2 import aruco
from cvzone.HandTrackingModule import HandDetector
import time
from threading import Thread

class WebcamStream:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffering
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Lower resolution
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.ret, self.frame = self.cap.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()  # Start thread
        return self

    def update(self):
        while not self.stopped:
            self.ret, self.frame = self.cap.read()

    def read(self):
        return self.ret, self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()

class ARCalculator:
    def __init__(self):
        # Aruco setup
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
        self.aruco_params = aruco.DetectorParameters()
        self.aruco_detector = aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
        
        # Hand detector setup
        self.hand_detector = HandDetector(
            staticMode=False,
            maxHands=1,
            modelComplexity=1,
            detectionCon=0.8,
            minTrackCon=0.5
        )
        
        # UI configuration
        self.ui_scale_factor = 2.1
        self.button_width, self.button_height = 60, 60
        self.button_spacing = 5
        self.display_height = 80
        self.slider_width = 30
        self.ui_visibility = 0.0
        self.is_sliding = False
        self.slider_grab_pos = 0
        
        # Colors with hover effect
        self.button_colors = {
            'normal': (100, 100, 100, 150),
            'hover': (173, 216, 230, 180),  # Light blue
            'pressed': (0, 0, 255, 150),
            'display': (50, 50, 50, 200),
            'slider': (200, 200, 200, 200)
        }
        
        # Calculator state
        self.button_labels = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["C", "0", ".", "+"],
            ["(", ")", "<", "="]
        ]
        self.current_input = ""
        self.current_result = ""
        self.last_button_press_time = 0
        self.debounce_time = 0.3
        self.active_buttons = []
        
        # Initialize camera (with multithreading)
        ip_url = "http://192.168.0.104:8080/video"
        #self.stream = WebcamStream(ip_url).start()
        self.stream = WebcamStream(0).start()
        time.sleep(1.0)  # Allow camera to warm up
        
        # Create window
        cv2.namedWindow("AR Calculator", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("AR Calculator", 800, 600)
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()

    def get_button_coords(self, ui_top_left):
        coords = []
        total_width = 4 * self.button_width + 3 * self.button_spacing
        
        # Slider button
        slider_x = int(ui_top_left[0] + total_width * self.ui_visibility)
        coords.append({
            "label": "slider",
            "x1": slider_x,
            "y1": int(ui_top_left[1]),
            "x2": slider_x + self.slider_width,
            "y2": int(ui_top_left[1] + self.display_height + 5 * (self.button_height + self.button_spacing)),
            "state": "normal",
            "is_slider": True
        })
        
        if self.ui_visibility > 0:
            # Display box
            display_x = int(ui_top_left[0] - total_width * (1 - self.ui_visibility))
            coords.append({
                "label": "display",
                "x1": display_x,
                "y1": int(ui_top_left[1]),
                "x2": display_x + total_width,
                "y2": int(ui_top_left[1] + self.display_height),
                "state": "display",
                "is_slider": False
            })
            
            # Calculator buttons
            for row_idx, row in enumerate(self.button_labels):
                for col_idx, label in enumerate(row):
                    x1 = int(display_x + col_idx * (self.button_width + self.button_spacing))
                    y1 = int(ui_top_left[1] + self.display_height + self.button_spacing + 
                             row_idx * (self.button_height + self.button_spacing))
                    x2 = x1 + self.button_width
                    y2 = y1 + self.button_height
                    coords.append({
                        "label": label,
                        "x1": x1, "y1": y1,
                        "x2": x2, "y2": y2,
                        "state": "normal",
                        "is_slider": False
                    })
        
        return coords

    def detect_button_press(self, fingertip_pos, button_coords):
        current_time = time.time()
        if current_time - self.last_button_press_time < self.debounce_time:
            return None
            
        pressed_button = None
        for button in button_coords:
            if button["x1"] <= fingertip_pos[0] <= button["x2"] and button["y1"] <= fingertip_pos[1] <= button["y2"]:
                if button.get("is_slider", False):
                    self.is_sliding = True
                    self.slider_grab_pos = fingertip_pos[0]
                    return "slider"
                
                button["state"] = "pressed"
                pressed_button = button["label"]
                
                # Handle special buttons
                if button["label"] == "=":
                    self.calculate_result()
                elif button["label"] == "C":
                    self.current_input = ""
                    self.current_result = ""
                elif button["label"] == "<":
                    self.current_input = self.current_input[:-1]
                else:
                    self.current_input += button["label"]
                
                self.last_button_press_time = current_time
                break
            else:
                if not button.get("is_slider", False):
                    button["state"] = "normal"
        
        return pressed_button

    def update_slider_position(self, current_pos):
        if not self.is_sliding:
            return
            
        delta = current_pos - self.slider_grab_pos
        self.slider_grab_pos = current_pos
        
        self.ui_visibility += delta / (4 * self.button_width + 3 * self.button_spacing)
        self.ui_visibility = max(0.0, min(1.0, self.ui_visibility))

    def calculate_result(self):
        if not self.current_input:
            return
            
        try:
            self.current_result = str(eval(self.current_input))
        except:
            self.current_result = "Error"

    def draw_ui(self, frame, button_coords):
        overlay = frame.copy()
        
        for button in button_coords:
            if button["label"] == "slider":
                # Draw slider button
                color = self.button_colors["slider"]
                cv2.rectangle(overlay, (button["x1"], button["y1"]), 
                            (button["x2"], button["y2"]), color[:3], -1)
                cv2.rectangle(overlay, (button["x1"], button["y1"]), 
                            (button["x2"], button["y2"]), (0, 0, 0), 2)
                
                # Draw slider arrow
                arrow_size = 15
                center_x = button["x1"] + self.slider_width // 2
                center_y = button["y1"] + (button["y2"] - button["y1"]) // 2
                if self.ui_visibility < 0.5:
                    pts = np.array([[center_x, center_y], 
                                 [center_x + arrow_size, center_y - arrow_size],
                                 [center_x + arrow_size, center_y + arrow_size]])
                else:
                    pts = np.array([[center_x, center_y],
                                 [center_x - arrow_size, center_y - arrow_size],
                                 [center_x - arrow_size, center_y + arrow_size]])
                cv2.fillPoly(overlay, [pts], (0, 0, 0))
                
            elif button["label"] == "display":
                # Draw display box
                color = self.button_colors["display"]
                cv2.rectangle(overlay, (button["x1"], button["y1"]), 
                            (button["x2"], button["y2"]), color[:3], -1)
                cv2.rectangle(overlay, (button["x1"], button["y1"]), 
                            (button["x2"], button["y2"]), (0, 0, 0), 2)
                
                # Display input and result
                input_text = self.current_input if len(self.current_input) < 20 else "..." + self.current_input[-17:]
                cv2.putText(overlay, input_text, 
                            (button["x1"] + 10, button["y1"] + 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                            (255, 255, 255), 2)
                
                if self.current_result:
                    cv2.putText(overlay, f"= {self.current_result}", 
                                (button["x1"] + 10, button["y1"] + 60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                                (200, 200, 0), 2)
            else:
                # Enhanced button drawing with hover effects
                color = self.button_colors[button["state"]]
                
                # Add glow effect for hover state
                if button["state"] == "hover":
                    glow = overlay.copy()
                    cv2.rectangle(glow, 
                                (button["x1"]-3, button["y1"]-3), 
                                (button["x2"]+3, button["y2"]+3), 
                                (173, 216, 230), -1)
                    overlay = cv2.addWeighted(overlay, 0.7, glow, 0.3, 0)
                
                # Draw button
                cv2.rectangle(overlay, (button["x1"], button["y1"]), 
                            (button["x2"], button["y2"]), color[:3], -1)
                cv2.rectangle(overlay, (button["x1"], button["y1"]), 
                            (button["x2"], button["y2"]), (0, 0, 0), 2)
                
                # Draw label
                text_size = cv2.getTextSize(button["label"], cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                text_x = button["x1"] + (self.button_width - text_size[0]) // 2
                text_y = button["y1"] + (self.button_height + text_size[1]) // 2
                cv2.putText(overlay, button["label"], (text_x, text_y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Blend the overlay
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

    def run(self):
        while True:
            ret, frame = self.stream.read()
            if not ret:
                break

            # Flip frame and resize to 800x600
            frame = cv2.flip(frame, 1)
            display_frame = cv2.resize(frame, (800, 600))
            
            # Detect hands first
            hands, _ = self.hand_detector.findHands(display_frame, flipType=False)
            
            # Detect markers on the display frame (800x600)
            corners, ids, _ = self.aruco_detector.detectMarkers(display_frame)
            
            if ids is not None:
                for i, marker_id in enumerate(ids):
                    if marker_id in [0, 8]:
                        corner_pts = corners[i][0].astype(np.float32)
                        
                        # Get bottom right corner of marker (point index 2)
                        bottom_right = corner_pts[2]
                        
                        # Calculate UI top-left position
                        ui_top_left = bottom_right.copy()
                        
                        # Get button coordinates
                        button_coords = self.get_button_coords(ui_top_left)
                        self.active_buttons = button_coords
                        
                        # Draw UI
                        self.draw_ui(display_frame, button_coords)
                        
                        # Process hand interaction
                        if hands:
                            hand = hands[0]
                            lmList = hand["lmList"]
                            
                            if len(lmList) > 12:
                                index_tip = lmList[8][0:2]
                                thumb_tip = lmList[4][0:2]
                                
                                distance = np.linalg.norm(np.array(index_tip) - np.array(thumb_tip))
                                cv2.circle(display_frame, (int(index_tip[0]), int(index_tip[1])), 10, 
                                          (0, 255, 0) if distance > 30 else (0, 0, 255), -1)
                                
                                if self.is_sliding:
                                    if distance < 30:
                                        self.update_slider_position(index_tip[0])
                                    else:
                                        self.is_sliding = False
                                        if self.ui_visibility > 0.7:
                                            self.ui_visibility = 1.0
                                        elif self.ui_visibility < 0.3:
                                            self.ui_visibility = 0.0
                                else:
                                    if distance < 30:
                                        pressed_button = self.detect_button_press(index_tip, button_coords)
                                        if pressed_button == "slider":
                                            self.is_sliding = True
                                            self.slider_grab_pos = index_tip[0]
                                    else:
                                        for button in button_coords:
                                            if button.get("is_slider", False):
                                                continue
                                            if button["x1"] <= index_tip[0] <= button["x2"] and button["y1"] <= index_tip[1] <= button["y2"]:
                                                button["state"] = "hover"
                                                break

            # Display FPS
            if self.frame_count % 10 == 0:
                fps = self.frame_count / (time.time() - self.start_time)
                cv2.putText(display_frame, f"FPS: {int(fps)}", (20, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
            
            cv2.imshow("AR Calculator", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.ui_scale_factor = min(3.0, self.ui_scale_factor + 0.1)
            elif key == ord('a'):
                self.ui_scale_factor = max(1.0, self.ui_scale_factor - 0.1)

            self.frame_count += 1

        self.stream.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    calculator = ARCalculator()
    calculator.run()