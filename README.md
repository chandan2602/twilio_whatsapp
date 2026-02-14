# WhatsApp Registration Bot with Shanghazi AI Assistant 🤖

A FastAPI-based WhatsApp bot that automates user registration through conversational AI. The bot collects user information, generates login credentials, and provides a seamless onboarding experience via WhatsApp.

## 📋 Features

- **Conversational Registration**: Interactive step-by-step user registration via WhatsApp
- **Automated Credential Generation**: Generates unique login IDs and passwords
- **Data Persistence**: Stores user data in JSON format
- **Twilio Integration**: Uses Twilio API for WhatsApp messaging
- **FastAPI Backend**: Modern, fast Python web framework
- **AI-Powered Responses**: Friendly conversational interface

## 🛠️ Technologies Used

- **Python 3.8+**
- **FastAPI** - Web framework
- **Twilio** - WhatsApp messaging API
- **OpenAI** - AI capabilities (initialized but not actively used in current flow)
- **Uvicorn** - ASGI server
- **python-dotenv** - Environment variable management

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <project-directory>
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
ACCOUNT_SID=your_twilio_account_sid
AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NO=your_twilio_whatsapp_number
OPENAI_API_KEY=your_openai_api_key
```

## 🔧 Configuration

### Twilio Setup

1. **Create a Twilio Account**
   - Sign up at: https://www.twilio.com/try-twilio
   - Get $15 free credit for testing

2. **Get Your Twilio Credentials**
   - Dashboard: https://console.twilio.com/
   - Find your `Account SID` and `Auth Token`

3. **Set Up WhatsApp Sandbox**
   - Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
   - Follow instructions to connect your WhatsApp number
   - Send the join code (e.g., "join <your-code>") to the Twilio WhatsApp number

4. **Configure Webhook**
   - In Twilio Console, go to: Messaging → Settings → WhatsApp Sandbox Settings
   - Set "When a message comes in" to: `https://your-ngrok-url/webhook`
   - Method: `HTTP POST`

### ngrok Setup

1. **Download and Install ngrok**
   - Download from: https://ngrok.com/download
   - Sign up for free account: https://dashboard.ngrok.com/signup

2. **Authenticate ngrok**
   ```bash
   ngrok config add-authtoken <your-auth-token>
   ```
   - Get your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken

3. **Start ngrok Tunnel**
   ```bash
   ngrok http 8000
   ```
   - This creates a public URL that forwards to your local server on port 8000
   - Copy the `Forwarding` URL (e.g., `https://abc123.ngrok.io`)

4. **Update Twilio Webhook**
   - Use the ngrok URL in your Twilio WhatsApp Sandbox settings
   - Webhook URL: `https://your-ngrok-url.ngrok.io/webhook`

## 🚀 Running the Application

### 1. Start the FastAPI Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at: `http://localhost:8000`

### 2. Start ngrok (in a separate terminal)

```bash
ngrok http 8000
```

### 3. Test the Bot

1. Send a WhatsApp message to your Twilio number
2. Follow the bot's prompts to complete registration

## 💬 Bot Conversation Flow

1. **Greeting**: Bot introduces itself as Shanghazi
2. **Purpose**: Asks what brings the user
3. **Name**: Collects user's full name
4. **Mobile**: Collects mobile number
5. **Email**: Collects email address
6. **Credentials**: Generates and sends login credentials with portal link

### Example Conversation

```
Bot: Hello! 👋 I'm Shanghazi, your virtual assistant. Welcome to our service!
     May I know what brings you here today?

User: I want to register

Bot: Thank you for sharing! 😊
     To proceed, could you please provide your full name?

User: John Doe

Bot: Nice to meet you, John Doe! 📱
     Please share your mobile number.

User: 1234567890

Bot: Great! 📧
     Lastly, please provide your email address.

User: john@example.com

Bot: ✅ Registration Complete!
     Your credentials:
     🆔 Login ID: ABC12345
     🔑 Password: xYz9876543
     
     🌐 Login here:
     https://698f34515845f1a3d193ce26--kncci.netlify.app/
     
     Please save these details securely. How can I assist you further?
```

## 📁 Project Structure

```
.
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── users.json          # User data storage
├── .env                # Environment variables (create this)
└── README.md           # This file
```

## 🔐 Security Notes

- Never commit your `.env` file to version control
- Add `.env` to your `.gitignore` file
- Keep your Twilio credentials and API keys secure
- Use environment variables for all sensitive data
- Consider using a proper database for production (PostgreSQL, MongoDB, etc.)

## 📊 User Data Storage

User data is stored in `users.json` with the following structure:

```json
{
  "whatsapp:+1234567890": {
    "purpose": "registration",
    "name": "John Doe",
    "mobile": "1234567890",
    "email": "john@example.com",
    "login_id": "ABC12345",
    "password": "xYz9876543"
  }
}
```

## 🔗 Important Links

### Twilio
- **Sign Up**: https://www.twilio.com/try-twilio
- **Console**: https://console.twilio.com/
- **WhatsApp Sandbox**: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
- **Documentation**: https://www.twilio.com/docs/whatsapp
- **Python SDK**: https://www.twilio.com/docs/libraries/python

### ngrok
- **Download**: https://ngrok.com/download
- **Sign Up**: https://dashboard.ngrok.com/signup
- **Dashboard**: https://dashboard.ngrok.com/
- **Documentation**: https://ngrok.com/docs
- **Get Auth Token**: https://dashboard.ngrok.com/get-started/your-authtoken

### FastAPI
- **Documentation**: https://fastapi.tiangolo.com/
- **Tutorial**: https://fastapi.tiangolo.com/tutorial/

### OpenAI
- **API Keys**: https://platform.openai.com/api-keys
- **Documentation**: https://platform.openai.com/docs/

## 🐛 Troubleshooting

### Bot Not Responding
- Check if the FastAPI server is running
- Verify ngrok tunnel is active
- Ensure Twilio webhook URL is correctly set
- Check Twilio console for error logs

### Webhook Errors
- Verify the webhook URL includes `/webhook` endpoint
- Ensure ngrok URL is HTTPS
- Check server logs for errors

### Authentication Issues
- Verify all environment variables are set correctly
- Check Twilio credentials in the console
- Ensure WhatsApp sandbox is properly configured

## 📝 API Endpoints

### `POST /webhook`
Receives incoming WhatsApp messages from Twilio and processes user registration.

**Parameters:**
- `Body`: Message content
- `From`: Sender's WhatsApp number

**Response:** TwiML XML response

### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "WhatsApp Bot Running"
}
```

## 🚀 Deployment

For production deployment, consider:

1. **Use a proper hosting service** (AWS, Heroku, DigitalOcean, etc.)
2. **Replace ngrok** with a permanent domain
3. **Use a database** instead of JSON file storage
4. **Add authentication** and rate limiting
5. **Implement logging** and monitoring
6. **Add error handling** and validation
7. **Use HTTPS** for all endpoints

## 📄 License

[Add your license here]

## 👥 Contributing

[Add contribution guidelines here]

## 📧 Contact

[Add your contact information here]

---

**Note**: This bot is currently configured for development/testing. For production use, implement proper security measures, database storage, and error handling.
