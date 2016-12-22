import datetime
import json
import logging
import os
import requests
import sys

from flask import Flask, request, Response, g, jsonify

import peewee as pw
import playhouse.postgres_ext as playhouse

import api
from config import Config
import game
import models

app = Flask(__name__)
app.config.from_object('config.Config')

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

@app.before_request
def before_request():
        g.db = models.db
        g.app = app
        g.db.connect()


@app.after_request
def after_request(response):
        g.db.close()
        return response


@app.route('/ttt', methods=['POST']) 
def inbound():
        app.logger.debug("REQUEST =======")
        
        if request.form.get('token') == Config.SLACK_WEBHOOK_SECRET:
                
                channel = request.form.get('channel_id')
                username = request.form.get('user_name')
                user_id = request.form.get('user_id')
                command = request.form.get('command')
                text = request.form.get('text')
                res_url = request.form.get('response_url')

                try:
                        command_response = api.get_command((username, user_id), text, channel)
                except (game.GameInitError, game.BoardError, api.CommandError) as e:
                        command_response = e

                res_text = {
                        "response_type": "in_channel",
                        "attachments": [
                                {
                                        "fallback": "",
                                        "text": "Current TicTacToe in channel: {}".format(request.form.get('channel_name')),
                                        "fields": [
                                                {
                                                        "title": "{} command issued by @{}!".format(text.upper(), username),
                                                        "value": "```\n{}\n```".format(command_response)
                                                }
                                        ],
                                        "ts": str(datetime.datetime.now()),
                                        "mrkdwn_in": ["text", "pretext", "footer"]
                                }
                        ]
                }
                
                requests.post(res_url, json=res_text)
                r = Response(mimetype='application/json')
                r.data = res_text

                return r, 200

        return Response(mimetype='application/json'), 200


@app.route('/', methods=['GET'])
def test():
        return Response('ticslashtoe server running', mimetype='application/json')

if __name__ == "__main__":

        app.run(debug=True)
