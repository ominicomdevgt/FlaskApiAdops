from flask import Flask, request
from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from db_config import mysql
import pymysql


app = Flask(__name__)
api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')


# Todo
# shows a single todo item and lets you delete a todo item
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


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
            

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201

        try:
            _json = request.json
            _AccountID = _json['AccountID']
            _Account = _json['Account']
            _Media = _json['Media']
            if _Account and _AccountID and _Media and request.method == 'POST':
                sql = "INSERT INTO "
                data = (_AccountID, _Account, _Media,)
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute(sql, data)
                conn.commit()
                resp = jsonify('User added successfully!')
                resp.status_code = 200
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()

##
## Se tiene que agregar cada ruta a la aplicacion, ruta -> class
##
api.add_resource(Bitacora, '/bitacora')
api.add_resource(Todo, '/todos/<todo_id>')


if __name__ == '__main__':
    app.run(debug=True)