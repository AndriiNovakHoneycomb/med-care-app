import click
from flask.cli import with_appcontext
from .seeders import seed_database

def register_commands(app):
    app.cli.add_command(seed_db_command)

@click.command('seed-db')
@with_appcontext
def seed_db_command():
    """Seed the database with initial data."""
    seed_database() 