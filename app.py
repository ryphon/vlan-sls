#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# coding: utf-8
from asg import ASGDirector
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def yay():
    return {'yay?': 'yay!'}, 200


@app.route('/game', methods=['POST'])
def gameStartup():
    try:
        data = request.get_json()
        if 'password' in data:
            if data['password'] != 'gnuISnotUNIX':
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
        status = resp['ResponseMetadata']['HTTPStatusCode']
        if status == 200:
            ret = {
                'success': True,
                'errorMsg': None
            }
        else:
            ret = {
                'success': False,
                'errorMsg': 'Bad AWS Status Code'
            }
    except Exception as e:
        ret['success'] = False
        ret['errorMsg'] = e
    return ret, status


@app.route('/statusAll', methods=['GET'])
def allStatus():
    try:
        asg = ASGDirector()
        ret = asg.statusAll()
        status = 200
    except Exception as e:
        ret['success'] = False
        ret['errorMsg'] = e
        status = 500
    return ret, status


@app.route('/status/<game>/<game_type>', methods=['GET'])
def gameStatus(game, game_type):
    ret = dict()
    try:
        asg = ASGDirector()
        ret = asg.status(game, game_type)
        status = 200
        return ret, status
    except Exception as e:
        ret['success'] = False
        ret['errorMsg'] = e
        status = 500
        return ret, status
