from .app import app
import monApp.views
from .app import app, db
import monApp.commands
import monApp.database # Importe le package database, qui expose les modèles via son __init__.py