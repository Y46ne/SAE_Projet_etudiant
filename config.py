import os

SECRET_KEY = "2lzUl{$*D6#`8uXqlU."

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'monApp.db')
BOOTSTRAP_SERVE_LOCAL = True