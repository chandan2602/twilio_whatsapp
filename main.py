from fastapi import FastAPI, Form, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from openai import OpenAI
import os
import json
import random
import string
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize clients
twilio_client = Client(os.getenv("ACCOUNT_SID"), os.getenv("AUTH_TOKEN"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NO")

# Store user sessions and data
user_sessions = {}
user_data = {}

def generate_credentials():
    login_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return login_id, password

def save_user_data(phone, data):
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f:
            json.dump({}, f)
    
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    users[phone] = data
    
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

@app.post("/webhook")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    user_message = Body.strip()
    user_phone = From
    
    # Initialize session for new user
    if user_phone not in user_sessions:
        user_sessions[user_phone] = {"step": "greeting", "data": {}}
        ai_reply = "Hello! 👋 I'm Shanghazi, your virtual assistant. Welcome to our service!\n\nMay I know what brings you here today?"
    else:
        session = user_sessions[user_phone]
        step = session["step"]
        
        if step == "greeting":
            session["data"]["purpose"] = user_message
            session["step"] = "ask_name"
            ai_reply = "Thank you for sharing! 😊\n\nTo proceed, could you please provide your full name?"
        
        elif step == "ask_name":
            session["data"]["name"] = user_message
            session["step"] = "ask_mobile"
            ai_reply = f"Nice to meet you, {user_message}! 📱\n\nPlease share your mobile number."
        
        elif step == "ask_mobile":
            session["data"]["mobile"] = user_message
            session["step"] = "ask_email"
            ai_reply = "Great! 📧\n\nLastly, please provide your email address."
        
        elif step == "ask_email":
            session["data"]["email"] = user_message
            login_id, password = generate_credentials()
            
            session["data"]["login_id"] = login_id
            session["data"]["password"] = password
            
            save_user_data(user_phone, session["data"])
            
            ai_reply = f"✅ Registration Complete!\n\nYour credentials:\n🆔 Login ID: {login_id}\n🔑 Password: {password}\n\n🌐 Login here:\nhttps://698f34515845f1a3d193ce26--kncci.netlify.app/\n\nPlease save these details securely. How can I assist you further?"
            
            session["step"] = "completed"
        
        else:
            ai_reply = "How can I help you today? 😊"
    
    resp = MessagingResponse()
    resp.message(ai_reply)
    
    return Response(content=str(resp), media_type="application/xml")

@app.get("/")
async def root():
    return {"status": "WhatsApp Bot Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
