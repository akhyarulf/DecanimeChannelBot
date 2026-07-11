from flask import Flask, request
import requests
import html
import json
import os
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

BOT_TOKEN = os.environ.get(
    'BOT_TOKEN',
    '8420493182:AAHbSO6RhLTScqU2eXeuEvNXc7_HP8R1pyI'
)

CHAT_ID = os.environ.get(
    'CHAT_ID',
    '@decanimechannel'
)

app = Flask(__name__)


def translate_to_indo(text):
    if not text.strip():
        return "Tidak ada sinopsis."

    try:
        text_truncated = text[:1000]
        translated = GoogleTranslator(
            source='auto',
            target='id'
        ).translate(text_truncated)

        if len(text) > 1000:
            translated += "..."

        return translated

    except Exception as e:
        print(e)
        return text


def bersihin_html(raw_html):
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator="\n").strip()


@app.route('/wp-webhook', methods=['POST'])
def wp_hook():

    data = request.json

    if not data:
        return "Empty Payload", 400

    if data.get("post_type") not in ["movies", "tvshows"]:
        return "Skip", 200

    title = html.escape(data.get("title", "Tanpa Judul"))
    link = data.get("link", "#")
    featured_image = data.get("featured_image", "")

    country = data.get("country", "-")
    runtime = data.get("runtime", "-")
    imdb_rating = data.get("imdb_rating", "-")
    release_date = data.get("release_date", "")

    year = ""
    if release_date:
        year = release_date[:4]

    tax = data.get("taxonomies", {})

    genre_list = tax.get("genres", [])
    quality_list = tax.get("quality", [])
    cast_list = tax.get("dtcast", [])

    genres = " • ".join(genre_list) if genre_list else "-"
    quality = ", ".join(quality_list) if quality_list else "-"
    cast = ", ".join(cast_list) if cast_list else "-"

    content_raw = data.get("content", "")
    sinopsis = bersihin_html(content_raw)
    sinopsis = translate_to_indo(sinopsis)

    hashtags = ["#Decanime", "#Movies"]

    for g in genre_list:
        hashtags.append("#" + g.replace(" ", ""))

    if country:
        hashtags.append("#" + country.replace(" ", ""))

    if year:
        hashtags.append("#" + year)

    caption = (
        f"🎬 <b>{title}</b>\n\n"

        f"<b>Genre:</b>\n"
        f"{html.escape(genres)}\n\n"

        f"<b>Info:</b>\n"
        f"Negara: {html.escape(country)}\n"
        f"Durasi: {runtime} Menit\n"
        f"Kualitas: {html.escape(quality)}\n"
        f"Rating: {imdb_rating}/10 IMDb\n\n"

        f"<b>Sinopsis:</b>\n"
        f"{html.escape(sinopsis)}\n\n"

        f"<b>Pemain:</b>\n"
        f"{html.escape(cast)}\n\n"

        f"▶️ <b>Streaming & Download di Decanime</b>\n"
        f"{link}\n\n"

        f"{' '.join(hashtags)}"
    )

    if len(caption) > 1024:
        caption = caption[:1021] + "..."

    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "🎬 Streaming & Download",
                    "url": link
                }
            ]
        ]
    }

    if not featured_image:
        return "No Image", 400

    try:

        res = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            data={
                "chat_id": CHAT_ID,
                "photo": featured_image,
                "caption": caption,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(reply_markup)
            },
            timeout=20
        )

        if res.ok:
            return "OK", 200

        return res.text, 500

    except Exception as e:
        return str(e), 500
