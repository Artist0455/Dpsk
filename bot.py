import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
from pyrogram import Client

# Bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8244179451:AAF8LT22EcppuWET3msokmpnbmGWiaQxMOs")

# Pre-defined API credentials
API_CREDENTIALS = [
    {"api_id": 2040, "api_hash": "b18441a1ff607e10a989891a5462e627"},
    {"api_id": 6, "api_hash": "eb06d4abfb49dc3eeb1aeb98ae0f581e"},
    {"api_id": 4, "api_hash": "014b35b6184100b085b0d0572f9b5103"},
]

# Welcome message
async def start(update: Update, context: CallbackContext) -> None:
    bot_username = (await context.bot.get_me()).username
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
• Automatically saved messages mein send
• Pyrogram format
• Music bots ke liye perfect

🚀 **How to Use:**
1. 'Generate String Session' button click karein
2. Apna phone number bhejein (with country code)
3. Verification code bhejein
4. Session aapke saved messages mein automatically save ho jayega

━━━━━━━━━━━━━━━━━━━━
✨ **Powered by:** @idxhelp
━━━━━━━━━━━━━━━━━━━━

👇 **Start karne ke liye button click karein:**
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Generate session button handler
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
        context.user_data['user_id'] = query.from_user.id

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
                
                # API credentials select karein
                creds = API_CREDENTIALS[0]
                
                await update.message.reply_text(
                    f"✅ **Phone Number Received:** `{text}`\n\n"
                    f"🔐 **Connecting to Telegram...**\n\n"
                    f"✨ **Powered by:** @idxhelp",
                    parse_mode='Markdown'
                )
                
                # Pyrogram client start karein - Render compatible session name
                session_name = f"session_{user_id}"
                client = Client(
                    session_name,
                    api_id=creds['api_id'],
                    api_hash=creds['api_hash'],
                    phone_number=text,
                    in_memory=True  # Render pe file system issues se bachne ke liye
                )
                
                await client.connect()
                
                # Send code
                try:
                    sent_code = await client.send_code(text)
                    context.user_data['phone_code_hash'] = sent_code.phone_code_hash
                    context.user_data['client'] = client
                    
                    await update.message.reply_text(
                        "📨 **Verification code sent to your Telegram account!**\n\n"
                        "Please send the 5-digit code you received:\n\n"
                        "✨ **Powered by:** @idxhelp",
                        parse_mode='Markdown'
                    )
                    
                except Exception as e:
                    if "FLOOD_WAIT" in str(e):
                        await update.message.reply_text(
                            "⏳ **Telegram flood wait error!**\n\n"
                            "Please try again after some time.\n\n"
                            "✨ **Powered by:** @idxhelp",
                            parse_mode='Markdown'
                        )
                        context.user_data.clear()
                    else:
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
                    "Please send in correct format:\n"
                    "**Example:** `+919876543210`\n\n"
                    "✨ **Powered by:** @idxhelp",
                    parse_mode='Markdown'
                )
        
        elif step == 'code':
            if text.isdigit() and len(text) == 5:
                client = context.user_data['client']
                phone = context.user_data['phone']
                phone_code_hash = context.user_data['phone_code_hash']
                
                await update.message.reply_text(
                    "🔐 **Verifying code...**\n\n"
                    "Please wait...\n\n"
                    "✨ **Powered by:** @idxhelp",
                    parse_mode='Markdown'
                )
                
                try:
                    # Sign in with code
                    await client.sign_in(
                        phone_number=phone,
                        phone_code_hash=phone_code_hash,
                        phone_code=text
                    )
                    
                    # Get string session
                    string_session = await client.export_session_string()
                    
                    await update.message.reply_text(
                        "✅ **Successfully signed in!**\n\n"
                        "📤 **Sending session to your Saved Messages...**\n\n"
                        "✨ **Powered by:** @idxhelp",
                        parse_mode='Markdown'
                    )
                    
                    # Send session to saved messages
                    try:
                        bot_username = (await context.bot.get_me()).username
                        await client.send_message("me", 
                            f"🔐 **Your String Session**\n\n"
                            f"**Session:** `{string_session}`\n\n"
                            f"📝 **Generated by:** @{bot_username}\n"
                            f"📱 **Phone:** `{phone}`\n\n"
                            f"⚠️ **Important:**\n"
                            f"• Is session ko kisi se share na karein\n"
                            f"• Secure jagah save karein\n"
                            f"• Music bots mein use karein\n\n"
                            f"✨ **Powered by:** @idxhelp"
                        )
                        
                        # Success message with buttons
                        success_keyboard = [
                            [InlineKeyboardButton("📢 Official Channel", url="https://t.me/idxhelp")],
                            [InlineKeyboardButton("🔄 New Session", callback_data="generate_session")],
                            [InlineKeyboardButton("👥 Add to Group", url=f"https://t.me/{bot_username}?startgroup=true")]
                        ]
                        success_markup = InlineKeyboardMarkup(success_keyboard)
                        
                        await update.message.reply_text(
                            "🎉 **String Session Successfully Generated!**\n\n"
                            f"✅ **Session sent to your Saved Messages!**\n\n"
                            f"📱 **Phone:** `{phone}`\n"
                            f"🔐 **Check your Telegram Saved Messages**\n\n"
                            f"⚠️ **Session securely saved in your account**\n\n"
                            f"✨ **Powered by:** @idxhelp",
                            reply_markup=success_markup,
                            parse_mode='Markdown'
                        )
                        
                    except Exception as e:
                        await update.message.reply_text(
                            f"✅ **Session Generated but couldn't send to Saved Messages**\n\n"
                            f"🔐 **Your String Session:**\n"
                            f"`{string_session}`\n\n"
                            f"⚠️ **Please save this session securely**\n\n"
                            f"✨ **Powered by:** @idxhelp",
                            parse_mode='Markdown'
                        )
                    
                    await client.disconnect()
                    await client.stop()
                    
                    context.user_data.clear()
                    
                except Exception as e:
                    error_msg = str(e)
                    if "phone_code_expired" in error_msg:
                        await update.message.reply_text(
                            "❌ **Verification code expired!**\n\n"
                            "Please start again with /start\n\n"
                            "✨ **Powered by:** @idxhelp",
                            parse_mode='Markdown'
                        )
                    elif "phone_code_invalid" in error_msg:
                        await update.message.reply_text(
                            "❌ **Invalid verification code!**\n\n"
                            "Please check the code and try again.\n\n"
                            "✨ **Powered by:** @idxhelp",
                            parse_mode='Markdown'
                        )
                    else:
                        await update.message.reply_text(
                            f"❌ **Error:** `{error_msg}`\n\n"
                            "Please try again with /start\n\n"
                            "✨ **Powered by:** @idxhelp",
                            parse_mode='Markdown'
                        )
                    
                    # Cleanup
                    try:
                        await client.disconnect()
                        await client.stop()
                    except:
                        pass
                    context.user_data.clear()
                    
            else:
                await update.message.reply_text(
                    "❌ **Invalid code!**\n\n"
                    "Please send the 5-digit verification code:\n\n"
                    "✨ **Powered by:** @idxhelp",
                    parse_mode='Markdown'
                )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Unexpected Error:** `{str(e)}`\n\n"
            "Please try again with /start\n\n"
            "✨ **Powered by:** @idxhelp",
            parse_mode='Markdown'
        )
        # Cleanup on error
        if 'client' in context.user_data:
            try:
                client = context.user_data['client']
                await client.disconnect()
                await client.stop()
            except:
                pass
        context.user_data.clear()

# Help command
async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = """
🆘 **Help Guide - String Session Generator**

📱 **How to Generate Session:**
1. /start command bhejein
2. 'Generate String Session' button click karein
3. Apna phone number bhejein (with country code)
4. Verification code bhejein
5. Session automatically aapke Saved Messages mein save ho jayega

🔐 **What is String Session?**
• Yeh aapke Telegram account ka authentication token hai
• Music bots banane ke liye use hota hai
• User bots ke liye use hota hai

⚠️ **Security Tips:**
• Session kisi se share na karein
• Secure jagah save karein
• Sirf trusted bots mein use karein

📞 **Phone Number Format:**
• Country code ke saath: `+919876543210`
• Without spaces

🔧 **Support:**
• Official Channel: @idxhelp
• Support Group: @idxhelp

✨ **Powered by:** @idxhelp
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Direct session command
async def session_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "🔐 **Direct Session Generation**\n\n"
        "Please send your Phone Number with country code:\n"
        "**Example:** `+919876543210`\n\n"
        "✨ **Powered by:** @idxhelp",
        parse_mode='Markdown'
    )
    context.user_data['step'] = 'phone'
    context.user_data['user_id'] = update.effective_user.id

# Error handler
async def error_handler(update: Update, context: CallbackContext) -> None:
    print(f"Error: {context.error}")

# Main function
def main():
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
    
    # Start bot
    print("🤖 Number-based Session Generator Bot Started!")
    print("✨ Powered by: @idxhelp")
    print("📱 Features: Real session generation, Auto-save to Saved Messages")
    print("🚀 Deployed on: Render")
    
    # Run bot
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
