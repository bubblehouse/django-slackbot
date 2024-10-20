# -*- coding: utf-8 -*-
import json
import base64
import logging
import random
from urllib.parse import urlencode, parse_qs, urlparse

import requests

from django_slackbot.chat import app

log = logging.getLogger(__name__)

@app.command("/frink")
def frink(ack, respond, command):
    ack()
    result = handler("https://frinkiac.com", command)
    respond(result)

@app.command("/morbo")
def morbo(ack, respond, command):
    ack()
    result = handler("https://morbotron.com", command)
    respond(result)

@app.action({
    "block_id": "select-screenshot",
    "action_id": "post"
})
def post_image(ack, action, respond, say):
    ack()
    respond(
        response_type = "ephemeral",
        replace_original = True,
        delete_original = True,
        text = ''
    )
    say(
        blocks = [{
            "type": "image",
            "image_url": action['value'],
            "alt_text": ""
        }]
    )

@app.action({
    "block_id": "select-screenshot",
    "action_id": "shuffle"
})
def shuffle_image(ack, action, respond):
    ack()
    response = parse_qs(action['value'])
    site_url = response['u'][0]
    query = response['q'][0]
    response = random.choice(get_results(site_url, query))
    caption = get_caption(
        site_url,
        response['Episode'],
        response['Timestamp']
    )
    image_url = site_url + "/img/%s/%s.jpg" % (caption['Frame']['Episode'], caption['Frame']['Timestamp'])
    respond(
        response_type = "ephemeral",
        replace_original = True,
        **create_confirmation_message(site_url, query, image_url)
    )

@app.action({
    "block_id": "select-screenshot",
    "action_id": "cancel"
})
def cancel_iamge(ack, respond):
    ack()
    respond(
        response_type = "ephemeral",
        replace_original = True,
        delete_original = True,
        text = ''
    )

@app.action({
    "block_id": "select-screenshot",
    "action_id": "add-meme"
})
def meme_image(ack, respond, body, action, client):
    ack()
    data = parse_qs(action['value'])
    url = urlparse(data['i'][0])
    _, _, episode, timestamp_jpg = url.path.split('/')
    caption = get_caption(
        url.scheme + "://" + url.hostname,
        episode,
        timestamp_jpg.split('.')[0]
    )
    meme_text = '\n'.join([x['Content'] for x in caption['Subtitles']])
    respond(
        response_type = "ephemeral",
        replace_original = True,
        delete_original = True,
        text = ''
    )
    client.dialog_open(trigger_id=body['trigger_id'], dialog=json.dumps(dict(
        callback_id = "update-meme",
        title = "Add a Meme",
        submit_label = "Add",
        state = action['value'],
        elements = [{
            "type": "textarea",
            "label": "Meme Text",
            "name": "meme",
            "value": meme_text
        }]
    )))

@app.action({
    "type": "dialog_submission",
    "callback_id": "update-meme"
})
def update_meme(ack, respond, action):
    ack()
    data = parse_qs(action['state'])
    image_url = update_meme_text(data['i'][0], action['submission']['meme'])
    respond(
        response_type = "ephemeral",
        replace_original = True,
        **create_confirmation_message(data['u'][0], data['q'][0], image_url)
    )

def handler(site_url, command):
    query = command['text']
    response = get_results(site_url, query)
    caption = get_caption(
        site_url,
        response[0]['Episode'],
        response[0]['Timestamp']
    )

    image_url = site_url + "/img/%s/%s.jpg" % (caption['Frame']['Episode'], caption['Frame']['Timestamp'])
    log.debug("Confirming post of %s" % image_url, extra=command)
    message = create_confirmation_message(site_url, query, image_url)
    return message

def get_results(site_url, query):
    api_url = site_url + "/api/search"
    url = api_url + '?' + urlencode(dict(q=query))
    r = requests.get(url)
    return json.loads(r.text)

def get_caption(site_url, episode, timestamp):
    caption_url = site_url + "/api/caption"
    url = caption_url + '?' + urlencode(dict(e=episode,t=timestamp))
    r = requests.get(url)
    return json.loads(r.text)

def create_confirmation_message(site_url, query, image_url):
    message = {
        "blocks": [{
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": query,
                "emoji": True
            },
            "image_url": image_url,
            "alt_text": "Screenshot confirmation"
        }, {
            "type": "actions",
            "block_id": "select-screenshot",
            "elements": [{
                "type": "button",
                "style": "primary",
                "text": {
                    "type": "plain_text",
                    "text": "Post",
                    "emoji": True
                },
                "value": image_url,
                "action_id": "post"
            }, {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Add Meme",
                    "emoji": True
                },
                "value": urlencode(dict(q=query, u=site_url, i=image_url)),
                "action_id": "add-meme"
            }, {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Shuffle",
                    "emoji": True
                },
                "value": urlencode(dict(q=query, u=site_url)),
                "action_id": "shuffle"
            }, {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Cancel",
                    "emoji": True
                },
                "value": "cancel",
                "action_id": "cancel"
            }]
        }]
    }
    return message

def update_meme_text(image_url, meme_text):
    image_url = image_url.replace('/img/', '/meme/')
    url, _ = image_url.split("?", maxsplit=1) if '?' in image_url else (image_url, '')
    meme64 = base64.b64encode(meme_text.encode('utf8'))
    return url + "?b64lines=" + meme64.decode("utf8")
