from flask_marshmallow import Marshmallow
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail

ma = Marshmallow()
db = MongoEngine()
lm = LoginManager()
mail = Mail()

extensions = (ma, db, lm, mail)
