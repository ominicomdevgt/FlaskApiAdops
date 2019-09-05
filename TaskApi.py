from flask import Flask, request
from flask import jsonify
from app import app
from flask_restful import reqparse, abort, Api, Resource
from models import Bitacora, BitacoraSchema, Dmarca, DmarcaSchema
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

api = Api(app)


class GetBitacora(Resource):
    def get(self):
        try:
            bitacora_shema = BitacoraSchema()
            bitacora_shema = BitacoraSchema(many=True)
            bitacora = Bitacora.query.all()
            result = bitacora_shema.dump(bitacora)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())
            

class GetDmarca(Resource):
    def get(self):
        try:
            dmarcaSchema = DmarcaSchema()
            dmarcaSchema = DmarcaSchema(many=True)
            dmarca = Dmarca.query.all()
            result = dmarcaSchema.dump(dmarca)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())
##
## Se tiene que agregar cada ruta a la aplicacion, ruta -> class
##
api.add_resource(GetBitacora, '/task/Compra')
api.add_resource(GetDmarca, '/task/Dmarca')



if __name__ == '__main__':
    app.run(debug=True)
    