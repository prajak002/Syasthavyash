from twilio.rest import Client 
 
account_sid = 'AC0d30f84270b3689417dacb75d48fbd1b' 
auth_token = '7aedc4aaf0c30d3ec769839d42443212' 
client = Client(account_sid, auth_token) 
def SendMessage(body,phn_number):
 message = client.messages.create(  
                              messaging_service_sid='MG7b472457a8d1aaa499a676e8bbc6f3e1', 
                              body=body,      
                              to=phn_number 
                          ) 
 print (message.sid)
