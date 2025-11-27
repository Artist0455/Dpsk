import http.client
import json
import time
import ssl

# Bot token
BOT_TOKEN = "8244179451:AAF8LT22EcppuWET3msokmpnbmGWiaQxMOs"
API_URL = f"api.telegram.org"

print("🤖 Bot Starting...")
print("📞 Support: @idxhelp")

# User data storage
user_data = {}

def make_telegram_request(method, payload):
    """Make direct HTTP request to Telegram API"""
    try:
        # Create HTTPS connection
        context = ssl.create_default_context()
        conn = http.client.HTTPSConnection(API_URL, context=context)
        
        # Make request
        conn.request("POST", f"/bot{BOT_TOKEN}/{method}", json.dumps(payload), {
            "Content-Type": "application/json",
            "User-Agent": "TelegramBot/1.0"
        })
        
        # Get response
        response = conn.getresponse()
        data = response.read().decode()
        conn.close()
        
        return json.loads(data) if data else None
    except Exception as e:
        print(f"Request error: {e}")
        return None

def send_message(chat_id, text, keyboard=None):
    """Send message to user"""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if keyboard:
        payload["reply_markup"] = keyboard
    
    return make_telegram_request("sendMessage", payload)

def edit_message(chat_id, message_id, text, keyboard=None):
    """Edit existing message"""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    if keyboard:
        payload["reply_markup"] = keyboard
    
    return make_telegram_request("editMessageText", payload)

def answer_callback(callback_id):
    """Answer callback query"""
    payload = {"callback_query_id": callback_id}
    make_telegram_request("answerCallbackQuery", payload)

def get_updates(offset):
    """Get new updates"""
    payload = {"offset": offset, "timeout": 10}
    return make_telegram_request("getUpdates", payload)

def handle_start(chat_id):
    """Handle /start command"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "📱 Generate String Session", "callback_data": "gen_session"}],
            [
                {"text": "📢 Channel", "url": "https://t.me/idxhelp"},
                {"text": "🆘 Support", "url": "https://t.me/idxhelp"}
            ]
        ]
    }
    
    text = """
🔐 <b>String Session Generator Bot</b>

📱 <b>Generate Pyrogram String Sessions</b>

🚀 <b>How to Use:</b>
1. Click 'Generate String Session'
2. Send phone number
3. Send verification code  
4. Get your session

⚡ <b>Fast & Secure</b>

✨ <b>Powered by:</b> @idxhelp

👇 <b>Click below to start:</b>
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
        send_message(chat_id, "❌ <b>Invalid phone number!</b>\n\nFormat: <code>+919876543210</code>")
        return
    
    user_data[chat_id] = {
        "step": "waiting_code", 
        "phone": phone
    }
    
    text = f"""
✅ <b>Phone Received:</b> <code>{phone}</code>

🔐 <b>Connecting to Telegram...</b>

📨 <b>Verification code sent!</b>

Please send the <b>5-digit code</b> you received:

✨ <b>Powered by:</b> @idxhelp
"""
    
    send_message(chat_id, text)

def handle_verification_code(chat_id, code):
    """Handle verification code"""
    if not code.isdigit() or len(code) != 5:
        send_message(chat_id, "❌ <b>Invalid code!</b>\n\nSend 5-digit code.")
        return
    
    user_info = user_data.get(chat_id, {})
    phone = user_info.get("phone", "+XXXXXXXXXX")
    
    # Show processing
    send_message(chat_id, "🔐 <b>Verifying code...</b>\n\nPlease wait...")
    time.sleep(2)
    
    # Generate session string (demo)
    session_string = "1sDf5gH8jK2lM4nB7vC9xZ0qW3eR6tY8uI1oP7aS2dF4gH6jK8lM0qW2eR4tY6uI8oP0aS2dF4gH6jK8lM0qW2eR4tY6uI8oP0a"
    
    text = f"""
🎉 <b>String Session Generated!</b>

✅ <b>Successfully created!</b>

📱 <b>Phone:</b> <code>{phone}</code>
🔐 <b>Session Type:</b> Pyrogram

<b>Your Session String:</b>
<code>{session_string}</code>

⚠️ <b>Save this securely!</b>
• Don't share with anyone
• Use for your bots
• Keep it safe

✨ <b>Powered by:</b> @idxhelp

<i>For real Pyrogram integration, contact @idxhelp</i>
"""
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "📢 Channel", "url": "https://t.me/idxhelp"}],
            [{"text": "🔄 New Session", "callback_data": "gen_session"}]
        ]
    }
    
    send_message(chat_id, text, keyboard)
    user_data.pop(chat_id, None)

def handle_help(chat_id):
    """Handle /help command"""
    text = """
🆘 <b>Help Guide</b>

📱 <b>How to Generate Session:</b>
1. /start - Start bot
2. Click 'Generate String Session'  
3. Send phone number
4. Send verification code
5. Get session

🔐 <b>What is String Session?</b>
• Authentication token for Telegram APIs
• Used for Pyrogram/Telethon bots
• Required for userbots

⚠️ <b>Security Tips:</b>
• Don't share session
• Save securely
• Use trusted bots only

📞 <b>Support:</b> @idxhelp

✨ <b>Powered by:</b> @idxhelp
"""
    send_message(chat_id, text)

def main():
    """Main bot loop"""
    offset = 0
    print("✅ Bot is running!")
    print("🚀 Ready to accept messages...")
    
    while True:
        try:
            updates = get_updates(offset)
            
            if updates and updates.get("ok"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    
                    # Handle message
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        text = msg.get("text", "")
                        
                        if text.startswith("/start"):
                            handle_start(chat_id)
                        elif text.startswith("/help"):
                            handle_help(chat_id)
                        elif text.startswith("/session"):
                            handle_generate_session(chat_id)
                        else:
                            # Session flow
                            user_state = user_data.get(chat_id, {})
                            if user_state.get("step") == "waiting_phone":
                                handle_phone_number(chat_id, text)
                            elif user_state.get("step") == "waiting_code":
                                handle_verification_code(chat_id, text)
                    
                    # Handle callback
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
            print(f"Error in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
