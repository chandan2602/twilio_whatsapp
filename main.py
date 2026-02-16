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

def save_user_data(phone, data):
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f:
            json.dump({}, f)
    
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    users[phone] = data
    
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=2)

@app.post("/")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    user_message = Body.strip().lower()
    user_phone = From
    
    # Initialize session for new user
    if user_phone not in user_sessions:
        user_sessions[user_phone] = {"step": "greeting", "data": {}}
        ai_reply = "Welcome to KNCCI.\n\nThis is a curated India-Kenya business introduction network designed for serious operators, institutional players, and long-term partnerships.\n\nI'll guide you through a few questions to understand your positioning, intent, and expansion priorities. Our objective is not volume — it is precision. Every profile is reviewed carefully before introductions are made.\n\nWhen you're ready, please say 'Start'."
    else:
        session = user_sessions[user_phone]
        step = session["step"]
        
        if step == "greeting":
            if "start" in user_message or "yes" in user_message or "begin" in user_message:
                session["step"] = "ask_full_name"
                ai_reply = "Thank you. Let's begin with identity and leadership context.\n\nMay I have your full name?"
            else:
                ai_reply = "When you're ready to begin, please say 'Start'."
        
        elif step == "ask_full_name":
            session["data"]["full_name"] = Body.strip()
            first_name = Body.strip().split()[0] if Body.strip() else "there"
            session["data"]["first_name"] = first_name
            session["step"] = "ask_company_name"
            ai_reply = f"Thank you, {first_name}.\n\nKindly confirm the name of your organization."
        
        elif step == "ask_company_name":
            session["data"]["company_name"] = Body.strip()
            session["step"] = "ask_designation"
            ai_reply = "Understood.\n\nWhat is your role within the organization?\n\nIn one or two sentences, please share the mandate you hold and the decisions you influence."
        
        elif step == "ask_designation":
            session["data"]["designation"] = Body.strip()
            session["step"] = "ask_country"
            ai_reply = "Thank you.\n\nTo contextualize your network relevance — which country are you currently operating from?\n\nPlease choose:\n1. India\n2. Kenya\n3. Other"
        
        elif step == "ask_country":
            country_map = {"1": "India", "2": "Kenya", "3": "Other"}
            country = country_map.get(user_message, Body.strip())
            session["data"]["country"] = country
            session["step"] = "ask_city"
            ai_reply = "And your primary city of operations?"
        
        elif step == "ask_city":
            session["data"]["city"] = Body.strip()
            session["step"] = "ask_industry"
            ai_reply = "Noted.\n\nNow, at a strategic level — which industry defines your core business activity?\n\nPlease choose:\n1. Technology\n2. Manufacturing\n3. Agriculture\n4. Healthcare\n5. Education\n6. Logistics\n7. Finance\n8. Energy\n9. Others"
        
        elif step == "ask_industry":
            industry_map = {
                "1": "Technology",
                "2": "Manufacturing",
                "3": "Agriculture",
                "4": "Healthcare",
                "5": "Education",
                "6": "Logistics",
                "7": "Finance",
                "8": "Energy",
                "9": "Others"
            }
            industry = industry_map.get(user_message, Body.strip())
            session["data"]["industry"] = industry
            session["step"] = "ask_business_description"
            
            if industry in ["Technology", "1"]:
                ai_reply = f"{industry} is a wide spectrum.\n\nTo ensure we curate relevant introductions, please briefly describe:\n\n• Your primary offerings (products, platforms, or services)\n• Target customers or markets\n• Current growth priorities\n\nClarity here determines the quality of introductions."
            else:
                ai_reply = f"Understood — {industry}.\n\nTo ensure we curate relevant introductions, please briefly describe:\n\n• Your primary offerings\n• Target customers or markets\n• Current growth priorities\n\nClarity here determines the quality of introductions."
        
        elif step == "ask_business_description":
            session["data"]["business_description"] = Body.strip()
            session["step"] = "ask_company_stage"
            ai_reply = "Thank you.\n\nHow would you classify your company's current stage?\n\nPlease choose:\n1. Startup\n2. Growth Stage\n3. SME\n4. Enterprise\n5. Institution / Government"
        
        elif step == "ask_company_stage":
            stage_map = {
                "1": "Startup",
                "2": "Growth Stage",
                "3": "SME",
                "4": "Enterprise",
                "5": "Institution / Government"
            }
            stage = stage_map.get(user_message, Body.strip())
            session["data"]["company_stage"] = stage
            session["step"] = "ask_partnership_type"
            
            if stage in ["Enterprise", "4"]:
                ai_reply = "Understood.\n\nAt the enterprise level, partnerships must be deliberate.\n\nWhat type of engagement are you actively seeking within the India-Kenya corridor?\n\nPlease choose:\n1. Distributor\n2. Investor\n3. Technology Partner\n4. Local Business Partner\n5. Strategic Partnership\n6. Institutional Collaboration\n7. Market Expansion"
            elif stage in ["Institution / Government", "5"]:
                ai_reply = "Noted.\n\nInstitutional alignment requires precision.\n\nWhat type of engagement are you actively seeking within the India-Kenya corridor?\n\nPlease choose:\n1. Distributor\n2. Investor\n3. Technology Partner\n4. Local Business Partner\n5. Strategic Partnership\n6. Institutional Collaboration\n7. Market Expansion"
            else:
                ai_reply = "Understood.\n\nWhat type of engagement are you actively seeking within the India-Kenya corridor?\n\nPlease choose:\n1. Distributor\n2. Investor\n3. Technology Partner\n4. Local Business Partner\n5. Strategic Partnership\n6. Institutional Collaboration\n7. Market Expansion"
        
        elif step == "ask_partnership_type":
            partnership_map = {
                "1": "Distributor",
                "2": "Investor",
                "3": "Technology Partner",
                "4": "Local Business Partner",
                "5": "Strategic Partnership",
                "6": "Institutional Collaboration",
                "7": "Market Expansion"
            }
            partnership = partnership_map.get(user_message, Body.strip())
            session["data"]["partnership_type"] = partnership
            session["step"] = "ask_target_market"
            ai_reply = "Appreciated.\n\nWhich market are you targeting?\n\nPlease choose:\n1. India\n2. Kenya\n3. Both"
        
        elif step == "ask_target_market":
            market_map = {"1": "India", "2": "Kenya", "3": "Both"}
            market = market_map.get(user_message, Body.strip())
            session["data"]["target_market"] = market
            session["step"] = "ask_profile_link"
            ai_reply = "Noted.\n\nFor verification and context, please share your company website, LinkedIn profile, or institutional profile link."
        
        elif step == "ask_profile_link":
            session["data"]["profile_link"] = Body.strip()
            session["step"] = "ask_email"
            ai_reply = "Thank you.\n\nFinally, please provide your official email address for verification and future correspondence."
        
        elif step == "ask_email":
            session["data"]["email"] = Body.strip()
            save_user_data(user_phone, session["data"])
            
            first_name = session["data"].get("first_name", "")
            ai_reply = f"Thank you, {first_name}.\n\nYour application has been submitted successfully.\n\nOur team will review your profile with care. You will be notified once your profile is vetted and relevant introductions become available.\n\nWe prioritize quality over speed — expect to hear from us within 3-5 business days."
            session["step"] = "completed"
        
        else:
            # Completed or general queries
            if "status" in user_message or "update" in user_message:
                ai_reply = "Your application is under review by the KNCCI team. We prioritize precision in our matching process.\n\nYou will be contacted directly once relevant opportunities are identified."
            elif "match" in user_message or "connection" in user_message or "introduction" in user_message:
                ai_reply = "KNCCI operates on a curated introduction model.\n\nWe match based on industry alignment, strategic intent, geographic focus, and business stage. Both parties must consent before any introduction is made.\n\nOur team will reach out when a relevant match is identified."
            elif "support" in user_message or "help" in user_message or "contact" in user_message:
                ai_reply = "For any inquiries, our team will respond within 24-48 hours.\n\nThank you for your patience."
            else:
                ai_reply = "Your application is currently under review.\n\nThe KNCCI team will contact you once your profile is vetted and relevant opportunities are identified.\n\nWe appreciate your patience."
    
    resp = MessagingResponse()
    resp.message(ai_reply)
    
    return Response(content=str(resp), media_type="application/xml")

@app.post("/webhook")
async def whatsapp_webhook_alt(Body: str = Form(...), From: str = Form(...)):
    return await whatsapp_webhook(Body, From)

@app.get("/health")
async def health():
    return {"status": "WhatsApp Bot Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
