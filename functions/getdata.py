from functions.FirebaseDB import db
def getPlayHistorypushups(user_id):
        a=[]
        users=db.child("users").child(user_id).child("history").get()
        for user in users.each():
            date_of_play=user.key()
            pushups=db.child("users").child(user_id).child("history").child(date_of_play).child("pushups").get().val()
            data=[date_of_play,pushups]
            a.append(data)
        return a

def getPlayHistorysquats(user_id):
        a=[]
        users=db.child("users").child(user_id).child("history").get()
        for user in users.each():
            date_of_play=user.key()
            squats=db.child("users").child(user_id).child("history").child(date_of_play).child("squats").get().val()
            data=[date_of_play,squats]
            a.append(data)
        return a

def getPlayHistoryFootsteps(user_id):
        a=[]
        users=db.child("users").child(user_id).child("history").get()
        for user in users.each():
            date_of_play=user.key()
            footsteps=db.child("users").child(user_id).child("history").child(date_of_play).child("footsteps").get().val()
            data=[date_of_play,footsteps]
            a.append(data)
        return a

def getPlayHistoryjumps(user_id):
        a=[]
        users=db.child("users").child(user_id).child("history").get()
        for user in users.each():
            date_of_play=user.key()
            jumps=db.child("users").child(user_id).child("history").child(date_of_play).child("jumps").get().val()
            data=[date_of_play,jumps]
            a.append(data)
        return a

def getPlayHistoryCaloryBurnt(user_id):
        a=[]
        users=db.child("users").child(user_id).child("history").get()
        for user in users.each():
            date_of_play=user.key()
            pushups=db.child("users").child(user_id).child("history").child(date_of_play).child("pushups").get().val()
            squats=db.child("users").child(user_id).child("history").child(date_of_play).child("squats").get().val()
            footsteps=db.child("users").child(user_id).child("history").child(date_of_play).child("footsteps").get().val()
            jumps=db.child("users").child(user_id).child("history").child(date_of_play).child("jumps").get().val()
            calories_burnt_data=CaloriesBurnt(pushups,squats,footsteps,jumps)
            data=[date_of_play,calories_burnt_data]
            a.append(data)
        return a

def CaloriesBurnt(pushups,squats,footsteps,jumps):
    pushups=int(pushups)
    squats=int(squats)
    footsteps=int(footsteps)
    jumps=int(jumps)
    burntcalorie=(0.75*pushups) + (0.55 * squats) + (0.10 * footsteps) + (0.20 * jumps)
    burntcalorie=round(burntcalorie)
    return burntcalorie