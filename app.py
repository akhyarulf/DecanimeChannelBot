from flask import Flask, request
import requests
from bs4 import BeautifulSoup
import html
import json
from deep_translator import GoogleTranslator

BOT_TOKEN = '8420493182:AAFT69h6guoysRP5u46ZkKDQc2_f7DGdnX4'
CHAT_ID = '-1002490501639'

app = Flask(__name__)

def ambil_gambar_dari_html(url):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        img_tag = soup.select_one('img.wp-post-image') or soup.find('img')
        if img_tag:
            return img_tag.get('src')
    except Exception as e:
        print('❌ Gagal scrape gambar:', e)
    return ''

def translate_to_indo(text):
    try:
        return GoogleTranslator(source='auto', target='id').translate(text)
    except:
        return text

@app.route('/wp-webhook', methods=['POST'])
def wp_hook():
    data = request.json
    if data.get('post_type') not in ['movies', 'tvshows']:
        return 'Skip', 200

    title = html.escape(data.get('title', 'Tanpa Judul'))
    link = data.get('link', '#')
    content = data.get('content', '')
    featured_image = data.get('featured_image')

    if not featured_image:
        featured_image = ambil_gambar_dari_html(link)

    tax = data.get('taxonomies', {})
    genres = ', '.join(tax.get('genres', []))
    cast = ', '.join(tax.get('dtcast', []))

    sinopsis = BeautifulSoup(content, 'html.parser').get_text(separator="\n").strip()
    sinopsis_indo = translate_to_indo(sinopsis)

    caption = f"""🎬 <b>{title}</b>

🎭 <b>Genre:</b> {html.escape(genres)}
🎥 <b>Cast:</b> {html.escape(cast)}

📝 <b>Sinopsis (Terjemahan):</b>
{html.escape(sinopsis_indo)}
"""

    reply_markup = {
        "inline_keyboard": [
            [{"text": "▶️ Tonton Sekarang", "url": link}]
        ]
    }

    res = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={
            "chat_id": CHAT_ID,
            "photo": featured_image,
            "caption": caption,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(reply_markup)
        }
    )

    if res.ok:
        print("✅ Terkirim ke Telegram")
        return 'OK', 200
    else:
        print("❌ Gagal kirim:", res.text)
        return 'Gagal', 500

if __name__ == '__main__':
    app.run()
