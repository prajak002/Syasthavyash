from flask import Flask,render_template,Response,request,redirect,session
from functions.communicate import SendMessage
from functions.pushups import calculate_angle
from functions.FirebaseDB import db
from functions.user_info import user_info_storage
from functions.reward import GetReward,UpdateReward
from functions.BMICalculator import BMI
from functions.getdata import getPlayHistoryCaloryBurnt,getPlayHistorypushups,getPlayHistorysquats,getPlayHistoryFootsteps,getPlayHistoryjumps
from functions.DailyGoalMeter import GoalCalc
import cv2
import mediapipe as mp
import datetime
from sawo import createTemplate,verifyToken
import json
import pyautogui
import random

app=Flask(__name__)
app.secret_key="Thisishackathon"

createTemplate("templates/partials", flask=True)

load = ''
loaded = 0


def setPayload(payload):
    global load
    load = payload


def setLoaded(reset=False):
    global loaded
    if reset:
        loaded = 0
    else:
        loaded += 1

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic



pushups_counter=0
squats_counter=0
footsteps=0
jumps=0

@app.route("/register",methods = ["GET","POST"])
def register():
    if request.method == "POST":
     try:
      name=request.form["name"]
      email=request.form["email"]
      age=request.form["age"]
      height=request.form["height"]
      weight=request.form["weight"]
      mobile=request.form["mobile"]
      user_info_storage(name,age,height,weight,email,mobile)
      return redirect("/authentication")
     except:
      message="Something went wrong! Please try again"
      return render_template("signup.html",message=message)
    return render_template("signup.html")

@app.route("/authentication")
def login_page():
    setLoaded()
    setPayload(load if loaded < 2 else '')
    sawo = {
        "auth_key": "08a4e9aa-24e9-4415-a1da-3598200fa50f",
        "to": "login",
        "identifier": "email"
    }
    return render_template("login.html", sawo=sawo, load=load)
    

@app.route("/login", methods=["POST", "GET"])
def login():
    payload = json.loads(request.data)["payload"]
    setLoaded(True)
    setPayload(payload)
    status = 200 if(verifyToken(payload)) else 404
    user_id = payload['user_id']
    session['usr'] = user_id
    email=payload['identifier']
    all_users = db.child("users").get()
    for user in all_users.each():
     user_id=user.key()
     path="users/"+user_id+"/profile/email"
     user_email=db.child(path).get().val()
     if (user_email==email) :
      db.child("users").child(user_id).child("profile").update({"session":session['usr']})
    return {"status": status}


@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")

@app.route("/select-reward",methods=["GET","POST"])
def rewards():
        session['usr']
        all_users = db.child("users").get()
        for user in all_users.each():
         user_id=user.key()
         path="users/"+user_id+"/profile/session"
         user_session=db.child(path).get().val()
         if (user_session==session['usr']) :
          user_ID=user_id
        if request.method == "POST":
            reward=request.form["reward"]
            UpdateReward(reward,user_ID)
            return redirect("/dashboard") 
        return render_template("reward.html")

@app.route("/dashboard")
def dashboard():
     try:
        session['usr']
        all_users = db.child("users").get()
        for user in all_users.each():
         user_id=user.key()
         path="users/"+user_id+"/profile/session"
         user_session=db.child(path).get().val()
         if (user_session==session['usr']) :
          user_name=db.child("users").child(user_id).child("profile").child("name").get().val()
          user_height=db.child("users").child(user_id).child("profile").child("height").get().val()
          user_weight=db.child("users").child(user_id).child("profile").child("weight").get().val()
          user_age=db.child("users").child(user_id).child("profile").child("age").get().val()
          user_phn=db.child("users").child(user_id).child("profile").child("mobile").get().val()
          user_ID=user_id
        user_bmi,user_health_status=BMI(user_height,user_weight)
        reward_selected=GetReward(user_ID)
        now = datetime.datetime.now().ctime().split()
        present_date=now[1]+" "+now[2]
        if db.child("users").child(user_ID).child("history").child(present_date).get().val() is None:
            goal=400+random.randint(0,100)
            db.child("users").child(user_ID).child("profile").update({"present_day_goal":goal})
            body="Hello!"+user_name+",We hope you are fit and fine.Today's Fitness Goal is"+str(goal)+" Calories"
            SendMessage(body,user_phn)
        if db.child("users").child(user_ID).child("history").get().val() is not None:
         graph_data_pushups=getPlayHistorypushups(user_ID)
         graph_data_squats=getPlayHistorysquats(user_ID)
         graph_data_footsteps=getPlayHistoryFootsteps(user_ID)
         graph_data_jumps=getPlayHistoryjumps(user_ID)
         graph_data_calories=getPlayHistoryCaloryBurnt(user_ID)
         present_day_goal=db.child("users").child(user_id).child("profile").child("present_day_goal").get().val()
         present_day_goal=int(present_day_goal)
         goalmeter=str(GoalCalc(user_ID,present_day_goal))
         return render_template("dashboard.html",name=user_name,reward=reward_selected,age=user_age,bmi=user_bmi,health_status=user_health_status,
                                goal=present_day_goal,dailyGoal=goalmeter,graph_data_pushups=graph_data_pushups,graph_data_squats=graph_data_squats,
                                graph_data_footsteps=graph_data_footsteps,graph_data_jumps=graph_data_jumps,graph_data_calories=graph_data_calories)
        else:
         present_day_goal=db.child("users").child(user_id).child("profile").child("present_day_goal").get().val()
         present_day_goal=int(present_day_goal)
         goalmeter=str(GoalCalc(user_ID,present_day_goal))
         return render_template("dashboard.html",name=user_name,reward=reward_selected,age=user_age,bmi=user_bmi,health_status=user_health_status,
                                 message="No Records Found",dailyGoal=goalmeter)
      except:
          return redirect("/authentication")

@app.route("/")
def main():
    return render_template("index.html")

@app.route('/pushups-portal',methods=["GET","POST"])
def pushups_index():
  try:
        session['usr']
        if request.method == "POST":
         return redirect('/senddatapushups')
        return render_template('pushups.html')
  except:
      return redirect('/authentication')

@app.route('/senddatapushups')
def SendData():
  try:
        session['usr']
        all_users = db.child("users").get()
        for user in all_users.each():
         user_id=user.key()
         path="users/"+user_id+"/profile/session"
         user_session=db.child(path).get().val()
         if (user_session==session['usr']) :
          user_ID=user_id
        now = datetime.datetime.now().ctime().split()
        present_date=now[1]+" "+now[2]
        if db.child("users").child(user_ID).child("history").child(present_date).child("pushups").get().val() is not None:
         present_data=db.child("users").child(user_ID).child("history").child(present_date).child("pushups").get().val()
         present_data=int(present_data)
         updated_data=present_data+pushups_counter
         db.child("users").child(user_ID).child("history").child(present_date).update({"pushups":updated_data})
        else:
          db.child("users").child(user_ID).child("history").child(present_date).update({"pushups":pushups_counter})  

        if  db.child("users").child(user_ID).child("history").child(present_date).child("squats").get().val() is None:
             db.child("users").child(user_ID).child("history").child(present_date).update({"squats":int("0")})
        if  db.child("users").child(user_ID).child("history").child(present_date).child("footsteps").get().val() is None:
             db.child("users").child(user_ID).child("history").child(present_date).update({"footsteps":int("0")})
        if  db.child("users").child(user_ID).child("history").child(present_date).child("jumps").get().val() is None:
             db.child("users").child(user_ID).child("history").child(present_date).update({"jumps":int("0")})
        return redirect('/dashboard')
  except:
     return redirect('/authentication')

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/authentication")

@app.route('/videopushups')
def videopushups():
    return Response(pushups(),mimetype='multipart/x-mixed-replace; boundary=frame')

def pushups():
 global pushups_counter
 pushups_counter=0
 pushups_stage=None
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
            left_elbow_x_coordinate = results.pose_landmarks.landmark[13].x
            left_elbow_y_coordinate = results.pose_landmarks.landmark[13].y
            right_elbow_x_coordinate = results.pose_landmarks.landmark[14].x
            right_elbow_y_coordinate = results.pose_landmarks.landmark[14].y
            left_wrist_x_coordinate = results.pose_landmarks.landmark[15].x
            left_wrist_y_coordinate = results.pose_landmarks.landmark[15].y
            right_wrist_x_coordinate = results.pose_landmarks.landmark[16].x
            right_wrist_y_coordinate = results.pose_landmarks.landmark[16].y

            #Tuples
            right_shoulder=[right_shoulder_x_coordinate,right_shoulder_y_coordinate]
            left_shoulder=[left_shoulder_x_coordinate,left_shoulder_y_coordinate]
            right_elbow=[right_elbow_x_coordinate,right_elbow_y_coordinate]
            left_elbow=[left_elbow_x_coordinate,left_elbow_y_coordinate]
            right_wrist=[right_wrist_x_coordinate,right_wrist_y_coordinate]
            left_wrist=[left_wrist_x_coordinate,left_wrist_y_coordinate]

            #Calculation of Angles
            left_hand_angle = calculate_angle(right_shoulder,right_elbow,right_wrist)
            right_hand_angle = calculate_angle(left_shoulder,left_elbow,left_wrist)
            #Visualizing Angles

            # Curl counter logic
            if right_hand_angle > 170 :
                pushups_stage = "up"
            if right_hand_angle > 165 and right_hand_angle < 170 and pushups_stage =='up':
                pushups_stage="down"
                pushups_counter +=1
        except:
            cv2.putText(image, "Please come into the camera", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
        finally:
            # Render curl counter
            # Setup status box
            cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
        
        # Rep data
            cv2.putText(image, 'REPS', (15,12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            cv2.putText(image, str(pushups_counter), 
                    (10,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        
        # Stage data
            cv2.putText(image, 'STAGE', (65,12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            cv2.putText(image, pushups_stage, 
                    (60,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        
            # Draw landmark annotation on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
           
            mp_drawing.draw_landmarks(
               image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
               mp_drawing.DrawingSpec(color=(254, 230, 158), thickness=4, circle_radius=4),
               mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=4, circle_radius=2))


        ret,buffer=cv2.imencode('.jpg',image)
        image=buffer.tobytes()
        yield(b'--frame\r\n' 
                     b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

        if cv2.waitKey(0) == 27 & 0xFF == ord('q'):
            break
 cap.release()
 cv2.destroyAllWindows()

def squats():
  cap = cv2.VideoCapture(0)
  global squats_counter
  squats_counter=0
  squats_stage=None
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
            

            # Squats counter logic
            if right_side_angle > 170:
                squats_stage = "up"
            if right_side_angle < 125 and squats_stage =='up':
                squats_stage="down"
                squats_counter +=1
                print(squats_counter)
        except:
            cv2.putText(image, "Please come into the camera", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
        finally:
            # Render curl counter
            # Setup status box
            cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
        
        # Rep data
            cv2.putText(image, 'SQUATS', (15,12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            cv2.putText(image, str(squats_counter), 
                    (10,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        
        # Stage data
            cv2.putText(image, 'STAGE', (65,12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            cv2.putText(image, squats_stage, 
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
        ret,buffer=cv2.imencode('.jpg',image)
        image=buffer.tobytes()
        yield(b'--frame\r\n' 
                     b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
        if cv2.waitKey(10) == 27 & 0xFF == ord('q'):
            break
  cap.release()
  cv2.destroyAllWindows()

@app.route('/squats-portal',methods=["GET","POST"])
def squats_index():
  try:
        session['usr']
        if request.method == "POST":
         return redirect('/senddatasquats')
        return render_template('squats.html')
  except:
      return redirect('/authentication')

@app.route('/senddatasquats')
def SendDataSquats():
 try:
        session['usr']
        all_users = db.child("users").get()
        for user in all_users.each():
         user_id=user.key()
         path="users/"+user_id+"/profile/session"
         user_session=db.child(path).get().val()
         if (user_session==session['usr']) :
          user_ID=user_id
        now = datetime.datetime.now().ctime().split()
        present_date=now[1]+" "+now[2]
        if db.child("users").child(user_ID).child("history").child(present_date).child("squats").get().val() is not None:
         present_data=db.child("users").child(user_ID).child("history").child(present_date).child("squats").get().val()
         present_data=int(present_data)
         updated_data=present_data+squats_counter
         db.child("users").child(user_ID).child("history").child(present_date).update({"squats":updated_data})
        else:
          db.child("users").child(user_ID).child("history").child(present_date).update({"squats":squats_counter})  

        if  db.child("users").child(user_ID).child("history").child(present_date).child("pushups").get().val() is None:
             db.child("users").child(user_ID).child("history").child(present_date).update({"pushups":int("0")})
        if  db.child("users").child(user_ID).child("history").child(present_date).child("footsteps").get().val() is None:
             db.child("users").child(user_ID).child("history").child(present_date).update({"footsteps":int("0")})
        if  db.child("users").child(user_ID).child("history").child(present_date).child("jumps").get().val() is None:
             db.child("users").child(user_ID).child("history").child(present_date).update({"jumps":int("0")})
        return redirect('/dashboard')
 except:
     return redirect('/authentication')

@app.route('/videosquats')
def videosquats():
    return Response(squats(),mimetype='multipart/x-mixed-replace; boundary=frame')


def running():
 lane = 'middle'

 # For webcam input:
 cap = cv2.VideoCapture(0)
 loop_counter = 0
 going_left = 0
 going_right = 0
 global footsteps
 global jumps
 footsteps = 0
 jumps = 0


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
              footsteps += 1
              cv2.putText(image, "RUNNING", (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            else:
                pyautogui.keyUp('w')

            # Jump
            if left_waist_y_coordinate < waist_line and right_waist_y_coordinate < waist_line:
                #print("Jump")
                pyautogui.keyDown('w')
                pyautogui.keyDown('space')
                pyautogui.keyUp('w')
                jumps += 1
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

        ret,buffer=cv2.imencode('.jpg',image)
        image=buffer.tobytes()
        yield(b'--frame\r\n' 
                     b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
        if cv2.waitKey(5) & 0xFF == 27:
            break
        loop_counter += 1

 cap.release()

@app.route('/videorunning')
def videorunning():
    return Response(running(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/running-portal',methods=["POST","GET"])
def run_index():
 try:
     session['usr']
     if request.method == "POST":
         return redirect('/senddatarunning')
     return render_template('run.html')
 except:
     return redirect('/authentication')


@app.route('/senddatarunning')
def SendDataRunning():
  try:
        session['usr']
        all_users = db.child("users").get()
        for user in all_users.each():
         user_id=user.key()
         path="users/"+user_id+"/profile/session"
         user_session=db.child(path).get().val()
         if (user_session==session['usr']) :
          user_ID=user_id
        now = datetime.datetime.now().ctime().split()
        present_date=now[1]+" "+now[2]
        if db.child("users").child(user_ID).child("history").child(present_date).child("footsteps").get().val() is not None:
         present_data_footsteps=db.child("users").child(user_ID).child("history").child(present_date).child("footsteps").get().val()
         present_data_footsteps=int(present_data_footsteps)
         updated_data_footsteps=present_data_footsteps+footsteps
         present_data_jumps=db.child("users").child(user_ID).child("history").child(present_date).child("jumps").get().val()
         present_data_jumps=int(present_data_jumps)
         updated_data_jumps=present_data_jumps+jumps
         print(footsteps)
         db.child("users").child(user_ID).child("history").child(present_date).update({"footsteps":updated_data_footsteps})
         db.child("users").child(user_ID).child("history").child(present_date).update({"jumps":updated_data_jumps})
        else:
          db.child("users").child(user_ID).child("history").child(present_date).update({"footsteps":footsteps}) 
          db.child("users").child(user_ID).child("history").child(present_date).update({"jumps":jumps})  

        if  db.child("users").child(user_ID).child("history").child(present_date).child("squats").get().val() is None:
             db.child("users").child(user_ID).child("history").child(present_date).update({"squats":int("0")})
        if  db.child("users").child(user_ID).child("history").child(present_date).child("pushups").get().val() is None:
             db.child("users").child(user_ID).child("history").child(present_date).update({"pushups":int("0")})
        return redirect('/dashboard')
  except:
     return redirect('/authentication')

@app.route("/positionlocator")
def posplay():
    return render_template("positionlocator.html")

def positionlocator():

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
            # If loading a video, use 'break' instead of 'continue'.ww
            break
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
              cv2.putText(image, "RUNNING", (200, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

            # Jump
            if left_waist_y_coordinate <= waist_line and right_waist_y_coordinate <= waist_line:
                #print("Jump")
                cv2.putText(image, "JUMP", (200, 350), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            # Go left
            if right_shoulder_x_coordinate < left_line:
                print(right_shoulder_x_coordinate)

                if lane != 'left':
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
            # Go right
            elif left_shoulder_x_coordinate > right_line:
                print(left_shoulder_x_coordinate)

                if lane != 'right':
                    going_right += 1
                    cv2.putText(image, str(going_right), (412, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                    lane = 'right'
                    # cv2.line(img=image, pt1=(412, 100), pt2=(412, 100), color=(255, 0, 0), thickness=50, lineType=8,
                    #         shift=0)
                else:
                    cv2.putText(image, str(going_right), (412, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                    cv2.line(img=image, pt1=(412, 100), pt2=(412, 100), color=(255, 0, 0), thickness=50, lineType=8,
                             shift=0)
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
                    cv2.line(img=image, pt1=(240, 200), pt2=(240, 200), color=(255, 0, 0), thickness=50, lineType=8,
                             shift=0)
                    lane='middle'
                elif lane == 'right':
                    print("left")
                    cv2.line(img=image, pt1=(270, 200), pt2=(270, 200), color=(255, 0, 0), thickness=50, lineType=8,
                             shift=0)
                    lane='middle'
                cv2.putText(image, "MIDDLE", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
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
            mp_drawing.draw_landmarks(
               image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            cv2.putText(image, str(going_left), (235, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            # cv2.line(img=image, pt1=(k*256, 200), pt2=(k*256, 200), color=(255, 0, 0), thickness=20, lineType=8, shift=0)
        ret,buffer=cv2.imencode('.jpg',image)
        image=buffer.tobytes()
        yield(b'--frame\r\n' 
                     b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
        if cv2.waitKey(5) & 0xFF == 27:
            break
        loop_counter += 1

 cap.release() 

@app.route('/videoposition')
def videoposition():
    return Response(positionlocator(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(debug=True)
