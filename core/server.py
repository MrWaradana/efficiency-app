import click
from digital_twin_migration.models import db
from flasgger import Swagger
from flask import Flask
from flask.blueprints import Blueprint
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import text

import app.routes as routes
from core.cache import Cache, RedisBackend, CustomKeyMaker
from core.config import config
from core.exceptions import handle_exception
from core.schema import ma
from core.utils import response

# Initialize extensions
migrate = Migrate()
swagger = Swagger()
database = db
marshmallow = ma


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Server Configuration
    app.debug = config.DEBUG
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config["SECRET_KEY"] = config.SECRET_KEY

    # Bind extensions to the app
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    swagger.init_app(app)

    # CORS Configuration
    CORS(app)
    
    # Redis
    Cache.init(RedisBackend, CustomKeyMaker)

    # Create command functions
    @click.command(name="drop")
    @with_appcontext
    def drop():
        db.drop_all()
        print("DB Dropped!")
        return "DB Dropped!"

    @click.command(name="seed")
    @with_appcontext
    def seed():
        # Add your seeding logic here
        print("Database seeded!")
        return "Database seeded!"

    app.cli.add_command(drop)
    app.cli.add_command(seed)

    @app.route("/")
    def main():
        is_db_ok = "It's Working"
        try:
            # Test database connection
            db.engine.connect().execute(text("SELECT 1"))
        except Exception as e:
            is_db_ok = str(e)

        return response(200, True, is_db_ok)

    @app.errorhandler(Exception)
    def handle_error(e):
        # Define your custom error handling logic here
        return handle_exception(e)

    # Register Blueprints
    for blueprint in vars(routes).values():
        if isinstance(blueprint, Blueprint):
            app.register_blueprint(blueprint, url_prefix=config.APPLICATION_ROOT)

    return app
