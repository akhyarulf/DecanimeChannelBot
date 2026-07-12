from flask import Flask, request
import requests
import html
import os
import re
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
        return GoogleTranslator(
            source='auto',
            target='id'
        ).translate(text[:900])
    except:
        return text

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


@app.route('/wp-webhook', methods=['POST'])

def wp_hook():
    data = request.json
    if not data:
        return "Empty",400
    post_type = data.get(
        'post_type'
    )
    if post_type not in [
        'movies',
        'tvshows'
    ]:
        return "Skip",200
    title = data.get(
        'title',
        'Tanpa Judul'
    )
    link = data.get(
        'link',
        '#'
    )
    image = data.get(
        'featured_image'
    )
    country = data.get(
        'country',
        '-'
    )
    rating = data.get(
        'rating',
        '-'
    )
    rating_source = data.get(
        'rating_source',
        'TMDB'
    )
    tax = data.get(
        'taxonomies',
        {}
    )
    genres_list = tax.get(
        'genres',
        []
    )
    cast_list = tax.get(
        'dtcast',
        []
    )
    quality_list = tax.get(
        'quality',
        []
    )
    genres = ', '.join(
        genres_list
    )
    cast = ', '.join(
        cast_list
    )
    quality = ', '.join(
        quality_list
    ) if quality_list else 'HD'
    synopsis = clean_html(
        data.get(
            'content',
            ''
        )
    )
    synopsis = translate_to_indo(
        synopsis
    )

    if post_type == 'movies':
        category = '#Movies'
    else:
        category = '#Series'

    hashtags = [
        '#Decanime',

        category

    ]

    # semua genre masuk hashtag

    for genre in genres_list:
        tag = re.sub(
            r'[^a-zA-Z0-9]',
            '',
            genre.replace(', ', ' • ')
        )
        if tag:
            hashtags.append(
                '#'+tag
            )


    if country:
        country_tag = re.sub(
            r'[^a-zA-Z0-9]',
            '',
            country.replace(
                ' ',
                ''
            )
        )
        if country_tag:
            hashtags.append(
                '#'+country_tag
            )


    caption = f"""
🎬 <b>{html.escape(title)}</b>

{html.escape(genres)}
{html.escape(country)} • {html.escape(quality)}
{html.escape(rating)}/10 {rating_source}

<b>Sinopsis:</b>
{html.escape(synopsis)}

<b>Pemain:</b>
{html.escape(cast)}

▶️ <a href="{link}">Streaming &amp; Download di Decanime</a>

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
                "chat_id":CHAT_ID,
                "photo":image,
                "caption":caption,
                "parse_mode":"HTML"
            },
            timeout=20
        )
        if response.ok:
            return "Terkirim",200
        return response.text,500
    except Exception as e:
        return str(e),500
