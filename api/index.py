from flask import Flask, request
import requests
import html
import re

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator


# ======================
# TELEGRAM
# ======================

BOT_TOKEN = "8420493182:AAHbSO6RhLTScqU2eXeuEvNXc7_HP8R1pyI"
CHAT_ID = "@decanimechannel"


# ======================
# APP
# ======================

app = Flask(__name__)


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
        separator=" "
    ).strip()



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
            text[:1200]
        )


    except Exception as e:

        print(
            "Translate Error:",
            e
        )

        return text



# ======================
# RINGKAS SINOPSIS
# ======================

def ringkas_sinopsis(text):

    if not text:

        return "Tidak ada sinopsis."


    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )


    result = " ".join(
        sentences[:2]
    )


    if len(result) > 320:

        result = (
            result[:320]
            .rsplit(" ",1)[0]
            + "..."
        )


    return result



# ======================
# WEBHOOK WP
# ======================

@app.route(
    "/wp-webhook",
    methods=["POST"]
)

def wp_hook():


    data = request.json


    if not data:

        return "Empty Payload",400



    post_type = data.get(
        "post_type"
    )


    if post_type not in [
        "movies",
        "tvshows"
    ]:

        return "Skip",200



    # ======================
    # DATA BASIC
    # ======================

    title = data.get(
        "title",
        "Tanpa Judul"
    )


    link = data.get(
        "link",
        "#"
    )


    image = data.get(
        "featured_image",
        ""
    )


    release_date = data.get(
        "release_date",
        ""
    )


    if release_date:

        title += f" ({release_date[:4]})"



    # ======================
    # TAXONOMY
    # ======================

    tax = data.get(
        "taxonomies",
        {}
    )


    genre_list = tax.get(
        "genres",
        []
    )


    cast_list = tax.get(
        "dtcast",
        []
    )


    genres = " • ".join(
        genre_list
    )


    cast = ", ".join(
        cast_list[:20]
    )


    if len(cast_list) > 20:

        cast += ", dll."



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


    synopsis = ringkas_sinopsis(
        synopsis
    )



    # ======================
    # HASHTAG
    # ======================

    hashtags = [

        "#Decanime",

        "#Movies"
        if post_type == "movies"
        else "#Series"

    ]


    for genre in genre_list:

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
                "#" + tag
            )



    hashtag_text = " ".join(
        hashtags
    )



    # ======================
    # CAPTION
    # EDIT BAGIAN INI JIKA MAU UBAH FORMAT
    # ======================

    caption = f"""
<b>{html.escape(title)}</b>

{html.escape(genres)}

{html.escape(synopsis)}

<b>Pemain:</b>
{html.escape(cast)}

<a href="{html.escape(link, quote=True)}">▶️ Streaming &amp; Download di Decanime</a>

{hashtag_text}
"""



    caption = caption.strip()



    # Telegram max caption 1024
    if len(caption) > 1024:

        caption = caption[:1000] + "..."



    # ======================
    # SEND TELEGRAM
    # ======================

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

            return "OK",200


        return response.text,500



    except Exception as e:

        print(
            "Telegram Error:",
            e
        )

        return str(e),500
