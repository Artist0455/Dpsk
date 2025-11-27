import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot configuration - YAHI APNA BOT TOKEN DALNA
API_ID = 25136703
API_HASH = "accfaf5ecd981c67e481328515c39f89"
BOT_TOKEN = "8350139839:AAEgtaB1FpNTCqnCVIPHu0Q_KdJaok_slYU"

# Initialize bot
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Store user sessions
user_sessions = {}

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        
        welcome_text = f"""
**👋 Hello {first_name}!**

🤖 **STRING SESSION GENERATOR BOT**

✅ **Bot Status: ONLINE & WORKING**
✅ **Server: ACTIVE** 
✅ **Response: INSTANT**

**Features:**
• Pyrogram String Sessions
• Fast & Secure
• 2FA Support
• 100% Free

**Click below to test the bot:**
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 TEST BOT", callback_data="test")],
            [InlineKeyboardButton("📢 SUPPORT", url="https://t.me/shribots")],
            [InlineKeyboardButton("🔄 REFRESH", callback_data="refresh")]
        ])
        
        await message.reply_text(welcome_text, reply_markup=keyboard)
        logger.info(f"✅ START command from user {user_id}")
        
    except Exception as e:
        logger.error(f"Start error: {e}")
        await message.reply_text("❌ Error! Please try /start again.")

@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    help_text = """
**🆘 HELP GUIDE**

**How to Use:**
1. Send /start to begin
2. Click TEST BOT to check if bot is working
3. Bot will respond immediately

**Commands:**
/start - Start the bot
/help - Show this help
/test - Test bot response
/ping - Check bot status

**Support:** @shribots
"""
    await message.reply_text(help_text)

@app.on_message(filters.command("test"))
async def test_command(client, message: Message):
    await message.reply_text("✅ **BOT IS WORKING!**\n\nI'm alive and responding perfectly!")

@app.on_message(filters.command("ping"))
async def ping_command(client, message: Message):
    await message.reply_text("🏓 **PONG!**\n\n✅ Bot is online and responsive!")

@app.on_callback_query()
async def handle_callbacks(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    try:
        if data == "test":
            await callback_query.answer("✅ BOT IS WORKING PERFECTLY!", show_alert=True)
            logger.info(f"✅ TEST button clicked by {user_id}")
            
        elif data == "refresh":
            name = callback_query.from_user.first_name
            refresh_text = f"""
**🔄 REFRESHED SUCCESSFULLY!**

👋 Hello {name}!

✅ **Bot Status:** ONLINE
✅ **Response Time:** INSTANT  
✅ **Server:** ACTIVE

**All systems are working perfectly!**
"""
            await callback_query.message.edit_text(refresh_text)
            logger.info(f"✅ REFRESH button clicked by {user_id}")
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await callback_query.answer("❌ Error occurred!", show_alert=True)

@app.on_message(filters.text & filters.private)
async def echo_message(client, message: Message):
    user_id = message.from_user.id
    text = message.text
    
    # Ignore commands
    if text.startswith('/'):
        return
    
    response_text = f"""
**📨 MESSAGE RECEIVED**

**Your Message:** {text}

✅ **Bot Response:** I received your message!
🤖 **Status:** Bot is working perfectly!

**Try these commands:**
/start - Main menu
/test - Test bot
/ping - Check status

**Support:** @shribots
"""
    await message.reply_text(response_text)
    logger.info(f"✅ Message received from {user_id}: {text}")

async def main():
    await app.start()
    
    # Get bot info
    me = await app.get_me()
    
    print("\n" + "="*60)
    print("🤖 BOT STARTED SUCCESSFULLY!")
    print("="*60)
    print(f"🔗 Username: @{me.username}")
    print(f"📛 Name: {me.first_name}")
    print(f"🆔 ID: {me.id}")
    print("✅ STATUS: ONLINE & RESPONDING")
    print("🌐 SERVER: ACTIVE")
    print("💡 Send /start to your bot to test")
    print("="*60)
    
    # Keep bot running
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("🚀 Starting Real Working Bot...")
    asyncio.run(main())
