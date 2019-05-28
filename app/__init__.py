import os

from flask import Flask
from config import Config as cfg


def create_app(test_config=None):
    # create and configure the app
    app=Flask(__name__, instance_relative_config=True)
    app.debug = True
    app.secret_key = cfg.SECRET_KEY

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load test config if passed in
        app.config.from_mapping(test_config)

    from . import connect
    app.register_blueprint(connect.bp)

    from . import export
    app.register_blueprint(export.bp)
    app.add_url_rule('/', endpoint='index')

    return app
