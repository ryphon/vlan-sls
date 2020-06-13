#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# coding: utf-8

from flask import Flask, request

app = Flask(__name__)


@app.route('/<var>')
def yay(var):
    return var, 200


@app.route('/game', methods=['POST'])
def gamestartup():
    data = request.json
    return data, 200
