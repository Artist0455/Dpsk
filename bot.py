import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration - PLEASE CHANGE THESE FOR SECURITY!
BOT_TOKEN = "8339585926:AAEeluPGVakchVJ7TPDlIkio6A1HPYy4wRg"
DEEPSEEK_API_KEY = "sk-9b569ed95c7947fb982587f53bec6e15"

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        '👋 नमस्ते! मैं DeepSeek AI Bot हूं!\n\n'
        '💡 आप मुझसे कुछ भी पूछ सकते हैं - questions, help, coding, writing, etc.\n\n'
        '📝 बस कोई भी message type करें!'
    )

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text('💡 बस कोई भी message type करें, मैं AI की help से reply दूंगा!')

async def handle_message(update: Update, context: CallbackContext):
    try:
        user_message = update.message.text
        logger.info(f"User asked: {user_message}")
        
        # DeepSeek API call
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": user_message}],
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
            
            # Split long messages
            if len(bot_reply) > 4096:
                for i in range(0, len(bot_reply), 4096):
                    await update.message.reply_text(bot_reply[i:i+4096])
            else:
                await update.message.reply_text(bot_reply)
                
        else:
            await update.message.reply_text("❌ Technical issue. Please try again later.")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Sorry, something went wrong.")

def main():
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Start bot
        logger.info("🤖 Bot starting...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")

if __name__ == '__main__':
    main()
