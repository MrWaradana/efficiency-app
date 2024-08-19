import click
from flask.cli import with_appcontext
from models import db
from .excels import excels_seeder
from .units import units_seeder
from .variables import variables_seeder


@click.command(name="seeder")
@with_appcontext
def mainSeeder():

    excels_seeder()
    units_seeder()
    variables_seeder()
