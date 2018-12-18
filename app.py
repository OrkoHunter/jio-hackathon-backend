# -*- coding: utf-8 -*-
import os
import sys

from flask import Flask, render_template, redirect, request
from flask_session import Session

"""
Fetch static data
"""
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__, static_url_path='/static')
    sess = Session()
    app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)

    define_routes(app)
    return app


def define_routes(app):
    # Valid routes
    @app.route("/")
    def main():
        return render_template('index.html')


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
