# -*- coding: UTF-8 -*-
from flask import Flask, request
import sys
from flask import jsonify
from app import app, db
from flask_restful import reqparse, abort, Api, Resource
from models import Bitacora, BitacoraSchema, Dmarca, DmarcaSchema,Accountxmarca,AccountxMarcaSchema,Accounts,AccountsSchema, Dcliente, DclienteSchema,Errorscampaings,ErrorsCampaingsSchema, ReportSchema, LocalMedia, LocalMediaSchema, DetailLocalMedia, DetailLocalMediaSchema
from flask_sqlalchemy import SQLAlchemy,time
from flask_marshmallow import Marshmallow
from datetime import datetime, timedelta
import os
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required, jwt_refresh_token_required, get_jwt_identity,JWTManager
import jwt
import re
from sqlalchemy.sql import func,text
import numpy as mp
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)


api = Api(app)



class GetBitacora(Resource):
    def get(self):
        try:
            bitacora_shema = BitacoraSchema()
            bitacora_shema = BitacoraSchema(many=True)
            bitacora = db.session.query(func.date_format(Bitacora.CreateDate,'%d-%m-%Y').label('CreateDate'),Bitacora.Resultado, Bitacora.Operacion, Bitacora.bitacoraID, Bitacora.Documento ).order_by(Bitacora.bitacoraID.desc()).limit(500).all()
            result = bitacora_shema.dump(bitacora)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())

class GetBitacoraFull(Resource):
    def get(self):
        try:
            bitacora_shema = BitacoraSchema()
            bitacora_shema = BitacoraSchema(many=True)
            bitacora = db.session.query(func.date_format(Bitacora.CreateDate,'%d-%m-%Y').label('CreateDate'),Bitacora.Resultado, Bitacora.Operacion, Bitacora.bitacoraID, Bitacora.Documento ).order_by(Bitacora.bitacoraID.desc()).all()
            result = bitacora_shema.dump(bitacora)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())


class GetBitacoraFiles(Resource):
    def get(self):
        try:
            bitacora_shema = BitacoraSchema()
            bitacora_shema = BitacoraSchema(many=True)
            query = db.session.query(Bitacora.Documento, "bitacoraID")
            query = query.from_statement(text("select distinct Documento,bitacoraID, cast(@row := @row + 1 as unsigned) as bitacoraID from bitacora, (select @row := 0) as init group by Documento limit 500"))
            result = bitacora_shema.dump(query)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())


class GetAccountxMarca(Resource):
    def get(self,idMarca):
        try:
            dmarcaSchema = AccountxMarcaSchema()
            dmarcaSchema = AccountxMarcaSchema(many=True)
            query = db.session.query(('AccountID'),('Medio'),'idAccountxMarca',('nombre'),'marca')
            query = query.from_statement(text("""
            select distinct AccountID, Medio, idAccountxMarca, marca, nombre from  (
            select AccountsID AccountID, Media 'Medio', idAccountxMarca, marca, a.Account nombre from Accounts a inner join accountxmarca am on a.AccountsID = am.account where am.marca = {}
            union all
            select AccountsID AccountID, Media 'Medio', null as idAccountxMarca, null as marca, Account nombre from Accounts
            )
            t group by AccountID order by idAccountxMarca desc;
            """.format(idMarca)))
            result = dmarcaSchema.dump(query)
            result = jsonify(result)
            if result:
                return result
            else:
                return 'AccountID Not Found',404
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())



class PostMarcaxAccount(Resource):
     def post(self,idAccount,idMarca,Estado,User):
        busqueda = Accountxmarca.query.filter(Accountxmarca.account == idAccount, Accountxmarca.marca==idMarca).first()
        try:
            if busqueda:
                if int(Estado) == 0:
                    db.session.delete(busqueda)
                    db.session.commit()
                    return 'Account Marca Eliminado', 202
            else:
                a = Accountxmarca(idAccount,idMarca,User)
                db.session.add(a)
                db.session.commit()
                return 'Account Marca Ingresado Correctamente', 201
            return 'Account Marca ya se encuentra Asignado', 200
        except Exception as e:
            print(e)
            return 'Cuenta o Marca no encontrada', 400
        finally:
            pass



class GetAccount(Resource):
    def get(self):
        try:
            accountSchema = AccountsSchema()
            accountSchema = AccountsSchema(many=True)
            account = Accounts.query.all()
            result = accountSchema.dump(account)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())

class GetAccountNames(Resource):
    def get(self):
        try:
            Names=[]
            accountSchema = AccountsSchema()
            accountSchema = AccountsSchema(many=True)
            account = Accounts.query.all()
            result = accountSchema.dump(account)
            for x in result:
                Names.append(x['Account'])
            return Names
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())

class GetDmarca(Resource):
    def get(self):
        try:
            dmarca_shema = DmarcaSchema()
            dmarca_shema = DmarcaSchema(many=True)
            dmarca = db.session.query(Dmarca.id,Dmarca.fullname(Dmarca,Dcliente.nombre).label("fullname")).join().filter(Dmarca.idcliente == Dcliente.id).all()
            result = dmarca_shema.dump(dmarca)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())

class GetDmarcaName(Resource):
    def get(self):
        try:
            Names=[]
            dmarca_shema = DmarcaSchema()
            dmarca_shema = DmarcaSchema(many=True)
            dmarca = db.session.query(Dmarca.id,Dmarca.fullname(Dmarca,Dcliente.nombre).label("fullname")).join().filter(Dmarca.idcliente == Dcliente.id).all()
            result = jsonify(dmarca)
            result = dmarca_shema.dump(dmarca)
            for x in result:
                Names.append(x['fullname'])
            return Names
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())


class CRUDAccount(Resource):
    def post(self,idAccount,Account,Medio,Country):
        try:
            a = Accounts(idAccount,Account,Medio,Country)
            db.session.add(a)
            db.session.commit()
            return 'Account Ingresado Correctamente', 201
        except Exception as e:
            print(e)
            return 'Account no Ingresada', 400
        finally:
            pass
    def put(self,idAccount,Account,Medio,Country):
        try:
            a = Accounts.query.filter(Accounts.AccountsID==idAccount).first()
            a.Account = Account
            a.Media = Medio
            a.Country = Country
            db.session.commit()
            return 'Account Ingresado Correctamente', 201
        except Exception as e:
            print(e)
            return 'Account no Ingresada', 400
        finally:
            pass

    def delete(self,idAccount,Account,Medio,Country):
        try:
            Accounts.query.filter(Accounts.AccountsID == idAccount).delete()
            db.session.commit()
            return 'Eliminado Correcatamente', 200
        except Exception as e:
            print(e)
            return 'Account no Ingresada', 400
        finally:
            pass

class TokenJWT(Resource):
    def get(self):
        user = {}
        try:
            access_token = create_access_token(identity=1234)
            refresh_token = create_refresh_token(identity=1234)
            user['token'] = access_token
            user['refresh'] = refresh_token
            return jsonify(user),200
        except Exception as e:
            return e

class GetErrores(Resource):
    @jwt_required

    def get(self,idusuario):
        try:

            dmarcaSchema = ErrorsCampaingsSchema()
            dmarcaSchema = ErrorsCampaingsSchema(many=True)
            hoy = datetime.now().strftime("%Y-%m-%d")
            query = db.session.query('iderror','idcuenta','cuenta','CampaingID','Camapingname','Error','TipoErrorID','DescripcionError','GrupoError','Icono','Comentario','Estado','Media','Fecha','tipousuario','plataforma','marca','cliente')
            query = query.from_statement(text("""
            (Select distinct a.idErrorsCampaings as iderror,d.AccountsID as idcuenta,d.Account as cuenta,a.CampaingID,b.Campaingname Camapingname,a.Error,a.TipoErrorID, c.Descripcion as DescripcionError,c.GrupoError,c.Icono,a.Comentario,a.Estado, a.Media, DATE_FORMAT(a.CreateDate, "%d/%m/%Y") as Fecha ,c.tipousuario,d.Media as plataforma, IFNULL( m.nombre,"SIN ASIGNAR") marca, IFNULL(cl.nombre,"SIN ASIGNAR") cliente
                from ErrorsCampaings a
                INNER JOIN Campaings b on a.CampaingID=b.CampaingID
                INNER JOIN Accounts  d on b.AccountsID=d.AccountsID
                INNER JOIN TiposErrores c on a.TipoErrorID=c.TipoErrorID
                left JOIN accountxmarca am on am.account = d.AccountsID
                left JOIN mfcgt.dmarca m on m.id = am.marca
                left JOIN mfcgt.dcliente cl on cl.id = m.idcliente
                left join mfcgt.mfcasignacion asg on asg.idmarca = m.id
                where
                a.Estado>0
                and
                b.EndDate > "{}"
                and
                (a.StatusCampaing="ACTIVE"
                or a.StatusCampaing="enabled")
                and asg.idusuario = {})
                union all
                ( select distinct a1.idErrorsCampaings as iderror,b1.AccountsID as idcuenta, b1.AccountsID as cuenta, a1.CampaingID, b1.Campaingname Camapingname, a1.Error, a1.TipoErrorID, c1.Descripcion as DescripcionError,c1.GrupoError,c1.Icono,a1.Comentario,a1.Estado,a1.Media, DATE_FORMAT(a1.CreateDate, "%d/%m/%Y") as Fecha,c1.TipoUsuario,d1.Media as plataforma, "SIN ASIGNAR" marca, "SIN ASIGNAR" cliente
                from ErrorsCampaings a1
                inner join CampaingsAM b1 on b1.CampaingID = a1.CampaingID
                inner join TiposErrores c1 on c1.TipoErrorID = a1.TipoErrorID
                INNER JOIN Accounts  d1 on b1.AccountsID=d1.AccountsID
                left JOIN accountxmarca am1 on am1.account = d1.AccountsID
                left JOIN mfcgt.dmarca m1 on m1.id = am1.marca
                left join mfcgt.mfcasignacion asg1 on asg1.idmarca = m1.id
                where a1.Estado >0 )
                order by idcuenta, fecha desc
            """.format(hoy,idusuario)))
            result = dmarcaSchema.dump(query)
            return result

        except Exception as e:
            return {"reason": "unauthorized","message": "You are not authorized to use this service Adops-OMG"}, 401
            print(e)
        finally:
            print(datetime.now())


class GetErroresCount(Resource):
    def get(self,idusuario):
        try:
            dmarcaSchema = ErrorsCampaingsSchema()
            dmarcaSchema = ErrorsCampaingsSchema(many=True)
            hoy = datetime.now().strftime("%Y-%m-%d")
            query = db.session.query('iderror','idcuenta','cuenta','CampaingID','Camapingname','Error','TipoErrorID','DescripcionError','GrupoError','Icono','Comentario','Estado','Media','Fecha','tipousuario','plataforma','marca','cliente')
            query = query.from_statement(text("""
            algo
            """))
            result = dmarcaSchema.dump(query)
            return result

        except Exception as e:
            print(e)
        finally:
            print(datetime.now())


class SecretResource(Resource):

    def get(self):

        try:
            access_token = create_access_token(identity = 'hola')
            refresh_token = create_refresh_token(identity = 'hola')
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        except:
            return {'message': 'Something went wrong'}, 500

class LoginS(Resource):
    def get(self, user,pas):

        access_token = jwt.encode({'public_id':'chupame el perro','exp': datetime.utcnow() + timedelta(minutes=30)},app.config['SECRET_KEY'])
        access_token = create_access_token('perro')
        return jsonify({'token' : access_token })


class UploadImage(Resource):
    def post(self, fname):
        try:
            file = request.files['file']

        except:
            # return error
            return {'False'}



class GetReporte(Resource):
    def get(self,idusuario):
        try:
            campaings = []
            report = ReportSchema()
            report = ReportSchema(many=True)
            query = db.session.query('Account','CampaingID', 'Media','Campaingname','Cost','StartDate' ,  'EndDate' ,   'presupuesto',  'objetivo', 'result','State', 'TotalDias', 'DiasServidos','DiasPorservir',
            'ValorEsperado', 'ValorReal','PorcentajeEsperadoV','PorcentajeRealV','KPIEsperado', 'KPIReal','PorcentajeEsperadoK','PorcentajeRealK')
            query = query.from_statement(text("""
                    select  a.Account as Account ,c.CampaingID CampaingID,  a.Media Media,  c.Campaingname Campaingname,sum(d.Cost) Cost, date_format(c.StartDate, '%Y-%m-%d') StartDate ,
                    date_format(c.EndDate,'%Y-%m-%d') EndDate , SUBSTRING_INDEX (SUBSTRING_INDEX(c.Campaingname, '_', 11),'_',-1) presupuesto,
                    SUBSTRING_INDEX (SUBSTRING_INDEX(c.Campaingname, '_', 13),'_',-1) objetivo,ifnull(sum(d.result),0) result,c.Campaignstatus State, '0' as 'TotalDias',"0" as 'DiasServidos',"0" as 'DiasPorservir',
                    "0" as 'ValorEsperado',"0" as 'ValorReal', "0" as 'PorcentajeEsperadoV',"0" as 'PorcentajeRealV',"0" as 'KPIEsperado',"0" as 'KPIReal', "0" as 'PorcentajeEsperadoK',"0" as 'PorcentajeRealK'
                    from Dailycampaing d
                    inner join Campaings c on c.CampaingID = d.CampaingID
                    inner join Accounts a on c.AccountsID = a.AccountsID
                    inner join Accountxmarca am on am.account = a.AccountsID
                    inner join mfcgt.mfcasignacion asg on asg.idmarca = am.marca
                    where c.Campaignstatus in ('ACTIVE','enabled')   and asg.idusuario = {}
                    group by d.CampaingID;
                    """.format(idusuario)))
            result = report.dump(query)
            for row in result:
                Nomenclatura = row['Campaingname']
                searchObj = re.search(r'^(GT|CAM|RD|US|SV|HN|NI|CR|PA|RD|PN|CHI|HUE|PR)_([a-zA-ZáéíóúÁÉÍÓÚÑñ\s0-9-/.+&]+)_([a-zA-Z0-9-/.+&]+)_([a-zA-ZáéíóúÁÉÍÓÚÑñ0-9-/.+&]+)_([a-zA-ZáéíóúÁÉÍÓÚÑñ0-9-/.+&]+)_([a-zA-ZáéíóúÁÉÍÓÚÑñ0-9-/.+&]+)_([a-zA-Z-/.+]+)_([a-zA-ZáéíóúÁÉÍÓÚÑñ.+]+)_(ENE|FEB|MAR|ABR|MAY|JUN|JUL|AGO|SEP|OCT|NOV|DIC)_(19|2019)_([0-9,.]+)_(BA|AL|TR|TRRS|TRRRSS|IN|DES|RV|CO)_([0-9,.]+)_(CPM|CPMA|CPVi|CPC|CPI|CPD|CPV|CPCo|CPME|CPE|PF|RF|MC|CPCO|CPCO)_([0-9.,]+)_([a-zA-Z-/áéíóúÁÉÍÓÚÑñ.+]+)_([a-zA-Z-/áéíóúÁÉÍÓÚÑñ.+]+)_([a-zA-Z-/áéíóúÁÉÍÓÚÑñ.+]+)_([0-9,.-]+)?(_B-)?(_)?([0-9.]+)?(_S-)?(_)?([0-9.]+)?(\s)?(\(([0-9.)]+)\))?$', Nomenclatura, re.M | re.I)
                if searchObj:
                    if row['StartDate'] != '0000-00-00' and row['EndDate'] != '0000-00-00':
                        Start = datetime.strptime(row['StartDate'], "%Y-%m-%d")
                        End = datetime.strptime(row['EndDate'], "%Y-%m-%d")
                        row['TotalDias'] = End - Start
                        row['DiasServidos'] = datetime.now() -  Start
                        row['DiasPorservir'] = End - datetime.now()
                        if row['TotalDias'].days > 0:
                            porcentDay = row['DiasServidos'].days / (row['TotalDias'].days)
                        row['ValorEsperado'] = round(float(row['presupuesto']) * porcentDay,2)
                        if float( row['presupuesto']) > 0:
                            row['PorcentajeEsperadoV'] = round(float( row['ValorEsperado'])/ float( row['presupuesto']),2)
                            row['PorcentajeRealV'] = round(float(row['Cost'])/ float(row['presupuesto']),2)
                        row['KPIEsperado'] = round(float(row['objetivo']) * porcentDay,2)
                        if float( row['objetivo']) > 0:
                            row['PorcentajeEsperadoK'] = round(float( row['KPIEsperado'])/ float( row['objetivo']),2)
                            row['PorcentajeRealK'] = round(float(row['result'])/ float(row['objetivo']),2)
                        row['TotalDias'] = row['TotalDias'].days
                        row['DiasServidos'] = row['DiasServidos'].days
                        row['DiasPorservir'] = row['DiasPorservir'].days
                        campaings.append(row)
            campaings = jsonify(campaings)
            return campaings

        except Exception as e:
            print(e)
        finally:
            print(datetime.now())


class GetReporteML(Resource):
    def get(self,idusuario):
        try:
            lm = LocalMediaSchema()
            lm = LocalMediaSchema(many=True)
            data = LocalMedia.query.all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())


class GetReporteDetailML(Resource):
    def get(self,idlocal):
        try:
            lm = DetailLocalMediaSchema()
            lm = DetailLocalMediaSchema(many=True)
            data = DetailLocalMedia.query.filter(DetailLocalMedia.LocalMediaID == idlocal).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())


class GetGroupByODClML(Resource):
    def get(self):
        try:
            lm = LocalMediaSchema()
            lm = LocalMediaSchema(many=True)
            data = LocalMedia.query.filter(LocalMedia.State == 1).group_by(LocalMedia.Odc).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())


class GetReporteDetODC(Resource):
    def get(self,Odc):
        try:
            lm = DetailLocalMediaSchema()
            lm = DetailLocalMediaSchema(many=True)
            data = db.session.query(DetailLocalMedia.StartWeek, DetailLocalMedia.EndWeek,DetailLocalMedia.Nomenclatura, DetailLocalMedia.Formato, DetailLocalMedia.Objetivo,DetailLocalMedia.Impresiones,DetailLocalMedia.Clicks,DetailLocalMedia.Ctr,DetailLocalMedia.Consumo).join().filter(DetailLocalMedia.LocalMediaID == LocalMedia.LocalMediaID , LocalMedia.Odc == Odc).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())




##
## Se tiene que agregar cada ruta a la aplicacion, ruta -> class
##

api.add_resource(GetBitacora, '/task/Bitacora')
api.add_resource(GetBitacoraFull, '/task/BitacoraFull')
api.add_resource(GetBitacoraFiles, '/task/BitacoraNames')
api.add_resource(GetAccountxMarca, '/task/AccountxMarca/<string:idMarca>')
api.add_resource(PostMarcaxAccount, '/task/InsertAccountxMarca/<string:idAccount>&<string:idMarca>&<string:Estado>&<string:User>')
api.add_resource(GetAccount, '/task/AccountAll')
api.add_resource(GetAccountNames, '/task/AccountNames')
api.add_resource(GetDmarca, '/task/Marca')
api.add_resource(GetDmarcaName, '/task/MarcaNames')
api.add_resource(CRUDAccount, '/task/Account/<string:idAccount>&<string:Account>&<string:Medio>&<string:Country>')
api.add_resource(LoginS, '/task/Token/<string:user>&<string:pas>')
api.add_resource(GetErrores, '/Errores/<string:idusuario>')
api.add_resource(UploadImage, '/Upload/<string:fname>')
api.add_resource(GetReporte, '/Reporte/<string:idusuario>')
api.add_resource(GetReporteML, '/Reporte/ArchivosLM/<string:idusuario>')
api.add_resource(GetReporteDetailML, '/Reporte/DetalleLM/<string:idlocal>')
api.add_resource(GetGroupByODClML, '/Reporte/ODC')
api.add_resource(GetReporteDetODC, '/Reporte/ODC/<string:Odc>')

if __name__ == '__main__':
    JWTManager(app)
    app.run(debug=False)
