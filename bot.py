from flask import Flask, request, jsonify
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid, FloodWait
)
import asyncio
import threading
import os
import logging
import time
import re

# Flask app setup
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8350139839:AAHKChyb6VhRtJYx8R4BKDttllh-AhbSPMM")
API_ID = int(os.environ.get("API_ID", 25136703))
API_HASH = os.environ.get("API_HASH", "accfaf5ecd981c67e481328515c39f89")

# Support Channel
SUPPORT_CHANNEL = "shribots"

# Welcome Messages
WELCOME_MESSAGE = """
🤖 **Welcome to String Session Generator Bot!**

I will help you generate Pyrogram String Session for your Telegram account.

**Features:**
✅ Fast & Secure Session Generation
✅ Only Mobile Verification Required  
✅ No API ID/Hash Asked from Users
✅ 2FA Password Support
✅ 100% Free Service

Click /start to begin your session generation!
"""

START_MESSAGE = """
🎉 **String Session Generator Started!**

I'll help you generate a Pyrogram String Session for your Telegram account.

**How it works:**
1. Send your phone number (with country code)
2. You'll receive a verification code on Telegram
3. Send that verification code to me
4. Get your String Session instantly!

**Commands:**
/start - Show this message
/generate - Start session generation
/cancel - Cancel current process

Click /generate to begin! 🚀
"""

HELP_MESSAGE = f"""
📖 **Help Guide**

**What is String Session?**
String Session is a way to authorize your Telegram account in Pyrogram applications without using bot tokens.

**How to use:**
1. Use /generate to start
2. Enter your phone number (with country code)
3. Enter verification code sent to your Telegram
4. If you have 2FA, enter your password
5. Copy your generated string session

**Safety Tips:**
🔒 Never share your string session with anyone
🗑️ Regenerate if you suspect it's compromised
💾 Store it in a secure place

**Support:**
Join our channel for updates and support: @{SUPPORT_CHANNEL}
"""

# Initialize Pyrogram Client
bot = Client(
    "session_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_user_session(self, user_id, phone_number):
        """Create a new session for user"""
        try:
            client = Client(
                f"user_{user_id}",
                api_id=API_ID,
                api_hash=API_HASH,
                in_memory=True
            )
            
            self.sessions[user_id] = {
                'client': client,
                'phone_number': phone_number,
                'step': 'phone',
                'created_at': time.time()
            }
            
            logger.info(f"New session created for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating session for {user_id}: {e}")
            return False
    
    def get_user_session(self, user_id):
        """Get user session data"""
        return self.sessions.get(user_id)
    
    def update_session_step(self, user_id, step):
        """Update user session step"""
        if user_id in self.sessions:
            self.sessions[user_id]['step'] = step
            return True
        return False
    
    def delete_user_session(self, user_id):
        """Delete user session"""
        if user_id in self.sessions:
            try:
                session_data = self.sessions[user_id]
                client = session_data['client']
                if hasattr(client, 'is_connected') and client.is_connected:
                    client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting client: {e}")
            finally:
                del self.sessions[user_id]
                logger.info(f"Session deleted for user {user_id}")

# Initialize session manager
session_manager = SessionManager()

# Create inline keyboards
def get_start_keyboard():
    """Keyboard for start command"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
        [InlineKeyboardButton("📢 Support Channel", url=f"https://t.me/{SUPPORT_CHANNEL}")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ])

def get_support_keyboard():
    """Keyboard with support button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Support Channel", url=f"https://t.me/{SUPPORT_CHANNEL}")]
    ])

def get_session_keyboard():
    """Keyboard after session generation"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Support Channel", url=f"https://t.me/{SUPPORT_CHANNEL}")],
        [InlineKeyboardButton("🔄 Generate New", callback_data="generate")]
    ])

def validate_phone_number(phone):
    """Validate phone number format"""
    pattern = r'^\+\d{10,15}$'
    return re.match(pattern, phone) is not None

def validate_code(code):
    """Validate verification code format"""
    return code.isdigit() and len(code) == 6

# Bot Handlers
@bot.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handle /start command"""
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        
        welcome_text = f"👋 Hello **{first_name}**!\n\n{WELCOME_MESSAGE}"
        
        await message.reply_text(
            welcome_text,
            reply_markup=get_start_keyboard(),
            disable_web_page_preview=True
        )
        logger.info(f"Start command received from {user_id}")
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@bot.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle /help command"""
    await message.reply_text(
        HELP_MESSAGE,
        reply_markup=get_support_keyboard(),
        disable_web_page_preview=True
    )

@bot.on_message(filters.command("generate"))
async def generate_command(client: Client, message: Message):
    """Handle /generate command"""
    try:
        user_id = message.from_user.id
        
        # Check if user already has active session
        if session_manager.get_user_session(user_id):
            await message.reply_text("⚠️ You already have an active session. Please complete it first or use /cancel to start over.")
            return
        
        # Create new session
        session_manager.create_user_session(user_id, "")
        
        await message.reply_text(
            "📱 **Step 1: Phone Number**\n\n"
            "Please send your phone number in international format:\n"
            "• Example: **+919876543210**\n"
            "• Example: **+1234567890**\n\n"
            "Or use /cancel to stop the process.",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error in generate command: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@bot.on_message(filters.command("cancel"))
async def cancel_command(client: Client, message: Message):
    """Handle /cancel command"""
    user_id = message.from_user.id
    session_manager.delete_user_session(user_id)
    await message.reply_text("✅ Process cancelled. Use /generate to start again.")

@bot.on_message(filters.command("support"))
async def support_command(client: Client, message: Message):
    """Handle /support command"""
    await message.reply_text(
        f"📢 **Support Channel**\n\nJoin our channel for updates and support:\n@**{SUPPORT_CHANNEL}**",
        reply_markup=get_support_keyboard()
    )

# Callback query handler
@bot.on_callback_query()
async def handle_callbacks(client: Client, callback_query):
    """Handle inline keyboard callbacks"""
    try:
        data = callback_query.data
        user_id = callback_query.from_user.id
        
        if data == "generate":
            # Check if user already has active session
            if session_manager.get_user_session(user_id):
                await callback_query.answer("You already have an active session!", show_alert=True)
                return
            
            # Create new session
            session_manager.create_user_session(user_id, "")
            
            await callback_query.message.edit_text(
                "📱 **Step 1: Phone Number**\n\n"
                "Please send your phone number in international format:\n"
                "• Example: **+919876543210**\n"
                "• Example: **+1234567890**\n\n"
                "Or use /cancel to stop the process.",
                disable_web_page_preview=True
            )
            
        elif data == "help":
            await callback_query.message.edit_text(
                HELP_MESSAGE,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
                    [InlineKeyboardButton("📢 Support Channel", url=f"https://t.me/{SUPPORT_CHANNEL}")]
                ]),
                disable_web_page_preview=True
            )
            
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error in callback: {e}")
        await callback_query.answer("Error occurred!", show_alert=True)

@bot.on_message(filters.text & filters.private)
async def handle_text_messages(client: Client, message: Message):
    """Handle all text messages"""
    try:
        user_id = message.from_user.id
        text = message.text.strip()
        
        # Ignore command messages
        if text.startswith('/'):
            return
        
        user_session = session_manager.get_user_session(user_id)
        
        if not user_session:
            # No active session - prompt to start
            await message.reply_text(
                "🤖 Welcome! I can generate Pyrogram string sessions.\n\nUse /generate to start the process or /help for more information.",
                reply_markup=get_start_keyboard()
            )
            return
        
        current_step = user_session['step']
        
        if current_step == 'phone':
            await handle_phone_number(client, message, user_session, text)
        
        elif current_step == 'code':
            await handle_verification_code(client, message, user_session, text)
        
        elif current_step == 'password':
            await handle_2fa_password(client, message, user_session, text)
            
    except Exception as e:
        logger.error(f"Error handling text message: {e}")
        await message.reply_text("❌ An error occurred. Please use /generate to start over.")

async def handle_phone_number(client: Client, message: Message, user_session, phone_number):
    """Handle phone number input"""
    user_id = message.from_user.id
    
    # Validate phone number format
    if not validate_phone_number(phone_number):
        await message.reply_text(
            "❌ Invalid phone number format.\n\n"
            "Please send your phone number in international format:\n"
            "• **+919876543210** (India)\n"
            "• **+1234567890** (US)\n\n"
            "Make sure it starts with '+' and includes country code.",
            disable_web_page_preview=True
        )
        return
    
    try:
        # Update session with phone number
        user_session['phone_number'] = phone_number
        user_client = user_session['client']
        
        await user_client.connect()
        
        # Send verification code
        sent_code = await user_client.send_code(phone_number)
        
        # Update session data
        user_session['phone_code_hash'] = sent_code.phone_code_hash
        session_manager.update_session_step(user_id, 'code')
        
        await message.reply_text(
            "📨 **Step 2: Verification Code**\n\n"
            "I've sent a verification code to your Telegram account.\n\n"
            "Please check your messages and send me the **6-digit code** you received.\n\n"
            "Or use /cancel to stop the process.",
            disable_web_page_preview=True
        )
        logger.info(f"Verification code sent to {phone_number}")
        
    except PhoneNumberInvalid:
        await message.reply_text("❌ Invalid phone number.\n\nPlease check your phone number and try again with country code.")
        session_manager.delete_user_session(user_id)
    except FloodWait as e:
        await message.reply_text(f"⏳ Too many attempts. Please wait {e.value} seconds before trying again.")
        session_manager.delete_user_session(user_id)
    except Exception as e:
        error_msg = str(e).lower()
        await message.reply_text("❌ Error sending verification code. Please try again with /generate")
        logger.error(f"Error sending code: {e}")
        session_manager.delete_user_session(user_id)

async def handle_verification_code(client: Client, message: Message, user_session, code):
    """Handle verification code input"""
    user_id = message.from_user.id
    phone_number = user_session['phone_number']
    
    # Validate code format
    if not validate_code(code):
        await message.reply_text("❌ Invalid code format.\n\nPlease send the **6-digit** verification code you received.\nExample: **123456**")
        return
    
    try:
        user_client = user_session['client']
        
        # Sign in with the code
        await user_client.sign_in(
            phone_number=phone_number,
            phone_code_hash=user_session['phone_code_hash'],
            phone_code=code
        )
        
        # Generate string session
        string_session = await user_client.export_session_string()
        
        # Send success message
        success_message = (
            f"✅ **String Session Generated Successfully!**\n\n"
            f"**Your String Session:**\n"
            f"```{string_session}```\n\n"
            f"**Important Instructions:**\n"
            f"🔒 **Keep it Secure:** Never share this session string\n"
            f"🗑️ **Regenerate if compromised:** Use /generate to create new one\n"
            f"💾 **Store Safely:** Save it in a secure place\n\n"
            f"**Support:**\n"
            f"Join @{SUPPORT_CHANNEL} for help and updates.\n\n"
            f"🎉 **Thank you for using our service!**"
        )
        
        await message.reply_text(
            success_message,
            reply_markup=get_session_keyboard(),
            disable_web_page_preview=True
        )
        logger.info(f"String session generated for user {user_id}")
        
        # Clean up
        await user_client.disconnect()
        session_manager.delete_user_session(user_id)
        
    except PhoneCodeInvalid:
        await message.reply_text("❌ Invalid verification code.\n\nPlease check the code and try again.\nMake sure you're entering the latest code received.")
    except PhoneCodeExpired:
        await message.reply_text("❌ Verification code expired.\n\nPlease start over with /generate to get a new code.")
        session_manager.delete_user_session(user_id)
    except SessionPasswordNeeded:
        session_manager.update_session_step(user_id, 'password')
        await message.reply_text(
            "🔒 **Step 3: 2FA Password**\n\n"
            "Your account has two-step verification enabled.\n\n"
            "Please send your **2FA password** to continue.\n\n"
            "Or use /cancel to stop the process.",
            disable_web_page_preview=True
        )
    except FloodWait as e:
        await message.reply_text(f"⏳ Too many attempts. Please wait {e.value} seconds before trying again.")
        session_manager.delete_user_session(user_id)
    except Exception as e:
        await message.reply_text("❌ Error verifying code. Please start over with /generate")
        logger.error(f"Error verifying code: {e}")
        session_manager.delete_user_session(user_id)

async def handle_2fa_password(client: Client, message: Message, user_session, password):
    """Handle 2FA password input"""
    user_id = message.from_user.id
    
    try:
        user_client = user_session['client']
        
        # Check password and sign in
        await user_client.check_password(password=password)
        
        # Generate string session
        string_session = await user_client.export_session_string()
        
        # Send success message
        success_message = (
            f"✅ **String Session Generated Successfully!**\n\n"
            f"**Your String Session:**\n"
            f"```{string_session}```\n\n"
            f"**Important Instructions:**\n"
            f"🔒 **Keep it Secure:** Never share this session string\n"
            f"🗑️ **Regenerate if compromised:** Use /generate to create new one\n"
            f"💾 **Store Safely:** Save it in a secure place\n\n"
            f"**Support:**\n"
            f"Join @{SUPPORT_CHANNEL} for help and updates.\n\n"
            f"🎉 **Thank you for using our service!**"
        )
        
        await message.reply_text(
            success_message,
            reply_markup=get_session_keyboard(),
            disable_web_page_preview=True
        )
        logger.info(f"String session generated with 2FA for user {user_id}")
        
        # Clean up
        await user_client.disconnect()
        session_manager.delete_user_session(user_id)
        
    except PasswordHashInvalid:
        await message.reply_text("❌ Invalid 2FA password.\n\nPlease check your password and try again.\n\nOr use /cancel to stop the process.")
    except Exception as e:
        await message.reply_text("❌ Error verifying password. Please start over with /generate")
        logger.error(f"Error verifying 2FA: {e}")
        session_manager.delete_user_session(user_id)

# Flask Routes
@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "Telegram String Session Bot",
        "version": "2.0",
        "support_channel": f"@{SUPPORT_CHANNEL}",
        "bot_status": "active",
        "endpoints": {
            "home": "/",
            "health": "/health",
            "stats": "/stats"
        }
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "active_sessions": len(session_manager.sessions),
        "support_channel": SUPPORT_CHANNEL,
        "bot_connected": True
    })

@app.route('/stats')
def stats():
    return jsonify({
        "active_sessions": len(session_manager.sessions),
        "service": "String Session Generator Bot",
        "support": f"@{SUPPORT_CHANNEL}",
        "uptime": "running",
        "status": "operational"
    })

# Bot Runner Functions
async def start_telegram_bot():
    """Start the Telegram bot"""
    try:
        logger.info("🤖 Starting Telegram Bot...")
        await bot.start()
        
        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"✅ Bot Started Successfully: @{bot_info.username}")
        
        print("\n" + "="*60)
        print("🎉 TELEGRAM STRING SESSION BOT STARTED SUCCESSFULLY!")
        print("="*60)
        print(f"🤖 Bot: @{bot_info.username}")
        print(f"📛 Name: {bot_info.first_name}")
        print(f"🆔 ID: {bot_info.id}")
        print(f"📢 Support: @{SUPPORT_CHANNEL}")
        print(f"🔗 Status: ✅ ACTIVE & RUNNING")
        print(f"🌐 Deployment: 🚀 RENDER")
        print("="*60)
        print("💡 Send /start to your bot to test it!")
        print("="*60)
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        print(f"❌ BOT START FAILED: {e}")
        raise e

def run_bot():
    """Run bot in background thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_telegram_bot())
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
        print(f"❌ BOT STOPPED: {e}")
    finally:
        loop.close()

# Application Startup
if __name__ == "__main__":
    print("🚀 Initializing String Session Bot...")
    
    # Create sessions directory
    os.makedirs("sessions", exist_ok=True)
    
    # Start Telegram bot in background thread
    logger.info("Starting Telegram Bot in background thread...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Give bot time to start
    time.sleep(3)
    
    # Start Flask server
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask server on port {port}")
    
    print(f"🌐 Flask server starting on port {port}...")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )
