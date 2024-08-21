from flask import Flask
from flask.blueprints import Blueprint
from flask_migrate import Migrate
from flask_cors import CORS
import click
from flask.cli import with_appcontext
from sqlalchemy import text

from utils import handle_exception, response

import config
import routes

# from models import db
from digital_twin_migration.models import db
from seeds import mainSeeder


"""Create an application."""
server = Flask(__name__)

"""Server Configuration"""
server.debug = config.DEBUG
# server.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI
server.config["SQLALCHEMY_DATABASE_URI"] = (
    # "postgresql+psycopg2://aimo:aimo%21%40%23@localhost:5432/ircfa"
    config.DB_URI
)
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS
server.config["SECRET_KEY"] = config.SECRET_KEY
server.config["IMAGE_URL"] = config.IMAGE_URL


"""Database Configuration"""
db.init_app(server)
db.app = server

"""Migration Configuration"""
migrate = Migrate(server, db)

"""CORS Configuration"""
CORS(server)


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
        db.session.execute(text("SELECT 1")).all()
    except Exception:
        is_db_ok = "Something wrong with database"

    return response(
        message=is_db_ok,
        status="ok",
        status_code=200
    )


@server.errorhandler(Exception)
def handle_error(e):
    return handle_exception(e)


for blueprint in vars(routes).values():
    if isinstance(blueprint, Blueprint):
        server.register_blueprint(blueprint, url_prefix=config.APPLICATION_ROOT)

if __name__ == "__main__":
    server.run(host="127.0.0.1", port="3001")
