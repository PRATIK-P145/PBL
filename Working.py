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

    def checkClick(self, x, y):
        if self.pos[0] < x < self.pos[0] + self.width and \
                self.pos[1] < y < self.pos[1] + self.height:
            return True
        return False


# Buttons
buttonListValues = [['7', '8', '9', '*'],
                    ['4', '5', '6', '-'],
                    ['1', '2', '3', '+'],
                    ['0', '/', '.', '=']]
buttonList = []
for y in range(4):
    for x in range(4):
        xpos = x * 100 + 50
        ypos = y * 100 + 150
        buttonList.append(Button((xpos, ypos), 100, 100, buttonListValues[y][x]))

# Variables
myEquation = ''
delayCounter = 0

# Webcam Setup
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    # Draw UI
    cv2.rectangle(img, (50, 50), (450, 150), (225, 225, 225), cv2.FILLED)
    cv2.rectangle(img, (50, 50), (450, 150), (50, 50, 50), 3)
    for button in buttonList:
        button.draw(img)

    # Check for Hand
    if hands:
        lmList = hands[0]['lmList']
        if len(lmList) >= 12:
            x1, y1, _ = lmList[8]
            x2, y2, _ = lmList[12]
            length, _, img = detector.findDistance((x1, y1), (x2, y2), img)
            print(length)

            if length < 50 and delayCounter == 0:
                for button in buttonList:
                    if button.checkClick(x1, y1):
                        myValue = button.value
                        if myValue == '=':
                            try:
                                myEquation = str(eval(myEquation))
                            except:
                                myEquation = 'Error'
                        else:
                            myEquation += myValue
                        delayCounter = 1

    # Prevent multiple clicks
    if delayCounter != 0:
        delayCounter += 1
        if delayCounter > 10:
            delayCounter = 0

    # Display equation
    cv2.putText(img, myEquation, (60, 120), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)

    # Show frame
    cv2.imshow("Calculator",img)
    key = cv2.waitKey(1)

    if key== ord('c'):
        myEquation = ''
    elif key == ord("x"):
        break
