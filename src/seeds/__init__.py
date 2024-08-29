import click
from flask.cli import with_appcontext
from .case import case_seeder


@click.command(name="seeder")
@with_appcontext
def mainSeeder():
    case_seeder()
