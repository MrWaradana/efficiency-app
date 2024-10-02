import pytest
from testcontainers.postgres import PostgresContainer
from core.server import create_app
from digital_twin_migration.database import db

@pytest.fixture(scope="session")
def postgres_container():
    """Starts a Postgres Testcontainer"""
    with PostgresContainer("postgres:14") as postgres:
        yield postgres

@pytest.fixture
def app(postgres_container):
    """Create Flask test app using Testcontainer Postgres DB"""
    app = create_app()

    # Configure the app to use the test database
    app.config["SQLALCHEMY_DATABASE_URI"] = postgres_container.get_connection_url()
    app.config["TESTING"] = True
    
    # Set up the test database
    with app.app_context():
        db.create_all()
    
    yield app

    # Teardown: Drop the test database
    with app.app_context():
        db.session.remove()
        # db.drop_all()

@pytest.fixture
def client(app):
    """Provides a test client for the Flask app"""
    return app.test_client()
