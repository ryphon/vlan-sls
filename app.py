#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# coding: utf-8
from asg import ASGDirector
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def yay():
    return 'yay!', 200


@app.route('/game', methods=['POST'])
def gameStartup():
    data = request.get_json()
    if 'password' in data:
        if data['password'] == 'gnuISnotUNIX':
            return 'fuck you', 401
    else:
        return 'fuck you', 401
    if 'game' in data:
        game = data['game']
    if 'gameType' in data:
        game_type = data['gameType']
    if 'action' in data:
        action = data['action']
    asg = ASGDirector()
    resp = asg.scale(game, game_type, action)
    return resp, 200


@app.route('/status/<game>/<game_type>', methods=['GET'])
def gameStatus(game, game_type):
    asg = ASGDirector()
    resp = asg.status(game, game_type)
    return resp, 200
