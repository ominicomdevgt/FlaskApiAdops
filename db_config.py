from app import app
from flaskext.mysql import MySQL

mysql = MySQL()
# Coneccion a la base de datos 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'omgdev'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Sdev@2002!'
app.config['MYSQL_DATABASE_DB'] = 'MediaPlatforms'
app.config['MYSQL_DATABASE_HOST'] = '3.95.117.169'
mysql.init_app(app)