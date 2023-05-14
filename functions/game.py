import cv2
import mediapipe as mp
import pyautogui
import datetime

now = datetime.datetime.now().ctime().split()
present_date=now[1]+" "+now[2]

# if db.child("users").child(mac_id).child("history").child(present_date).get().val() is not None:
#  footsteps = db.child("users").child(mac_id).child("history").child(present_date).child("footsteps").get().val()
#  footsteps=int(footsteps)
#  jumps = db.child("users").child(mac_id).child("history").child(present_date).child("jumps").get().val()
#  jumps=int(jumps)
# else:
#     db.child("users").child(mac_id).child("history").child(present_date).update({"footsteps":0})
#     footsteps= db.child("users").child(mac_id).child("history").child(present_date).child("footsteps").get().val()
#     footsteps=int(footsteps)
#     db.child("users").child(mac_id).child("history").child(present_date).update({"jumps":0})
#     jumps = db.child("users").child(mac_id).child("history").child(present_date).child("jumps").get().val()
#     jumps=int(jumps)

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
lane = 'middle'

# For webcam input:
cap = cv2.VideoCapture(0)
loop_counter = 0
going_left = 0
going_right = 0



with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue
        def change_res(width, height):
          cap.set(3, width)
          cap.set(4, height)

        change_res(640,640)
        # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False

        results = holistic.process(image)
        # For center
        # cv2.line(img=image, pt1=(256, 200), pt2=(256, 200), color=(0, 0, 255), thickness=20, lineType=8, shift=0)
        # For left line
        cv2.line(img=image, pt1=(215, 0), pt2=(215, 512), color=(0, 255, 0), thickness=2, lineType=8, shift=0)
        # For left line bound
        cv2.line(img=image, pt1=(5, 0), pt2=(5, 512), color=(0, 255, 0), thickness=2, lineType=8, shift=0)
        # For right line
        cv2.line(img=image, pt1=(425, 0), pt2=(425, 512), color=(0, 255, 0), thickness=2, lineType=8, shift=0)
        # For right line bound
        cv2.line(img=image, pt1=(635, 0), pt2=(635, 512), color=(0, 255, 0), thickness=2, lineType=8, shift=0)
        # For waistline
        cv2.line(img=image, pt1=(215, 350), pt2=(425, 350), color=(0, 0, 255), thickness=2, lineType=8, shift=0)

        # For Running

        cv2.line(img=image, pt1=(0, 450), pt2=(640, 450), color=(0, 0, 255), thickness=2, lineType=8, shift=0)
        
        #cv2.line(img=image, pt1=(175, 400), pt2=(337, 400), color=(0, 0, 255), thickness=2, lineType=8, shift=0)

        left_line = 1 / 512 * 215
        right_line = 1 / 512 * 425  # 0.658
        waist_line = (1 / 512 * 300)
        running_line = (1/512 * 452)
        try:
            right_shoulder_x_coordinate = results.pose_landmarks.landmark[11].x
            left_shoulder_x_coordinate = results.pose_landmarks.landmark[12].x
            left_waist_y_coordinate = results.pose_landmarks.landmark[24].y
            right_waist_y_coordinate = results.pose_landmarks.landmark[23].y
            right_knee_y_coordinate =  results.pose_landmarks.landmark[25].y
            right_knee_x_coordinate =  results.pose_landmarks.landmark[25].x
            left_knee_y_coordinate =  results.pose_landmarks.landmark[26].y
            left_knee_x_coordinate =  results.pose_landmarks.landmark[26].x
            # cv2.putText(image, str(left_waist_y_coordinate), (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
            #Running
            if right_knee_y_coordinate<=running_line or left_knee_y_coordinate<=running_line:
              pyautogui.keyDown('w')
            #   footsteps += 1
              cv2.putText(image, "RUNNING", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            else:
                pyautogui.keyUp('w')

            # Jump
            if left_waist_y_coordinate < waist_line and right_waist_y_coordinate < waist_line:
                #print("Jump")
                pyautogui.keyDown('w')
                pyautogui.keyDown('space')
                pyautogui.keyUp('w')
                # jumps += 1
                cv2.putText(image, "JUMP", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            else:
                pyautogui.keyUp('space')
            # Go left
            if right_shoulder_x_coordinate < left_line:
                print(right_shoulder_x_coordinate)

                if lane != 'left':
                    pyautogui.keyDown('a')
                    going_left += 1
                    cv2.putText(image, str(going_left), (82, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                    lane = 'left'
                    #cv2.line(img=image, pt1=(82, 100), pt2=(82, 100), color=(255, 0, 0), thickness=50, lineType=8,
                    #         shift=0)
                else:
                    cv2.putText(image, str(going_left), (82, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                    cv2.line(img=image, pt1=(82, 100), pt2=(82, 100), color=(255, 0, 0), thickness=50, lineType=8,
                             shift=0)
                cv2.putText(image, "LEFT", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                pyautogui.keyUp('a')
            # Go right
            elif left_shoulder_x_coordinate > right_line:
                print(left_shoulder_x_coordinate)

                if lane != 'right':
                    pyautogui.keyDown('d')
                    going_right += 1
                    cv2.putText(image, str(going_right), (412, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                    lane = 'right'
                    # cv2.line(img=image, pt1=(412, 100), pt2=(412, 100), color=(255, 0, 0), thickness=50, lineType=8,
                    #         shift=0)
                else:
                    cv2.putText(image, str(going_right), (412, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                    cv2.line(img=image, pt1=(412, 100), pt2=(412, 100), color=(255, 0, 0), thickness=50, lineType=8,
                             shift=0)
                pyautogui.keyUp('d')
                cv2.putText(image, "RIGHT", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            # Go down
            #elif left_waist_y_coordinate > waist_line + 0.3 and right_waist_y_coordinate > waist_line + 0.3:
                #print("Down")
                #pyautogui.press('down')
                #cv2.putText(image, "DOWN", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            # Go middle
            elif left_shoulder_x_coordinate >= left_line and right_shoulder_x_coordinate <= right_line:
                if lane == 'left':
                    print("right")
                    pyautogui.keyDown('d')
                    cv2.line(img=image, pt1=(240, 200), pt2=(240, 200), color=(255, 0, 0), thickness=50, lineType=8,
                             shift=0)
                    lane='middle'
                elif lane == 'right':
                    print("left")
                    pyautogui.press('a')
                    cv2.line(img=image, pt1=(270, 200), pt2=(270, 200), color=(255, 0, 0), thickness=50, lineType=8,
                             shift=0)
                    lane='middle'
                cv2.putText(image, "MIDDLE", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            # db.child("users").child(mac_id).child("history").child(present_date).update({"footsteps":footsteps})
            # db.child("users").child(mac_id).child("history").child(present_date).update({"jumps":jumps})
        except:
            cv2.putText(image, "Please come into the camera", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
        finally:
            # Draw landmark annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            # mp_drawing.draw_landmarks(
            #    image, results.face_landmarks, mp_holistic.FACE_CONNECTIONS)
            mp_drawing.draw_landmarks(
                image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(
                image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
            # mp_drawing.draw_landmarks(
            #    image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            cv2.putText(image, str(going_left), (235, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            cv2.imshow('MediaPipe Holistic', image)
            # cv2.line(img=image, pt1=(k*256, 200), pt2=(k*256, 200), color=(255, 0, 0), thickness=20, lineType=8, shift=0)
            
        if cv2.waitKey(5) & 0xFF == 27:
            break
        loop_counter += 1
cap.release()