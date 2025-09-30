import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'fjtickets.sqlite'),
    )

    if test_config is None:
        # outside of test, try to load the instance configuration
        app.config.from_pyfile('config.py', silent=True)
    else:
        # otherwise if there is a test configuration, load it
        app.config.from_mapping(test_config)

    # check that the instance folder has been created
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # testing whether the URL system works
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from.import db
    db.init_app(app)

    from.import auth
    app.register_blueprint(auth.bp)

    from.import ticket
    app.register_blueprint(ticket.bp)
    app.add_url_rule('/', endpoint='index')

    return app