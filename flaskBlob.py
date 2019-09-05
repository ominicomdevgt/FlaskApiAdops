from flask import Flask, request
from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from db_config import mysql
import pymysql


app = Flask(__name__)
api = Api(app)

# Bitacora
# muestra una lista de todos los elementos de la bitacora de operaciones 
class Bitacora(Resource):
    def get(self):
        try:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM bitacora;")
            rows = cursor.fetchall()
            resp = jsonify(rows)
            resp.status_code = 200
            return resp
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()
            

    

##
## Se tiene que agregar cada ruta a la aplicacion, ruta -> class
##
api.add_resource(Bitacora, '/bitacora')



if __name__ == '__main__':
    app.run(debug=True)