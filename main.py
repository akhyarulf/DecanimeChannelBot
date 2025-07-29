from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# === GANTI BAGIAN INI ===
BOT_TOKEN = '8420493182:AAFT69h6guoysRP5u46ZkKDQc2_f7DGdnX4'
CHAT_ID = '-1002490501639'  # Gunakan chat ID grup (format minus)
# ========================

@app.route('/')
def index():
    return 'Webhook Telegram Bot by Deta Space'

@app.route('/wp-webhook', methods=['POST'])
def wp_webhook():
    try:
        data = request.get_json()

        # Debug data yang diterima
        print("📥 Data masuk:", data)

        title = data.get('title', 'Tanpa Judul')
        link = data.get('link', '')
        message = f"🆕 <b>{title}</b>\n🔗 <a href='{link}'>Buka postingan</a>"

        # Kirim ke Telegram
        send_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        response = requests.post(send_url, json=payload)
        print("📤 Status kirim:", response.status_code)

        return jsonify({'status': 'ok', 'telegram_status': response.status_code})

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
