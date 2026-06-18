# extensions.py — inisialisasi db & login_manager di sini
# agar tidak terjadi circular import antara app.py dan models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
