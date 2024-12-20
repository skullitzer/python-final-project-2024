from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import request, jsonify

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipe_manager.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Import and register the blueprint
    from .routes import main
    app.register_blueprint(main)

    return app