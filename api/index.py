from flask import Flask, request
import requests
import html
import json
import os
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

# Token aman, bisa diatur lewat dashboard Vercel nanti
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8420493182:AAHbSO6RhLTScqU2eXeuEvNXc7_HP8R1pyI')
CHAT_ID = os.environ.get('CHAT_ID', '-1002490501639')

app = Flask(__name__)

def translate_to_indo(text):
    if not text.strip():
        return "Tidak ada sinopsis."
    try:
        text_truncated = text[:1000]
        translated = GoogleTranslator(source='auto', target='id').translate(text_truncated)
        if len(text) > 1000:
            translated += "..."
        return translated
    except Exception as e:
        print(f"⚠️ Gagal translate: {e}")
        return text

def bersihin_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator="\n")

@app.route('/wp-webhook', methods=['POST'])
def wp_hook():
    data = request.json
    if not data:
        return 'Empty Payload', 400

    post_type = data.get('post_type')
    if post_type not in ['movies', 'tvshows']:
        return 'Skip', 200

    title = html.escape(data.get('title', 'Tanpa Judul'))
    link = data.get('link', '#')
    content_raw = data.get('content', '')
    featured_image = data.get('featured_image', '')

    tax = data.get('taxonomies', {})
    genres = ', '.join(tax.get('genres', [])) if tax.get('genres') else 'Uncategorized'
    cast = ', '.join(tax.get('dtcast', [])) if tax.get('dtcast') else '-'

    sinopsis = bersihin_html(content_raw)
    sinopsis_indo = translate_to_indo(sinopsis)

    caption = f"🎬 <b>{title}</b>\n\n" \
              f"🎭 <b>Genre:</b> {html.escape(genres)}\n" \
              f"🎥 <b>Cast:</b> {html.escape(cast)}\n\n" \
              f"📝 <b>Sinopsis:</b>\n{html.escape(sinopsis_indo)}"

    if len(caption) > 1021:
        caption = caption[:1018] + "..."

    reply_markup = {
        "inline_keyboard": [
            [{"text": "▶️ Tonton Sekarang", "url": link}]
        ]
    }

    if not featured_image:
        return 'No image', 400

    try:
        res = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', 
            data={
                'chat_id': CHAT_ID,
                'photo': featured_image,
                'caption': caption,
                'parse_mode': 'HTML',
                'reply_markup': json.dumps(reply_markup)
            },
            timeout=15
        )
        if res.ok:
            return 'Terkirim', 200
        else:
            return f'Gagal Telegram: {res.text}', 500
    except Exception as e:
        return 'Network Error', 500

# Bagian app.run() dihapus karena jalannya server dihandle langsung oleh Vercel
