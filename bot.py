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
It's a way to authorize your Telegram account in Pyrogram apps.

**How to Generate:**
1. Use /generate or click Generate button
2. Send your phone number (with country code)
3. Send the 6-digit verification code
4. If you have 2FA, send your password
5. Copy your generated session string

**Example Phone Numbers:**
• +919876543210 (India)
• +1234567890 (US)

**Safety Tips:**
🔒 Never share your session string
🔑 Store it securely

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
            "⚠️ **You already have an active session!**\n\nPlease complete your current session first or use /cancel to start over.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel Session", callback_data="cancel")]
            ])
        )
        return
    
    user_sessions[user_id] = {"step": "phone"}
    
    await message.reply_text(
        "📱 **Step 1 of 3: Phone Number**\n\n"
        "Please send your **phone number** in international format:\n\n"
        "**Examples:**\n"
        "• +919876543210 (India)\n"
        "• +1234567890 (US)\n"
        "• +441234567890 (UK)\n\n"
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
        f"📢 **Support Channel**\n\nJoin our channel for updates and support:\n**@{SUPPORT_CHANNEL}**",
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
                "• +919876543210 (India)\n"
                "• +1234567890 (US)\n\n"
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
                "✅ **Session cancelled!**\n\nYou can start a new session anytime:",
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
    
    if text.startswith('/'):
        return
    
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
    
    if not re.match(r'^\+\d{10,15}$', phone):
        await message.reply_text(
            "❌ **Invalid Phone Number Format!**\n\n"
            "Please send in **international format**:\n\n"
            "**Valid Examples:**\n"
            "• +919876543210\n"
            "• +1234567890\n\n"
            "🔸 **Must start with +**\n"
            "🔸 **10-15 digits only**\n\n"
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
            "📨 **Step 2 of 3: Verification Code**\n\n"
            "✅ **Verification code sent!**\n\n"
            "Please check your Telegram messages and send me the **6-digit code** you received.\n\n"
            "Type /cancel to stop."
        )
        logger.info(f"Code sent to {phone}")
        
    except PhoneNumberInvalid:
        await message.reply_text(
            "❌ **Invalid Phone Number!**\n\nPlease check and try again with correct country code."
        )
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    except FloodWait as e:
        wait_time = e.value
        await message.reply_text(
            f"⏳ **Too Many Attempts!**\n\nPlease wait **{wait_time} seconds** before trying again."
        )
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    except Exception as e:
        logger.error(f"Phone error: {e}")
        await message.reply_text("❌ **Error sending code!**\n\nPlease try again with /generate")
        if user_id in user_sessions:
            del user_sessions[user_id]

async def handle_code_input(client, message, code, session):
    user_id = message.from_user.id
    
    if not (code.isdigit() and len(code) == 6):
        await message.reply_text(
            "❌ **Invalid Code Format!**\n\nPlease send exactly **6 digits**:\n\n**Example:** 123456"
        )
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
        
        # FIXED: Simple success message without complex f-string
        success_msg = f"🎉 **STRING SESSION GENERATED SUCCESSFULLY!** 🎉\n\n"
        success_msg += f"**Your Session String:**\n```{string_session}```\n\n"
        success_msg += f"**Important Instructions:**\n"
        success_msg += f"🔒 **KEEP IT SECURE** - Never share with anyone\n"
        success_msg += f"🗑️ **REGENERATE** if compromised\n"
        success_msg += f"💾 **STORE SAFELY** - Save in secure place\n\n"
        success_msg += f"**Usage in Pyrogram:**\n"
        success_msg += f"```python\nfrom pyrogram import Client\n\n"
        success_msg += f"app = Client(\n"
        success_msg += f"    \"my_account\",\n"
        success_msg += f"    session_string=\"{string_session}\",\n"
        success_msg += f"    api_id=API_ID,\n"
        success_msg += f"    api_hash=API_HASH\n"
        success_msg += f")\n```\n\n"
        success_msg += f"**Support:** @{SUPPORT_CHANNEL}\n\n"
        success_msg += f"⚠️ **This is your account access key - Guard it carefully!**"
        
        await message.reply_text(
            success_msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Support Channel", url=f"https://t.me/{SUPPORT_CHANNEL}")],
                [InlineKeyboardButton("🔄 Generate New", callback_data="generate")]
            ]),
            disable_web_page_preview=True
        )
        
        logger.info(f"Session generated for user {user_id}")
        await user_client.disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    except PhoneCodeInvalid:
        await message.reply_text("❌ **Invalid Verification Code!**\n\nPlease check and enter the **latest code** you received.")
    
    except PhoneCodeExpired:
        await message.reply_text("❌ **Code Expired!**\n\nPlease start over with /generate to get a new code.")
        await session["client"].disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    except SessionPasswordNeeded:
        session["step"] = "password"
        await message.reply_text(
            "🔐 **Step 3 of 3: 2FA Password**\n\n"
            "Your account has **Two-Step Verification** enabled.\n\n"
            "Please send your **2FA password** to continue:\n\n"
            "Type /cancel to stop."
        )
    
    except FloodWait as e:
        await message.reply_text(f"⏳ **Too Many Attempts!**\n\nPlease wait **{e.value} seconds** before trying again.")
        await session["client"].disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    except Exception as e:
        logger.error(f"Code error: {e}")
        await message.reply_text("❌ **Error verifying code!**\n\nPlease start over with /generate")
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
        
        # FIXED: Simple success message
        success_msg = f"🎉 **STRING SESSION GENERATED SUCCESSFULLY!** 🎉\n\n"
        success_msg += f"**Your Session String:**\n```{string_session}```\n\n"
        success_msg += f"**Important Instructions:**\n"
        success_msg += f"🔒 **KEEP IT SECURE** - Never share with anyone\n"
        success_msg += f"🗑️ **REGENERATE** if compromised\n"
        success_msg += f"💾 **STORE SAFELY** - Save in secure place\n\n"
        success_msg += f"**Support:** @{SUPPORT_CHANNEL}\n\n"
        success_msg += f"✅ **2FA verification successful!**"
        
        await message.reply_text(
            success_msg,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Support Channel", url=f"https://t.me/{SUPPORT_CHANNEL}")],
                [InlineKeyboardButton("🔄 Generate New", callback_data="generate")]
            ]),
            disable_web_page_preview=True
        )
        
        logger.info(f"Session generated with 2FA for user {user_id}")
        await user_client.disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]
    
    except PasswordHashInvalid:
        await message.reply_text("❌ **Invalid 2FA Password!**\n\nPlease check your password and try again.")
    
    except Exception as e:
        logger.error(f"Password error: {e}")
        await message.reply_text("❌ **Error verifying password!**\n\nPlease start over with /generate")
        if "client" in session:
            await session["client"].disconnect()
        if user_id in user_sessions:
            del user_sessions[user_id]

# Start the bot
async def main():
    await bot.start()
    print("\n" + "="*60)
    print("🤖 STRING SESSION BOT STARTED SUCCESSFULLY!")
    print("="*60)
    
    me = await bot.get_me()
    print(f"Bot Username: @{me.username}")
    print(f"Bot Name: {me.first_name}")
    print(f"Support: @{SUPPORT_CHANNEL}")
    print("Status: ✅ ACTIVE & RUNNING")
    print("="*60)
    print("💡 Send /start to your bot to test it!")
    print("="*60)
    
    await idle()

if __name__ == "__main__":
    print("🚀 Starting Telegram String Session Bot...")
    asyncio.run(main())
