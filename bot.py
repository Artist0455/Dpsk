import os
import logging
import asyncio
import re
from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid, FloodWait
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8350139839:AAHKChyb6VhRtJYx8R4BKDttllh-AhbSPMM"
API_ID = 25136703
API_HASH = "accfaf5ecd981c67e481328515c39f89"
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

# Welcome Message
WELCOME_MESSAGE = """🎉 **Welcome to String Session Generator Bot!** 🎉

🤖 **I Can Generate Pyrogram String Sessions**

✨ **Features:**
✅ Fast & Secure Session Generation
✅ 2FA Password Support  
✅ 100% Free Service
✅ Easy to Use

📱 **How to Use:**
1. Click /generate to start
2. Enter your phone number
3. Enter verification code
4. Get your string session!

🔒 **Your privacy is safe with us!**"""

# Keyboards
def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
        [InlineKeyboardButton("📢 Support Channel", url=f"https://t.me/{SUPPORT_CHANNEL}")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])

def support_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Support", url=f"https://t.me/{SUPPORT_CHANNEL}")]
    ])

# Start command
@bot.on_message(filters.command("start"))
async def start_command(client, message: Message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        
        welcome_text = f"👋 **Hello {first_name}!**\n\n{WELCOME_MESSAGE}"
        
        await message.reply_text(
            welcome_text,
            reply_markup=start_keyboard(),
            disable_web_page_preview=True
        )
        logger.info(f"✅ Start command from user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

# Help command
@bot.on_message(filters.command("help"))
async def help_command(client, message: Message):
    help_text = f"""📖 **Help Guide**

**How to Generate Session:**
1. Use /generate 
2. Send phone number (with country code)
3. Send verification code (6-digit)
4. Send 2FA password (if enabled)
5. Copy your session string

**Support:** @{SUPPORT_CHANNEL}"""
    
    await message.reply_text(
        help_text,
        reply_markup=support_keyboard(),
        disable_web_page_preview=True
    )

# Generate command
@bot.on_message(filters.command("generate"))
async def generate_command(client, message: Message):
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        await message.reply_text("⚠️ **You have an active session!** Use /cancel first.")
        return
    
    user_sessions[user_id] = {"step": "phone"}
    
    await message.reply_text(
        "📱 **Step 1: Phone Number**\n\n"
        "Send your phone number:\n"
        "• +919876543210 (India)\n"
        "• +1234567890 (US)\n\n"
        "Type /cancel to stop."
    )

# Cancel command
@bot.on_message(filters.command("cancel"))
async def cancel_command(client, message: Message):
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        if "client" in user_sessions[user_id]:
            try:
                await user_sessions[user_id]["client"].disconnect()
            except:
                pass
        del user_sessions[user_id]
        await message.reply_text("✅ **Session cancelled!** Use /generate to start again.")
    else:
        await message.reply_text("ℹ️ **No active session.** Use /generate to start.")

# Handle callback queries
@bot.on_callback_query()
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
                "Send your phone number:\n"
                "• +919876543210 (India)\n"
                "• +1234567890 (US)\n\n"
                "Type /cancel to stop."
            )
        
        elif data == "help":
            help_text = f"""📖 **How to Use:**

1. Click Generate Session
2. Send phone number  
3. Send verification code
4. Get your session string

**Support:** @{SUPPORT_CHANNEL}"""
            
            await callback_query.message.edit_text(
                help_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
                    [InlineKeyboardButton("📢 Support", url=f"https://t.me/{SUPPORT_CHANNEL}")]
                ])
            )
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await callback_query.answer("Error occurred!", show_alert=True)

# Handle text messages
@bot.on_message(filters.text & filters.private)
async def handle_text_messages(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text.startswith('/'):
        return
    
    if user_id not in user_sessions:
        await message.reply_text(
            f"👋 **Welcome!**\n\n{WELCOME_MESSAGE}",
            reply_markup=start_keyboard()
        )
        return
    
    session = user_sessions[user_id]
    current_step = session["step"]
    
    if current_step == "phone":
        await handle_phone_input(client, message, text, session)
    elif current_step == "code":
        await handle_code_input(client, message, text, session)
    elif current_step == "password":
        await handle_password_input(client, message, text, session)

async def handle_phone_input(client, message, phone, session):
    user_id = message.from_user.id
    
    if not re.match(r'^\+\d{10,15}$', phone):
        await message.reply_text(
            "❌ **Invalid format!**\n\n"
            "Send like: +919876543210\n\n"
            "Try again or /cancel to stop."
        )
        return
    
    try:
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
            "✅ **Code sent!**\n\n"
            "Send the 6-digit code you received.\n\n"
            "Type /cancel to stop."
        )
        logger.info(f"Code sent to {phone}")
        
    except PhoneNumberInvalid:
        await message.reply_text("❌ **Invalid number!** Check country code.")
        if user_id in user_sessions:
            del user_sessions[user_id]
    except FloodWait as e:
        await message.reply_text(f"⏳ **Wait {e.value} seconds** before trying.")
        if user_id in user_sessions:
            del user_sessions[user_id]
    except Exception as e:
        logger.error(f"Phone error: {e}")
        await message.reply_text("❌ **Error!** Try /generate again")
        if user_id in user_sessions:
            del user_sessions[user_id]

async def handle_code_input(client, message, code, session):
    user_id = message.from_user.id
    
    if not (code.isdigit() and len(code) == 6):
        await message.reply_text("❌ **Invalid code!** Send 6 digits only.")
        return
    
    try:
        user_client = session["client"]
        phone = session["phone"]
        
        await user_client.sign_in(
            phone_number=phone,
            phone_code_hash=session["phone_code_hash"],
            phone_code=code
        )
        
        string_session = await user_client.export_session_string()
        
        success_msg = f"🎉 **SESSION GENERATED!** 🎉\n\n"
        success_msg += f"**Your Session:**\n```{string_session}```\n\n"
        success_msg += f"🔒 **Keep it secure!**\n"
        success_msg += f"**Support:** @{SUPPORT_CHANNEL}"
        
        await message.reply_text(
            success_msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Support", url=f"https://t.me/{SUPPORT_CHANNEL}")],
                [InlineKeyboardButton("🔄 New Session", callback_data="generate")]
            ])
        )
        
        logger.info(f"Session generated for {user_id}")
        await user_client.disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    except PhoneCodeInvalid:
        await message.reply_text("❌ **Wrong code!** Check and try again.")
    except PhoneCodeExpired:
        await message.reply_text("❌ **Code expired!** Use /generate for new code.")
        await session["client"].disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]
    except SessionPasswordNeeded:
        session["step"] = "password"
        await message.reply_text(
            "🔐 **Step 3: 2FA Password**\n\n"
            "Send your 2FA password:\n\n"
            "Type /cancel to stop."
        )
    except FloodWait as e:
        await message.reply_text(f"⏳ **Wait {e.value} seconds**")
        await session["client"].disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]
    except Exception as e:
        logger.error(f"Code error: {e}")
        await message.reply_text("❌ **Error!** Use /generate again")
        if "client" in session:
            await session["client"].disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]

async def handle_password_input(client, message, password, session):
    user_id = message.from_user.id
    
    try:
        user_client = session["client"]
        await user_client.check_password(password)
        
        string_session = await user_client.export_session_string()
        
        success_msg = f"🎉 **SESSION GENERATED!** 🎉\n\n"
        success_msg += f"**Your Session:**\n```{string_session}```\n\n"
        success_msg += f"🔒 **Keep it secure!**\n"
        success_msg += f"✅ **2FA verified!**\n"
        success_msg += f"**Support:** @{SUPPORT_CHANNEL}"
        
        await message.reply_text(
            success_msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Support", url=f"https://t.me/{SUPPORT_CHANNEL}")],
                [InlineKeyboardButton("🔄 New Session", callback_data="generate")]
            ])
        )
        
        logger.info(f"2FA session for {user_id}")
        await user_client.disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    except PasswordHashInvalid:
        await message.reply_text("❌ **Wrong password!** Try again.")
    except Exception as e:
        logger.error(f"Password error: {e}")
        await message.reply_text("❌ **Error!** Use /generate again")
        if "client" in session:
            await session["client"].disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]

# Start bot
async def main():
    print("🚀 Starting Telegram Bot...")
    await bot.start()
    
    me = await bot.get_me()
    print(f"✅ Bot Started: @{me.username}")
    print(f"🤖 Name: {me.first_name}")
    print("📱 Bot is now running and responding...")
    
    # Keep running
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
