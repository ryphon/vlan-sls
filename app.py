#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# coding: utf-8

import boto3
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def yay():
    return 'yay!', 200


@app.route('/game', methods=['POST', 'GET'])
def gamestartup():
    if request.method == 'POST':
        data = request.json
        return data, 200
    else:
        return 'game', 200


@app.route('/aaron/<mood>')
def aaron(mood):
    string = 'an {} aaron is watching me right now!'.format(mood)
    return string, 200
