import pytest
from monApp.app import app as flask_app, db as sqlalchemy_db

@pytest.fixture(scope='function')
def app():
    """
    Crée une application Flask isolée pour chaque test,
    avec une base SQLite en mémoire et les triggers initiaux.
    """
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key"
    })

    with flask_app.app_context():
        sqlalchemy_db.create_all()

        yield flask_app  

        sqlalchemy_db.session.remove()
        sqlalchemy_db.drop_all()

@pytest.fixture()
def client(app):
    """Un client de test pour l'application."""
    return app.test_client()

@pytest.fixture()
def db_session(app):
    """
    Fixture pour la base de données qui encapsule chaque test dans une transaction
    et la rollback à la fin.
    """
    with app.app_context():
        connection = sqlalchemy_db.engine.connect()
        transaction = connection.begin()
        
        sqlalchemy_db.session.begin_nested()
        
        yield sqlalchemy_db.session

        transaction.rollback()
        connection.close()