from flask import Flask, render_template
from app.routes import main_bp, admin_bp
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
import os

load_dotenv()


def create_app():
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')

    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Protección CSRF
    csrf = CSRFProtect(app)

    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
