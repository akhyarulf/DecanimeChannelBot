from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = '8420493182:AAFT69h6guoysRP5u46ZkKDQc2_f7DGdnX4'
CHAT_ID = '-1002490501639'  # contoh: -1001234567890

@app.route('/')
def index():
    return 'Bot Aktif!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    title = data.get('title')
    link = data.get('link')
    
    if title and link:
        message = f"🆕 {title}\n🔗 {link}"
        send_text = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(send_text, data={
            'chat_id': CHAT_ID,
            'text': message
        })
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
