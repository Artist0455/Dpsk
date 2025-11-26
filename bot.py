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

# Bot configuration - APNA BOT TOKEN YAHI DALNA
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

# Welcome Message with emojis
WELCOME_MESSAGE = """
🎉 **Welcome to String Session Generator Bot!** 🎉

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

🔒 **Your privacy is safe with us!**
"""

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

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Start", callback_data="back_start")]
    ])

# Start command with welcome message
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
        logger.info(f"Start command from user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

# Help command
@bot.on_message(filters.command("help"))
async def help_command(client, message: Message):
    help_text = f"""
📖 **Help Guide - String Session Bot**

**What is String Session?**
It's a way to authorize your Telegram account in Pyrogram apps without using bot tokens.

**How to Generate:**
1. Use /generate or click Generate button
2. Send your phone number (with country code)
3. Send the 6-digit verification code
4. If you have 2FA, send your password
5. Copy your generated session string

**Example Phone Numbers:**
• **+919876543210** (India)
• **+1234567890** (US)

**Safety Tips:**
🔒 Never share your session string
🔑 Store it securely
🔄 Regenerate if compromised

**Need Help?** Join @{SUPPORT_CHANNEL}
"""
    
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
        await message.reply_text(
            "⚠️ **You already have an active session!**\n\n"
            "Please complete your current session first or use /cancel to start over.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel Session", callback_data="cancel")]
            ])
        )
        return
    
    # Start new session
    user_sessions[user_id] = {"step": "phone"}
    
    await message.reply_text(
        "📱 **Step 1 of 3: Phone Number**\n\n"
        "Please send your **phone number** in international format:\n\n"
        "**Examples:**\n"
        "• `+919876543210` (India)\n"
        "• `+1234567890` (US)\n"
        "• `+441234567890` (UK)\n\n"
        "🔸 **Must start with +**\n"
        "🔸 **Include country code**\n\n"
        "Type /cancel to stop.",
        disable_web_page_preview=True
    )

# Cancel command
@bot.on_message(filters.command("cancel"))
async def cancel_command(client, message: Message):
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        # Clean up client if exists
        if "client" in user_sessions[user_id]:
            try:
                await user_sessions[user_id]["client"].disconnect()
            except:
                pass
        del user_sessions[user_id]
        await message.reply_text("✅ **Session cancelled!** Use /generate to start again.")
    else:
        await message.reply_text("ℹ️ **No active session found.** Use /generate to start.")

# Support command
@bot.on_message(filters.command("support"))
async def support_command(client, message: Message):
    await message.reply_text(
        f"📢 **Support Channel**\n\n"
        f"Join our channel for updates and support:\n"
        f"**@{SUPPORT_CHANNEL}**\n\n"
        f"Feel free to ask any questions! 💬",
        reply_markup=support_keyboard()
    )

# Handle callback queries
@bot.on_callback_query()
async def handle_callbacks(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    try:
        if data == "generate":
            if user_id in user_sessions:
                await callback_query.answer("You already have an active session!", show_alert=True)
                return
            
            user_sessions[user_id] = {"step": "phone"}
            
            await callback_query.message.edit_text(
                "📱 **Step 1 of 3: Phone Number**\n\n"
                "Please send your **phone number** in international format:\n\n"
                "**Examples:**\n"
                "• `+919876543210` (India)\n"
                "• `+1234567890` (US)\n"
                "• `+441234567890` (UK)\n\n"
                "🔸 **Must start with +**\n"
                "🔸 **Include country code**\n\n"
                "Type /cancel to stop.",
                disable_web_page_preview=True
            )
        
        elif data == "help":
            help_text = f"""
📖 **How to Use This Bot:**

**Step-by-Step Guide:**
1. **Click Generate Session** 
2. **Send Phone Number** (with country code)
3. **Send Verification Code** (6-digit)
4. **Send 2FA Password** (if enabled)
5. **Copy Your Session String**

**Safety Instructions:**
🔐 Keep your session string private
🗑️ Delete if shared accidentally  
💾 Store in secure place

**Support:** @{SUPPORT_CHANNEL}
"""
            await callback_query.message.edit_text(
                help_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
                    [InlineKeyboardButton("📢 Support", url=f"https://t.me/{SUPPORT_CHANNEL}")]
                ]),
                disable_web_page_preview=True
            )
        
        elif data == "back_start":
            welcome_text = f"👋 **Welcome back!**\n\n{WELCOME_MESSAGE}"
            await callback_query.message.edit_text(
                welcome_text,
                reply_markup=start_keyboard(),
                disable_web_page_preview=True
            )
        
        elif data == "cancel":
            if user_id in user_sessions:
                if "client" in user_sessions[user_id]:
                    try:
                        await user_sessions[user_id]["client"].disconnect()
                    except:
                        pass
                del user_sessions[user_id]
            
            await callback_query.message.edit_text(
                "✅ **Session cancelled!**\n\n"
                "You can start a new session anytime using the button below:",
                reply_markup=start_keyboard()
            )
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await callback_query.answer("Error occurred!", show_alert=True)

# Handle all text messages
@bot.on_message(filters.text & filters.private)
async def handle_text_messages(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Ignore commands
    if text.startswith('/'):
        return
    
    # If no active session, show start message
    if user_id not in user_sessions:
        await message.reply_text(
            f"👋 **Welcome!**\n\n{WELCOME_MESSAGE}",
            reply_markup=start_keyboard(),
            disable_web_page_preview=True
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
    
    # Validate phone number
    if not re.match(r'^\+\d{10,15}$', phone):
        await message.reply_text(
            "❌ **Invalid Phone Number Format!**\n\n"
            "Please send in **international format**:\n\n"
            "**Valid Examples:**\n"
            "• `+919876543210`\n"
            "• `+1234567890`\n"
            "• `+441234567890`\n\n"
            "🔸 **Must start with +**\n"
            "🔸 **10-15 digits only**\n\n"
            "Try again or /cancel to stop."
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
        
        # Send verification code
        sent_code = await user_client.send_code(phone)
        
        # Update session
        session["client"] = user_client
        session["phone"] = phone
        session["phone_code_hash"] = sent_code.phone_code_hash
        session["step"] = "code"
        
        await message.reply_text(
            "📨 **Step 2 of 3: Verification Code**\n\n"
            "✅ **Verification code sent!**\n\n"
            "Please check your Telegram messages and send me the **6-digit code** you received.\n\n"
            "🔹 **Code is 6 digits** (e.g., 123456)\n"
            "🔹 **Enter code quickly** (expires in few minutes)\n"
            "🔹 **Check both PM and Saved Messages**\n\n"
            "Type /cancel to stop."
        )
        logger.info(f"Code sent to {phone}")
        
    except PhoneNumberInvalid:
        await message.reply_text(
            "❌ **Invalid Phone Number!**\n\n"
            "The phone number you entered is invalid.\n"
            "Please check and try again with correct country code."
        )
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    except FloodWait as e:
        wait_time = e.value
        await message.reply_text(
            f"⏳ **Too Many Attempts!**\n\n"
            f"Please wait **{wait_time} seconds** before trying again.\n"
            f"This is a Telegram restriction for security."
        )
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    except Exception as e:
        logger.error(f"Phone error: {e}")
        await message.reply_text(
            "❌ **Error sending code!**\n\n"
            "Please try again with /generate\n"
            "If problem continues, contact support."
        )
        if user_id in user_sessions:
            del user_sessions[user_id]

async def handle_code_input(client, message, code, session):
    user_id = message.from_user.id
    
    # Validate code
    if not (code.isdigit() and len(code) == 6):
        await message.reply_text(
            "❌ **Invalid Code Format!**\n\n"
            "Please send exactly **6 digits**:\n\n"
            "**Example:** `123456`\n\n"
            "Check your Telegram messages and send the correct code."
        )
        return
    
    try:
        user_client = session["client"]
        phone = session["phone"]
        
        # Sign in with code
        await user_client.sign_in(
            phone_number=phone,
            phone_code_hash=session["phone_code_hash"],
            phone_code=code
        )
        
        # Generate string session
        string_session = await user_client.export_session_string()
        
        # Success message
        success_msg = f"""
🎉 **STRING SESSION GENERATED SUCCESSFULLY!** 🎉

**Your Session String:**
```{string_session}```

**Important Instructions:**
🔒 **KEEP IT SECURE** - Never share with anyone
🗑️ **REGENERATE** if you suspect it's compromised  
💾 **STORE SAFELY** - Save in secure place

**Usage in Pyrogram:**
```python
from pyrogram import Client

app = Client(
    "my_account",
    session_string="{string_session}",
    api_id=API_ID,
    api_hash=API_HASH
)
