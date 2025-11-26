import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid, FloodWait
)
import asyncio
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8350139839:AAHKChyb6VhRtJYx8R4BKDttllh-AhbSPMM")
API_ID = int(os.environ.get("API_ID", 25136703))
API_HASH = os.environ.get("API_HASH", "accfaf5ecd981c67e481328515c39f89")
SUPPORT_CHANNEL = "shribots"

# Initialize bot
bot = Client(
    "session_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# Store user sessions
user_sessions = {}

def validate_phone(phone):
    return re.match(r'^\+\d{10,15}$', phone) is not None

def validate_code(code):
    return code.isdigit() and len(code) == 6

# Keyboards
def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
        [InlineKeyboardButton("📢 Support", url=f"https://t.me/{SUPPORT_CHANNEL}")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ])

def support_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Support Channel", url=f"https://t.me/{SUPPORT_CHANNEL}")]
    ])

# Start command
@bot.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
    try:
        name = message.from_user.first_name
        text = f"""👋 **Hello {name}!**

🤖 **String Session Generator Bot**

I can generate Pyrogram string sessions for your Telegram account.

**Features:**
✅ Fast & Secure
✅ 2FA Support  
✅ 100% Free

Click **Generate Session** to begin!"""
        
        await message.reply_text(
            text,
            reply_markup=start_keyboard(),
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Start error: {e}")

# Help command  
@bot.on_message(filters.command("help"))
async def help_cmd(client, message: Message):
    text = f"""📖 **Help Guide**

**How to generate session:**
1. Send /generate or click Generate button
2. Enter your phone number (with country code)
3. Enter verification code from Telegram
4. If 2FA enabled, enter your password
5. Copy your generated session string

**Safety Tips:**
🔒 Never share your session string
🗑️ Regenerate if compromised  
💾 Store securely

**Support:** @{SUPPORT_CHANNEL}"""
    
    await message.reply_text(text, reply_markup=support_keyboard())

# Generate command
@bot.on_message(filters.command("generate"))
async def generate_cmd(client, message: Message):
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        await message.reply_text("⚠️ You have an active session. Use /cancel first.")
        return
    
    user_sessions[user_id] = {"step": "phone"}
    await message.reply_text(
        "📱 **Step 1: Phone Number**\n\n"
        "Send your phone number in international format:\n"
        "• **+919876543210** (India)\n" 
        "• **+1234567890** (US)\n\n"
        "Or /cancel to stop."
    )

# Cancel command
@bot.on_message(filters.command("cancel"))
async def cancel_cmd(client, message: Message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        # Disconnect client if exists
        if "client" in user_sessions[user_id]:
            try:
                await user_sessions[user_id]["client"].disconnect()
            except:
                pass
        del user_sessions[user_id]
    
    await message.reply_text("✅ Cancelled. Use /generate to start again.")

# Callback queries
@bot.on_callback_query()
async def handle_callbacks(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    if data == "generate":
        if user_id in user_sessions:
            await callback_query.answer("Session already active!", show_alert=True)
            return
            
        user_sessions[user_id] = {"step": "phone"}
        await callback_query.message.edit_text(
            "📱 **Step 1: Phone Number**\n\n"
            "Send your phone number in international format:\n"
            "• **+919876543210** (India)\n"
            "• **+1234567890** (US)\n\n"
            "Or /cancel to stop."
        )
    
    elif data == "help":
        text = f"""📖 **Help Guide**

**Steps to generate session:**
1. Click Generate Session  
2. Enter phone number with country code
3. Enter verification code
4. Enter 2FA password (if enabled)
5. Copy your session string

**Support:** @{SUPPORT_CHANNEL}"""
        
        await callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Generate", callback_data="generate")],
                [InlineKeyboardButton("📢 Support", url=f"https://t.me/{SUPPORT_CHANNEL}")]
            ])
        )
    
    await callback_query.answer()

# Handle text messages
@bot.on_message(filters.text & filters.private)
async def handle_text(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text.startswith('/'):
        return
        
    if user_id not in user_sessions:
        await message.reply_text(
            "🤖 Welcome! Use /generate to start session generation.",
            reply_markup=start_keyboard()
        )
        return
        
    session = user_sessions[user_id]
    step = session["step"]
    
    if step == "phone":
        await handle_phone(client, message, text, session)
    elif step == "code":
        await handle_code(client, message, text, session)
    elif step == "password":
        await handle_password(client, message, text, session)

async def handle_phone(client, message, phone, session):
    user_id = message.from_user.id
    
    if not validate_phone(phone):
        await message.reply_text(
            "❌ Invalid format! Send phone with country code:\n"
            "• **+919876543210**\n"
            "• **+1234567890**"
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
        
        session["client"] = user_client
        session["phone"] = phone
        session["phone_code_hash"] = sent_code.phone_code_hash
        session["step"] = "code"
        
        await message.reply_text(
            "📨 **Step 2: Verification Code**\n\n"
            "I sent a 6-digit code to your Telegram.\n\n"
            "Send me that code here:\n\n"
            "Or /cancel to stop."
        )
        
    except PhoneNumberInvalid:
        await message.reply_text("❌ Invalid phone number! Check and try again.")
        if user_id in user_sessions:
            del user_sessions[user_id]
    except FloodWait as e:
        await message.reply_text(f"⏳ Flood wait! Try again in {e.value} seconds.")
        if user_id in user_sessions:
            del user_sessions[user_id]
    except Exception as e:
        await message.reply_text("❌ Error! Try again with /generate")
        logger.error(f"Phone error: {e}")
        if user_id in user_sessions:
            del user_sessions[user_id]

async def handle_code(client, message, code, session):
    user_id = message.from_user.id
    
    if not validate_code(code):
        await message.reply_text("❌ Invalid code! Send 6-digit code only.")
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
        
        success_msg = f"""
✅ **Session Generated Successfully!**

**Your String Session:**
```{string_session}```

**Important:**
🔒 Keep this session secure
🗑️ Regenerate if compromised  
💾 Store safely

**Support:** @{SUPPORT_CHANNEL}

Thank you! 🎉
        """
        
        await message.reply_text(
            success_msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Support", url=f"https://t.me/{SUPPORT_CHANNEL}")],
                [InlineKeyboardButton("🔄 New Session", callback_data="generate")]
            ]),
            disable_web_page_preview=True
        )
        
        # Cleanup
        await user_client.disconnect()
        del user_sessions[user_id]
        
    except PhoneCodeInvalid:
        await message.reply_text("❌ Wrong code! Check and try again.")
    except PhoneCodeExpired:
        await message.reply_text("❌ Code expired! Start over with /generate")
        await session["client"].disconnect()
        del user_sessions[user_id]
    except SessionPasswordNeeded:
        session["step"] = "password"
        await message.reply_text(
            "🔒 **Step 3: 2FA Password**\n\n"
            "Your account has 2FA enabled.\n\n"
            "Send your 2FA password:\n\n"
            "Or /cancel to stop."
        )
    except Exception as e:
        await message.reply_text("❌ Error! Start over with /generate")
        logger.error(f"Code error: {e}")
        if "client" in session:
            await session["client"].disconnect()
        del user_sessions[user_id]

async def handle_password(client, message, password, session):
    user_id = message.from_user.id
    
    try:
        user_client = session["client"]
        await user_client.check_password(password)
        
        # Generate session
        string_session = await user_client.export_session_string()
        
        success_msg = f"""
✅ **Session Generated Successfully!**

**Your String Session:**
```{string_session}```

**Important:**
🔒 Keep this session secure
🗑️ Regenerate if compromised
💾 Store safely

**Support:** @{SUPPORT_CHANNEL}

Thank you! 🎉
        """
        
        await message.reply_text(
            success_msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Support", url=f"https://t.me/{SUPPORT_CHANNEL}")],
                [InlineKeyboardButton("🔄 New Session", callback_data="generate")]
            ]),
            disable_web_page_preview=True
        )
        
        # Cleanup
        await user_client.disconnect()
        del user_sessions[user_id]
        
    except PasswordHashInvalid:
        await message.reply_text("❌ Wrong 2FA password! Try again.")
    except Exception as e:
        await message.reply_text("❌ Error! Start over with /generate")
        logger.error(f"Password error: {e}")
        if "client" in session:
            await session["client"].disconnect()
        del user_sessions[user_id]

# Start bot
async def main():
    await bot.start()
    print("✅ Bot Started Successfully!")
    print("🤖 Bot is now running...")
    
    # Get bot info
    me = await bot.get_me()
    print(f"Bot: @{me.username}")
    print(f"Name: {me.first_name}")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
