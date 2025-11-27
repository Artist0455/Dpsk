import os
import logging
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot configuration
API_ID = 25136703
API_HASH = "accfaf5ecd981c67e481328515c39f89"
BOT_TOKEN = "8350139839:AAEgtaB1FpNTCqnCVIPHu0Q_KdJaok_slYU"

# Initialize bot
app = Client("session_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# Store user sessions
user_sessions = {}

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        
        welcome_text = f"""
👋 **Hello {first_name}!**

🤖 **Welcome to String Session Generator Bot**

I can generate Pyrogram string sessions for your Telegram account.

**Features:**
✅ Fast & Secure
✅ 2FA Support  
✅ 100% Free

Click the button below to get started!"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
            [InlineKeyboardButton("📢 Support Channel", url="https://t.me/shribots")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ])
        
        await message.reply_text(welcome_text, reply_markup=keyboard)
        logger.info(f"✅ User {user_id} received welcome message")
        
    except Exception as e:
        logger.error(f"Start error: {e}")
        await message.reply_text("❌ An error occurred. Please try /start again.")

@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    help_text = """
📖 **How to Use This Bot:**

**To Generate Session:**
1. Click **Generate Session** button
2. Send your phone number (with country code)
3. Send the verification code you receive
4. If you have 2FA, send your password
5. Copy your generated session string

**Example Phone Numbers:**
• +919876543210 (India)
• +1234567890 (US)

**Support:** @shribots
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
        [InlineKeyboardButton("📢 Support", url="https://t.me/shribots")]
    ])
    
    await message.reply_text(help_text, reply_markup=keyboard)

@app.on_message(filters.command("generate"))
async def generate_command(client, message: Message):
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        await message.reply_text("⚠️ You have an active session! Use /cancel first.")
        return
    
    user_sessions[user_id] = {"step": "phone"}
    
    await message.reply_text(
        "📱 **Step 1: Phone Number**\n\n"
        "Please send your phone number:\n"
        "**Example:** +919876543210\n\n"
        "Type /cancel to stop."
    )

@app.on_message(filters.command("cancel"))
async def cancel_command(client, message: Message):
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        if "client" in user_sessions[user_id]:
            try:
                await user_sessions[user_id]["client"].disconnect()
            except:
                pass
        del user_sessions[user_id]
    
    await message.reply_text("✅ Session cancelled! Use /generate to start again.")

@app.on_callback_query()
async def handle_callbacks(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    try:
        if data == "generate":
            if user_id in user_sessions:
                await callback_query.answer("You have an active session!", show_alert=True)
                return
            
            user_sessions[user_id] = {"step": "phone"}
            
            await callback_query.message.edit_text(
                "📱 **Step 1: Phone Number**\n\n"
                "Please send your phone number:\n"
                "**Example:** +919876543210\n\n"
                "Type /cancel to stop."
            )
            
        elif data == "help":
            help_text = """
📖 **Quick Guide:**

1. **Send Phone Number** (with + country code)
2. **Send Verification Code** (6-digit) 
3. **Get Your Session String**

**Support:** @shribots
"""
            await callback_query.message.edit_text(
                help_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
                    [InlineKeyboardButton("📢 Support", url="https://t.me/shribots")]
                ])
            )
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await callback_query.answer("Error occurred!", show_alert=True)

@app.on_message(filters.text & filters.private)
async def handle_text_messages(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text.startswith('/'):
        return
    
    if user_id not in user_sessions:
        await message.reply_text("👋 Welcome! Use /start to begin.")
        return
    
    session = user_sessions[user_id]
    step = session.get("step", "phone")
    
    if step == "phone":
        await handle_phone_input(client, message, text, session)

async def handle_phone_input(client, message, phone, session):
    user_id = message.from_user.id
    
    if not phone.startswith('+') or len(phone) < 10:
        await message.reply_text("❌ Invalid format! Send: +919876543210")
        return
    
    try:
        user_client = Client(f"user_{user_id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
        await user_client.connect()
        sent_code = await user_client.send_code(phone)
        
        session["client"] = user_client
        session["phone"] = phone
        session["phone_code_hash"] = sent_code.phone_code_hash
        session["step"] = "code"
        
        await message.reply_text("📨 **Code Sent!**\nSend the 6-digit code:\n\n/cancel to stop.")
        
    except Exception as e:
        logger.error(f"Phone error: {e}")
        await message.reply_text("❌ Error! Try /generate again.")
        if user_id in user_sessions:
            del user_sessions[user_id]

async def main():
    await app.start()
    print("=" * 60)
    print("✅ BOT STARTED SUCCESSFULLY!")
    me = await app.get_me()
    print(f"🤖 Bot: @{me.username}")
    print(f"📛 Name: {me.first_name}")
    print("🌐 Bot is now responding to messages...")
    print("💡 Send /start to your bot to test it!")
    print("=" * 60)
    
    await idle()

if __name__ == "__main__":
    print("🚀 Starting Telegram Bot...")
    asyncio.run(main())
