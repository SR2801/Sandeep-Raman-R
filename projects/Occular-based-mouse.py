import cv2
import mediapipe as mp
import pyautogui
import datetime
import time
from plyer import notification


pyautogui.FAILSAFE = False
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()
ratio = screen_w / screen_h

# Initialise
_, frame = cam.read()
frame = cv2.add(frame, 50)

frame = cv2.flip(frame, 1)
# frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=50)
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
output = face_mesh.process(rgb_frame)
landmark_points = output.multi_face_landmarks
landmarks = landmark_points[0].landmark
frame_h, frame_w, _ = frame.shape
print(frame_h, frame_w)

top_forehead_landmark = landmarks[10]  # Landmark for the top of the forehead
bottom_nose_landmark = landmarks[6]  # Landmark for the bottom of the nose
left_ear_landmark = landmarks[34]  # Landmark for the left ear

# Calculate the midpoint between the ears
# ear_midpoint = find_midpoint(left_ear_landmark, right_ear_landmark)

# Calculate the points for the rectangle
top_left_point = (int(left_ear_landmark.x * frame_w), int(top_forehead_landmark.y * frame_h))
print("Top left", top_left_point)
# bottom_right_point = (int(right_ear_landmark.x * frame_w), int(bottom_nose_landmark.y * frame_h))
h = int((bottom_nose_landmark.y * frame_h) - (top_forehead_landmark.y * frame_h))
print(h)
w = h * ratio
print(w)
bottom_right_point = (int((left_ear_landmark.x * frame_w) + w), int(bottom_nose_landmark.y * frame_h))
print("Bottom right", bottom_right_point)

# Draw the rectangle
# image_with_rectangle = image.copy()
cv2.rectangle(frame, top_left_point, bottom_right_point, (0, 255, 0), 2)
mid=((top_left_point[0]+bottom_right_point[0])//2,(top_left_point[1]+bottom_right_point[1])//2)
print(mid)
# Utility parameters
eyeClose = 0.008
lclosed=False
blink=True
count = 0
ssTime = 0  # Screenshot threshold for time between two blinks
lTime = 0
rTime = 0
fTime = 0

# Application running
while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    # frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=50)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape
    clock = time.time()
    
    if landmark_points:
        landmarks = landmark_points[0].landmark
        for i, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0))
            if i == 1:
                cv2.circle(frame, (x, y), 3, (255, 0, 255))
                # screen_x = (screen_w * landmark.x)
                # screen_y = (screen_h * landmark.y)
                # screen_x = ((int(landmark.x) - top_left_point[0]) / w) * screen_w
                # screen_y = (int(landmark.y) - bottom_right_point[1] / h) * screen_h
                screen_x = (x - top_left_point[0]) * screen_w / w
                screen_y = (y - top_left_point[1]) * screen_h / h
                pyautogui.moveTo(screen_x, screen_y)
                # pyautogui.sleep(0.1)
        left = [landmarks[145], landmarks[159]]
        right = [landmarks[374], landmarks[386]]
        for landmark in left:
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 255))
        cv2.circle(frame, (mid[0], mid[1]), 3, (0, 255, 255))
        cv2.rectangle(frame, top_left_point, bottom_right_point, (0, 255, 255), 2)
        if ((left[0].y - left[1].y) < eyeClose) and ((right[0].y - right[1].y) > eyeClose):
            if lclosed:
                print("Left closed")
                pyautogui.mouseDown()
            # print("Left click")
            # print('Time diff:' + str(diff))
            diff = int((clock - lTime) * 10)
            # print('Time diff:' + str(diff))
            # pyautogui.click()
            if 5 < diff < 15:
                pyautogui.click(clicks=2)
            else:
                pyautogui.click()
            lTime = clock
            lclosed=True
            # pyautogui.sleep(0.5)
        elif lclosed:
            print("Left open")
            pyautogui.mouseUp(600)
            lclosed=False
        if (right[0].y - right[1].y) < eyeClose < (left[0].y - left[1].y):
            print("Right click")
            diff = (clock - rTime) * 10
            # print('Time diff:' + str(diff))
            diff = int((clock - rTime) * 10)

            print('Time diff:' + str(diff))
            if 5 < diff < 15:
                pyautogui.click(button='right', clicks=2)
            else:
                pyautogui.click(button='right')
            rTime = clock
        if (right[0].y - right[1].y) < eyeClose and (left[0].y - left[1].y) < eyeClose:
            print("Blink")
            diff = int((clock - ssTime) * 10)
            print('Time diff:' + str(diff))
            if 10 < diff < 20:
                print(screen_y,mid)
                if screen_y>mid[1]:
                    pyautogui.scroll(500)
                if screen_y<=mid[1]:
                    pyautogui.scroll(-500)
                blink=True
                ct = str(datetime.datetime.now())
                im1 = pyautogui.screenshot()
                ct = ct.replace(':', '.')
                # ss_name = r'C:\Users\sande\OneDrive\Pictures\Project Screenshots\screenshot' + ct + '.png'
                # print("Screenshot successfully captured: ", ss_name)
                # im1.save(ss_name)
                # notification.notify(
                #     title="Screenshot saved!",
                #     message=ss_name,
                #     timeout=2  # Display duration in seconds
                # )
            ssTime = clock
            # pyautogui.click(button='right')
            # pyautogui.sleep(1)
    cv2.imshow('Eye Controlled Mouse', frame)
    # cv2.imshow('Eye Controlled Mouse brightened', brightened_frame)
    cv2.waitKey(1)
