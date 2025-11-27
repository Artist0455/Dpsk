import os
import logging
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid, FloodWait
)
from telethon import TelegramClient, events, Button
from telethon.errors import (
    PhoneNumberInvalidError, PhoneCodeInvalidError, PhoneCodeExpiredError,
    SessionPasswordNeededError, PasswordHashInvalidError, FloodWaitError
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot configuration
API_ID = 25136703
API_HASH = "accfaf5ecd981c67e481328515c39f89"
BOT_TOKEN = "8350139839:AAEgtaB1FpNTCqnCVIPHu0Q_KdJaok_slYU"

# Initialize both clients
pyro_app = Client("pyro_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)
tele_client = TelegramClient("tele_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Store user sessions
user_sessions = {}

# ==================== PYROGRAM HANDLERS ====================

@pyro_app.on_message(filters.command("start"))
async def pyro_start_command(client, message: Message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        
        welcome_text = f"""
👋 **Hello {first_name}!**

🤖 **String Session Generator Bot**

I can generate both **Pyrogram** and **Telethon** string sessions for your Telegram account.

**Choose your library:**"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 Pyrogram Session", callback_data="pyro_generate")],
            [InlineKeyboardButton("⚡ Telethon Session", callback_data="tele_generate")],
            [InlineKeyboardButton("📢 Support Channel", url="https://t.me/shribots")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ])
        
        await message.reply_text(welcome_text, reply_markup=keyboard)
        logger.info(f"User {user_id} started the bot")
        
    except Exception as e:
        logger.error(f"Pyro start error: {e}")
        await message.reply_text("❌ An error occurred. Please try /start again.")

@pyro_app.on_message(filters.command("help"))
async def pyro_help_command(client, message: Message):
    help_text = """
📖 **How to Use This Bot:**

**For Pyrogram Session:**
1. Click **Pyrogram Session** button
2. Send your phone number (with country code)
3. Send verification code
4. Get your Pyrogram session string

**For Telethon Session:**
1. Click **Telethon Session** button  
2. Send your phone number (with country code)
3. Send verification code
4. Get your Telethon session string

**Example Phone Numbers:**
• +919876543210 (India)
• +1234567890 (US)

**Support:** @shribots
    """
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Pyrogram", callback_data="pyro_generate")],
        [InlineKeyboardButton("⚡ Telethon", callback_data="tele_generate")],
        [InlineKeyboardButton("📢 Support", url="https://t.me/shribots")]
    ])
    
    await message.reply_text(help_text, reply_markup=keyboard)

@pyro_app.on_message(filters.command("pyrogram"))
async def pyro_generate_command(client, message: Message):
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        await message.reply_text("⚠️ You have an active session! Use /cancel first.")
        return
    
    user_sessions[user_id] = {"step": "phone", "type": "pyrogram"}
    await message.reply_text("🔥 **Pyrogram Session**\n\nSend your phone number:\n**Example:** +919876543210\n\n/cancel to stop.")

@pyro_app.on_message(filters.command("telethon"))
async def tele_generate_command(client, message: Message):
    user_id = message.from_user.id
    
    if user_id in user_sessions:
        await message.reply_text("⚠️ You have an active session! Use /cancel first.")
        return
    
    user_sessions[user_id] = {"step": "phone", "type": "telethon"}
    await message.reply_text("⚡ **Telethon Session**\n\nSend your phone number:\n**Example:** +919876543210\n\n/cancel to stop.")

@pyro_app.on_message(filters.command("cancel"))
async def pyro_cancel_command(client, message: Message):
    user_id = message.from_user.id
    await cancel_session(user_id)
    await message.reply_text("✅ Session cancelled! Use /start to begin again.")

@pyro_app.on_callback_query()
async def pyro_callbacks(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    try:
        if data == "pyro_generate":
            if user_id in user_sessions:
                await callback_query.answer("Active session exists!", show_alert=True)
                return
            
            user_sessions[user_id] = {"step": "phone", "type": "pyrogram"}
            await callback_query.message.edit_text(
                "🔥 **Pyrogram Session**\n\nSend your phone number:\n**Example:** +919876543210\n\n/cancel to stop."
            )
            
        elif data == "tele_generate":
            if user_id in user_sessions:
                await callback_query.answer("Active session exists!", show_alert=True)
                return
            
            user_sessions[user_id] = {"step": "phone", "type": "telethon"}
            await callback_query.message.edit_text(
                "⚡ **Telethon Session**\n\nSend your phone number:\n**Example:** +919876543210\n\n/cancel to stop."
            )
            
        elif data == "help":
            help_text = """
📖 **Choose Session Type:**

**Pyrogram Session:**
- For Pyrogram based projects
- Use with pyrogram library

**Telethon Session:**
- For Telethon based projects  
- Use with telethon library

Click your preferred option below:"""
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔥 Pyrogram", callback_data="pyro_generate")],
                [InlineKeyboardButton("⚡ Telethon", callback_data="tele_generate")],
                [InlineKeyboardButton("📢 Support", url="https://t.me/shribots")]
            ])
            
            await callback_query.message.edit_text(help_text, reply_markup=keyboard)
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await callback_query.answer("Error occurred!", show_alert=True)

@pyro_app.on_message(filters.text & filters.private)
async def pyro_text_handler(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text.startswith('/'):
        return
    
    if user_id not in user_sessions:
        await message.reply_text("👋 Welcome! Use /start to generate sessions.")
        return
    
    session = user_sessions[user_id]
    step = session.get("step", "phone")
    session_type = session.get("type", "pyrogram")
    
    if step == "phone":
        await handle_phone_input(message, text, session, session_type)
    elif step == "code":
        await handle_code_input(message, text, session, session_type)
    elif step == "password":
        await handle_password_input(message, text, session, session_type)

# ==================== TELETHON HANDLERS ====================

@tele_client.on(events.NewMessage(pattern='/start'))
async def tele_start_handler(event):
    try:
        user_id = event.sender_id
        sender = await event.get_sender()
        
        welcome_text = f"""
👋 **Hello {sender.first_name}!**

🤖 **String Session Generator Bot**

I can generate both **Pyrogram** and **Telethon** string sessions.

**Choose your library:**"""
        
        buttons = [
            [Button.inline("🔥 Pyrogram Session", b"pyro_generate")],
            [Button.inline("⚡ Telethon Session", b"tele_generate")],
            [Button.url("📢 Support Channel", "https://t.me/shribots")],
            [Button.inline("ℹ️ Help", b"help")]
        ]
        
        await event.reply(welcome_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Tele start error: {e}")
        await event.reply("❌ An error occurred. Please try /start again.")

@tele_client.on(events.NewMessage(pattern='/help'))
async def tele_help_handler(event):
    help_text = """
📖 **How to Use This Bot:**

Use /pyrogram for Pyrogram sessions
Use /telethon for Telethon sessions

**Support:** @shribots
    """
    
    buttons = [
        [Button.inline("🔥 Pyrogram", b"pyro_generate")],
        [Button.inline("⚡ Telethon", b"tele_generate")],
        [Button.url("📢 Support", "https://t.me/shribots")]
    ]
    
    await event.reply(help_text, buttons=buttons)

@tele_client.on(events.CallbackQuery)
async def tele_callbacks(event):
    user_id = event.sender_id
    data = event.data.decode('utf-8')
    
    try:
        if data == "pyro_generate":
            if user_id in user_sessions:
                await event.answer("Active session exists!", alert=True)
                return
            
            user_sessions[user_id] = {"step": "phone", "type": "pyrogram"}
            await event.edit("🔥 **Pyrogram Session**\n\nSend your phone number:\n**Example:** +919876543210\n\n/cancel to stop.")
            
        elif data == "tele_generate":
            if user_id in user_sessions:
                await event.answer("Active session exists!", alert=True)
                return
            
            user_sessions[user_id] = {"step": "phone", "type": "telethon"}
            await event.edit("⚡ **Telethon Session**\n\nSend your phone number:\n**Example:** +919876543210\n\n/cancel to stop.")
            
        elif data == "help":
            help_text = """
📖 **Choose Session Type:**

Click your preferred option below:"""
            
            buttons = [
                [Button.inline("🔥 Pyrogram", b"pyro_generate")],
                [Button.inline("⚡ Telethon", b"tele_generate")],
                [Button.url("📢 Support", "https://t.me/shribots")]
            ]
            
            await event.edit(help_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Tele callback error: {e}")
        await event.answer("Error occurred!", alert=True)

# ==================== COMMON HANDLERS ====================

async def handle_phone_input(message, phone, session, session_type):
    user_id = message.from_user.id
    
    if not phone.startswith('+') or len(phone) < 10:
        await message.reply_text("❌ Invalid format! Send:\n**Example:** +919876543210")
        return
    
    try:
        if session_type == "pyrogram":
            user_client = Client(f"pyro_user_{user_id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
            await user_client.connect()
            sent_code = await user_client.send_code(phone)
            phone_code_hash = sent_code.phone_code_hash
        else:  # telethon
            user_client = TelegramClient(f"tele_user_{user_id}", API_ID, API_HASH)
            await user_client.connect()
            sent_code = await user_client.send_code_request(phone)
            phone_code_hash = sent_code.phone_code_hash
        
        session["client"] = user_client
        session["phone"] = phone
        session["phone_code_hash"] = phone_code_hash
        session["step"] = "code"
        
        await message.reply_text("📨 **Code Sent!**\nSend the 6-digit code:\n\n/cancel to stop.")
        
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await message.reply_text("❌ Invalid number! Check country code.")
        if user_id in user_sessions: del user_sessions[user_id]
    except (FloodWait, FloodWaitError) as e:
        wait_time = e.value if hasattr(e, 'value') else e.seconds
        await message.reply_text(f"⏳ Wait {wait_time} seconds.")
        if user_id in user_sessions: del user_sessions[user_id]
    except Exception as e:
        logger.error(f"Phone error: {e}")
        await message.reply_text("❌ Error! Try again.")
        if user_id in user_sessions: del user_sessions[user_id]

async def handle_code_input(message, code, session, session_type):
    user_id = message.from_user.id
    
    if not code.isdigit() or len(code) != 6:
        await message.reply_text("❌ Send 6-digit code only!")
        return
    
    try:
        user_client = session["client"]
        phone = session["phone"]
        
        if session_type == "pyrogram":
            await user_client.sign_in(phone_number=phone, phone_code_hash=session["phone_code_hash"], phone_code=code)
            string_session = await user_client.export_session_string()
            lib_name = "PYROGRAM"
        else:  # telethon
            await user_client.sign_in(phone=phone, code=code, phone_code_hash=session["phone_code_hash"])
            string_session = user_client.session.save()
            lib_name = "TELETHON"
        
        success_text = f"""
✅ **{lib_name} SESSION GENERATED!**

```{string_session}```

🔒 **Keep it secure!**
🤖 **Bot:** @CombinedSessionBot
        """
        await message.reply_text(success_text)
        await user_client.disconnect()
        del user_sessions[user_id]
        
    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        await message.reply_text("❌ Wrong code! Try again.")
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        await message.reply_text("❌ Code expired! Start over.")
        await session["client"].disconnect()
        del user_sessions[user_id]
    except (SessionPasswordNeeded, SessionPasswordNeededError):
        session["step"] = "password"
        await message.reply_text("🔐 **2FA Enabled**\nSend your password:\n\n/cancel to stop.")
    except Exception as e:
        logger.error(f"Code error: {e}")
        await message.reply_text("❌ Error! Start over.")
        if "client" in session: await session["client"].disconnect()
        if user_id in user_sessions: del user_sessions[user_id]

async def handle_password_input(message, password, session, session_type):
    user_id = message.from_user.id
    
    try:
        user_client = session["client"]
        
        if session_type == "pyrogram":
            await user_client.check_password(password)
            string_session = await user_client.export_session_string()
            lib_name = "PYROGRAM"
        else:  # telethon
            await user_client.sign_in(password=password)
            string_session = user_client.session.save()
            lib_name = "TELETHON"
        
        success_text = f"""
✅ **{lib_name} SESSION GENERATED!**

```{string_session}```

🔐 **2FA Verified!**
🔒 **Keep it secure!**
        """
        await message.reply_text(success_text)
        await user_client.disconnect()
        del user_sessions[user_id]
        
    except (PasswordHashInvalid, PasswordHashInvalidError):
        await message.reply_text("❌ Wrong password! Try again.")
    except Exception as e:
        logger.error(f"Password error: {e}")
        await message.reply_text("❌ Error! Start over.")
        if "client" in session: await session["client"].disconnect()
        if user_id in user_sessions: del user_sessions[user_id]

async def cancel_session(user_id):
    if user_id in user_sessions:
        if "client" in user_sessions[user_id]:
            try:
                await user_sessions[user_id]["client"].disconnect()
            except: pass
        del user_sessions[user_id]

# ==================== START BOTS ====================

async def start_bots():
    # Start Pyrogram bot
    await pyro_app.start()
    pyro_me = await pyro_app.get_me()
    print(f"✅ Pyrogram Bot Started: @{pyro_me.username}")
    
    # Telethon bot is already started
    tele_me = await tele_client.get_me()
    print(f"✅ Telethon Bot Started: @{tele_me.username}")
    
    print("🤖 Both bots are now running and ready!")
    print("💡 Send /start to test the bot")
    
    # Keep both running
    await asyncio.gather(
        idle(),
        tele_client.run_until_disconnected()
    )

if __name__ == "__main__":
    print("🚀 Starting Combined Pyrogram + Telethon Bot...")
    asyncio.run(start_bots())
