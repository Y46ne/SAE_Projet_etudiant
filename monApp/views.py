from .app import app, db, login_manager
from config import *
from flask import render_template, request, url_for, redirect, flash, jsonify
from monApp.database import User, Assure, Assureur, Logement, Piece, Bien, Sinistre, impacte
from monApp.forms import *
from flask_login import login_user, logout_user, login_required, current_user
from hashlib import sha256



# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(debug=True)
