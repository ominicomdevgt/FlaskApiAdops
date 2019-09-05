from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql://root:1234@localhost/mediaplatforms"
app.config['SQLALCHEMY_BINDS'] = {
    'users':    "mysql://root:1234@localhost/mediaplatforms",
    'mfc':  "mysql://root:1234@localhost/mfcgt"
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
ma = Marshmallow(app)