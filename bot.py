import os
import logging
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# =============================================
# 🎯 CONFIGURATION SETTINGS
# =============================================
class Config:
    BOT_TOKEN = "8339585926:AAEeluPGVakchVJ7TPDlIkio6A1HPYy4wRg"
    DEEPSEEK_API_KEY = "sk-9b569ed95c7947fb982587f53bec6e15"
    OWNER_ID = 8272213732
    DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
    MODEL_NAME = "deepseek-chat"

# =============================================
# 🔧 INITIAL SETUP
# =============================================
# Setup comprehensive logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Flask app for Render health checks
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DeepSeek AI Bot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f2f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status { color: #22c55e; font-weight: bold; }
            .feature { background: #e8f5e8; padding: 10px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 DeepSeek AI Telegram Bot</h1>
            <p class="status">✅ Bot is running successfully!</p>
            
            <div class="feature">
                <h3>🚀 Features:</h3>
                <ul>
                    <li>AI-Powered Conversations</li>
                    <li>Code Assistance</li>
                    <li>Multi-language Support</li>
                    <li>24/7 Availability</li>
                </ul>
            </div>
            
            <p><strong>Owner ID:</strong> {OWNER_ID}</p>
            <p><strong>Powered by:</strong> DeepSeek AI + Python + Render</p>
        </div>
    </body>
    </html>
    """.format(OWNER_ID=Config.OWNER_ID)

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "running", "timestamp": str(asyncio.get_event_loop().time())}

# =============================================
# 🎯 DEEPSEEK API SERVICE
# =============================================
class DeepSeekService:
    @staticmethod
    async def get_ai_response(user_message: str) -> str:
        """
        Get AI response from DeepSeek API
        """
        try:
            headers = {
                'Authorization': f'Bearer {Config.DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": Config.MODEL_NAME,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a helpful AI assistant. Provide clear, concise and helpful responses in the same language as the user's query."
                    },
                    {
                        "role": "user", 
                        "content": user_message
                    }
                ],
                "stream": False,
                "temperature": 0.7
            }
            
            response = requests.post(
                Config.DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"API Error {response.status_code}: {response.text}")
                return "❌ माफ करें, technical issue आ रहा है। कृपया कुछ देर बाद try करें।"
                
        except requests.exceptions.Timeout:
            return "⏰ Request timeout. Please try again."
        except Exception as e:
            logger.error(f"DeepSeek API Error: {e}")
            return "❌ Sorry, I encountered an error. Please try again later."

# =============================================
# 💬 TELEGRAM BOT HANDLERS
# =============================================
class BotHandlers:
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /start command with beautiful welcome message
        """
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
/about - Bot के बारे में जानें

**Bot Owner ID:** `{Config.OWNER_ID}`
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /help command
        """
        help_text = """
🆘 **Help Guide - सहायता मार्गदर्शिका**

📖 **How to Use:**
• Simply type any message and I'll respond
• Ask questions in any language
• Get coding help, writing assistance, etc.

🔧 **Available Commands:**
/start - Start the bot
/help - Show this help message  
/about - About this bot

💡 **Examples:**
• "Python में list कैसे बनाएं?"
• "Explain quantum computing"
• "Help me write an email"
• "What is 2+2?"

❓ **Need more help?**
Just type your question naturally!
        """
        await update.message.reply_text(help_text)

    @staticmethod
    async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /about command
        """
        about_text = f"""
🤖 **About This Bot**

**Powered By:** DeepSeek AI
**Developer:** {Config.OWNER_ID}
**Platform:** Telegram + Render
**AI Model:** DeepSeek Chat

🌟 **Features:**
• Advanced AI Conversations
• Multi-language Understanding  
• Code Generation & Debugging
• Content Creation
• 24/7 Availability

🔐 **Privacy:** Your conversations are processed securely through DeepSeek API.

📞 **Support:** Contact owner ID: {Config.OWNER_ID}
        """
        await update.message.reply_text(about_text)

    @staticmethod
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle all text messages from users
        """
        user = update.effective_user
        user_message = update.message.text
        
        # Log the message
        logger.info(f"📩 User {user.id} ({user.first_name}): {user_message}")
        
        # Send "typing..." action
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, 
            action="typing"
        )
        
        try:
            # Get AI response
            bot_response = await DeepSeekService.get_ai_response(user_message)
            
            # Send response
            await update.message.reply_text(bot_response)
            logger.info(f"✅ Response sent to user {user.id}")
            
        except Exception as e:
            error_msg = f"❌ Error processing message: {e}"
            logger.error(error_msg)
            await update.message.reply_text("❌ Sorry, an error occurred. Please try again.")

    @staticmethod
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle errors in the bot
        """
        logger.error(f"🚨 Error while processing update: {context.error}")

# =============================================
# 🚀 BOT INITIALIZATION & STARTUP
# =============================================
def initialize_bot():
    """
    Initialize and configure the Telegram bot
    """
    try:
        # Create Application instance
        application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", BotHandlers.start_command))
        application.add_handler(CommandHandler("help", BotHandlers.help_command))
        application.add_handler(CommandHandler("about", BotHandlers.about_command))
        
        # Add message handler
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            BotHandlers.handle_message
        ))
        
        # Add error handler
        application.add_error_handler(BotHandlers.error_handler)
        
        logger.info("✅ Bot initialized successfully!")
        return application
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize bot: {e}")
        raise

def start_flask_app():
    """
    Start Flask app for web server
    """
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)

def main():
    """
    Main function to start both Flask and Telegram Bot
    """
    logger.info("🚀 Starting DeepSeek AI Telegram Bot...")
    
    try:
        # Start Flask in a separate thread
        flask_thread = threading.Thread(target=start_flask_app)
        flask_thread.daemon = True
        flask_thread.start()
        logger.info("✅ Flask server started on port 8000")
        
        # Initialize and start bot
        bot_application = initialize_bot()
        
        # Start polling
        logger.info("🔄 Starting bot polling...")
        bot_application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.error(f"💥 Failed to start application: {e}")

# =============================================
# 🎯 APPLICATION ENTRY POINT
# =============================================
if __name__ == '__main__':
    # Startup banner
    print("=" * 50)
    print("🤖 DEEPSEEK AI TELEGRAM BOT STARTING...")
    print("=" * 50)
    
    # Start the application
    main()
