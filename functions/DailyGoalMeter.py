import datetime
from functions.getdata import CaloriesBurnt
from functions.FirebaseDB import db


now = datetime.datetime.now().ctime().split()
present_date=now[1]+" "+now[2]


def GoalCalc(user_id,goal):
    try:
     pushups=db.child("users/"+user_id+"/history/"+present_date+"/pushups").get().val()
     squats=db.child("users/"+user_id+"/history/"+present_date+"/squats").get().val()
     footsteps=db.child("users/"+user_id+"/history/"+present_date+"/footsteps").get().val()
     jumps=db.child("users/"+user_id+"/history/"+present_date+"/jumps").get().val()
     burntcalories=CaloriesBurnt(pushups,squats,footsteps,jumps)
     goal=int(goal)
     burntpercent=(burntcalories/goal)*100
     burntpercent=round(burntpercent)
     if burntpercent < 100:
         return burntpercent
     else:
         return 100
    except:
        return 0
