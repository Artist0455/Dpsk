from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import logging
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Your bot credentials
API_ID = 25136703
API_HASH = "accfaf5ecd981c67e481328515c39f89"
BOT_TOKEN = "8350139839:AAEgtaB1FpNTCqnCVIPHu0Q_KdJaok_slYU"

# Create bot instance
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    try:
        name = message.from_user.first_name
        text = f"""
**👋 Hello {name}!**

🤖 **I AM WORKING BOT**

✅ **Bot Status: ONLINE**
✅ **Server: RUNNING** 
✅ **Response: ACTIVE**

**Click below buttons to test me:**
"""
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 TEST BUTTON", callback_data="test")],
            [InlineKeyboardButton("📢 SUPPORT", url="https://t.me/shribots")],
            [InlineKeyboardButton("🔄 REFRESH", callback_data="refresh")]
        ])
        
        await message.reply_text(text, reply_markup=buttons)
        print(f"✅ START command received from {message.from_user.id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Test callback
@app.on_callback_query(filters.regex("test"))
async def test_callback(client, callback_query):
    await callback_query.answer("✅ BOT IS WORKING!", show_alert=True)
    print("✅ TEST button clicked")

# Refresh callback  
@app.on_callback_query(filters.regex("refresh"))
async def refresh_callback(client, callback_query):
    name = callback_query.from_user.first_name
    text = f"""
**🔄 REFRESHED**

👋 Hello {name}!

✅ **Bot is still running perfectly!**
🕒 **Server time: Working**

**All systems operational!**
"""
    await callback_query.message.edit_text(text)
    print("✅ REFRESH button clicked")

# Echo any text message
@app.on_message(filters.text & filters.private)
async def echo(client, message: Message):
    if message.text.startswith('/'):
        return
        
    text = f"""
**📨 MESSAGE RECEIVED**

**Your Message:** {message.text}

✅ **Bot is responding perfectly!**
🤖 **I'm alive and working!**

Try /start to see main menu.
"""
    await message.reply_text(text)
    print(f"✅ Message received: {message.text}")

# Start the bot
async def main():
    await app.start()
    bot = await app.get_me()
    print("\n" + "="*50)
    print("🤖 BOT STARTED SUCCESSFULLY!")
    print(f"🔗 Username: @{bot.username}")
    print(f"📛 Name: {bot.first_name}")
    print(f"🆔 ID: {bot.id}")
    print("✅ STATUS: ONLINE & RESPONDING")
    print("💡 Send /start to your bot to test")
    print("="*50 + "\n")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("🚀 Starting Real Working Bot...")
    asyncio.run(main())
