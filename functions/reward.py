from functions.FirebaseDB import db

def UpdateReward(reward,userid):
    db.child("users").child(userid).child("profile").update({"reward":reward})

def GetReward(userid):
    try:
     reward=db.child("users").child(userid).child("profile/reward").get().val()
     return reward
    except:
        msg="No reward Selected"
        return msg