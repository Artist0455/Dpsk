from flask import Flask, request, jsonify
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import threading
import os
import logging
import time

# Flask app setup
app = Flask(__name__)

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
                f"sessions/{user_id}_{int(time.time())}",
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
    
    def delete_user_session(self, user_id):
        """Delete user session"""
        if user_id in self.sessions:
            try:
                client = self.sessions[user_id]['client']
                if client.is_connected:
                    client.disconnect()
            except:
                pass
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
            reply_markup=get_start_keyboard()
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
        reply_markup=get_support_keyboard()
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
        
        await message.reply_text(
            "📱 **Step 1: Phone Number**\n\n"
            "Please send your phone number in international format:\n"
            "• Example: **+919876543210**\n"
            "• Example: **+1234567890**\n\n"
            "Or use /cancel to stop the process."
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
            
            await callback_query.message.edit_text(
                "📱 **Step 1: Phone Number**\n\n"
                "Please send your phone number in international format:\n"
                "• Example: **+919876543210**\n"
                "• Example: **+1234567890**\n\n"
                "Or use /cancel to stop the process."
            )
            
        elif data == "help":
            await callback_query.message.edit_text(
                HELP_MESSAGE,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🚀 Generate Session", callback_data="generate")],
                    [InlineKeyboardButton("📢 Support Channel", url=f"https://t.me/{SUPPORT_CHANNEL}")]
                ])
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
    if not (phone_number.startswith('+') and len(phone_number) > 10):
        await message.reply_text(
            "❌ Invalid phone number format.\n\n"
            "Please send your phone number in international format:\n"
            "• **+919876543210** (India)\n"
            "• **+1234567890** (US)\n\n"
            "Make sure it starts with '+' and includes country code."
        )
        return
    
    try:
        # Create user session if not exists
        if not session_manager.get_user_session(user_id):
            session_manager.create_user_session(user_id, phone_number)
            user_session = session_manager.get_user_session(user_id)
        
        # Create user client and send code
        user_client = user_session['client']
        await user_client.connect()
        
        sent_code = await user_client.send_code(phone_number)
        
        # Update session data
        user_session['phone_code_hash'] = sent_code.phone_code_hash
        session_manager.update_session_step(user_id, 'code')
        
        await message.reply_text(
            "📨 **Step 2: Verification Code**\n\n"
            "I've sent a verification code to your Telegram account.\n\n"
            "Please check your messages and send me the **6-digit code** you received.\n\n"
            "Or use /cancel to stop the process."
        )
        logger.info(f"Verification code sent to {phone_number}")
        
    except Exception as e:
        error_msg = str(e).lower()
        if "phone number invalid" in error_msg:
            await message.reply_text("❌ Invalid phone number.\n\nPlease check your phone number and try again with country code.")
        elif "flood" in error_msg:
            await message.reply_text("⏳ Too many attempts. Please wait a while before trying again.")
        else:
            await message.reply_text("❌ Error sending verification code. Please try again with /generate")
            logger.error(f"Error sending code: {e}")
        
        # Clean up
        session_manager.delete_user_session(user_id)

async def handle_verification_code(client: Client, message: Message, user_session, code):
    """Handle verification code input"""
    user_id = message.from_user.id
    phone_number = user_session['phone_number']
    
    # Validate code format
    if not (code.isdigit() and len(code) == 6):
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
        
        # Send success message - FIXED: No f-string issue
        success_message = f"""✅ **String Session Generated Successfully!**

**Your String Session:**
```{string_session}```

**Important Instructions:**
🔒 **Keep it Secure:** Never share this session string
🗑️ **Regenerate if compromised:** Use /generate to create new one
💾 **Store Safely:** Save it in a secure place

**Usage in Pyrogram:**
```python
from pyrogram import Client

app = Client(
    "my_account",
    session_string="{string_session}",
    api_id=API_ID,
    api_hash=API_HASH
)
