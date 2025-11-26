import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask

# Flask app for Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram + DeepSeek Bot is Active!"

# Configuration
BOT_TOKEN = "8339585926:AAEeluPGVakchVJ7TPDlIkio6A1HPYy4wRg"
DEEPSEEK_API_KEY = "sk-9b569ed95c7947fb982587f53bec6e15"
OWNER_ID = 8272213732

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"👋 नमस्ते {user.mention_html()}!\n\n"
        "🤖 मैं DeepSeek AI से powered एक smart bot हूं!\n\n"
        "💡 आप मुझसे कुछ भी पूछ सकते हैं - questions, help, coding, writing, etc.\n\n"
        "📝 बस अपना message type करें और मैं आपकी help करूंगा!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🆘 **Available Commands:**

/start - Bot शुरू करें
/help - यह help message
/owner - Bot owner के बारे में जानकारी

💬 **Regular Usage:**
बस कोई भी message type करें और मैं उसका reply दूंगा!

🔧 **Features:**
- Text conversations
- Question answering  
- Coding help
- Creative writing
- और भी बहुत कुछ!
"""
    await update.message.reply_text(help_text)

async def owner_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner_text = """
👨‍💻 **Bot Owner Information:**

🆔 Owner ID: 8272213732
📧 Contact: @username (Telegram)

🤖 This bot is powered by:
- DeepSeek AI API
- Python Telegram Bot
- Render Deployment
"""
    await update.message.reply_text(owner_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"User {user_id} asked: {user_message}")
        
        # DeepSeek API call
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
            
            # Send response to user
            await update.message.reply_text(bot_reply)
            logger.info(f"Response sent to user {user_id}")
            
        else:
            error_msg = f"❌ API Error: {response.status_code} - {response.text}"
            await update.message.reply_text("माफ करें, technical issue आ रहा है। कृपया कुछ देर बाद try करें।")
            logger.error(error_msg)
            
    except Exception as e:
        error_message = f"❌ Unexpected error: {str(e)}"
        await update.message.reply_text("माफ करें, कुछ error आया। कृपया बाद में try करें।")
        logger.error(error_message)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot."""
    try:
        # Create Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("owner", owner_info))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        # Start the Bot
        logger.info("🤖 Bot is starting...")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == '__main__':
    main()
