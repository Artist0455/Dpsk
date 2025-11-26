import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, render_template_string
import threading

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8339585926:AAEeluPGVakchVJ7TPDlIkio6A1HPYy4wRg"
DEEPSEEK_API_KEY = "sk-9b569ed95c7947fb982587f53bec6e15"
OWNER_ID = "8272213732"

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== FLASK APP ====================
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DeepSeek AI Bot</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        .logo {
            font-size: 48px;
            margin-bottom: 20px;
        }
        .status {
            background: #22c55e;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            margin: 20px 0;
        }
        .features {
            text-align: left;
            margin: 30px 0;
        }
        .feature-item {
            background: #f8fafc;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .owner-info {
            background: #fff7ed;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🤖</div>
        <h1>DeepSeek AI Telegram Bot</h1>
        <div class="status">✅ Bot is Running Successfully!</div>
        
        <div class="features">
            <h3>🚀 Features:</h3>
            <div class="feature-item">
                <strong>💬 AI Conversations</strong> - Intelligent chat with DeepSeek AI
            </div>
            <div class="feature-item">
                <strong>💻 Coding Help</strong> - Programming assistance in multiple languages
            </div>
            <div class="feature-item">
                <strong>🌐 Multi-language</strong> - Supports Hindi, English and more
            </div>
            <div class="feature-item">
                <strong>⏰ 24/7 Available</strong> - Always ready to help
            </div>
        </div>
        
        <div class="owner-info">
            <strong>👨‍💻 Owner ID:</strong> {{ owner_id }}<br>
            <strong>🔧 Platform:</strong> Render + Python + Telegram
        </div>
        
        <p><strong>📞 How to use:</strong> Search for the bot on Telegram and send /start</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, owner_id=OWNER_ID)

@app.route('/health')
def health():
    return {"status": "healthy", "service": "telegram-bot", "owner": OWNER_ID}

# ==================== DEEPSEEK API SERVICE ====================
async def get_ai_response(user_message):
    """Get response from DeepSeek API"""
    try:
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Provide clear and helpful responses in the same language as the user."
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
            'https://api.deepseek.com/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            logger.error(f"API Error: {response.status_code}")
            return "❌ माफ करें, technical issue आ रहा है। कृपया कुछ देर बाद try करें।"
            
    except Exception as e:
        logger.error(f"DeepSeek API Error: {e}")
        return "❌ Sorry, I encountered an error. Please try again later."

# ==================== TELEGRAM BOT HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
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

**Bot Owner ID:** `{OWNER_ID}`
    """
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
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

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = f"""
🤖 **About This Bot**

**Powered By:** DeepSeek AI
**Developer:** {OWNER_ID}
**Platform:** Telegram + Render
**AI Model:** DeepSeek Chat

🌟 **Features:**
• Advanced AI Conversations
• Multi-language Understanding  
• Code Generation & Debugging
• Content Creation
• 24/7 Availability

🔐 **Privacy:** Your conversations are processed securely through DeepSeek API.

📞 **Support:** Contact owner ID: {OWNER_ID}
    """
    await update.message.reply_text(about_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    user_message = update.message.text
    user = update.effective_user
    
    logger.info(f"User {user.id} ({user.first_name}): {user_message}")
    
    # Send typing action
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    # Get AI response
    bot_response = await get_ai_response(user_message)
    
    # Send response (split if too long)
    if len(bot_response) > 4096:
        for i in range(0, len(bot_response), 4096):
            await update.message.reply_text(bot_response[i:i+4096])
    else:
        await update.message.reply_text(bot_response)
    
    logger.info(f"Response sent to user {user.id}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Error: {context.error}")

# ==================== BOT INITIALIZATION ====================
def setup_bot():
    """Setup and start the Telegram bot"""
    try:
        # Create Application (new way in python-telegram-bot v20+)
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        logger.info("✅ Telegram Bot application created successfully!")
        return application
        
    except Exception as e:
        logger.error(f"❌ Failed to setup bot: {e}")
        return None

def start_flask():
    """Start Flask server"""
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)

def main():
    """Main function"""
    logger.info("🚀 Starting DeepSeek AI Telegram Bot...")
    
    # Start Flask in background thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("✅ Flask server started on port 8000")
    
    # Setup and start Telegram bot
    application = setup_bot()
    
    if application:
        try:
            logger.info("🔄 Starting bot polling...")
            application.run_polling(drop_pending_updates=True)
            logger.info("🤖 Bot is now running and ready to receive messages!")
        except Exception as e:
            logger.error(f"💥 Error during polling: {e}")
    else:
        logger.error("💥 Failed to start bot")

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 DEEPSEEK AI TELEGRAM BOT - STARTING...")
    print("📱 Bot Token:", BOT_TOKEN[:10] + "..." + BOT_TOKEN[-5:])
    print("🔑 API Key:", DEEPSEEK_API_KEY[:10] + "..." + DEEPSEEK_API_KEY[-5:])
    print("👤 Owner ID:", OWNER_ID)
    print("=" * 60)
    main()
