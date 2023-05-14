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
