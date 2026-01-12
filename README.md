# PBL
<h1>Touchless Virtual Calculator using Computer Vision</h1>

---

# 🚀 Local Setup Guide (Step-by-Step)

Follow these steps **exactly in order**.
Skipping steps will break the project.

---

## Step 1: Verify Python version (MANDATORY)

Open a terminal / command prompt **inside the project folder** and run:

```bash
python --version
```

### ✅ Supported versions

* Python **3.9.x**
* Python **3.10.x**

### ❌ Not supported

* Python 3.11
* Python 3.12+

If your version is **not supported**, stop here and install Python 3.10 before continuing. Click here -> [Python Version Issue](#python-version-issue)

---

## Step 2: Create a virtual environment (DO NOT SKIP)

This isolates dependencies and prevents system conflicts.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```


After activation, verify:

```bash
python --version
```

It **must still show 3.9 or 3.10**.

---

## Step 3: Upgrade pip inside the virtual environment

```bash
pip install --upgrade pip
```

This avoids installation errors later.

---

## Step 4: Install required dependencies

Run **exactly this command**:

```bash
pip install opencv-python opencv-contrib-python numpy cvzone mediapipe
```

### Why this matters

* `opencv-contrib-python` → required for **Aruco marker detection**
* `cvzone + mediapipe` → required for **hand tracking**

If any package fails to install, **do not continue** until it succeeds.

---

## Step 5: Verify camera access

Run this test:

```bash
python - <<EOF
import cv2
cap = cv2.VideoCapture(0)
print("Camera opened:", cap.isOpened())
cap.release()
EOF
```

### Expected output

```text
Camera opened: True
```

If `False`:

* Close Zoom / Teams / browser camera usage
* Try restarting your system
* Ensure webcam permissions are enabled

---

## Step 6: Generate and prepare an ArUco marker (REQUIRED)

This project **will not work without a marker**.

* Print `marker_0.png` on paper **OR**
* Display it full-screen on another device

📌 Ensure:

* Marker is clearly visible
* Good lighting
* Marker is not tilted too much

---

## Step 7: Run the application

Inside the activated virtual environment:

```bash
python main.py
```

(Replace `main.py` with the actual filename if different.)

---

## Step 8: How to interact with the application

### UI activation

* Show the **ArUco marker** to the camera
* Calculator UI appears **next to the marker**

### Hand gestures

* **Hover** → index finger over button
* **Click** → pinch index finger + thumb
* **Slide UI** → pinch slider and drag horizontally
* **Release** → unpinch fingers

### Keyboard controls

* `q` → quit application
* `s` → increase UI scale
* `a` → decrease UI scale

---

## Step 9: Expected behavior checklist

If setup is correct:

* Webcam feed opens
* FPS counter appears
* UI appears when marker is visible
* Buttons respond to pinch gestures

If any of these fail → setup is incomplete.

---

## Step 10: Common setup issues & fixes

### ❌ `ModuleNotFoundError: cv2.aruco`

✔ Fix:

```bash
pip install opencv-contrib-python
```

---

### ❌ Hand not detected

✔ Fix:

* Improve lighting
* Keep hand within camera frame
* Avoid cluttered background

---

### ❌ Marker detected but UI misplaced

✔ Fix:

* Marker must be fully visible
* Avoid extreme angles
* Print marker larger

---

## Final note (important)

This project depends on **real-time vision + gestures**.
Environment quality (camera, lighting, background) **directly affects performance**.

If it works smoothly once, it will work consistently.

---
---

## **🔹 Project Plan: Virtual Calculator using Tkinter & OpenCV**  

### **🟢 Step 1: Set Up the Project (1 Hour)**  
- Install required libraries:  
  ```bash
  pip install opencv-python numpy mediapipe
  ```
- Create a project folder (`VirtualCalculator/`)  
  - Inside, create files:  
    - `main.py` (Main script)  
    - `hand_tracker.py` (Hand tracking module)  
    - `ui.py` (Handles the translucent UI elements)  

---

### **🟢 Step 2: Implement Live Video Feed (1.5 Hours)**  
✅ Use OpenCV to capture video from the webcam:  
- Open a video window using `cv2.VideoCapture(0)`.  
- Display the live video feed using `cv2.imshow()`.  

---

### **🟢 Step 3: Implement Hand Tracking (2-3 Hours)**  
✅ Use **MediaPipe** or OpenCV to detect the hand in the webcam feed:  
- Implement a function to **detect hand landmarks**.  
- Track the index finger’s position for interaction.  
- Draw points on fingertips for debugging.  

---

### **🟢 Step 4: Design the UI with Tkinter (2-3 Hours)**  
✅ **Custom-styled translucent buttons**:  
- Use `canvas.create_rectangle()` to draw translucent buttons.  
- Position buttons for numbers (0-9) and operations (+, -, ×, ÷, =)  
- Make the buttons overlay on the video feed.  

---

### **🟢 Step 5: Implement Gesture-Based Selection (3-4 Hours)**  
✅ Detect when a user selects a button:  
- Check if the **index finger hovers over a button** for a short duration.  
- If the user holds the position, simulate a button press.  
- Add feedback (e.g., change button color temporarily).  

---

### **🟢 Step 6: Implement Basic Calculator Logic (2-3 Hours)**  
✅ Store user input and perform calculations:  
- Keep track of pressed numbers and operations.  
- Display the current input and result **overlayed on the video feed**.  
- Use `eval()` or a custom function to compute results.  

---

### **🟢 Step 7: Final Refinements & Testing (2-3 Hours)**  
✅ **Improve UI/UX**:  
- Add animations for button clicks.  
- Improve gesture detection accuracy.  

✅ **Test in different lighting conditions**  
✅ **Optimize performance to reduce lag**  

---

## **🟣 Suggested Timeline (Flexible)**  
| Day | Task | Time Est. |
|------|------|----------|
| Day 1 | Set up project, install dependencies, and start video feed | 1.5 hrs |
| Day 2 | Implement hand tracking | 2-3 hrs |
| Day 3 | Design custom UI | 2-3 hrs |
| Day 4 | Implement gesture-based button selection | 3-4 hrs |
| Day 5 | Add calculator logic and overlay results | 2-3 hrs |
| Day 6 | Test, optimize, and refine | 2-3 hrs |

---

This structured approach will help you stay focused and avoid feeling overwhelmed.  
Would you like any modifications or additional guidance on specific steps? 😊

---
## Python Version Issue
---

# If your Python version is NOT suitable (fix it properly)

Your project needs **Python 3.9 or 3.10**.
If you’re on **3.11 / 3.12**, expect random breakage.

---

## Step 1: Check what you currently have

```bash
python --version
```

If it says **3.9.x or 3.10.x** → stop, you’re fine.
Anything else → continue.

---

## Step 2: Install a compatible Python version

### 🔹 Windows (cleanest method)

1. Go to **python.org → Downloads**
2. Download **Python 3.10.x (64-bit)**
3. Run installer:

   * ✅ **Check “Add Python to PATH”**
   * ✅ Choose **Customize installation**
   * ✅ Install for **All Users**
4. Finish installation

Verify:

```bash
python --version
```

If it still shows the old version, don’t panic — go to Step 3.

---

### 🔹 macOS (recommended way)

```bash
brew install python@3.10
```

Verify:

```bash
python3.10 --version
```

---

### 🔹 Linux (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

Verify:

```bash
python3.10 --version
```

---

## Step 3: DO NOT replace system Python (critical)

Brutal truth:

> **Never fight the system Python. You will lose.**

Instead, **explicitly use the correct version**.

---

## Step 4: Create virtual environment using the correct Python

This is the most important command in this whole process.

### Windows

```bash
py -3.10 -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3.10 -m venv venv
source venv/bin/activate
```

Confirm:

```bash
python --version
```

It **must** say `3.10.x`.

If it doesn’t — you messed up the venv. Delete it and redo.

---


