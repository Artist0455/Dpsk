import requests
import time

# Configuration
BOT_TOKEN = "8339585926:AAEeluPGVakchVJ7TPDlIkio6A1HPYy4wRg"
DEEPSEEK_API_KEY = "sk-9b569ed95c7947fb982587f53bec6e15"

print("🚀 Starting DeepSeek AI Bot...")

def call_deepseek_api(message):
    """Call DeepSeek API and return response"""
    try:
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": message}]
        }
        
        response = requests.post(
            'https://api.deepseek.com/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: API returned status {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def get_updates(offset=None):
    """Get new messages from Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {'timeout': 30, 'offset': offset}
    
    try:
        response = requests.get(url, params=params, timeout=35)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def send_message(chat_id, text):
    """Send message to Telegram user"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    
    try:
        requests.post(url, json=data, timeout=10)
        return True
    except:
        return False

def process_message(update):
    """Process incoming message"""
    if 'message' not in update:
        return None
    
    message = update['message']
    chat_id = message['chat']['id']
    text = message.get('text', '')
    update_id = update['update_id']
    
    print(f"📩 Received: {text}")
    
    if text.startswith('/start'):
        welcome_msg = """
🎉 नमस्ते! मैं DeepSeek AI Bot हूं!

🤖 मैं AI की मदद से आपके सवालों के जवाब दे सकता हूं।

💡 बस कोई भी message type करें जैसे:
• "Hello"
• "Python में list कैसे बनाएं?"
• "2+2 क्या है?"
• "Email लिखने में मदद करें"

मैं आपकी help करूंगा! 😊
        """
        send_message(chat_id, welcome_msg)
        return update_id
        
    elif text.startswith('/'):
        # Ignore other commands
        return update_id
        
    else:
        # Get AI response
        ai_response = call_deepseek_api(text)
        send_message(chat_id, ai_response)
        return update_id

def main():
    """Main bot loop"""
    print("✅ Bot started successfully!")
    print("📱 Waiting for messages...")
    
    last_update_id = None
    
    while True:
        try:
            # Get updates from Telegram
            updates_data = get_updates(last_update_id)
            
            if updates_data and updates_data.get('ok'):
                for update in updates_data['result']:
                    last_update_id = process_message(update)
                    
                    if last_update_id:
                        last_update_id += 1  # Move to next update
                
            # Wait before next check
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
