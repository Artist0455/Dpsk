import requests
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8339585926:AAEeluPGVakchVJ7TPDlIkio6A1HPYy4wRg"
DEEPSEEK_API_KEY = "sk-9b569ed95c7947fb982587f53bec6e15"

print("🚀 Starting AI Bot with Debug...")

def get_ai_response(message):
    """Get AI response with detailed debugging"""
    try:
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": message}],
            "max_tokens": 500
        }
        
        logger.info(f"Calling DeepSeek API with message: {message}")
        
        response = requests.post(
            'https://api.deepseek.com/chat/completions',
            headers=headers,
            json=data,
            timeout=45
        )
        
        logger.info(f"API Response Status: {response.status_code}")
        logger.info(f"API Response Headers: {response.headers}")
        
        if response.status_code == 200:
            result = response.json()
            response_text = result['choices'][0]['message']['content']
            logger.info(f"API Success - Response: {response_text[:100]}...")
            return response_text
            
        elif response.status_code == 401:
            logger.error("API Error 401: Unauthorized - Invalid API Key")
            return "❌ API Key invalid. Please check DeepSeek dashboard."
            
        elif response.status_code == 402:
            logger.error("API Error 402: Payment Required")
            return "❌ API quota exceeded. Please add credits to DeepSeek account."
            
        elif response.status_code == 429:
            logger.error("API Error 429: Rate Limit Exceeded")
            return "❌ Rate limit exceeded. Please wait a moment."
            
        else:
            logger.error(f"API Error {response.status_code}: {response.text}")
            return f"❌ API Error {response.status_code}. Please try again later."
            
    except requests.exceptions.Timeout:
        logger.error("API Timeout")
        return "❌ Request timeout. Please try again."
        
    except requests.exceptions.ConnectionError:
        logger.error("Connection Error")
        return "❌ Connection error. Please check your internet."
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"❌ Unexpected error: {str(e)}"

def get_updates(offset=None):
    """Get new messages from Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {'timeout': 30, 'offset': offset}
    
    try:
        response = requests.get(url, params=params, timeout=35)
        logger.info(f"Telegram API Status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Telegram API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Telegram connection error: {e}")
        return None

def send_message(chat_id, text):
    """Send message to Telegram user"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Split long messages
    if len(text) > 4096:
        text = text[:4090] + "..."
    
    data = {'chat_id': chat_id, 'text': text}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"Message sent to {chat_id}")
            return True
        else:
            logger.error(f"Send message failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Send message error: {e}")
        return False

def process_message(update):
    """Process incoming message"""
    if 'message' not in update:
        return None
    
    message = update['message']
    chat_id = message['chat']['id']
    text = message.get('text', '')
    update_id = update['update_id']
    
    logger.info(f"📩 Processing message from {chat_id}: {text}")
    
    if text.startswith('/start'):
        welcome_msg = """
🎉 नमस्ते! मैं DeepSeek AI Bot हूं!

🤖 मैं AI की मदद से आपके सवालों के जवाब दे सकता हूं।

💡 बस कोई भी message type करें:
• "Hello"
• "Python में list कैसे बनाएं?"
• "2+2 क्या है?"
• कुछ भी पूछें!

मैं आपकी help करूंगा! 😊
        """
        send_message(chat_id, welcome_msg)
        return update_id
        
    elif text.startswith('/status'):
        status_msg = "✅ Bot is running and active!"
        send_message(chat_id, status_msg)
        return update_id
        
    elif text.startswith('/'):
        # Ignore other commands
        return update_id
        
    else:
        # Get AI response
        thinking_msg = "🤔 Thinking..."
        send_message(chat_id, thinking_msg)
        
        ai_response = get_ai_response(text)
        send_message(chat_id, ai_response)
        return update_id

def main():
    """Main bot loop"""
    logger.info("✅ Bot started successfully!")
    logger.info("📱 Waiting for messages...")
    
    last_update_id = None
    
    while True:
        try:
            updates_data = get_updates(last_update_id)
            
            if updates_data and updates_data.get('ok'):
                for update in updates_data['result']:
                    last_update_id = process_message(update)
                    if last_update_id:
                        last_update_id += 1
            else:
                logger.info("No new messages...")
                
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"❌ Main loop error: {e}")
            time.sleep(10)

if __name__ == '__main__':
    main()
