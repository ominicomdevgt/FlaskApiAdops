# -*- coding: UTF-8 -*-
from flask import Flask, request
import sys
from flask import jsonify
from app import app, db
from flask_restful import reqparse, abort, Api, Resource
from models import Bitacora, BitacoraSchema, Dmarca, DmarcaSchema,Accountxmarca,AccountxMarcaSchema,Accounts,AccountsSchema, Dcliente, DclienteSchema,Errorscampaings,ErrorsCampaingsSchema, ReportSchema, LocalMedia, LocalMediaSchema, DetailLocalMedia, DetailLocalMediaSchema, ErrorsCampaingsCountSchema, Dcliente,DclienteSchema,CostSchema, LeadAdsCampaings, LeadAdsCampaingsSchema, Invitados,InvitadosSchema, mfcaprobacion,aprobacionSchema,Results_campaings,Results_campaingsSchema, rCampaings, rCampaingsSchema,rCampaingMetrics, rCampaingMetricsSchema
import models
from flask_sqlalchemy import SQLAlchemy,time
from flask_marshmallow import Marshmallow
from datetime import datetime, timedelta
import os
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required, jwt_refresh_token_required, get_jwt_identity,JWTManager
import jwt
import re
from sqlalchemy.sql import func,text, desc
import numpy as mp
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import Actualizacion_Datos#, Mis_Flows

parser = reqparse.RequestParser()

api = Api(app)



class GetBitacora(Resource):
    #@jwt_required
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
    @jwt_required
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
            db.session.close()
            print(datetime.now())


class GetBitacoraFiles(Resource):
    @jwt_required
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
            db.session.close()
            print(datetime.now())


class GetAccountxMarca(Resource):
    # @jwt_required
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
            db.session.close()
            print(datetime.now())




class PostMarcaxAccount(Resource):
     @jwt_required 
     def post(self,idAccount,idMarca,Estado,User):
        busqueda = db.session.query(Accountxmarca.idAccountxMarca).filter(Accountxmarca.account == idAccount, Accountxmarca.marca==idMarca).first()
        try:
            if busqueda:
                if int(Estado) == 0:

                    Accountxmarca.query.filter(Accountxmarca.idAccountxMarca == busqueda.idAccountxMarca).delete()
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
            db.session.close()
            pass



class GetAccount(Resource):
    @jwt_required
    def get(self):
        try:
            accountSchema = AccountsSchema()
            accountSchema = AccountsSchema(many=True)
            account =  db.session.query(Accounts.AccountsID, Accounts.Account, Accounts.Media,Accounts.CreateDate,Accounts.Country ).order_by(Accounts.AccountsID.desc()).all()
            result = accountSchema.dump(account)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class GetAccountNames(Resource):
    @jwt_required
    def get(self):
        try:
            Names=[]
            accountSchema = AccountsSchema()
            accountSchema = AccountsSchema(many=True)
            account =  db.session.query(Accounts.AccountsID, Accounts.Account, Accounts.Media,Accounts.CreateDate,Accounts.Country ).order_by(Accounts.AccountsID.desc()).all()
            result = accountSchema.dump(account)
            for x in result:
                Names.append(x['Account'])
            return Names
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class GetDmarca(Resource):
    @jwt_required
    def get(self):
        try:
            dmarca_shema = DmarcaSchema()
            dmarca_shema = DmarcaSchema(many=True)
            dmarca = db.session.query(Dmarca.id,Dmarca.fullname(Dmarca,Dcliente.nombre).label("fullname")).join().filter(Dmarca.idcliente == Dcliente.id).distinct(Dmarca.id).all()
            result = dmarca_shema.dump(dmarca)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class GetDmarcaName(Resource):
    @jwt_required
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
            db.session.close()
            print(datetime.now())


class CRUDAccount(Resource):
    @jwt_required
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
            db.session.close()
            pass
    @jwt_required
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
            db.session.close()
            pass
    @jwt_required
    def delete(self,idAccount,Account,Medio,Country):
        try:
            Accounts.query.filter(Accounts.AccountsID == idAccount).delete()
            db.session.commit()
            return 'Eliminado Correcatamente', 200
        except Exception as e:
            print(e)
            return 'Account no Ingresada', 400
        finally:
            db.session.close()
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
            (Select distinct a.idErrorsCampaings as iderror,d.AccountsID as idcuenta,d.Account as cuenta,a.CampaingID,b.Campaingname Camapingname,a.Error,a.TipoErrorID, c.Descripcion as DescripcionError,c.GrupoError,c.Icono,a.Comentario,a.Estado, d.Media, DATE_FORMAT(a.CreateDate, "%d/%m/%Y") as Fecha ,c.tipousuario,d.Media as plataforma, IFNULL( m.id,"SIN ASIGNAR") marca, IFNULL(cl.id,"SIN ASIGNAR") cliente
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
                b.EndDate > "{}" and d.Media !='AM'
                and
                (a.StatusCampaing="ACTIVE"
                or a.StatusCampaing="enabled")
                and asg.idusuario = {}
                group by a.idErrorsCampaings
                order by idcuenta, fecha desc
                )
                Union all (
                Select distinct a.idErrorsCampaings as iderror,d.AccountsID as idcuenta,d.Account as cuenta,a.CampaingID,
                b.Campaingname Camapingname,a.Error,a.TipoErrorID, c.Descripcion as DescripcionError,
                c.GrupoError,c.Icono,a.Comentario,a.Estado, d.Media, DATE_FORMAT(a.CreateDate, "%d/%m/%Y") as Fecha ,
                c.tipousuario,d.Media as plataforma,"SIN ASIGNAR" marca, "SIN ASIGNAR" cliente
                from ErrorsCampaings a

                INNER JOIN Campaings b on a.CampaingID=b.CampaingID

                INNER JOIN Accounts  d on b.AccountsID=d.AccountsID
                INNER JOIN TiposErrores c on a.TipoErrorID=c.TipoErrorID

                where
                a.Estado>0 and d.Media = 'AM'
                group by a.idErrorsCampaings
                order by idcuenta, fecha desc);
            """.format(hoy,idusuario)))
            result = dmarcaSchema.dump(query)
            return jsonify(result)

        except Exception as e:
            return {"reason": "unauthorized","message":  str(e)}, 401

        finally:
            db.session.close()
            print(datetime.now())


class GetCountsErrores(Resource):

    @jwt_required
    def get(self,idusuario):
        try:
            dmarcaSchema = ErrorsCampaingsCountSchema()
            dmarcaSchema = ErrorsCampaingsCountSchema(many=True)
            hoy = datetime.now().strftime("%Y-%m-%d")
            query = db.session.query('totales', 'totalinversion','totalnomeclatura','totalpaises' , 'ordenesdecompra','errorconsumo')
            query = query.from_statement(text("""
            select
            (select count(distinct e.idErrorsCampaings) from ErrorsCampaings e
				inner join Campaings c on c.CampaingID = e.CampaingID
				inner join Accounts a on a.AccountsID =  c.AccountsID
				inner join accountxmarca am on am.account = a.AccountsID
				inner join mfcgt.dmarca m on m.id = am.marca
				inner JOIN mfcgt.dcliente cl on cl.id = m.idcliente
				inner join mfcgt.mfcasignacion asg on asg.idmarca = m.id
				where e.Estado = 1 and c.EndDate > '{}'and  e.StatusCampaing in ('ACTIVE','enabled') and asg.idusuario = {} and e.Media !='AM' )  as totales,
            (select count(distinct  e.idErrorsCampaings) from ErrorsCampaings e
				inner join Campaings c on c.CampaingID = e.CampaingID
				inner join Accounts a on a.AccountsID =  c.AccountsID
				inner join accountxmarca am on am.account = a.AccountsID
				inner join mfcgt.dmarca m on m.id = am.marca
				inner JOIN mfcgt.dcliente cl on cl.id = m.idcliente
				inner join mfcgt.mfcasignacion asg on asg.idmarca = m.id
				where e.Estado = 1 and c.EndDate > '{}'and  e.StatusCampaing in ('ACTIVE','enabled') and asg.idusuario = {} and  e.TipoErrorID in (2,3,4,5) and e.Media !='AM')  as totalinversion,
            (select count(distinct e.idErrorsCampaings) from ErrorsCampaings e
				inner join Campaings c on c.CampaingID = e.CampaingID
				inner join Accounts a on a.AccountsID =  c.AccountsID
				inner join accountxmarca am on am.account = a.AccountsID
				inner join mfcgt.dmarca m on m.id = am.marca
				inner JOIN mfcgt.dcliente cl on cl.id = m.idcliente
				inner join mfcgt.mfcasignacion asg on asg.idmarca = m.id
				where e.Estado = 1 and c.EndDate > '{}'and  e.StatusCampaing in ('ACTIVE','enabled') and asg.idusuario = {} and  e.TipoErrorID in (1) and e.Media !='AM' )  as totalnomeclatura,
            (select count(distinct e.idErrorsCampaings) from ErrorsCampaings e
				inner join Campaings c on c.CampaingID = e.CampaingID
				inner join Accounts a on a.AccountsID =  c.AccountsID
				inner join accountxmarca am on am.account = a.AccountsID
				inner join mfcgt.dmarca m on m.id = am.marca
				inner JOIN mfcgt.dcliente cl on cl.id = m.idcliente
				inner join mfcgt.mfcasignacion asg on asg.idmarca = m.id
				where e.Estado = 1 and c.EndDate > '{}'and  e.StatusCampaing in ('ACTIVE','enabled') and asg.idusuario = {} and  e.TipoErrorID in (6))  as totalpaises,
            (select count(distinct e.idErrorsCampaings) from ErrorsCampaings e
				inner join Campaings c on c.CampaingID = e.CampaingID
				inner join Accounts a on a.AccountsID =  c.AccountsID
				inner join accountxmarca am on am.account = a.AccountsID
				inner join mfcgt.dmarca m on m.id = am.marca
				inner JOIN mfcgt.dcliente cl on cl.id = m.idcliente
				inner join mfcgt.mfcasignacion asg on asg.idmarca = m.id
				where e.Estado = 1 and c.EndDate > '{}' and  e.StatusCampaing in ('ACTIVE','enabled') and asg.idusuario = {} and  e.TipoErrorID in (7,8,9,10,11,12)) as ordenesdecompra,
            (select count(distinct e.idErrorsCampaings) from ErrorsCampaings e
				inner join Campaings c on c.CampaingID = e.CampaingID
				inner join Accounts a on a.AccountsID =  c.AccountsID
				inner join accountxmarca am on am.account = a.AccountsID
				inner join mfcgt.dmarca m on m.id = am.marca
				inner JOIN mfcgt.dcliente cl on cl.id = m.idcliente
				inner join mfcgt.mfcasignacion asg on asg.idmarca = m.id
				where e.Estado = 1 and c.EndDate > '{}' and  e.StatusCampaing in ('ACTIVE','enabled') and asg.idusuario = {} and  e.TipoErrorID  in (13,14,15)) as errorconsumo
            from ErrorsCampaings
            limit 1;
            """.format(hoy,idusuario,hoy,idusuario,hoy,idusuario,hoy,idusuario,hoy,idusuario,hoy,idusuario)))
            result = dmarcaSchema.dump(query)
            return jsonify(result)
        except Exception as e:
            return {"reason": "unauthorized","message": str(e)}, 401
        finally:
            db.session.close()
            print(datetime.now())


class GetErroresCount(Resource):
    @jwt_required
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
            db.session.close()
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

class GenToken(Resource):
    def get(self,idusuario):
        #Para produccion colocarlo
        JWTManager(app)
        expires = timedelta(days=1)
        access_token = create_access_token('api-flask-adops-!@#$',expires_delta=expires)
        return jsonify({'token' : access_token,
        'id':'123' })


class GetReporte(Resource):
    @jwt_required
    def get(self,idusuario):
        try:
            hoy = datetime.now().strftime("%Y-%m-%d")
            campaings = []
            report = ReportSchema()
            report = ReportSchema(many=True)
            query = db.session.query('Account','idcliente','CampaingID','Marca','idmarca', 'Media','Campaingname','InversionConsumida','KPIPlanificado','StartDate' ,  'EndDate' ,'mes',   'PresupuestoPlan',  'KPI', 'KPIConsumido','State', 'TotalDias','DiasEjecutados','DiasPorservir','PresupuestoEsperado', 'PorcentajePresupuesto','PorcentajeEsperadoV','PorcentajeRealV','KPIEsperado', 'PorcentajeKPI','PorcentajeEsperadoK','PorcentajeRealK','EstadoKPI','EstadoPresupuesto','abr','CostoPorResultadoR','CostoPorResultadoP')
            query = query.from_statement(text("""
                    select CLIENTE.Nombre as Account,  CLIENTE.Id idcliente, MARCA.id idmarca, METRICAS.CampaingID CampaingID,ACCOUNTS.Media Media, METRICAS.Campaingname Campaingname, round(sum(distinct METRICAS.Cost),2) as 'InversionConsumida',
                        date_format(ifnull( CAMPANAMP.StartDate,str_to_date(IMPLEMENTACIONES.multiplestiposa,'%m/%d/%Y')),'%d/%m/%Y') StartDate , MARCA.nombre as Marca,
                        date_format(str_to_date(IMPLEMENTACIONES.multiplestiposb,'%m/%d/%Y'),'%Y-%m-%d') EndDate , 
                        ifnull(IMPLEMENTACIONES.costo,ifnull(IMPLEMENTACIONES.multiplescostosb,IMPLEMENTACIONES.bonificacion))  PresupuestoPlan,
                        SUBSTRING_INDEX (SUBSTRING_INDEX(METRICAS.Campaingname, '_', 14),'_',-1) KPIPlanificado,OBJETIVO.Nombre as KPI, OBJETIVO.abreviatura as abr,
                        ifnull(sum(distinct METRICAS.result),0) 'KPIConsumido', CAMPANAMP.Campaignstatus State,MARCA.nombre Marca ,CLIENTE.nombre Cliente,date_format(now(),'%M') mes,
                        '0' as 'TotalDias','0' as 'DiasEjecutados','0' as 'DiasPorservir', "0" as 'PresupuestoEsperado',"0" as 'PorcentajePresupuesto',
                        "0" as 'PorcentajeEsperadoV',"0" as 'PorcentajeRealV',"0" as 'KPIEsperado',"0" as 'PorcentajeKPI', "0" as 'PorcentajeEsperadoK',"0" as 'PorcentajeRealK', "0" as 'EstadoKPI', "0" as 'EstadoPresupuesto',"0" as 'CostoPorResultadoR', IMPLEMENTACIONES.rating' CostoPorResultadoP'

                        from dailycampaing METRICAS
                        INNER JOIN Campaings CAMPANAMP on CAMPANAMP.Campaingname =  METRICAS.Campaingname
                        INNER JOIN Accounts ACCOUNTS on CAMPANAMP.AccountsID = ACCOUNTS.AccountsID
                        left JOIN mfcgt.mfccompradiaria as IMPLEMENTACIONES on METRICAS.CampaignIDMFC=IMPLEMENTACIONES.id
                        INNER JOIN mfcgt.mfccampana as CAMPANA on CAMPANA.id=IMPLEMENTACIONES.idcampana and CAMPANA.idversion=IMPLEMENTACIONES.idversion
                        INNER JOIN mfcgt.mfc as FLOW on FLOW.id=CAMPANA.idmfc and FLOW.idversion=CAMPANA.idversionmfc
                        INNER JOIN mfcgt.dmarca as MARCA on MARCA.id=FLOW.idmarca
                        INNER JOIN mfcgt.dcliente as CLIENTE on CLIENTE.id=MARCA.idcliente
                        INNER JOIN mfcgt.dformatodigital as FORMATO on FORMATO.id=IMPLEMENTACIONES.idformatodigital
                        INNER JOIN mfcgt.danuncio as ANUNCIO on ANUNCIO.id=FORMATO.idanuncio
                        INNER JOIN mfcgt.dmetrica as METRICA on METRICA.id=ANUNCIO.idmetrica
                        INNER JOIN mfcgt.dobjetivo as OBJETIVO on OBJETIVO.id=METRICA.idobjetivo
                        INNER JOIN mfcgt.mfcasignacion ASIGNACION on ASIGNACION.idmarca = MARCA.id 
                        where 
                        ASIGNACION.idusuario = {}
                        AND date_format(str_to_date(IMPLEMENTACIONES.multiplestiposb,'%m/%d/%Y'),'%Y-%m-%d')  > '{}'
                        group by METRICAS.CampaingID
                        ;
                    """.format(idusuario,hoy)))
            result = report.dump(query)
            for row in result:
                Nomenclatura = row['Campaingname']
                if row['KPI'] == 'AWARENESS' or row['KPI'] == 'ALCANCE':
                    row['KPIPlanificado'] = round((row['PresupuestoPlan'] / float(row['KPIPlanificado']) ) * 1000,2)
                    if row['KPIConsumido'] > 0:
                        row['KPIConsumido'] = round((row['InversionConsumida'] / float(row['KPIConsumido']) ) * 1000,2)
                else:
                    row['KPIPlanificado'] = round((row['PresupuestoPlan'] / float(row['KPIPlanificado']) ),2)
                    if row['KPIConsumido'] > 0:
                        row['KPIConsumido'] = round((row['InversionConsumida'] / float(row['KPIConsumido']) ),2)
                if Nomenclatura:
                    if row['StartDate'] != '0000-00-00' and row['EndDate'] != '0000-00-00':
                        Start = datetime.strptime(row['StartDate'], "%d/%m/%Y")
                        End = datetime.strptime(row['EndDate'], "%Y-%m-%d")
                        row['TotalDias'] = End - Start
                        row['DiasEjecutados'] = datetime.now() -  Start
                        row['DiasPorservir'] = End - datetime.now()
                        if row['TotalDias'].days > 0:
                            porcentDay = row['DiasEjecutados'].days / ((row['TotalDias'].days)  )
                        else:
                            porcentDay = 1
                        row['PresupuestoEsperado'] = round(float(row['PresupuestoPlan']) * porcentDay,2)
                        if float( row['PresupuestoPlan']) > 0:
                            row['PorcentajeEsperadoV'] = round(float( row['PresupuestoEsperado'])/ float( row['PresupuestoPlan']),2)
                            row['PorcentajeRealV'] = round(float(row['InversionConsumida'])/ float(row['PresupuestoPlan']),2)
                            row['PorcentajePresupuesto'] = round(float(row['PorcentajeRealV'] - 1),2)
                        row['KPIEsperado'] = round(float(row['KPIPlanificado']) * porcentDay,2)
                        if float( row['KPIPlanificado']) > 0:
                            row['PorcentajeEsperadoK'] = round(float( row['KPIEsperado'])/ float( row['KPIPlanificado']),2)
                            row['PorcentajeRealK'] = round(float(row['KPIConsumido'])/ float(row['KPIPlanificado']),2)
                            row['PorcentajeKPI'] =round(float(row['PorcentajeRealK'] - 1),2)
                        row['TotalDias'] = row['TotalDias'].days
                        row['DiasEjecutados'] = row['DiasEjecutados'].days
                        row['DiasPorservir'] = row['DiasPorservir'].days + 1
                        if porcentDay <= 0.25:
                            if abs(float(row['PorcentajePresupuesto'])) <= 0.15:
                                row['EstadoPresupuesto'] =  1
                            if abs(float(row['PorcentajeKPI'])) <= 0.15:
                                row['EstadoKPI'] =  1
                        elif porcentDay > 0.25 and porcentDay <=0.50:
                            if abs(float(row['PorcentajePresupuesto'])) <= 0.10:
                                row['EstadoPresupuesto'] =  1
                            if abs(float(row['PorcentajeKPI'])) <= 0.10:
                                row['EstadoKPI'] =  1
                        elif porcentDay > 0.50 and porcentDay <=0.85:
                            if abs(float(row['PorcentajePresupuesto'])) <= 0.05:
                                row['EstadoPresupuesto'] =  1
                            if abs(float(row['PorcentajeKPI'])) <= 0.05:
                                row['EstadoKPI'] =  1
                        elif porcentDay > 0.85:
                            if abs(float(row['PorcentajePresupuesto'])) <= 0.01:
                                row['EstadoPresupuesto'] =  1
                            if abs(float(row['PorcentajeKPI'])) <= 0.01:
                                row['EstadoKPI'] =  1
                        row['PorcentajeEsperadoV'] = round(float(row['PorcentajeEsperadoV'] * 100),0)
                        row['PorcentajeRealV'] = round(float(row['PorcentajeRealV'] * 100),0)
                        row['PorcentajePresupuesto'] = row['PorcentajePresupuesto'] * 100
                        row['PorcentajeEsperadoK'] = row['PorcentajeEsperadoK'] * 100
                        row['PorcentajeRealK'] = row['PorcentajeRealK'] * 100
                        row['PorcentajeKPI'] = int( int(row['PorcentajeRealK']) - int(row['PorcentajeEsperadoK']))
                        row['PorcentajePresupuesto'] = int(  row['PorcentajeRealV'] - row['PorcentajeEsperadoV'])
                        if int(row['PorcentajeEsperadoK']) > 0:
                            row['CostoPorResultadoP'] = round(row['PresupuestoEsperado'] / row['PorcentajeEsperadoK'],2)
                        if row['KPIConsumido'] > 0:
                            row['CostoPorResultadoR'] =round( row['InversionConsumida'] / row['KPIConsumido'],2)
                        if row['abr'] == 'CMP' or row['abr'] == 'CMPA':
                            row['CostoPorResultadoP'] = row['CostoPorResultadoP']*1000
                            row['CostoPorResultadoR'] = row['CostoPorResultadoR']*1000
                        row['PorcentajeEsperadoK'] = round(float(row['PorcentajeEsperadoK']),2)
                        row['PorcentajeRealK'] = round(float(row['PorcentajeRealK']),2)
                        campaings.append(row)
            campaings = jsonify(campaings)
            return campaings

        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())


class GetReporteCliente(Resource):
    @jwt_required
    def get(self,idcliente):
        try:
            hoy = datetime.now().strftime("%Y-%m-%d")
            campaings = []
            report = ReportSchema()
            report = ReportSchema(many=True)
            query = db.session.query('Account','idcliente','CampaingID','Marca','idmarca', 'Media','Campaingname','InversionConsumida','KPIPlanificado','StartDate' ,  'EndDate' ,'mes',   'PresupuestoPlan',  'KPI', 'KPIConsumido','State', 'TotalDias','DiasEjecutados','DiasPorservir','PresupuestoEsperado', 'PorcentajePresupuesto','PorcentajeEsperadoV','PorcentajeRealV','KPIEsperado', 'PorcentajeKPI','PorcentajeEsperadoK','PorcentajeRealK','EstadoKPI','EstadoPresupuesto','abr','CostoPorResultadoR','CostoPorResultadoP')
            query = query.from_statement(text("""
                    select CLIENTE.Nombre as Account,  CLIENTE.Id idcliente, MARCA.id idmarca, METRICAS.CampaingID CampaingID,ACCOUNTS.Media Media, METRICAS.Campaingname Campaingname, round(sum(distinct METRICAS.Cost),2) as 'InversionConsumida',
                        date_format(ifnull( CAMPANAMP.StartDate,str_to_date(IMPLEMENTACIONES.multiplestiposa,'%m/%d/%Y')),'%d/%m/%Y') StartDate , MARCA.nombre as Marca,
                        date_format(str_to_date(IMPLEMENTACIONES.multiplestiposb,'%m/%d/%Y'),'%Y-%m-%d') EndDate , 
                        ifnull(IMPLEMENTACIONES.costo,ifnull(IMPLEMENTACIONES.multiplescostosb,IMPLEMENTACIONES.bonificacion))  PresupuestoPlan,
                        SUBSTRING_INDEX (SUBSTRING_INDEX(METRICAS.Campaingname, '_', 14),'_',-1) KPIPlanificado,OBJETIVO.Nombre as KPI, OBJETIVO.abreviatura as abr,
                        ifnull(sum(distinct METRICAS.result),0) 'KPIConsumido', CAMPANAMP.Campaignstatus State,MARCA.nombre Marca ,CLIENTE.nombre Cliente,date_format(now(),'%M') mes,
                        '0' as 'TotalDias','0' as 'DiasEjecutados','0' as 'DiasPorservir', "0" as 'PresupuestoEsperado',"0" as 'PorcentajePresupuesto',
                        "0" as 'PorcentajeEsperadoV',"0" as 'PorcentajeRealV',"0" as 'KPIEsperado',"0" as 'PorcentajeKPI', "0" as 'PorcentajeEsperadoK',"0" as 'PorcentajeRealK', "0" as 'EstadoKPI', "0" as 'EstadoPresupuesto',"0" as 'CostoPorResultadoR', IMPLEMENTACIONES.rating' CostoPorResultadoP'

                        from dailycampaing METRICAS
                        INNER JOIN Campaings CAMPANAMP on CAMPANAMP.Campaingname =  METRICAS.Campaingname
                        INNER JOIN Accounts ACCOUNTS on CAMPANAMP.AccountsID = ACCOUNTS.AccountsID
                        left JOIN mfcgt.mfccompradiaria as IMPLEMENTACIONES on METRICAS.CampaignIDMFC=IMPLEMENTACIONES.id
                        INNER JOIN mfcgt.mfccampana as CAMPANA on CAMPANA.id=IMPLEMENTACIONES.idcampana and CAMPANA.idversion=IMPLEMENTACIONES.idversion
                        INNER JOIN mfcgt.mfc as FLOW on FLOW.id=CAMPANA.idmfc and FLOW.idversion=CAMPANA.idversionmfc
                        INNER JOIN mfcgt.dmarca as MARCA on MARCA.id=FLOW.idmarca
                        INNER JOIN mfcgt.dcliente as CLIENTE on CLIENTE.id=MARCA.idcliente
                        INNER JOIN mfcgt.dformatodigital as FORMATO on FORMATO.id=IMPLEMENTACIONES.idformatodigital
                        INNER JOIN mfcgt.danuncio as ANUNCIO on ANUNCIO.id=FORMATO.idanuncio
                        INNER JOIN mfcgt.dmetrica as METRICA on METRICA.id=ANUNCIO.idmetrica
                        INNER JOIN mfcgt.dobjetivo as OBJETIVO on OBJETIVO.id=METRICA.idobjetivo
                        INNER JOIN mfcgt.mfcasignacion ASIGNACION on ASIGNACION.idmarca = MARCA.id 
                        where 
                        CLIENTE.id = {} AND CAMPANAMP.Campaignstatus in ('ACTIVE','enabled')
                        group by METRICAS.CampaingID
                        ;

                    """.format(idcliente)))
            result = report.dump(query)

            for row in result:
                Nomenclatura = row['Campaingname']
                if row['KPI'] == 'AWARENESS' or row['KPI'] == 'ALCANCE':
                    row['KPIPlanificado'] = round((row['PresupuestoPlan'] / float(row['KPIPlanificado']) ) * 1000,2)
                    if row['KPIConsumido'] > 0:
                        row['KPIConsumido'] = round((row['InversionConsumida'] / float(row['KPIConsumido']) ) * 1000,2)
                else:
                    row['KPIPlanificado'] = round((row['PresupuestoPlan'] / float(row['KPIPlanificado']) ),2)
                    if row['KPIConsumido'] > 0:
                        row['KPIConsumido'] = round((row['InversionConsumida'] / float(row['KPIConsumido']) ),2)
                if Nomenclatura:
                    if row['StartDate'] != '0000-00-00' and row['EndDate'] != '0000-00-00':
                        Start = datetime.strptime(row['StartDate'], "%d/%m/%Y")
                        End = datetime.strptime(row['EndDate'], "%Y-%m-%d")
                        row['TotalDias'] = End - Start
                        row['DiasEjecutados'] = datetime.now() -  Start
                        row['DiasPorservir'] = End - datetime.now()
                        if row['TotalDias'].days > 0:
                            porcentDay = row['DiasEjecutados'].days / ((row['TotalDias'].days)  )
                        else:
                            porcentDay = 1
                        row['PresupuestoEsperado'] = round(float(row['PresupuestoPlan']) * porcentDay,2)
                        if float( row['PresupuestoPlan']) > 0:
                            row['PorcentajeEsperadoV'] = round(float( row['PresupuestoEsperado'])/ float( row['PresupuestoPlan']),2)
                            row['PorcentajeRealV'] = round(float(row['InversionConsumida'])/ float(row['PresupuestoPlan']),2)
                            row['PorcentajePresupuesto'] = round(float(row['PorcentajeRealV'] - 1),2)
                        row['KPIEsperado'] = round(float(row['KPIPlanificado']) * porcentDay,2)
                        if float( row['KPIPlanificado']) > 0:
                            row['PorcentajeEsperadoK'] = round(float( row['KPIEsperado'])/ float( row['KPIPlanificado']),2)
                            row['PorcentajeRealK'] = round(float(row['KPIConsumido'])/ float(row['KPIPlanificado']),2)
                            row['PorcentajeKPI'] =round(float(row['PorcentajeRealK'] - 1),2)
                        row['TotalDias'] = row['TotalDias'].days
                        row['DiasEjecutados'] = row['DiasEjecutados'].days
                        row['DiasPorservir'] = row['DiasPorservir'].days + 1
                        if porcentDay <= 0.25:
                            if abs(float(row['PorcentajePresupuesto'])) <= 0.15:
                                row['EstadoPresupuesto'] =  1
                            if abs(float(row['PorcentajeKPI'])) <= 0.15:
                                row['EstadoKPI'] =  1
                        elif porcentDay > 0.25 and porcentDay <=0.50:
                            if abs(float(row['PorcentajePresupuesto'])) <= 0.10:
                                row['EstadoPresupuesto'] =  1
                            if abs(float(row['PorcentajeKPI'])) <= 0.10:
                                row['EstadoKPI'] =  1
                        elif porcentDay > 0.50 and porcentDay <=0.85:
                            if abs(float(row['PorcentajePresupuesto'])) <= 0.05:
                                row['EstadoPresupuesto'] =  1
                            if abs(float(row['PorcentajeKPI'])) <= 0.05:
                                row['EstadoKPI'] =  1
                        elif porcentDay > 0.85:
                            if abs(float(row['PorcentajePresupuesto'])) <= 0.01:
                                row['EstadoPresupuesto'] =  1
                            if abs(float(row['PorcentajeKPI'])) <= 0.01:
                                row['EstadoKPI'] =  1
                        row['PorcentajeEsperadoV'] = round(float(row['PorcentajeEsperadoV'] * 100),0)
                        row['PorcentajeRealV'] = round(float(row['PorcentajeRealV'] * 100),0)
                        row['PorcentajePresupuesto'] = row['PorcentajePresupuesto'] * 100
                        row['PorcentajeEsperadoK'] = float(row['PorcentajeEsperadoK']) * 100
                        row['PorcentajeRealK'] = float(row['PorcentajeRealK']) * 100
                        row['PorcentajeKPI'] = int(int(row['PorcentajeRealK']) - int(row['PorcentajeEsperadoK']))
                        row['PorcentajePresupuesto'] = int(  row['PorcentajeRealV'] - row['PorcentajeEsperadoV'])
                        if int(row['PorcentajeEsperadoK']) > 0:
                            row['CostoPorResultadoP'] = round(row['PresupuestoEsperado'] / row['PorcentajeEsperadoK'],2)
                        if row['KPIConsumido'] > 0:
                            row['CostoPorResultadoR'] =round( row['InversionConsumida'] / row['KPIConsumido'],2)
                        if row['abr'] == 'CMP' or row['abr'] == 'CMPA':
                            row['CostoPorResultadoP'] = row['CostoPorResultadoP']*1000
                            row['CostoPorResultadoR'] = row['CostoPorResultadoR']*1000
                        row['PorcentajeEsperadoK'] = round(float(row['PorcentajeEsperadoK']),2)
                        row['PorcentajeRealK'] = round(float(row['PorcentajeRealK']),2)
                        campaings.append(row)
            
            campaings = jsonify(campaings)
            return campaings

        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class GetReporteML(Resource):
    @jwt_required
    def get(self,idusuario):
        try:
            lm = LocalMediaSchema()
            lm = LocalMediaSchema(many=True)
            data = db.session.query(LocalMedia.LocalMediaID,LocalMedia.Medio,LocalMedia.Cliente,LocalMedia.Pais,LocalMedia.Campana,LocalMedia.StartDate,LocalMedia.EndDate,LocalMedia.Mes,LocalMedia.ODC,LocalMedia.State ).order_by(LocalMedia.LocalMediaID).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())


class GetReporteMLID(Resource):
    @jwt_required
    def get(self,idlocal):
        try:
            lm = LocalMediaSchema()
            lm = LocalMediaSchema(many=True)
            data = db.session.query(LocalMedia.LocalMediaID,LocalMedia.Medio,LocalMedia.Cliente,LocalMedia.Pais,LocalMedia.Campana,LocalMedia.EndDate,LocalMedia.Mes,LocalMedia.ODC,LocalMedia.State ).filter(LocalMedia.LocalMediaID == idlocal).order_by(LocalMedia.LocalMediaID).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())




#('detailID', 'StartWeek','EndWeek', 'Nomenclatura', 'Formato','Objetivo','Impresiones', 'Clicks', 'Ctr', 'Consumo')
class GetReporteDetailML(Resource):
    @jwt_required
    def get(self,idlocal):
        try:
            lm = DetailLocalMediaSchema()
            lm = DetailLocalMediaSchema(many=True)
            data = db.session.query(DetailLocalMedia.detailID,DetailLocalMedia.StartWeek, DetailLocalMedia.EndWeek, DetailLocalMedia.Nomenclatura,DetailLocalMedia.Formato,DetailLocalMedia.Objetivo, DetailLocalMedia.Impresiones,DetailLocalMedia.Clicks,DetailLocalMedia.Ctr,DetailLocalMedia.Consumo ).filter(DetailLocalMedia.LocalMediaID == idlocal).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            print(datetime.now())
    def put(self,idlocal):
        try:
            a = LocalMedia.query.filter(LocalMedia.LocalMediaID==idlocal).first()
            a.State = 1
            db.session.commit()
            return 'Medio local actualizado correctamente Correctamente', 201
        except Exception as e:
            print(e)
            return 'Account no Ingresada', 400
        finally:
            pass
    def delete(self,idlocal):
        try:
            LocalMedia.query.filter(LocalMedia.LocalMediaID == idlocal).delete()
            DetailLocalMedia.query.filter(DetailLocalMedia.LocalMediaID == idlocal).delete()
            db.session.commit()
            return 'Eliminado Correcatamente', 200
        except Exception as e:
            print(e)
            return 'Account no Ingresada', 400
        finally:
            db.session.close()
            pass


class GetGroupByODClML(Resource):
    @jwt_required
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
            db.session.close()
            print(datetime.now())


class GetReporteDetODC(Resource):
    @jwt_required
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
            db.session.close()
            print(datetime.now())

class GetCliente(Resource):
    @jwt_required
    def get(self,idusuario):
        try:
            cshema = DclienteSchema()
            cshema = DclienteSchema(many=True)
            query = db.session.query('id','nombre')
            query = query.from_statement(text("""
            select distinct c.id,c.nombre, asi.idusuario from mfcgt.mfcasignacion asi
            inner join mfcgt.dmarca m on m.id = asi.idmarca
            inner join mfcgt.dcliente c on c.id = m.idcliente
            where asi.idusuario = {};
            """.format(idusuario)))
            result = cshema.dump(query)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class GetClienteMarca(Resource):
    @jwt_required
    def get(self,idcliente):
        try:
            cshema = DclienteSchema()
            cshema = DclienteSchema(many=True)
            query = db.session.query('id','nombre')
            query = query.from_statement(text("""
            select m.id,m.nombre from mfcgt.dmarca m
            inner join mfcgt.dcliente c on c.id = m.idcliente
            where c.id =  {};
            """.format(idcliente)))
            result = cshema.dump(query)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class PostEstadoErrors(Resource):
    @jwt_required
    def post(self,idError,idusuario):
        try:
            a = Errorscampaings.query.filter(Errorscampaings.iderrorscampaings==idError).first()
            a.estado = 0
            a.UsuarioOmitir = idusuario
            db.session.commit()
            return 'Error omitido correctamente Correctamente', 201
        except Exception as e:
            print(e)
            return 'Error no omitido', 400
        finally:
            db.session.close()
            pass

class GetCostCamp(Resource):
    @jwt_required
    def get(self,campaing):
        try:
            cshema = CostSchema()
            cshema = CostSchema(many=True)
            campaing = campaing.replace('|', '/')
            query = db.session.query('id','cost')
            query = query.from_statement(text("""
            select * from (select dc.id,c.Campaingname,  round(MAX(dc.Cost),2) cost from dailycampaing dc
            inner join Campaings c on dc.CampaingID = c.CampaingID
            group by c.CampaingID
            union all
            select h.CampaingID id,  Campaingname, (Cost) from HistoricCampaings h) as  t
            where t.Campaingname ='{}'
            ;
            """.format(campaing)))
            result = cshema.dump(query)
            if result==[]:
                result = None
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())


class PostDataLeads(Resource):
    def post(self,CampaingID,Nombre,Telefono,NIT,DPI,Email,Ubicacion,Plataforma,Producto):


        try:
            a = LeadAdsCampaings(CampaingID,Nombre,Telefono,NIT,DPI,Email,Ubicacion,Plataforma,Producto)

            db.session.add(a)
            db.session.commit()
            return 'Lead Ingresado Correctamente', 201

        except Exception as e:
            print(e)
            return 'Ocurrio un error', 400
        finally:
            db.session.close()
            pass

class GetDataLeads(Resource):
    def get(self,CampaingID,FechaInicio,FechaFin):
        try:

            hoy = datetime.now().strftime("%Y-%m-%d")
            date_time_Inicio = datetime.strptime(FechaInicio, '%Y-%m-%d')
            date_time_Fin = datetime.strptime(FechaFin, '%Y-%m-%d')
            campaings = []
            report = LeadAdsCampaingsSchema()
            report = LeadAdsCampaingsSchema(many=True)
            query = db.session.query('id', 'CampaingID', 'Nombre', 'Telefono', 'Email', 'NIT', 'DPI', 'Plataforma', 'Ubicacion', 'Producto', 'EstadoDpi','EstadoTelefono', 'EstadoEmail','EstadoGeneral','CreateDate')
            query = query.from_statement(text("""
                    select idLeadAdsCampaings id, CampaingID, Nombre, Telefono, Email, NIT, DPI, Plataforma, Ubicacion, Producto, date_format(CreateDate,'%d/%m/%Y') CreateDate, 0 as EstadoDpi, 0 as EstadoTelefono, 0 as EstadoEmail, 0 as EstadoGeneral
                    from LeadAdsCampaings
                    where CampaingID='{}' and (`CreateDate` >= '{} and CreateDate <= {}') order by CreateDate desc;
                    """.format(CampaingID,date_time_Inicio.date(),date_time_Fin.date())))
            result = report.dump(query)
            count = 0
            for row in result:
                DPI = row['DPI']
                DPI = str(DPI).replace(" ", "")
                DPI = str(DPI).replace("-", "")
                row['DPI'] = DPI
                if len(DPI) == 13:
                    row['EstadoDpi'] = 1
                Email = row['Email']
                searchObj = re.search(r"""^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$""", Email, re.M | re.I)
                if searchObj:
                    row['EstadoEmail'] = 1
                Number = str(row['Telefono'])
                if len(Number) >= 8:
                    row['EstadoTelefono'] = 1

                if row['EstadoDpi'] < 1 or row['EstadoEmail'] < 1 or row['EstadoTelefono'] < 1:
                    row['EstadoGeneral'] = 0
                else:
                    row['EstadoGeneral'] = 1
                campaings.append(row)
            campaings = jsonify(campaings)
            return campaings
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class GetInvitados(Resource):
    def get(self):
        try:
            lm = InvitadosSchema()
            lm = InvitadosSchema(many=True)
            data = db.session.query(Invitados.idUsuario.label('id'),Invitados.user.label('username'),Invitados.password,Invitados.user.label('firstName'),Invitados.user.label('lastName')).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())


class GetDuplicateLeads(Resource):
    def get(self,CampaingID,FechaInicio,FechaFin):
        try:
            date_time_Inicio = datetime.strptime(FechaInicio, '%Y-%m-%d')
            date_time_Fin = datetime.strptime(FechaFin, '%Y-%m-%d')
            report = LeadAdsCampaingsSchema()
            report = LeadAdsCampaingsSchema(many=True)
            query = db.session.query('id', 'CampaingID', 'Nombre', 'Telefono', 'Email', 'NIT', 'DPI', 'Plataforma', 'Ubicacion','Producto','CreateDate' , 'EstadoDpi','EstadoTelefono', 'EstadoEmail','EstadoGeneral')
            query = query.from_statement(text("""
                    select idLeadAdsCampaings id, CampaingID, Nombre, Telefono, Email, NIT, DPI, Plataforma, Ubicacion,Producto,date_format(CreateDate,'%d/%m/%Y') CreateDate, 0 as EstadoDpi, 0 as EstadoTelefono, 0 as EstadoEmail, 0 as EstadoGeneral
                    from LeadAdsCampaings
                    where CampaingID='{}' and (`CreateDate` >= '{} and CreateDate <= {}')
                    GROUP BY DPI
                    HAVING COUNT(DPI) > 1 order by CreateDate desc;
                    """.format(CampaingID,date_time_Inicio.date(),date_time_Fin.date())))
            result = report.dump(query)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class MisFLowsAprobados(Resource):
    def get(self,idmarca):
        try:
            if idmarca == '1':
                json=[
                    {
                        'estado':0,
                        'id':1,
                        'nombre':'',
                        'paisimplementar':''
                    }
                ]
                return json
            lm = models.mfccompradiaria()
            lm = models.mfcSchema(many=True)
            data = db.session.query(models.mfc.id,models.mfc.estado,models.mfc.nombre,
            models.dpais.nombre.label('paisimplementar')).join(models.mfc,
            models.mfc.paisimplementar == models.dpais.id).filter(
                models.mfc.idmarca == idmarca).order_by(desc(func.ifnull(models.mfc.fechaing,models.mfc.fechamod))).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class MisCampanas(Resource):
    def get(self,flowid):
        try:
            if flowid == '1':
                json=[
                    {
                        "costo": 0,
                        "costoplataforma": None,
                        "fechafin": "2020-01-31",
                        "fechainicio": "2020-01-01",
                        "id": 1,
                        "idversion": 1,
                        "nombre": "",
                        "nombreversion": ""
                    }
                ]
                return json
            lm = models.campanaSchema()
            lm = models.campanaSchema(many=True)
            query = db.session.query('id', 'idversion', 'nombre', 'nombreversion', 'fechainicio', 'fechafin', 'costo', 'costoplataforma')
            query = query.from_statement(text("""
                  select c.id,c.idversion,c.nombre,c.nombreversion,c.fechainicio, c.fechafin , sum(distinct d.costo) costo,
                    (
                        select sum(da.Cost) from dailycampaing da
                        inner join Campaings ca on ca.CampaingID = da.CampaingID
                        inner join mfcgt.mfccompradiaria com on  ca.Campaingname = com.multiplestiposg
                        inner join mfcgt.mfccampana m on m.id = com.idcampana
                        where m.id = c.id
                    ) costoplataforma
                    from mfcgt.mfccampana c
                    inner join mfcgt.mfccompradiaria d on d.idcampana = c.id
                    where c.idmfc = {}
                    group by c.id;
                    """.format(flowid)))

            result = lm.dump(query)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())


class MisLineasImplementadas(Resource):
    def get(self,campanaid):
        try:
            if campanaid == '1':
                json=[
                    {
                        'estado':0,
                        'id':1,
                        'nombre':'',
                        'paisimplementar':''
                    }
                ]
                print(json)
                return json
            lm = models.compradiariaSchema()
            lm = models.compradiariaSchema(many=True)
            query = db.session.query('id', 'nombre', 'fecha_inicio_mfc', 'fecha_fin_mfc', 'fecha_inicio_pl','fecha_fin_pl','costo_mfc', 'costo_pl')
            query = query.from_statement(text("""
                  select cd.id, ca.Campaingname nombre, cd.multiplestiposa fecha_inicio_mfc,cd.multiplestiposb fecha_fin_mfc,
                    date_format(ca.StartDate,'%m/%d/%Y') fecha_inicio_pl,date_format(ca.EndDate,'%m/%d/%Y') fecha_fin_pl ,
                    cd.costo costo_mfc,sum(da.Cost) costo_pl  from mfcgt.mfccompradiaria cd
                    inner join Campaings ca on ca.Campaingname = cd.multiplestiposg
                    inner join dailycampaing da on ca.CampaingID = da.CampaingID
                    where idcampana = {}
                    group by da.CampaingID;

                    """.format(campanaid)))
            result = lm.dump(query)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())


class GetResults_Campaings(Resource):
    #@jwt_required
    def get(self,idMarca):
        try:
            lm = Results_campaingsSchema()
            lm = Results_campaingsSchema(many=True)
            data = db.session.query(Results_campaings.idResult,Results_campaings.Description, \
            Results_campaings.Url,Results_campaings.Status,Results_campaings.idMarca) \
            .filter(Results_campaings.Status==1, Results_campaings.idMarca == idMarca).order_by(Results_campaings.Description).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())          
### Mis Flows
##
## Se tiene que agregar cada ruta a la aplicacion, ruta -> class
##

#Bitacora
api.add_resource(GetBitacora, '/task/Bitacora')
api.add_resource(GetBitacoraFull, '/task/BitacoraFull')
api.add_resource(GetBitacoraFiles, '/task/BitacoraNames')
#Adminstracion
api.add_resource(GetAccountxMarca, '/task/AccountxMarca/<string:idMarca>')
api.add_resource(PostMarcaxAccount, '/task/InsertAccountxMarca/<string:idAccount>&<string:idMarca>&<string:Estado>&<string:User>')
api.add_resource(GetAccount, '/task/AccountAll')
api.add_resource(GetAccountNames, '/task/AccountNames')
api.add_resource(GetDmarca, '/task/Marca')
api.add_resource(GetDmarcaName, '/task/MarcaNames')
api.add_resource(CRUDAccount, '/task/Account/<string:idAccount>&<string:Account>&<string:Medio>&<string:Country>')
api.add_resource(GetCostCamp, '/task/Costo/<string:campaing>')
#Token
api.add_resource(GenToken, '/task/Token/<string:idusuario>')
#Modulo de Errores GetCountsErrores
api.add_resource(GetErrores, '/Errores/<string:idusuario>')
api.add_resource(GetCountsErrores, '/Errores/Count/<string:idusuario>')
api.add_resource(PostEstadoErrors, '/Errores/Omitir/<string:idError>&<string:idusuario>')

#Modulo de Reportes
api.add_resource(GetReporte, '/Reporte/<string:idusuario>')
api.add_resource(GetReporteCliente, '/Reporte/Invitado/<string:idcliente>')
api.add_resource(GetReporteML, '/Reporte/ArchivosLM/<string:idusuario>')
api.add_resource(GetReporteMLID, '/Reporte/ArchivosLMEncabezado/<string:idlocal>')
api.add_resource(GetReporteDetailML, '/Reporte/DetalleLM/<string:idlocal>')
api.add_resource(GetGroupByODClML, '/Reporte/ODC')
api.add_resource(GetReporteDetODC, '/Reporte/ODC/<string:Odc>')
api.add_resource(GetCliente, '/Reporte/Cliente/<string:idusuario>')
api.add_resource(GetClienteMarca, '/Reporte/ClienteMarca/<string:idcliente>')
#LEAD CampaingID,Nombre,Telefono,NIT,DIP,Ubicacion,Plataforma,Email
api.add_resource(PostDataLeads, '/webhoop/Leads/<string:CampaingID>&<string:Nombre>&<string:Telefono>&<string:NIT>&<string:DPI>&<string:Email>&<string:Ubicacion>&<string:Plataforma>&<string:Producto>')
api.add_resource(GetDataLeads, '/webhoop/Leads/<string:CampaingID>&<string:FechaInicio>&<string:FechaFin>')
api.add_resource(GetDuplicateLeads, '/webhoop/Leads/Duplicados/<string:CampaingID>&<string:FechaInicio>&<string:FechaFin>')
api.add_resource(GetInvitados, '/Invitados')
#Mis Flows
api.add_resource(MisFLowsAprobados, '/Flows/<string:idmarca>')
api.add_resource(MisCampanas, '/Flows/Campana/<string:flowid>')
api.add_resource(MisLineasImplementadas, '/Flows/LineaImp/<string:campanaid>')
api.add_resource(GetResults_Campaings, '/Reports/<string:idMarca>')
#Actualizacion Datos
api.add_resource(Actualizacion_Datos.GetMetricsCampaing, '/DatosReportes/<string:IDMFC>&<string:Mes>')
api.add_resource(Actualizacion_Datos.UpdateMetricsCamps, '/DatosReportes/')
if __name__ == '__main__':
    JWTManager(app)
    app.run(debug=True,port=5050)