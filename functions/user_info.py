from functions.FirebaseDB import db

def user_info_storage(name,age,height,weight,email,mobile):
    user_id=get_user_id(email)
    data={
        "name":name,
        "age":age,
        "height":height,
        "weight":weight,
        "email":email,
        "mobile":"+91"+mobile
    }
    db.child("users").child(user_id).child("profile").set(data)
    


def get_user_id(email):
 a=email.split('.')
 user_id=a[0]
 return user_id
