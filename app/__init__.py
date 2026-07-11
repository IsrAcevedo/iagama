from flask import Flask
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
import os

from app.routes import main_bp, admin_bp

load_dotenv()

def create_app():
    app = Flask( __name__, template_folder='templates', static_folder='static')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    CSRFProtect(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app