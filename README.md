# Flask-Api

[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

Aplicacion de Flask Restfull con las siguientes librerias:

| Plugin | README |
| ------ | ------ |
| Flask_SqlAlchemy | [https://flask-sqlalchemy.palletsprojects.com/en/2.x/][PlDb] |
| Flask_Restfull | [https://flask-restful.readthedocs.io/en/latest/][PlGh] |
| Flask_Marshmellow | [https://flask-marshmallow.readthedocs.io/en/latest/][PlGd] |
| Flask_cors | [https://flask-cors.corydolphin.com/en/2.0.1/][PlOd] |


# New Features!

  - Api Endpoints for:
    - Account
    - Marca
    - AccountxMarca
 

]


### Installation

Es necesario installar Nginx (web server) Container, Gunicorn (WSGI HTTP Server), Flask (Python Web Service) y Supervisor (Control Process)

Install.

```sh
$ apt-get -y install python3-pip python3-dev nginx nano
```
Inciar instalando el  virtualenv package using pip:
```sh
$ sudo pip install virtualenv
```
Ahora podemos crear un ambiente virutal, para alogar nuestro Flask project
```sh
$ virtualenv Apis
```
Despues de installar la apliacion con el ambiente virtual se puede activar escribiendo 
```sh
$ source myprojectenv/bin/activate
```
### Install Flask and Gunicorn
Instalaremos usando la instancia local con pip  
```sh
$ pip install gunicorn flask
```
Para probar la aplicacion Flask se debe correr el siguiente comando  
```sh
$ python Api.py
```
Testing Gunicorn  
```sh
$ cd ~/Api
$ gunicorn --bind 0.0.0.0:5000 Api:app
```
### Supervisor
Se debe configurar el archivo en /etc/supervisord.conf con lo siguiente
```sh
[program:TaskApi]
directory=/home/Centos/API/Flask/TaskApi
gunicorn --bind 0.0.0.0:5000 TaskApi:app
autostart=true
autorestart=true
stderr_logfile=/var/log/Apis/Apis.err.log
stdout_logfile=/var/log/Apis/Apis.out.log
```
Para activar la configuracion, se debe correr el siguente comando:
```sh
$ sudo supervisord -c /etc/supervisord.conf
$ sudo supervisorctl -c /etc/supervisord.conf
```
Con esto se iniciara el proceso. Para comprar si el estatus de todas las aplicaciones que estan siendo monitoreadas usar el siguiente comando 
```sh
$ sudo supervisord status
```

**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
# FlaskApiAdops
