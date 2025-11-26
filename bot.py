import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8339585926:AAEeluPGVakchVJ7TPDlIkio6A1HPYy4wRg"
DEEPSEEK_API_KEY = "sk-9b569ed95c7947fb982587f53bec6e15"

print("🤖 Starting DeepSeek AI Telegram Bot...")
print(f"📱 Bot Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
print(f"🔑 API Key: {DEEPSEEK_API_KEY[:10]}...{DEEPSEEK_API_KEY[-5:]}")

async def start(update: Update, context: CallbackContext) -> None:
    """Send welcome message when user sends /start"""
    user = update.effective_user
    welcome_text = f"""
🎉 **नमस्ते {user.first_name}!** 🙏

🤖 **मैं DeepSeek AI Powered Bot हूं!**

✨ **मेरी capabilities:**
• 💬 Intelligent Conversations
• 💻 Coding & Programming Help  
• 📚 Learning Assistance
• ✍️ Content Writing
• 🔍 Problem Solving
• 🌐 Multi-language Support

🚀 **शुरुआत करें:**
बस कोई भी message type करें और मैं आपकी help करूंगा!

📝 **Available Commands:**
/start - Bot शुरू करें
/help - सहायता प्राप्त करें

**Developed with ❤️ for AI Enthusiasts**
    """
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send help message when user sends /help"""
    help_text = """
🆘 **Help Guide**

📖 **How to Use:**
• Simply type any message and I'll respond
• Ask questions in any language
• Get coding help, writing assistance, etc.

🔧 **Available Commands:**
/start - Start the bot
/help - Show this help message

💡 **Examples:**
• "Python में list कैसे बनाएं?"
• "Explain quantum computing"
• "Help me write an email"
• "What is 2+2?"

❓ **Need more help?**
Just type your question naturally!
    """
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle incoming messages"""
    try:
        user_message = update.message.text
        user = update.effective_user
        
        print(f"📩 User {user.id} ({user.first_name}): {user_message}")
        
        # Show typing action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Call DeepSeek API
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            "stream": False
        }
        
        response = requests.post(
            'https://api.deepseek.com/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            bot_reply = result['choices'][0]['message']['content']
            
            # Send response
            await update.message.reply_text(bot_reply)
            print(f"✅ Response sent to user {user.id}")
            
        else:
            error_msg = f"❌ API Error: {response.status_code}"
            await update.message.reply_text("माफ करें, technical issue आ रहा है। कृपया कुछ देर बाद try करें।")
            print(error_msg)
            
    except Exception as e:
        error_message = f"❌ Error: {str(e)}"
        await update.message.reply_text("माफ करें, कुछ error आया। कृपया बाद में try करें।")
        print(error_message)

def main() -> None:
    """Start the bot."""
    try:
        # Create the Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Start the Bot
        print("✅ Bot setup completed successfully!")
        print("🔄 Starting polling...")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"💥 Failed to start bot: {e}")

if __name__ == '__main__':
    main()
