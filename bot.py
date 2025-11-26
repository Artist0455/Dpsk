import os
import logging
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid, FloodWait
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration - APNA BOT TOKEN YAHI DALNA
API_ID = 25136703
API_HASH = "accfaf5ecd981c67e481328515c39f89"
BOT_TOKEN = "8350139839:AAHKChyb6VhRtJYx8R4BKDttllh-AhbSPMM"

# Initialize bot
app = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

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

Click the button below to generate your session!
        """
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
            [InlineKeyboardButton("📢 Support", url="https://t.me/shribots")]
        ])
        
        await message.reply_text(welcome_text, reply_markup=keyboard)
        logger.info(f"User {user_id} started the bot")
        
    except Exception as e:
        logger.error(f"Start error: {e}")
        await message.reply_text("❌ An error occurred. Please try /start again.")

@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    help_text = """
📖 **How to Use This Bot:**

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
    
    await message.reply_text(help_text)

@app.on_message(filters.command("generate"))
async def generate_command(client, message: Message):
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        await message.reply_text("⚠️ You already have an active session. Use /cancel first.")
        return
    
    user_sessions[user_id] = {"step": "phone"}
    
    await message.reply_text(
        "📱 **Step 1: Phone Number**\n\n"
        "Please send your phone number in international format:\n\n"
        "**Examples:**\n"
        "• `+919876543210`\n"
        "• `+1234567890`\n\n"
        "Type /cancel to stop."
    )

@app.on_callback_query(filters.regex("generate"))
async def generate_callback(client, callback_query):
    user_id = callback_query.from_user.id
    
    if user_id in user_sessions:
        await callback_query.answer("You already have an active session!", show_alert=True)
        return
    
    user_sessions[user_id] = {"step": "phone"}
    
    await callback_query.message.edit_text(
        "📱 **Step 1: Phone Number**\n\n"
        "Please send your phone number in international format:\n\n"
        "**Examples:**\n"
        "• `+919876543210`\n"
        "• `+1234567890`\n\n"
        "Type /cancel to stop."
    )
    await callback_query.answer()

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
        await message.reply_text("✅ Session cancelled. Use /generate to start again.")
    else:
        await message.reply_text("ℹ️ No active session found.")

@app.on_message(filters.text & filters.private)
async def handle_text(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Ignore commands
    if text.startswith('/'):
        return
    
    # If no active session
    if user_id not in user_sessions:
        await message.reply_text(
            "👋 Welcome! Use /generate to start session generation or /help for instructions."
        )
        return
    
    session = user_sessions[user_id]
    step = session.get("step", "phone")
    
    if step == "phone":
        await handle_phone(client, message, text, session)
    elif step == "code":
        await handle_code(client, message, text, session)
    elif step == "password":
        await handle_password(client, message, text, session)

async def handle_phone(client, message, phone, session):
    user_id = message.from_user.id
    
    # Simple phone validation
    if not phone.startswith('+') or len(phone) < 10:
        await message.reply_text(
            "❌ Invalid phone format!\n\n"
            "Please send with country code:\n"
            "• +919876543210\n"
            "• +1234567890\n\n"
            "Try again:"
        )
        return
    
    try:
        # Create user client
        user_client = Client(
            f"user_{user_id}",
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True
        )
        
        await user_client.connect()
        sent_code = await user_client.send_code(phone)
        
        # Update session
        session["client"] = user_client
        session["phone"] = phone
        session["phone_code_hash"] = sent_code.phone_code_hash
        session["step"] = "code"
        
        await message.reply_text(
            "📨 **Step 2: Verification Code**\n\n"
            "✅ Code sent! Please check your Telegram messages and send me the 6-digit code:\n\n"
            "Type /cancel to stop."
        )
        
    except PhoneNumberInvalid:
        await message.reply_text("❌ Invalid phone number. Please check and try again.")
        if user_id in user_sessions:
            del user_sessions[user_id]
    except FloodWait as e:
        await message.reply_text(f"⏳ Too many attempts. Wait {e.value} seconds.")
        if user_id in user_sessions:
            del user_sessions[user_id]
    except Exception as e:
        logger.error(f"Phone error: {e}")
        await message.reply_text("❌ Error sending code. Try /generate again.")
        if user_id in user_sessions:
            del user_sessions[user_id]

async def handle_code(client, message, code, session):
    user_id = message.from_user.id
    
    if not code.isdigit() or len(code) != 6:
        await message.reply_text("❌ Invalid code! Please send 6 digits only.")
        return
    
    try:
        user_client = session["client"]
        phone = session["phone"]
        
        await user_client.sign_in(
            phone_number=phone,
            phone_code_hash=session["phone_code_hash"],
            phone_code=code
        )
        
        # Success - generate session
        string_session = await user_client.export_session_string()
        
        success_text = f"""
✅ **STRING SESSION GENERATED!**

**Your Session:**
```{string_session}```

**Important:**
🔒 Keep this session secure
🚫 Never share with anyone
💾 Store it safely

**Thank you for using our service!** 🎉
        """
        
        await message.reply_text(success_text)
        
        # Cleanup
        await user_client.disconnect()
        del user_sessions[user_id]
        
    except PhoneCodeInvalid:
        await message.reply_text("❌ Wrong code! Please check and try again.")
    except PhoneCodeExpired:
        await message.reply_text("❌ Code expired! Use /generate for new code.")
        await session["client"].disconnect()
        del user_sessions[user_id]
    except SessionPasswordNeeded:
        session["step"] = "password"
        await message.reply_text(
            "🔐 **Step 3: 2FA Password**\n\n"
            "Your account has 2FA enabled.\n\n"
            "Please send your 2FA password:\n\n"
            "Type /cancel to stop."
        )
    except Exception as e:
        logger.error(f"Code error: {e}")
        await message.reply_text("❌ Error! Use /generate to start over.")
        if "client" in session:
            await session["client"].disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]

async def handle_password(client, message, password, session):
    user_id = message.from_user.id
    
    try:
        user_client = session["client"]
        await user_client.check_password(password)
        
        string_session = await user_client.export_session_string()
        
        success_text = f"""
✅ **STRING SESSION GENERATED!**

**Your Session:**
```{string_session}```

**2FA verified successfully!** 🔐

**Important:**
🔒 Keep this session secure
🚫 Never share with anyone

**Thank you!** 🎉
        """
        
        await message.reply_text(success_text)
        
        # Cleanup
        await user_client.disconnect()
        del user_sessions[user_id]
        
    except PasswordHashInvalid:
        await message.reply_text("❌ Wrong 2FA password! Try again.")
    except Exception as e:
        logger.error(f"Password error: {e}")
        await message.reply_text("❌ Error! Use /generate to start over.")
        if "client" in session:
            await session["client"].disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]

async def main():
    await app.start()
    print("✅ BOT STARTED SUCCESSFULLY!")
    print("🤖 Bot is now running and responding to messages...")
    
    # Get bot info
    me = await app.get_me()
    print(f"Bot: @{me.username}")
    print(f"Name: {me.first_name}")
    print(f"ID: {me.id}")
    
    # Keep running
    await idle()

if __name__ == "__main__":
    print("🚀 Starting Telegram Bot...")
    asyncio.run(main())
