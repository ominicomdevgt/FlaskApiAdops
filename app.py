from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_jwt_extended import JWTManager


app = Flask(__name__)
cors = CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql://omgdev:Sdev@2002!@3.95.117.169/MediaPlatforms"
app.config['SQLALCHEMY_BINDS'] = {
    'users':    "mysql://omgdev:Sdev@2002!@3.95.117.169/MediaPlatforms",
    'mfc':  "mysql://omgdev:Sdev@2002!@3.95.117.169/mfcgt"
}
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_POOL_RECYCLE'] = 120
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 40
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False



app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['SECRET_KEY'] = 'some-secret-string'

db = SQLAlchemy(app)
ma = Marshmallow(app)