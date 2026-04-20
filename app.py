from flask import Flask
from controller.config import Config
from controller.database import db
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

import controller.models
from controller.models import User
from controller.routes import register_routes
register_routes(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_admin():
    existing_admin = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
    if not existing_admin:
        admin = User(
            name="Admin",
            email=Config.ADMIN_EMAIL,
            role="admin"
        )
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        create_admin()
    app.run(debug=True)