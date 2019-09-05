from app import app
from flaskext.mysql import MySQL

mysql = MySQL()
# Coneccion a la base de datos 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
app.config['MYSQL_DATABASE_DB'] = 'MediaPlatforms'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)