from flask import Flask, request
import requests
import html
import json
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

        translated = GoogleTranslator(
            source='auto',
            target='id'
        ).translate(text[:1000])


        return translated


    except:

        return text





def bersihin_html(raw_html):

    if not raw_html:

        return ""


    soup = BeautifulSoup(
        raw_html,
        "html.parser"
    )


    return soup.get_text(
        separator="\n"
    ).strip()





@app.route('/wp-webhook', methods=['POST'])
def wp_hook():


    data = request.json


    if not data:

        return "Empty Payload",400



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


    runtime = data.get(
        'runtime',
        '-'
    )


    rating = data.get(
        'rating',
        '-'
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




    genres = ', '.join(
        genres_list
    )


    cast = ', '.join(
        cast_list
    )




    sinopsis = bersihin_html(

        data.get(
            'content',
            ''
        )

    )


    sinopsis = translate_to_indo(
        sinopsis
    )




    # Hashtag kategori

    if post_type == "movies":

        category = "#Movies"

    else:

        category = "#Series"




    hashtags = [

        "#Decanime",

        category

    ]



    # semua genre masuk hashtag

    for genre in genres_list:


        tag = re.sub(

            r'[^a-zA-Z0-9]',

            '',

            genre.replace(
                " ",
                ""
            )

        )


        if tag:

            hashtags.append(
                "#" + tag
            )




    if country:


        hashtags.append(

            "#" + re.sub(

                r'[^a-zA-Z0-9]',

                '',

                country.replace(
                    " ",
                    ""
                )

            )

        )





    caption = f"""

<b>{html.escape(title)}</b>

<b>Genre:</b> <i>{html.escape(genres)}</i>
<b>Negara:</b> <i>{html.escape(country)}</i>
<b>Durasi:</b> <i>{runtime} Menit</i>
<b>Rating:</b> <i>{rating}/10 IMDb</i>

<b>Sinopsis:</b>
{html.escape(sinopsis)}

<b>Pemain:</b>
{html.escape(cast)}

<a href="{link}">Streaming & Download</a>

{' '.join(hashtags)}

"""



    if len(caption) > 1024:

        caption = caption[:1020] + "..."




    if not image:

        return "No Image",400




    try:


        res = requests.post(

            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",

            data={


                "chat_id":CHAT_ID,


                "photo":image,


                "caption":caption,


                "parse_mode":"HTML"


            },


            timeout=20

        )



        if res.ok:

            return "Terkirim",200



        return res.text,500




    except Exception as e:

        return str(e),500
