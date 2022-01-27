from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message 


app = Flask(__name__)
cors = CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql://root:AnnalectDB2019@3.95.117.169/MediaPlatforms"
app.config['SQLALCHEMY_BINDS'] = {
    'users':    "mysql://root:AnnalectDB2019@3.95.117.169/MediaPlatforms",
    'mfc':  "mysql://root:AnnalectDB2019@3.95.117.169/mfcgt",
    'reports':  "mysql://root:AnnalectDB2019@3.95.117.169/MediaPlatformsReports",
    'frost':  "mysql://root:AnnalectDB2019@3.95.117.169/LaChalupa"
}
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_POOL_RECYCLE'] = 120
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 60
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False



app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['SECRET_KEY'] = 'some-secret-string'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'support@wolvisor.com'
app.config['MAIL_PASSWORD'] = 'elqbtqgcaicnnzsz'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

db = SQLAlchemy(app)
ma = Marshmallow(app)
mail = Mail(app) 