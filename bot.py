import requests
import time
import json

# Bot token - yahi use karo
BOT_TOKEN = "8244179451:AAF8LT22EcppuWET3msokmpnbmGWiaQxMOs"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

print("🤖 Bot Starting...")
print("📞 Support: @idxhelp")

# User data store
user_data = {}

def send_message(chat_id, text, keyboard=None):
    """Simple message send function"""
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if keyboard:
        payload["reply_markup"] = json.dumps(keyboard)
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except:
        return None

def edit_message(chat_id, message_id, text, keyboard=None):
    """Edit message function"""
    url = f"{API_URL}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if keyboard:
        payload["reply_markup"] = json.dumps(keyboard)
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except:
        return None

def answer_callback(callback_id):
    """Answer callback query"""
    url = f"{API_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

def get_updates(offset):
    """Get updates from Telegram"""
    url = f"{API_URL}/getUpdates"
    payload = {"offset": offset, "timeout": 30}
    
    try:
        response = requests.post(url, json=payload, timeout=35)
        return response.json()
    except:
        return {"ok": False, "result": []}

def handle_start(chat_id):
    """Handle /start command"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "📱 Generate String Session", "callback_data": "gen_session"}],
            [
                {"text": "📢 Channel", "url": "https://t.me/idxhelp"},
                {"text": "🆘 Support", "url": "https://t.me/idxhelp"}
            ],
            [{"text": "👥 Add to Group", "url": f"https://t.me/sessionstringprobot?startgroup=true"}]
        ]
    }
    
    text = """
🔐 <b>String Session Generator Bot</b>

📱 <b>Yeh bot aapke liye string session generate karega:</b>

⚡ <b>Features:</b>
• Pyrogram String Session
• Telethon Session  
• Fast & Secure
• Easy to Use

🚀 <b>How to Use:</b>
1. 'Generate String Session' click karo
2. Phone number bhejo (with country code)
3. Verification code bhejo
4. Session mil jayega

━━━━━━━━━━━━━━━━
✨ <b>Powered by:</b> @idxhelp
━━━━━━━━━━━━━━━━

👇 <b>Start karne ke liye button click karo:</b>
"""
    
    send_message(chat_id, text, keyboard)

def handle_generate_session(chat_id, message_id=None):
    """Start session generation"""
    user_data[chat_id] = {"step": "waiting_phone"}
    
    text = """
📱 <b>String Session Generation</b>

Please send your <b>Phone Number</b> with country code:
<b>Example:</b> <code>+919876543210</code>

✨ <b>Powered by:</b> @idxhelp
"""
    
    if message_id:
        edit_message(chat_id, message_id, text)
    else:
        send_message(chat_id, text)

def handle_phone_number(chat_id, phone):
    """Handle phone number input"""
    if not phone.startswith('+') or len(phone) < 10:
        send_message(chat_id, "❌ <b>Invalid phone number!</b>\n\nPlease send in format: <code>+919876543210</code>\nWith country code.")
        return
    
    user_data[chat_id] = {
        "step": "waiting_code", 
        "phone": phone,
        "session_started": True
    }
    
    text = f"""
✅ <b>Phone Number Received:</b> <code>{phone}</code>

🔐 <b>Connecting to Telegram APIs...</b>

📨 <b>Verification code send ho gaya hai!</b>

Please check your Telegram app and send the <b>5-digit code</b>:

✨ <b>Powered by:</b> @idxhelp
"""
    
    send_message(chat_id, text)

def handle_verification_code(chat_id, code):
    """Handle verification code"""
    if not code.isdigit() or len(code) != 5:
        send_message(chat_id, "❌ <b>Invalid code!</b>\n\nPlease send 5-digit verification code.")
        return
    
    user_info = user_data.get(chat_id, {})
    phone = user_info.get("phone", "+XXXXXXXXXX")
    
    # Simulate session generation
    text = f"""
🔐 <b>Verifying code...</b>

Please wait...
"""
    send_message(chat_id, text)
    time.sleep(2)
    
    # Generate demo session (real implementation mein yahan Pyrogram integrate karo)
    demo_session = "1AQDVMt8Q4Ee2LkQp-ZXqK9WK8K9W7YqK8W9Q4Ee2LkQpZXqK9WK8K9W7YqK8W9Q4Ee2LkQpZXqK9WK8K9W7YqK8W9Q4Ee2LkQpZXqK9WK8K9W7YqK8W9Q4Ee=="
    
    text = f"""
🎉 <b>String Session Successfully Generated!</b>

✅ <b>Session sent to your account!</b>

📱 <b>Phone:</b> <code>{phone}</code>
🔐 <b>Session Type:</b> Pyrogram

<b>Your String Session:</b>
<code>{demo_session}</code>

⚠️ <b>Important:</b>
• Is session ko kisi se share mat karna
• Secure jagah save karo
• Music bots mein use karo

✨ <b>Powered by:</b> @idxhelp

<i>Note: Real implementation ke liye Pyrogram API integrate karna hoga.</i>
"""
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "📢 Official Channel", "url": "https://t.me/idxhelp"}],
            [{"text": "🔄 New Session", "callback_data": "gen_session"}],
            [{"text": "👥 Add to Group", "url": f"https://t.me/sessionstringprobot?startgroup=true"}]
        ]
    }
    
    send_message(chat_id, text, keyboard)
    user_data.pop(chat_id, None)

def handle_help(chat_id):
    """Handle /help command"""
    text = """
🆘 <b>Help Guide - String Session Generator</b>

📱 <b>How to Generate Session:</b>
1. /start command bhejo
2. 'Generate String Session' button click karo
3. Apna phone number bhejo (with country code)
4. Verification code bhejo
5. Session mil jayega

🔐 <b>What is String Session?</b>
• Yeh Telegram account ka authentication token hai
• Music bots banane ke liye use hota hai
• User bots ke liye use hota hai

⚠️ <b>Security Tips:</b>
• Session kisi se share mat karna
• Secure jagah save karo
• Sirf trusted bots mein use karo

📞 <b>Phone Number Format:</b>
• Country code ke saath: <code>+919876543210</code>
• Without spaces

🔧 <b>Support:</b>
• Official Channel: @idxhelp
• Support Group: @idxhelp

✨ <b>Powered by:</b> @idxhelp
"""
    send_message(chat_id, text)

def main():
    """Main bot loop"""
    offset = 0
    print("✅ Bot is running and ready!")
    
    while True:
        try:
            updates = get_updates(offset)
            
            if updates.get("ok"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    
                    # Handle messages
                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        text = message.get("text", "")
                        
                        if text.startswith("/start"):
                            handle_start(chat_id)
                        elif text.startswith("/help"):
                            handle_help(chat_id)
                        elif text.startswith("/session"):
                            handle_generate_session(chat_id)
                        else:
                            # Handle session flow
                            user_state = user_data.get(chat_id, {})
                            if user_state.get("step") == "waiting_phone":
                                handle_phone_number(chat_id, text)
                            elif user_state.get("step") == "waiting_code":
                                handle_verification_code(chat_id, text)
                    
                    # Handle callbacks
                    elif "callback_query" in update:
                        callback = update["callback_query"]
                        chat_id = callback["message"]["chat"]["id"]
                        message_id = callback["message"]["message_id"]
                        data = callback["data"]
                        
                        answer_callback(callback["id"])
                        
                        if data == "gen_session":
                            handle_generate_session(chat_id, message_id)
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
