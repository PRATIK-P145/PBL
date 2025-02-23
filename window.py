import cv2
from cvzone.HandTrackingModule import HandDetector

class Button:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value

    def draw(self, img):
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (225, 225, 225), cv2.FILLED)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (50, 50, 50), 3)
        cv2.putText(img, self.value, (self.pos[0] + 30, self.pos[1] + 70), cv2.FONT_HERSHEY_PLAIN,
                    2, (50, 50, 50), 2)

    def checkClick(self, x, y, img):  # Pass img as argument
        if self.pos[0] < x < self.pos[0] + self.width and \
                self.pos[1] < y < self.pos[1] + self.height:
            cv2.rectangle(img, (self.pos[0] + 3, self.pos[1] + 3),
                          (self.pos[0] + self.width - 3, self.pos[1] + self.height - 3),
                          (255, 255, 255), cv2.FILLED)
            cv2.putText(img, self.value, (self.pos[0] + 25, self.pos[1] + 80), cv2.FONT_HERSHEY_PLAIN,
                        5, (0, 0, 0), 5)
            return True
        return False


# Buttons
buttonListValues = [['7', '8', '9', '*'],
                    ['4', '5', '6', '-'],
                    ['1', '2', '3', '+'],
                    ['0', '/', '.', '=']]
buttonList = []
for x in range(4):
    for y in range(4):
        xpos = x * 100 + 800
        ypos = y * 100 + 150

        buttonList.append(Button((xpos, ypos), 100, 100, buttonListValues[y][x]))

# Variables
myEquation = ''
delayCounter = 0

# Webcam
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    # Get image frame
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)

    # Draw Display Screen
    cv2.rectangle(img, (800, 70), (800 + 400, 70 + 100),
                  (225, 225, 225), cv2.FILLED)
    cv2.rectangle(img, (800, 70), (800 + 400, 70 + 100),
                  (50, 50, 50), 3)
    
    # Draw Buttons
    for button in buttonList:
        button.draw(img)

    # Check for Hand
    if hands:
        lmList = hands[0]['lmList']

        # Debugging Output
        print("Index Finger Tip:", lmList[8])  
        print("Middle Finger Tip:", lmList[12])

        # Extract x, y coordinates only
        x1, y1, _ = lmList[8]
        x2, y2, _ = lmList[12]

        # Calculate distance
        distance_info = detector.findDistance((x1, y1), (x2, y2), img)
        print(distance_info)

        if len(distance_info) == 4:
            length, _, _, img = distance_info  # Unpacking Fix
        else:
            length, _, img = distance_info  # If only three values are returned

        print(length)
        x, y, _ = lmList[8]

        # If clicked check which button and perform action
        if length < 50 and delayCounter == 0:
            for i, button in enumerate(buttonList):
                if button.checkClick(x, y, img):  # Pass img
                    myValue = buttonListValues[i % 4][i // 4]  # Fixed indexing

                    if myValue == '=':
                        try:
                            myEquation = str(eval(myEquation)) if myEquation else ''
                        except:
                            myEquation = "Error"
                    else:
                        myEquation += myValue
                    delayCounter = 1

    # Avoid multiple clicks
    if delayCounter != 0:
        delayCounter += 1
        if delayCounter > 10:
            delayCounter = 0

    # Write the Final answer
    cv2.putText(img, myEquation, (810, 130), cv2.FONT_HERSHEY_PLAIN,
                3, (0, 0, 0), 3)

    # Display
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    
    # Clear the equation
    if key == ord('c'):
        myEquation = ''
