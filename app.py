from flask import Flask, request
import requests
import html
import json
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

BOT_TOKEN = '8420493182:AAHbSO6RhLTScqU2eXeuEvNXc7_HP8R1pyI'
CHAT_ID = '-1002490501639'

app = Flask(__name__)

def translate_to_indo(text):
    try:
        translated = GoogleTranslator(source='auto', target='id').translate(text)
        return translated
    except Exception as e:
        print(f"⚠️ Gagal translate: {e}")
        return text

def bersihin_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator="\n")

@app.route('/wp-webhook', methods=['POST'])
def wp_hook():
    data = request.json

    post_type = data.get('post_type')
    if post_type not in ['movies', 'tvshows']:
        return 'Skip', 200

    # Ambil data dari payload WP
    title = html.escape(data.get('title', 'Tanpa Judul'))
    link = data.get('link', '#')
    content_raw = data.get('content', '')
    featured_image = data.get('featured_image', '')

    tax = data.get('taxonomies', {})
    genres = ', '.join(tax.get('genres', []))
    cast = ', '.join(tax.get('dtcast', []))

    # Bersihkan dan translate sinopsis
    sinopsis = bersihin_html(content_raw)
    sinopsis_indo = translate_to_indo(sinopsis)

    # Format caption
    caption = f"""🎬 <b>{title}</b>

🎭 <b>Genre:</b> {html.escape(genres)}
🎥 <b>Cast:</b> {html.escape(cast)}

📝 <b>Sinopsis:</b>
{html.escape(sinopsis_indo)}
"""

    # Inline button
    reply_markup = {
        "inline_keyboard": [
            [{"text": "▶️ Tonton Sekarang", "url": link}]
        ]
    }

    # Kirim ke Telegram
    if not featured_image:
        print("❌ Gagal kirim: gambar kosong")
        return 'No image', 400

    res = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', data={
        'chat_id': CHAT_ID,
        'photo': featured_image,
        'caption': caption,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps(reply_markup)
    })

    if res.ok:
        print("✅ Berhasil kirim post:", title)
        return 'Terkirim', 200
    else:
        print("❌ Gagal kirim:", res.text)
        return f'Gagal: {res.text}', 500

if __name__ == '__main__':
    app.run()
