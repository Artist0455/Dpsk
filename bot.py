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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot configuration from environment variables
API_ID = int(os.environ.get("API_ID", "25136703"))
API_HASH = os.environ.get("API_HASH", "accfaf5ecd981c67e481328515c39f89")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8350139839:AAEgtaB1FpNTCqnCVIPHu0Q_KdJaok_slYU")

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

🤖 **String Session Generator Bot**

I can generate **Pyrogram** string sessions for your Telegram account.

**Click below to start generating your session:**"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Generate Pyrogram Session", callback_data="generate")],
            [InlineKeyboardButton("📢 Support Channel", url="https://t.me/shribots")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
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

**To Generate Pyrogram Session:**
1. Click **Generate Session** button
2. Send your phone number (with country code)
3. Send the verification code you receive
4. If you have 2FA, send your password
5. Copy your generated session string

**Example Phone Numbers:**
• +919876543210 (India)
• +1234567890 (US)

**What is Pyrogram Session?**
It's a string that allows you to use your Telegram account with Pyrogram library.

**Safety Tips:**
🔒 Never share your session string
🗑️ Regenerate if compromised
💾 Store it securely

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
        await message.reply_text("⚠️ You have an active session! Please complete it first or use /cancel to start over.")
        return
    
    user_sessions[user_id] = {"step": "phone"}
    
    await message.reply_text(
        "📱 **Step 1: Phone Number**\n\n"
        "Please send your phone number in international format:\n\n"
        "**Examples:**\n"
        "• `+919876543210` (India)\n"
        "• `+1234567890` (US)\n"
        "• `+441234567890` (UK)\n\n"
        "🔸 **Must start with +**\n"
        "🔸 **Include country code**\n\n"
        "Type /cancel to stop the process."
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
    else:
        await message.reply_text("ℹ️ No active session found. Use /generate to start.")

@app.on_callback_query()
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
                "📱 **Step 1: Phone Number**\n\n"
                "Please send your phone number in international format:\n\n"
                "**Examples:**\n"
                "• `+919876543210` (India)\n"
                "• `+1234567890` (US)\n\n"
                "Type /cancel to stop the process."
            )
            
        elif data == "help":
            help_text = """
📖 **Quick Guide:**

1. **Click Generate Session**
2. **Send Phone Number** (with + country code)
3. **Send Verification Code** (6-digit)
4. **Get Your Session String**

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
    
    # Ignore command messages
    if text.startswith('/'):
        return
    
    # If no active session
    if user_id not in user_sessions:
        await message.reply_text(
            "👋 Welcome! Use /generate to start session generation or /help for instructions."
        )
        return
    
    session = user_sessions[user_id]
    current_step = session.get("step", "phone")
    
    if current_step == "phone":
        await handle_phone_input(client, message, text, session)
    elif current_step == "code":
        await handle_code_input(client, message, text, session)
    elif current_step == "password":
        await handle_password_input(client, message, text, session)

async def handle_phone_input(client, message, phone, session):
    user_id = message.from_user.id
    
    # Validate phone number
    if not phone.startswith('+') or len(phone) < 10:
        await message.reply_text(
            "❌ **Invalid Phone Number Format!**\n\n"
            "Please send in **international format**:\n\n"
            "**Valid Examples:**\n"
            "• `+919876543210`\n"
            "• `+1234567890`\n\n"
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
        
        # Update session data
        session["client"] = user_client
        session["phone"] = phone
        session["phone_code_hash"] = sent_code.phone_code_hash
        session["step"] = "code"
        
        await message.reply_text(
            "📨 **Step 2: Verification Code**\n\n"
            "✅ **Verification code sent successfully!**\n\n"
            "Please check your Telegram messages and send me the **6-digit code** you received.\n\n"
            "Type /cancel to stop the process."
        )
        logger.info(f"Verification code sent to {phone}")
        
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
            "❌ **Error sending verification code!**\n\n"
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
        success_text = f"""
✅ **PYROGRAM STRING SESSION GENERATED SUCCESSFULLY!**

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
