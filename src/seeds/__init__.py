import click
from flask.cli import with_appcontext
from .excels import excels_seeder
from .variables import variables_seeder


@click.command(name="seeder")
@with_appcontext
def mainSeeder():
    excels_seeder()
    variables_seeder()
