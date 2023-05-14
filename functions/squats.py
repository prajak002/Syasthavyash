import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

counter = 0 
stage = None
def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle

# For webcam input:
cap = cv2.VideoCapture(0)

with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
      
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        
        image.flags.writeable = False

        results = holistic.process(image)
        try:
            #Landmarks Point Co-ordinates
            right_shoulder_x_coordinate = results.pose_landmarks.landmark[12].x
            right_shoulder_y_coordinate = results.pose_landmarks.landmark[12].y
            left_shoulder_x_coordinate = results.pose_landmarks.landmark[11].x
            left_shoulder_y_coordinate = results.pose_landmarks.landmark[11].y
            left_waist_x_coordinate = results.pose_landmarks.landmark[23].x
            left_waist_y_coordinate = results.pose_landmarks.landmark[23].y
            right_waist_x_coordinate = results.pose_landmarks.landmark[24].x
            right_waist_y_coordinate = results.pose_landmarks.landmark[24].y
            left_knee_x_coordinate = results.pose_landmarks.landmark[25].x
            left_knee_y_coordinate = results.pose_landmarks.landmark[25].y
            right_knee_x_coordinate = results.pose_landmarks.landmark[26].x
            right_knee_y_coordinate = results.pose_landmarks.landmark[26].y

            #Tuples
            right_shoulder=[right_shoulder_x_coordinate,right_shoulder_y_coordinate]
            left_shoulder=[left_shoulder_x_coordinate,left_shoulder_y_coordinate]
            right_waist=[right_waist_x_coordinate,right_waist_y_coordinate]
            left_waist=[left_waist_x_coordinate,left_waist_y_coordinate]
            right_knee=[right_knee_x_coordinate,right_knee_y_coordinate]
            left_knee=[left_knee_x_coordinate,left_knee_y_coordinate]

            #Calculation of Angles
            right_side_angle = calculate_angle(right_shoulder,right_waist,right_knee)
            left_side_angle = calculate_angle(left_shoulder,left_waist,left_knee)
            
            #Visualizing Angles
            cv2.putText(image, str(right_side_angle), 
                           tuple(np.multiply(right_waist, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )

            cv2.putText(image, str(left_side_angle), 
                           tuple(np.multiply(left_waist, [640, 480]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )
            # Squats counter logic
            if right_side_angle > 170:
                stage = "up"
            if right_side_angle < 125 and stage =='up':
                stage="down"
                counter +=1
                print(counter)
        except:
            cv2.putText(image, "Please come into the camera", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
        finally:
            # Render curl counter
            # Setup status box
            cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
        
        # Rep data
            cv2.putText(image, 'SQUATS', (15,12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter), 
                    (10,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        
        # Stage data
            cv2.putText(image, 'STAGE', (65,12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            cv2.putText(image, stage, 
                    (60,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        
            # Draw landmark annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            # mp_drawing.draw_landmarks(
            #    image, results.face_landmarks, mp_holistic.FACE_CONNECTIONS)
            mp_drawing.draw_landmarks(
               image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
               mp_drawing.DrawingSpec(color=(254, 230, 158), thickness=4, circle_radius=4),
               mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=4, circle_radius=2))
            cv2.imshow('MediaPipe Holistic', image)
        if cv2.waitKey(10) == 27 & 0xFF == ord('q'):
            break
cap.release()
cv2.destroyAllWindows()