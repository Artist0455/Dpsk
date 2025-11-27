import os
import asyncio
import logging

# Bot configuration
BOT_TOKEN = "8244179451:AAF8LT22EcppuWET3msokmpnbmGWiaQxMOs"

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

print("🚀 Starting Telegram String Session Bot...")

try:
    # Try to import with compatibility
    import telegram
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
    
    # Try Pyrogram import
    from pyrogram import Client
    
    print("✅ All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying alternative approach...")
    exit(1)

# API credentials
API_CREDENTIALS = [
    {"api_id": 2040, "api_hash": "b18441a1ff607e10a989891a5462e627"},
    {"api_id": 6, "api_hash": "eb06d4abfb49dc3eeb1aeb98ae0f581e"},
    {"api_id": 4, "api_hash": "014b35b6184100b085b0d0572f9b5103"},
]

async def start(update: Update, context: CallbackContext) -> None:
    """Start command handler"""
    try:
        bot = await context.bot.get_me()
        bot_username = bot.username
    except:
        bot_username = "session_generator_bot"
    
    keyboard = [
        [InlineKeyboardButton("📱 Generate String Session", callback_data="generate_session")],
        [
            InlineKeyboardButton("📢 Channel", url="https://t.me/idxhelp"),
            InlineKeyboardButton("🆘 Support", url="https://t.me/idxhelp")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🔐 **String Session Generator Bot**

✨ **Generate Pyrogram String Sessions Easily**

📱 **How to Use:**
1. Click 'Generate String Session'
2. Send your phone number (with country code)
3. Send verification code
4. Get your session string

⚡ **Fast & Secure**
🔒 **Your data is safe**

**Powered by:** @idxhelp
"""
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: CallbackContext) -> None:
    """Button callback handler"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "generate_session":
        await query.edit_message_text(
            "📱 **String Session Generation**\n\n"
            "Please send your Phone Number with country code:\n"
            "**Example:** `+919876543210`\n\n"
            "We will generate your Pyrogram string session."
        )
        context.user_data['step'] = 'phone'
        context.user_data['user_id'] = query.from_user.id

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle user messages"""
    if 'step' not in context.user_data:
        return
    
    user_id = update.effective_user.id
    text = update.message.text
    step = context.user_data['step']
    
    try:
        if step == 'phone':
            if text.startswith('+') and text[1:].isdigit() and len(text) >= 10:
                context.user_data['phone'] = text
                context.user_data['step'] = 'code'
                
                await update.message.reply_text(
                    f"✅ **Phone Received:** `{text}`\n\n"
                    "🔐 **Connecting to Telegram...**\n"
                    "Please wait..."
                )
                
                # Use first API credentials
                creds = API_CREDENTIALS[0]
                
                # Create Pyrogram client
                client = Client(
                    f"session_{user_id}",
                    api_id=creds['api_id'],
                    api_hash=creds['api_hash'],
                    phone_number=text,
                    in_memory=True
                )
                
                await client.connect()
                
                try:
                    # Send code request
                    sent_code = await client.send_code(text)
                    context.user_data['phone_code_hash'] = sent_code.phone_code_hash
                    context.user_data['client'] = client
                    
                    await update.message.reply_text(
                        "📨 **Verification code sent!**\n\n"
                        "Please check your Telegram app and send the 5-digit code:"
                    )
                    
                except Exception as e:
                    error_msg = str(e)
                    if "FLOOD" in error_msg:
                        await update.message.reply_text("⏳ Too many attempts. Please wait and try again.")
                    else:
                        await update.message.reply_text(f"❌ Error: {error_msg}\n\nPlease try again with /start")
                    
                    await client.disconnect()
                    context.user_data.clear()
                        
            else:
                await update.message.reply_text(
                    "❌ **Invalid phone number!**\n\n"
                    "Please send in format: `+919876543210`\n"
                    "With country code, without spaces."
                )
        
        elif step == 'code':
            if text.isdigit() and len(text) == 5:
                if 'client' not in context.user_data:
                    await update.message.reply_text("❌ Session expired. Please start again with /start")
                    return
                
                client = context.user_data['client']
                phone = context.user_data['phone']
                phone_code_hash = context.user_data['phone_code_hash']
                
                await update.message.reply_text("🔐 **Verifying code...**")
                
                try:
                    # Sign in with code
                    await client.sign_in(
                        phone_number=phone,
                        phone_code_hash=phone_code_hash,
                        phone_code=text
                    )
                    
                    # Get session string
                    string_session = await client.export_session_string()
                    
                    # Send success message
                    success_text = f"""
🎉 **String Session Generated Successfully!**

🔐 **Your Session String:**
`{string_session}`

📱 **Phone:** `{phone}`

⚠️ **Important:**
• Save this session securely
• Don't share with anyone
• Use for your bots

**Generated by:** @{(await context.bot.get_me()).username}
**Powered by:** @idxhelp
"""
                    await update.message.reply_text(success_text)
                    
                    # Cleanup
                    await client.disconnect()
                    context.user_data.clear()
                    
                except Exception as e:
                    error_msg = str(e)
                    if "code expired" in error_msg.lower():
                        await update.message.reply_text("❌ Code expired. Please start again with /start")
                    elif "invalid code" in error_msg.lower():
                        await update.message.reply_text("❌ Invalid code. Please check and try again.")
                    else:
                        await update.message.reply_text(f"❌ Error: {error_msg}\n\nPlease try again with /start")
                    
                    # Cleanup
                    try:
                        await client.disconnect()
                    except:
                        pass
                    context.user_data.clear()
                    
            else:
                await update.message.reply_text("❌ Please send a valid 5-digit code.")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text("❌ Unexpected error. Please try again with /start")
        
        # Cleanup
        if 'client' in context.user_data:
            try:
                client = context.user_data['client']
                await client.disconnect()
            except:
                pass
        context.user_data.clear()

async def help_command(update: Update, context: CallbackContext) -> None:
    """Help command"""
    help_text = """
🤖 **String Session Bot Help**

📋 **Commands:**
/start - Start the bot
/help - Show this help
/session - Generate new session

📱 **Usage:**
1. Start bot
2. Send phone number (with + country code)
3. Send verification code
4. Get your session string

🔐 **What is String Session?**
- Authentication token for Telegram APIs
- Used for Pyrogram/Telethon bots
- Required for userbots and music bots

📞 **Support:** @idxhelp
"""
    await update.message.reply_text(help_text)

async def session_command(update: Update, context: CallbackContext) -> None:
    """Direct session command"""
    await update.message.reply_text(
        "🔐 **Generate String Session**\n\n"
        "Please send your Phone Number with country code:\n"
        "**Example:** `+919876543210`"
    )
    context.user_data['step'] = 'phone'
    context.user_data['user_id'] = update.effective_user.id

async def error_handler(update: Update, context: CallbackContext) -> None:
    """Global error handler"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Main function to start the bot"""
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("session", session_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        # Start the bot
        logger.info("🤖 Bot starting...")
        print("✅ Bot is running!")
        print("🔐 String Session Generator Ready")
        print("📞 Support: @idxhelp")
        
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Bot failed to start: {e}")

if __name__ == "__main__":
    main()
