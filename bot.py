import os
import asyncio
import aiohttp
import json
from datetime import datetime

# Bot Configuration
BOT_TOKEN = "8244179451:AAF8LT22EcppuWET3msokmpnbmGWiaQxMOs"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Store user sessions in memory
user_sessions = {}

class TelegramBot:
    def __init__(self):
        self.session = None
        
    async def start(self):
        self.session = aiohttp.ClientSession()
        print("🤖 Bot Started Successfully!")
        print("📞 Support: @idxhelp")
        await self.poll_updates()
    
    async def make_request(self, method, data):
        try:
            async with self.session.post(f"{API_URL}/{method}", json=data) as response:
                return await response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return None
    
    async def send_message(self, chat_id, text, reply_markup=None):
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            data["reply_markup"] = reply_markup
        return await self.make_request("sendMessage", data)
    
    async def edit_message(self, chat_id, message_id, text, reply_markup=None):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            data["reply_markup"] = reply_markup
        return await self.make_request("editMessageText", data)
    
    async def answer_callback(self, callback_id, text=None):
        data = {"callback_query_id": callback_id}
        if text:
            data["text"] = text
        return await self.make_request("answerCallbackQuery", data)
    
    async def poll_updates(self):
        offset = 0
        while True:
            try:
                data = {"offset": offset, "timeout": 30}
                result = await self.make_request("getUpdates", data)
                
                if result and result.get("ok"):
                    updates = result.get("result", [])
                    for update in updates:
                        offset = update["update_id"] + 1
                        await self.handle_update(update)
                else:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"Polling error: {e}")
                await asyncio.sleep(5)
    
    async def handle_update(self, update):
        try:
            if "message" in update:
                await self.handle_message(update["message"])
            elif "callback_query" in update:
                await self.handle_callback(update["callback_query"])
        except Exception as e:
            print(f"Update handling error: {e}")
    
    async def handle_message(self, message):
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        
        if text.startswith("/start"):
            keyboard = {
                "inline_keyboard": [
                    [{"text": "📱 Generate String Session", "callback_data": "generate_session"}],
                    [
                        {"text": "📢 Channel", "url": "https://t.me/idxhelp"},
                        {"text": "🆘 Support", "url": "https://t.me/idxhelp"}
                    ]
                ]
            }
            
            welcome_text = """
🔐 <b>String Session Generator Bot</b>

✨ <b>Generate Pyrogram String Sessions Easily</b>

📱 <b>How to Use:</b>
1. Click 'Generate String Session'
2. Send your phone number (with country code)
3. Send verification code
4. Get your session string

⚡ <b>Fast & Secure</b>
🔒 <b>Your data is safe</b>

<b>Powered by:</b> @idxhelp
"""
            await self.send_message(chat_id, welcome_text, keyboard)
            
        elif text.startswith("/help"):
            help_text = """
🤖 <b>String Session Bot Help</b>

📋 <b>Commands:</b>
/start - Start the bot
/help - Show this help

📱 <b>Usage:</b>
1. Start bot
2. Send phone number (with + country code)
3. Send verification code
4. Get your session string

🔐 <b>What is String Session?</b>
- Authentication token for Telegram APIs
- Used for Pyrogram/Telethon bots
- Required for userbots and music bots

📞 <b>Support:</b> @idxhelp
"""
            await self.send_message(chat_id, help_text)
            
        else:
            # Handle session generation flow
            await self.handle_session_flow(chat_id, text, message)
    
    async def handle_callback(self, callback):
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        data = callback["data"]
        
        await self.answer_callback(callback["id"])
        
        if data == "generate_session":
            user_sessions[chat_id] = {"step": "phone"}
            text = "📱 <b>String Session Generation</b>\n\nPlease send your Phone Number with country code:\n<b>Example:</b> <code>+919876543210</code>\n\n<b>Powered by:</b> @idxhelp"
            await self.edit_message(chat_id, message_id, text)
    
    async def handle_session_flow(self, chat_id, text, message):
        if chat_id not in user_sessions:
            return
        
        step = user_sessions[chat_id].get("step")
        
        if step == "phone":
            if text.startswith('+') and len(text) >= 10:
                user_sessions[chat_id].update({
                    "phone": text,
                    "step": "code"
                })
                await self.send_message(chat_id, f"✅ <b>Phone Received:</b> <code>{text}</code>\n\n🔐 <b>Connecting to Telegram...</b>\n\nPlease wait while we set up your session...")
                
                # Simulate session generation (you can integrate real Pyrogram here)
                await asyncio.sleep(2)
                
                # For demo - show session format
                demo_session = "1sDf5gH8jK2lM4nB7vC9xZ0qW3eR6tY8uI1oP7aS2dF4gH6jK8lM0qW2eR4tY6uI8oP0aS2dF4gH6jK8"
                session_text = f"""
🎉 <b>String Session Generated Successfully!</b>

🔐 <b>Your Session String:</b>
<code>{demo_session}</code>

📱 <b>Phone:</b> <code>{text}</code>

⚠️ <b>Important:</b>
• Save this session securely
• Don't share with anyone  
• Use for your bots

<b>Generated by this bot</b>
<b>Powered by:</b> @idxhelp

<i>Note: This is a demo session. Integrate real Pyrogram API for actual session generation.</i>
"""
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "🔄 Generate New", "callback_data": "generate_session"}],
                        [{"text": "📢 Channel", "url": "https://t.me/idxhelp"}]
                    ]
                }
                await self.send_message(chat_id, session_text, keyboard)
                user_sessions.pop(chat_id, None)
                
            else:
                await self.send_message(chat_id, "❌ <b>Invalid phone number!</b>\n\nPlease send in format: <code>+919876543210</code>\nWith country code, without spaces.")

async def main():
    bot = TelegramBot()
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
