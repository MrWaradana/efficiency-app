from flask import Flask
from flask.blueprints import Blueprint
from flask_migrate import Migrate
from flask_cors import CORS
import click
from flask.cli import with_appcontext
from sqlalchemy import text

from utils import handle_exception, response

from config import config
import routes

# from models import db
from digital_twin_migration.models import db
from seeds import mainSeeder

from schemas.ma import ma


"""Create an application."""
server = Flask(__name__)

"""Server Configuration"""
server.debug = config.DEBUG
server.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
server.config["SECRET_KEY"] = config.SECRET_KEY


"""Database Configuration"""
db.init_app(server)
db.app = server

"""Migration Configuration"""
migrate = Migrate(server, db)

"""CORS Configuration"""
CORS(server)

"""Marshmallow Configuration"""
ma.init_app(server)

# create command function
@click.command(name="drop")
@with_appcontext
def drop():
    db.drop_all()
    return "DB Dropped!"


server.cli.add_command(drop)
server.cli.add_command(mainSeeder)


@server.route("/")
def main():
    is_db_ok = "It's Working"
    try:
        # Test database connection
        db.engine.connect().execute(text("SELECT 1"))
    except Exception as e:
        is_db_ok = str(e)

    return response(message=is_db_ok, status="ok", status_code=200)


@server.errorhandler(Exception)
def handle_error(e):
    return handle_exception(e)


for blueprint in vars(routes).values():
    if isinstance(blueprint, Blueprint):
        server.register_blueprint(blueprint, url_prefix=config.APPLICATION_ROOT)

if __name__ == "__main__":
    server.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
