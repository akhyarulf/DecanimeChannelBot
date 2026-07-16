from flask import Flask, request
import requests
import html
import os
import re

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from google import genai


# ======================
# ENV
# ======================

BOT_TOKEN = os.environ.get(
    "8420493182:AAHbSO6RhLTScqU2eXeuEvNXc7_HP8R1pyI"
)

CHAT_ID = os.environ.get(
    "@decanimechannel"
)

GEMINI_API_KEY = os.environ.get(
    "AIzaSyCHI5t01JIbpcLfJy8VRZ1I_fJ2TfqgOEw"
)

print("BOT_TOKEN:", bool(BOT_TOKEN))
print("CHAT_ID:", bool(CHAT_ID))
print("GEMINI_API_KEY:", bool(GEMINI_API_KEY))

# ======================
# APP
# ======================

app = Flask(__name__)


# ======================
# GEMINI
# ======================

client = genai.Client(
    api_key=GEMINI_API_KEY
)



def summarize_synopsis(text):

    if not text.strip():

        return "Tidak ada sinopsis."


    try:

        prompt = f"""
Ringkas sinopsis film berikut menjadi 2-3 kalimat.

Aturan:
- Bahasa Indonesia natural
- Jangan spoiler
- Pertahankan nama karakter penting
- Fokus konflik utama
- Jangan menambahkan informasi baru

Sinopsis:
{text}
"""


        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )


        if response.text:

            return response.text.strip()


        return text


    except Exception as e:

        print(
            "Gemini Error:",
            e
        )

        return text





# ======================
# TRANSLATE
# ======================

def translate_to_indo(text):

    if not text.strip():

        return "Tidak ada sinopsis."


    try:

        return GoogleTranslator(
            source="auto",
            target="id"
        ).translate(
            text[:900]
        )


    except:

        return text





# ======================
# CLEAN HTML
# ======================

def clean_html(text):

    if not text:

        return ""


    soup = BeautifulSoup(
        text,
        "html.parser"
    )


    return soup.get_text(
        separator="\n"
    ).strip()





# ======================
# WEBHOOK
# ======================

@app.route(
    "/wp-webhook",
    methods=["POST"]
)

def wp_hook():


    data = request.json


    if not data:

        return "Empty",400



    post_type = data.get(
        "post_type"
    )


    if post_type not in [
        "movies",
        "tvshows"
    ]:

        return "Skip",200





    title = data.get(
        "title",
        "Tanpa Judul"
    )


    link = data.get(
        "link",
        "#"
    )


    image = data.get(
        "featured_image"
    )





    tax = data.get(
        "taxonomies",
        {}
    )


    genres_list = tax.get(
        "genres",
        []
    )


    cast_list = tax.get(
        "dtcast",
        []
    )





    genres = " • ".join(
        genres_list
    )


    cast = ", ".join(
        cast_list
    )





    # ======================
    # SINOPSIS
    # ======================

    synopsis = clean_html(
        data.get(
            "content",
            ""
        )
    )


    synopsis = translate_to_indo(
        synopsis
    )


    synopsis = summarize_synopsis(
        synopsis
    )





    # ======================
    # HASHTAG
    # ======================

    category = (
        "#Movies"
        if post_type == "movies"
        else "#Series"
    )


    hashtags = [

        "#Decanime",

        category

    ]



    for genre in genres_list:


        tag = re.sub(
            r"[^a-zA-Z0-9]",
            "",
            genre.replace(
                " ",
                ""
            )
        )


        if tag:

            hashtags.append(
                "#"+tag
            )





    # ======================
    # CAPTION
    # ======================


    caption = f"""
<b>{html.escape(title)}</b>

{html.escape(genres)}

{html.escape(synopsis)}

<b>Pemain:</b>
{html.escape(cast)}

<a href="{link}">▶️ Streaming &amp; Download di Decanime</a>

{' '.join(hashtags)}
"""





    if len(caption) > 1024:

        caption = caption[:1000] + "..."





    if not image:

        return "No Image",400





    try:


        response = requests.post(

            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",

            data={

                "chat_id": CHAT_ID,

                "photo": image,

                "caption": caption,

                "parse_mode": "HTML"

            },

            timeout=20

        )



        if response.ok:

            return "Terkirim",200



        return response.text,500



    except Exception as e:

        print(
            "Telegram Error:",
            e
        )

        return str(e),500
