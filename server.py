#!/usr/bin/env python
import io
import os
import requests
from PIL import Image, ImageFont, ImageDraw
from flask import Flask, request, send_file, make_response


app = Flask(__name__)


@app.route('/')
def nothing():
    return 'nothing here'


@app.route('/badge/<path:path>')
def bounty_badge(path):

    # Get values to draw on image
    usd_per_btc = requests.get(
        'https://bitpay.com/api/rates/usd').json()['rate']
    bounty_in_satoshi = requests.get(
        'https://blockchain.info/q/addressbalance/{0}'.format(path)).text
    bounty_in_btc = round((int(bounty_in_satoshi) / 10**8), 3)
    bounty_in_usd = round(bounty_in_btc * usd_per_btc, 2)

    # load up background image and fonts
    badge = Image.open('assets/bounty-bg.jpg')
    font_bounty = ImageFont.truetype('assets/western.ttf', 60)
    font_btc = ImageFont.truetype('assets/western.ttf', 50)
    font_usd = ImageFont.truetype('assets/western.ttf', 25)

    # draw on background
    draw = ImageDraw.Draw(badge)
    draw.text((10, 30), 'BOUNTY', fill='black', font=font_bounty)
    draw.text((20, 200), '{0} BTC'.format(
        bounty_in_btc), fill='black', font=font_btc)
    draw.text((55, 260), '({0} USD)'.format(bounty_in_usd),
              fill='black', font=font_usd)

    def serve_pil_image(pil_img):
        img_io = io.BytesIO()
        pil_img.save(img_io, 'JPEG', quality=70)
        img_io.seek(0)
        response = make_response(send_file(img_io, mimetype='image/jpeg'))
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Expires'] = -1
        return response

    return serve_pil_image(badge)

port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
