from flask import Flask, request
import requests
import html
from bs4 import BeautifulSoup

BOT_TOKEN = '8420493182:AAFT69h6guoysRP5u46ZkKDQc2_f7DGdnX4'
CHAT_ID = '-1002490501639'

app = Flask(__name__)

def translate_to_indo(text):
    try:
        r = requests.post(
            "https://api.deep-translator.com/translate",
            json={"source": "en", "target": "id", "text": text},
            timeout=10
        )
        if r.ok and 'data' in r.json():
            return r.json()['data']['translatedText']
    except Exception:
        pass
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
    featured_image = data.get('featured_image', '')  # pastikan ini dikirim

    tax = data.get('taxonomies', {})
    genres = ', '.join(tax.get('genres', []))
    cast = ', '.join(tax.get('dtcast', []))

    # Bersihkan dan translate sinopsis
    sinopsis = bersihin_html(content_raw)
    sinopsis_indo = translate_to_indo(sinopsis)

    # Format caption pesan
    caption = f"""🎬 <b>{title}</b>

🎭 <b>Genre:</b> {html.escape(genres)}
🎥 <b>Cast:</b> {html.escape(cast)}

📝 <b>Sinopsis:</b>
{html.escape(sinopsis_indo)}
"""

    # Inline button "Tonton Sekarang"
    reply_markup = {
        "inline_keyboard": [
            [{"text": "▶️ Tonton Sekarang", "url": link}]
        ]
    }

    # Kirim foto dengan caption + button
    res = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', data={
        'chat_id': CHAT_ID,
        'photo': featured_image,
        'caption': caption,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps(reply_markup)
    })

    if res.status_code == 200:
        return 'Terkirim', 200
    else:
        return f'Gagal: {res.text}', 500

if __name__ == '__main__':
    app.run()
