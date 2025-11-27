import os
import asyncio
import logging

# Bot token directly use karenge
BOT_TOKEN = "8244179451:AAF8LT22EcppuWET3msokmpnbmGWiaQxMOs"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🤖 Bot starting...")

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
    from pyrogram import Client
    
    print("✅ All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please check requirements.txt")
    exit(1)

# Pre-defined API credentials
API_CREDENTIALS = [
    {"api_id": 2040, "api_hash": "b18441a1ff607e10a989891a5462e627"},
    {"api_id": 6, "api_hash": "eb06d4abfb49dc3eeb1aeb98ae0f581e"},
    {"api_id": 4, "api_hash": "014b35b6184100b085b0d0572f9b5103"},
]

# Welcome message
async def start(update: Update, context: CallbackContext) -> None:
    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
    except:
        bot_username = "your_bot"
    
    keyboard = [
        [InlineKeyboardButton("📱 Generate String Session", callback_data="generate_session")],
        [
            InlineKeyboardButton("📢 Official Channel", url="https://t.me/idxhelp"),
            InlineKeyboardButton("🆘 Support", url="https://t.me/idxhelp")
        ],
        [InlineKeyboardButton("👥 Add to Group", url=f"https://t.me/{bot_username}?startgroup=true")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🔐 **String Session Generator Bot**

📱 **Yeh bot aapke phone number se string session generate karega:**

⚡ **Features:**
• Real string session generation
• Pyrogram format
• Music bots ke liye perfect

🚀 **How to Use:**
1. 'Generate String Session' button click karein
2. Apna phone number bhejein (with country code)
3. Verification code bhejein
4. Session aapko mil jayega

━━━━━━━━━━━━━━━━━━━━
✨ **Powered by:** @idxhelp
━━━━━━━━━━━━━━━━━━━━

👇 **Start karne ke liye button click karein:**
"""
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

# Button handler
async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == "generate_session":
        await query.edit_message_text(
            "📱 **String Session Generation**\n\n"
            "Please send your Phone Number with country code:\n"
            "**Example:** `+919876543210`\n\n"
            "✨ **Powered by:** @idxhelp",
            parse_mode='Markdown'
        )
        context.user_data['step'] = 'phone'

# Message handler
async def handle_message(update: Update, context: CallbackContext) -> None:
    if 'step' not in context.user_data:
        return
    
    user_id = update.effective_user.id
    text = update.message.text
    step = context.user_data['step']
    
    try:
        if step == 'phone':
            if text.startswith('+') and len(text) >= 10:
                context.user_data['phone'] = text
                context.user_data['step'] = 'code'
                
                creds = API_CREDENTIALS[0]
                
                await update.message.reply_text(
                    f"✅ **Phone Number Received:** `{text}`\n\n"
                    f"🔐 **Connecting to Telegram...**\n\n"
                    f"✨ **Powered by:** @idxhelp",
                    parse_mode='Markdown'
                )
                
                # Pyrogram client
                session_name = f"session_{user_id}"
                client = Client(
                    session_name,
                    api_id=creds['api_id'],
                    api_hash=creds['api_hash'],
                    phone_number=text,
                    in_memory=True
                )
                
                await client.connect()
                
                try:
                    sent_code = await client.send_code(text)
                    context.user_data['phone_code_hash'] = sent_code.phone_code_hash
                    context.user_data['client'] = client
                    
                    await update.message.reply_text(
                        "📨 **Verification code sent!**\n\n"
                        "Please send the 5-digit code:\n\n"
                        "✨ **Powered by:** @idxhelp",
                        parse_mode='Markdown'
                    )
                    
                except Exception as e:
                    await update.message.reply_text(
                        f"❌ **Error:** `{str(e)}`\n\n"
                        "Please try again with /start\n\n"
                        "✨ **Powered by:** @idxhelp",
                        parse_mode='Markdown'
                    )
                    context.user_data.clear()
                        
            else:
                await update.message.reply_text(
                    "❌ **Invalid phone number!**\n\n"
                    "**Example:** `+919876543210`\n\n"
                    "✨ **Powered by:** @idxhelp",
                    parse_mode='Markdown'
                )
        
        elif step == 'code':
            if text.isdigit() and len(text) == 5:
                if 'client' not in context.user_data:
                    await update.message.reply_text("❌ **Session expired!**\nStart again with /start", parse_mode='Markdown')
                    return
                    
                client = context.user_data['client']
                phone = context.user_data['phone']
                phone_code_hash = context.user_data['phone_code_hash']
                
                await update.message.reply_text("🔐 **Verifying code...**\n\n✨ **Powered by:** @idxhelp", parse_mode='Markdown')
                
                try:
                    await client.sign_in(phone_number=phone, phone_code_hash=phone_code_hash, phone_code=text)
                    string_session = await client.export_session_string()
                    
                    await update.message.reply_text("✅ **Successfully signed in!**\n\n✨ **Powered by:** @idxhelp", parse_mode='Markdown')
                    
                    # Session send karein
                    try:
                        bot_info = await context.bot.get_me()
                        bot_username = bot_info.username
                    except:
                        bot_username = "your_bot"
                    
                    success_keyboard = [
                        [InlineKeyboardButton("📢 Official Channel", url="https://t.me/idxhelp")],
                        [InlineKeyboardButton("🔄 New Session", callback_data="generate_session")]
                    ]
                    success_markup = InlineKeyboardMarkup(success_keyboard)
                    
                    await update.message.reply_text(
                        f"🎉 **String Session Generated!**\n\n"
                        f"🔐 **Your Session:**\n`{string_session}`\n\n"
                        f"📱 **Phone:** `{phone}`\n\n"
                        f"⚠️ **Save this session securely!**\n\n"
                        f"✨ **Powered by:** @idxhelp",
                        reply_markup=success_markup,
                        parse_mode='Markdown'
                    )
                    
                    await client.disconnect()
                    context.user_data.clear()
                    
                except Exception as e:
                    error_msg = str(e)
                    if "phone_code_expired" in error_msg:
                        await update.message.reply_text("❌ **Code expired!**\nStart again with /start", parse_mode='Markdown')
                    elif "phone_code_invalid" in error_msg:
                        await update.message.reply_text("❌ **Invalid code!**\nTry again", parse_mode='Markdown')
                    else:
                        await update.message.reply_text(f"❌ **Error:** `{error_msg}`\nStart again with /start", parse_mode='Markdown')
                    
                    try:
                        await client.disconnect()
                    except:
                        pass
                    context.user_data.clear()
                    
            else:
                await update.message.reply_text("❌ **Invalid code!**\nSend 5-digit code", parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ **Error:** `{str(e)}`\nStart again with /start", parse_mode='Markdown')
        context.user_data.clear()

# Help command
async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = """
🆘 **Help Guide**

📱 **How to Generate Session:**
1. /start command
2. 'Generate String Session' button
3. Phone number with country code
4. Verification code

📞 **Phone Format:** `+919876543210`

🔧 **Support:** @idxhelp

✨ **Powered by:** @idxhelp
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Error handler
async def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(f"Error: {context.error}")

# Main function
def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)
        
        print("✅ Bot setup successful!")
        print("🚀 Starting bot...")
        
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")
        exit(1)

if __name__ == "__main__":
    main()
