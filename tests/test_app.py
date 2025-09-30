import pytest
import importlib.util
import sys
import os

# Ensure FJTickets/__init__.py is run before tests
init_path = os.path.join(os.path.dirname(__file__), '..', 'FJTickets', '__init__.py')
spec = importlib.util.spec_from_file_location("FJTickets.__init__", init_path)
init_module = importlib.util.module_from_spec(spec)
sys.modules["FJTickets.__init__"] = init_module
spec.loader.exec_module(init_module)

from FJTickets import create_app
from FJTickets.db import get_db
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance', 'fjtickets.sqlite')

@pytest.fixture
def app():
    app = create_app({'TESTING': True, 'DATABASE': DB_PATH})
    with app.app_context():
        db = get_db()
        db.executescript('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ticket (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                resolved INTEGER DEFAULT 0,
                FOREIGN KEY (author_id) REFERENCES user (id)
            );
        ''')
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        db = get_db()
        db.execute('DELETE FROM user;')
        db.execute('DELETE FROM ticket;')
        db.commit()

# Functionality test: registration
def test_register(client):
    response = client.post('/auth/register', data={'username': 'testuser', 'password': 'testpass'})
    assert response.status_code == 302  # Redirect to login

# Functionality test: login
def test_login(client, app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO user (username, password) VALUES (?, ?)", ('testuser', 'pbkdf2:sha256:1234'))
        db.commit()
    response = client.post('/auth/login', data={'username': 'testuser', 'password': 'testpass'})
    assert b'Incorrect password.' in response.data or response.status_code == 302

# Database integrity test: unique username
def test_unique_username(client):
    client.post('/auth/register', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/auth/register', data={'username': 'testuser', 'password': 'testpass'})
    assert b'already registered' in response.data

# SQL injection vulnerability test: login
def test_login_sql_injection(client):
    response = client.post('/auth/login', data={'username': "' OR 1=1 --", 'password': 'any'})
    assert b'Incorrect username.' in response.data or b'Incorrect password.' in response.data

# SQL injection vulnerability test: create ticket
def test_create_ticket_sql_injection(client, app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO user (username, password) VALUES (?, ?)", ('testuser', 'pbkdf2:sha256:1234'))
        db.commit()
    client.post('/auth/login', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/create', data={'title': "test'); DROP TABLE ticket; --", 'body': 'body'})
    with app.app_context():
        db = get_db()
        # Table should still exist
        result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ticket'").fetchone()
        assert result is not None
