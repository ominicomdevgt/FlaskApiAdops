from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_jwt_extended import JWTManager


app = Flask(__name__)
cors = CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql://omgdev:Sdev@2002!@34.201.99.133/MediaPlatforms"
app.config['SQLALCHEMY_BINDS'] = {
    'users':    "mysql://omgdev:Sdev@2002!@34.201.99.133/MediaPlatforms",
    'mfc':  "mysql://omgdev:Sdev@2002!@34.201.99.133/mfcgt"
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['SECRET_KEY'] = 'some-secret-string'

db = SQLAlchemy(app)
ma = Marshmallow(app)