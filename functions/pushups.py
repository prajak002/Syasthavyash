import numpy as np
import datetime
import pyrebase

config={
  "apiKey": "AIzaSyDGSmAdvgNaTLznfZ3FjwxuoN4pY6s2G-Y",
  "authDomain": "fitai-acce0.firebaseapp.com",
  "projectId": "fitai-acce0",
  "databaseURL":"https://fitai-acce0-default-rtdb.firebaseio.com/",
  "storageBucket": "fitai-acce0.appspot.com",
  "messagingSenderId": "995820706549",
  "appId": "1:995820706549:web:b4127e8be5170b7b5603bc"
}

firebase=pyrebase.initialize_app(config)
db=firebase.database()

def SendData(counter,user_id):
  now = datetime.datetime.now().ctime().split()
  present_date=now[1]+" "+now[2]
  db.child("users").child(user_id).child("history").child("pushups").child(present_date).update({"counts":counter})

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle

