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

@app.post("/")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    user_message = Body.strip().lower()
    user_phone = From
    
    # Initialize session for new user
    if user_phone not in user_sessions:
        user_sessions[user_phone] = {"step": "greeting", "data": {}}
        ai_reply = "Welcome to KNCCI - a curated India-Kenya business introduction platform.\n\nPlease answer a few questions to submit your application. All profiles are vetted before approval.\n\nReply 'Start' to begin."
    else:
        session = user_sessions[user_phone]
        step = session["step"]
        
        if step == "greeting":
            if "start" in user_message or "yes" in user_message:
                session["step"] = "q1_full_name"
                ai_reply = "Q1. What is your Full Name?"
            else:
                ai_reply = "Reply 'Start' to begin your application."
        
        elif step == "q1_full_name":
            session["data"]["full_name"] = Body.strip()
            session["step"] = "q2_company_name"
            ai_reply = "Q2. What is your Company / Organization Name?"
        
        elif step == "q2_company_name":
            session["data"]["company_name"] = Body.strip()
            session["step"] = "q3_designation"
            ai_reply = "Q3. What is your Designation / Role in the organization?"
        
        elif step == "q3_designation":
            session["data"]["designation"] = Body.strip()
            session["step"] = "q4_country"
            ai_reply = "Q4. Which country are you based in?\n\nPlease choose:\n1. India\n2. Kenya\n3. Other"
        
        elif step == "q4_country":
            country_map = {"1": "India", "2": "Kenya", "3": "Other"}
            country = country_map.get(user_message, Body.strip())
            session["data"]["country"] = country
            session["step"] = "q5_city"
            ai_reply = "Q5. Which city are you located in?"
        
        elif step == "q5_city":
            session["data"]["city"] = Body.strip()
            session["step"] = "q6_industry"
            ai_reply = "Q6. What industry does your company operate in?\n\nPlease choose:\n1. Technology\n2. Manufacturing\n3. Agriculture\n4. Healthcare\n5. Education\n6. Logistics\n7. Finance\n8. Energy\n9. Others"
        
        elif step == "q6_industry":
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
            session["step"] = "q7_company_stage"
            ai_reply = "Q7. What is your company stage?\n\nPlease choose:\n1. Startup\n2. Growth Stage\n3. SME\n4. Enterprise\n5. Institution / Government"
        
        elif step == "q7_company_stage":
            stage_map = {
                "1": "Startup",
                "2": "Growth Stage",
                "3": "SME",
                "4": "Enterprise",
                "5": "Institution / Government"
            }
            stage = stage_map.get(user_message, Body.strip())
            session["data"]["company_stage"] = stage
            session["step"] = "q8_partnership_type"
            ai_reply = "Q8. What type of partnership or opportunity are you looking for?\n\nPlease choose:\n1. Distributor\n2. Investor\n3. Technology Partner\n4. Local Business Partner\n5. Strategic Partnership\n6. Institutional Collaboration\n7. Market Expansion"
        
        elif step == "q8_partnership_type":
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
            session["step"] = "q9_target_market"
            ai_reply = "Q9. Which market are you targeting?\n\nPlease choose:\n1. India\n2. Kenya\n3. Both"
        
        elif step == "q9_target_market":
            market_map = {"1": "India", "2": "Kenya", "3": "Both"}
            market = market_map.get(user_message, Body.strip())
            session["data"]["target_market"] = market
            session["step"] = "q10_business_description"
            ai_reply = "Q10. Please provide a short description of your business and the partnership you are seeking (max 200-300 words)."
        
        elif step == "q10_business_description":
            session["data"]["business_description"] = Body.strip()
            session["step"] = "q11_profile_link"
            ai_reply = "Q11. Please share your website, LinkedIn profile, or company profile link."
        
        elif step == "q11_profile_link":
            session["data"]["profile_link"] = Body.strip()
            session["step"] = "q12_email"
            ai_reply = "Q12. Please provide your official email address for verification."
        
        elif step == "q12_email":
            session["data"]["email"] = Body.strip()
            save_user_data(user_phone, session["data"])
            
            # Get partner examples based on partnership type
            partner_info = ""
            partnership = session["data"].get("partnership_type", "")
            
            if partnership == "Distributor":
                partner_info = "\n\nSample Distributors in Our Network:\n\nSimba Corporation (Kenya)\nSectors: Electronics, Automotive\nWebsite: https://www.simbacorp.com\n\nMetro Wholesale India\nSectors: FMCG, Consumer goods\nWebsite: https://www.metrowholesale.in"
            elif partnership == "Investor":
                partner_info = "\n\nSample Investors in Our Network:\n\nAccel Partners India\nFocus: Early to growth stage\nWebsite: https://www.accel.com\n\nChandaria Capital (Kenya)\nFocus: Manufacturing, FMCG\nWebsite: https://chandaria.com"
            elif partnership == "Technology Partner":
                partner_info = "\n\nSample Tech Partners in Our Network:\n\nTechMahindra (India)\nServices: Digital transformation, AI/ML\nWebsite: https://www.techmahindra.com\n\nCraft Silicon (Kenya)\nServices: Banking software, Fintech\nWebsite: https://www.craftsilicon.com"
            elif partnership == "Local Business Partner":
                partner_info = "\n\nSample Local Partners in Our Network:\n\nSameer Group (Kenya)\nSectors: Real estate, Manufacturing\nWebsite: https://www.sameergroup.com\n\nTata International (India)\nSectors: Multi-sector conglomerate\nWebsite: https://www.tatainternational.com"
            
            ai_reply = "Thank you. Your application has been submitted successfully. Our team will review your profile and notify you once approved." + partner_info
            session["step"] = "completed"
        
        else:
            # Completed or general queries
            if "match" in user_message or "connection" in user_message or "how" in user_message:
                ai_reply = "We suggest connections based on industry, goals, geography, and business stage. Both parties must agree before an introduction.\n\nOur team will review your profile and reach out with potential matches."
            elif "support" in user_message or "help" in user_message or "contact" in user_message:
                ai_reply = "Our team will review and get in touch shortly. Thank you for your patience."
            else:
                ai_reply = "Your application is under review. The KNCCI Expert Team will contact you once your profile is vetted."
    
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
