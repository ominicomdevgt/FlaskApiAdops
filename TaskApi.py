# -*- coding: UTF-8 -*-
from flask import Flask, request
import sys
from flask import jsonify
from flask_cors.core import CONFIG_OPTIONS
from sqlalchemy.sql.expression import case
from app import app, db, mail
from flask_restful import reqparse, abort, Api, Resource
from models import Bitacora, BitacoraSchema, Dmarca, DmarcaSchema,Accountxmarca,AccountxMarcaSchema,Accounts,AccountsSchema, Dcliente, DclienteSchema,Errorscampaings,ErrorsCampaingsSchema, ReportSchema, LocalMedia, LocalMediaSchema, DetailLocalMedia, DetailLocalMediaSchema, ErrorsCampaingsCountSchema, Dcliente,DclienteSchema,CostSchema, LeadAdsCampaings, LeadAdsCampaingsSchema, Invitados,InvitadosSchema, mfcaprobacion,aprobacionSchema,Results_campaings,Results_campaingsSchema, rCampaings, rCampaingsSchema,rCampaingMetrics, rCampaingMetricsSchema, LocalMedia, LocalMediaSchema,LocalMediaReports,LocalMediaReportsSchema,PuestosOmgGT,PuestosOmgGTSchema,LocalMediaReportsCountSchema,UsuarioOmgGT,Visitias_Sitio,Visitias_SitioSchema,usuarios_promocion_Sitio, usuarios_promocion_barca_Sitio, usuarios_promocion_barca_SitioSchema,usuarios_promocion_tonalight
import models
from flask_sqlalchemy import SQLAlchemy,time
from flask_marshmallow import Marshmallow
from datetime import datetime, timedelta
import os
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required, get_jwt_identity,JWTManager
import jwt
import re
from sqlalchemy.sql import func,text, desc
import numpy as np
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import Actualizacion_Datos
from flask_mail import Mail, Message 
import random
import secrets
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
    #@jwt_required
    def get(self,idusuario):
        try:
            dmarcaSchema = ErrorsCampaingsSchema()
            dmarcaSchema = ErrorsCampaingsSchema(many=True)
            hoy = datetime.now().strftime("%Y-%m-%d")
            query = db.session.query('iderror','idcuenta','cuenta','CampaingID',
            'Campaingname','Error','TipoErrorID','DescripcionError','GrupoError',
            'Icono','Comentario','Estado','Media','Fecha','tipousuario','plataforma',
            'marca','cliente','id_marca','id_cliente','FechaError')
            query = query.from_statement(text("""
            (Select distinct a.idErrorsCampaings as iderror,d.AccountsID as idcuenta,
            d.Account as cuenta,a.CampaingID,b.Campaingname Campaingname,a.Error,
            a.TipoErrorID, c.Descripcion as DescripcionError,c.GrupoError,c.Icono,
            a.Comentario,a.Estado, d.Media, DATE_FORMAT(a.CreateDate, "%d/%m/%Y") as Fecha ,
            c.tipousuario,d.Media as plataforma, IFNULL( m.id,"SIN ASIGNAR") id_marca,
             m.nombre marca, IFNULL(cl.id,"SIN ASIGNAR") id_cliente, cl.nombre cliente, a.CreateDate 'FechaError'
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
                c.tipousuario,d.Media as plataforma,"SIN ASIGNAR" marca, "SIN ASIGNAR" cliente, 0 id_marca, 0 id_cliente,a.CreateDate 'FechaError'
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
    #@jwt_required
    def get(self,idusuario):
        try:
            hoy = datetime.now().strftime("%Y-%m-%d")
            campaings = []
            report = ReportSchema()
            report = ReportSchema(many=True)
            query = db.session.query('Account','idcliente','CampaingID','Marca','idmarca', 'Media','Campaingname','InversionConsumida','KPIPlanificado','StartDate' ,  'EndDate' ,'mes',   'PresupuestoPlan',  'KPI', 'KPIConsumido','State', 'TotalDias','DiasEjecutados','DiasPorservir','PresupuestoEsperado', 'PorcentajePresupuesto','PorcentajeEsperadoV','PorcentajeRealV','KPIEsperado', 'PorcentajeKPI','PorcentajeEsperadoK','PorcentajeRealK','EstadoKPI','EstadoPresupuesto','abr','CostoPorResultadoR','CostoPorResultadoP','Campana','Version','NombreMetrica','MetricaPlanificada','MetricaConsumida')
            query = query.from_statement(text("""
                    select CLIENTE.Nombre as Account,  CLIENTE.Id idcliente, MARCA.id idmarca, METRICAS.CampaingID CampaingID,PLATAFORMA.nombre Media ,IMPLEMENTACIONES.multiplestiposg Campaingname, round(sum(distinct METRICAS.Cost),2) as 'InversionConsumida',
                        date_format(str_to_date(IMPLEMENTACIONES.multiplestiposa,'%m/%d/%Y'),'%d/%m/%Y') StartDate , MARCA.nombre as Marca,
                        date_format(str_to_date(IMPLEMENTACIONES.multiplestiposb,'%m/%d/%Y'),'%d/%m/%Y') EndDate , 
                        ifnull(ifnull(IMPLEMENTACIONES.costo,ifnull(IMPLEMENTACIONES.multiplescostosb,IMPLEMENTACIONES.bonificacion)),0)  PresupuestoPlan,
                        SUBSTRING_INDEX (SUBSTRING_INDEX(IMPLEMENTACIONES.multiplestiposg, '_', 14),'_',-1) KPIPlanificado,OBJETIVO.Nombre as KPI, OBJETIVO.abreviatura as abr,
                        ifnull(sum(distinct METRICAS.result),0) 'KPIConsumido', IMPLEMENTACIONES.estado State,MARCA.nombre Marca ,CLIENTE.nombre Cliente,date_format(now(),'%M') mes,CAMPANA.nombre Campana, IMPLEMENTACIONES.version Version, 
                        METRICA.nombre as 'NombreMetrica', SUBSTRING_INDEX (SUBSTRING_INDEX(IMPLEMENTACIONES.multiplestiposg, '_', 14),'_',-1) as 'MetricaPlanificada', ifnull(sum(distinct METRICAS.result),0) 'MetricaConsumida',
                        '0' as 'TotalDias','0' as 'DiasEjecutados','0' as 'DiasPorservir', "0" as 'PresupuestoEsperado',"0" as 'PorcentajePresupuesto',
                        "0" as 'PorcentajeEsperadoV',"0" as 'PorcentajeRealV',"0" as 'KPIEsperado',"0" as 'PorcentajeKPI', "0" as 'PorcentajeEsperadoK',"0" as 'PorcentajeRealK', "0" as 'EstadoKPI', "0" as 'EstadoPresupuesto',"0" as 'CostoPorResultadoR', IMPLEMENTACIONES.rating' CostoPorResultadoP'

                        from MediaPlatformsReports.CampaingMetrics_daily METRICAS                        
                        iNNER JOIN mfcgt.mfccompradiaria as IMPLEMENTACIONES on METRICAS.CampaignIDMFC=IMPLEMENTACIONES.id
                        INNER JOIN mfcgt.mfccampana as CAMPANA on CAMPANA.id=IMPLEMENTACIONES.idcampana and CAMPANA.idversion=IMPLEMENTACIONES.idversion
                        INNER JOIN mfcgt.mfc as FLOW on FLOW.id=CAMPANA.idmfc and FLOW.idversion=CAMPANA.idversionmfc
                        INNER JOIN mfcgt.dmarca as MARCA on MARCA.id=FLOW.idmarca
                        INNER JOIN mfcgt.dcliente as CLIENTE on CLIENTE.id=MARCA.idcliente
                        INNER JOIN mfcgt.dformatodigital as FORMATO on FORMATO.id=IMPLEMENTACIONES.idformatodigital
                        INNER JOIN mfcgt.danuncio as ANUNCIO on ANUNCIO.id=FORMATO.idanuncio
                        INNER JOIN mfcgt.dmetrica as METRICA on METRICA.id=ANUNCIO.idmetrica
                        INNER JOIN mfcgt.dobjetivo as OBJETIVO on OBJETIVO.id=METRICA.idobjetivo
                        INNER JOIN mfcgt.dplataforma PLATAFORMA ON PLATAFORMA.id = OBJETIVO.idplataforma
                        INNER JOIN mfcgt.mfcasignacion ASIGNACION on ASIGNACION.idmarca = MARCA.id 
                        where
                        ASIGNACION.idusuario = {}
                        AND date_format(str_to_date(IMPLEMENTACIONES.multiplestiposb,'%m/%d/%Y'),'%Y-%m-%d')  > '{}'
                        and IMPLEMENTACIONES.multiplestiposg is not null and IMPLEMENTACIONES.id !=(98936)
                        group by IMPLEMENTACIONES.ID
                        
                    Union ALL
                    select CLIENTE.Nombre as Account,  CLIENTE.Id idcliente, MARCA.id idmarca, METRICAS.ID CampaingID,PLATAFORMA.nombre Media ,IMPLEMENTACIONES.multiplestiposg Campaingname, round(sum(distinct METRICAS.UnitCost),2) as 'InversionConsumida',
                        date_format(str_to_date(IMPLEMENTACIONES.multiplestiposa,'%m/%d/%Y'),'%d/%m/%Y') StartDate , MARCA.nombre as Marca,
                        date_format(str_to_date(IMPLEMENTACIONES.multiplestiposb,'%m/%d/%Y'),'%d/%m/%Y') EndDate , 
                        ifnull(ifnull(IMPLEMENTACIONES.costo,ifnull(IMPLEMENTACIONES.multiplescostosb,IMPLEMENTACIONES.bonificacion)),0)  PresupuestoPlan,
                        SUBSTRING_INDEX (SUBSTRING_INDEX(IMPLEMENTACIONES.multiplestiposg, '_', 14),'_',-1) KPIPlanificado,OBJETIVO.Nombre as KPI, OBJETIVO.abreviatura as abr,
                        (CASE
                            WHEN (`METRICA`.`abreviatura` = 'IMP') THEN SUM(DISTINCT `METRICAS`.`Impressions`)
                            WHEN (`METRICA`.`abreviatura` = 'VIS') THEN SUM(DISTINCT `METRICAS`.`Clicks`)
                            WHEN (`METRICA`.`abreviatura` = 'CL') THEN SUM(DISTINCT `METRICAS`.`Clicks`)
                            WHEN (`METRICA`.`abreviatura` = 'REP') THEN SUM(DISTINCT `METRICAS`.`Videowachesat75`)
                            ELSE 0
                        END) AS  'KPIConsumido',
                        IMPLEMENTACIONES.estado State,MARCA.nombre Marca ,CLIENTE.nombre Cliente,date_format(now(),'%M') mes,CAMPANA.nombre Campana, IMPLEMENTACIONES.version Version,
                        METRICA.nombre as 'NombreMetrica', SUBSTRING_INDEX (SUBSTRING_INDEX(IMPLEMENTACIONES.multiplestiposg, '_', 14),'_',-1) as 'MetricaPlanificada', (CASE
                            WHEN (`METRICA`.`abreviatura` = 'IMP') THEN SUM(DISTINCT `METRICAS`.`Impressions`)
                            WHEN (`METRICA`.`abreviatura` = 'VIS') THEN SUM(DISTINCT `METRICAS`.`Clicks`)
                            WHEN (`METRICA`.`abreviatura` = 'CL') THEN SUM(DISTINCT `METRICAS`.`Clicks`)
                            WHEN (`METRICA`.`abreviatura` = 'REP') THEN SUM(DISTINCT `METRICAS`.`Videowachesat75`)
                            ELSE 0
                        END) as 'MetricaConsumida', 
                        '0' as 'TotalDias','0' as 'DiasEjecutados','0' as 'DiasPorservir', "0" as 'PresupuestoEsperado',"0" as 'PorcentajePresupuesto',
                        "0" as 'PorcentajeEsperadoV',"0" as 'PorcentajeRealV',"0" as 'KPIEsperado',"0" as 'PorcentajeKPI', "0" as 'PorcentajeEsperadoK',"0" as 'PorcentajeRealK', "0" as 'EstadoKPI', "0" as 'EstadoPresupuesto',"0" as 'CostoPorResultadoR', IMPLEMENTACIONES.rating' CostoPorResultadoP'

                        from MediaPlatformsReports.LocalMedia METRICAS                        
                        iNNER JOIN mfcgt.mfccompradiaria as IMPLEMENTACIONES on METRICAS.IDMFC=IMPLEMENTACIONES.id
                        INNER JOIN mfcgt.mfccampana as CAMPANA on CAMPANA.id=IMPLEMENTACIONES.idcampana and CAMPANA.idversion=IMPLEMENTACIONES.idversion
                        INNER JOIN mfcgt.mfc as FLOW on FLOW.id=CAMPANA.idmfc and FLOW.idversion=CAMPANA.idversionmfc
                        INNER JOIN mfcgt.dmarca as MARCA on MARCA.id=FLOW.idmarca
                        INNER JOIN mfcgt.dcliente as CLIENTE on CLIENTE.id=MARCA.idcliente
                        INNER JOIN mfcgt.dformatodigital as FORMATO on FORMATO.id=IMPLEMENTACIONES.idformatodigital
                        INNER JOIN mfcgt.danuncio as ANUNCIO on ANUNCIO.id=FORMATO.idanuncio
                        INNER JOIN mfcgt.dmetrica as METRICA on METRICA.id=ANUNCIO.idmetrica
                        INNER JOIN mfcgt.dobjetivo as OBJETIVO on OBJETIVO.id=METRICA.idobjetivo
                        INNER JOIN mfcgt.dplataforma PLATAFORMA ON PLATAFORMA.id = OBJETIVO.idplataforma
                        INNER JOIN mfcgt.mfcasignacion ASIGNACION on ASIGNACION.idmarca = MARCA.id 
                        where
                        ASIGNACION.idusuario = {}
                        AND date_format(str_to_date(IMPLEMENTACIONES.multiplestiposb,'%m/%d/%Y'),'%Y-%m-%d')  > '{}'
                        and IMPLEMENTACIONES.multiplestiposg is not null and IMPLEMENTACIONES.id !=(98936)
                        and METRICAS.State = 2
                        group by IMPLEMENTACIONES.ID        
                UNION ALL
                    select CLIENTE.Nombre as Account,  CLIENTE.Id idcliente, MARCA.id idmarca, METRICAS.AdSetID CampaingID,PLATAFORMA.nombre Media ,IMPLEMENTACIONES.multiplestiposg Campaingname, round(sum(distinct METRICAS.Cost),2) as 'InversionConsumida',
                        date_format(str_to_date(IMPLEMENTACIONES.multiplestiposa,'%m/%d/%Y'),'%d/%m/%Y') StartDate , MARCA.nombre as Marca,
                        date_format(str_to_date(IMPLEMENTACIONES.multiplestiposb,'%m/%d/%Y'),'%d/%m/%Y') EndDate , 
                        ifnull(ifnull(IMPLEMENTACIONES.costo,ifnull(IMPLEMENTACIONES.multiplescostosb,IMPLEMENTACIONES.bonificacion)),0)  PresupuestoPlan,
                        SUBSTRING_INDEX (SUBSTRING_INDEX(IMPLEMENTACIONES.multiplestiposg, '_', 14),'_',-1) KPIPlanificado,OBJETIVO.Nombre as KPI, OBJETIVO.abreviatura as abr,
                        ifnull(sum(distinct METRICAS.result),0) 'KPIConsumido', IMPLEMENTACIONES.estado State,MARCA.nombre Marca ,CLIENTE.nombre Cliente,date_format(now(),'%M') mes,CAMPANA.nombre Campana, IMPLEMENTACIONES.version Version, 
                        METRICA.nombre as 'NombreMetrica', SUBSTRING_INDEX (SUBSTRING_INDEX(IMPLEMENTACIONES.multiplestiposg, '_', 14),'_',-1) as 'MetricaPlanificada', ifnull(sum(distinct METRICAS.result),0) 'MetricaConsumida',
                        '0' as 'TotalDias','0' as 'DiasEjecutados','0' as 'DiasPorservir', "0" as 'PresupuestoEsperado',"0" as 'PorcentajePresupuesto',
                        "0" as 'PorcentajeEsperadoV',"0" as 'PorcentajeRealV',"0" as 'KPIEsperado',"0" as 'PorcentajeKPI', "0" as 'PorcentajeEsperadoK',"0" as 'PorcentajeRealK', "0" as 'EstadoKPI', "0" as 'EstadoPresupuesto',"0" as 'CostoPorResultadoR', IMPLEMENTACIONES.rating' CostoPorResultadoP'

                        from MediaPlatformsReports.AdSetMetrics_daily METRICAS                        
                        iNNER JOIN mfcgt.mfccompradiaria as IMPLEMENTACIONES on METRICAS.CampaignIDMFC=IMPLEMENTACIONES.id
                        INNER JOIN mfcgt.mfccampana as CAMPANA on CAMPANA.id=IMPLEMENTACIONES.idcampana and CAMPANA.idversion=IMPLEMENTACIONES.idversion
                        INNER JOIN mfcgt.mfc as FLOW on FLOW.id=CAMPANA.idmfc and FLOW.idversion=CAMPANA.idversionmfc
                        INNER JOIN mfcgt.dmarca as MARCA on MARCA.id=FLOW.idmarca
                        INNER JOIN mfcgt.dcliente as CLIENTE on CLIENTE.id=MARCA.idcliente
                        INNER JOIN mfcgt.dformatodigital as FORMATO on FORMATO.id=IMPLEMENTACIONES.idformatodigital
                        INNER JOIN mfcgt.danuncio as ANUNCIO on ANUNCIO.id=FORMATO.idanuncio
                        INNER JOIN mfcgt.dmetrica as METRICA on METRICA.id=ANUNCIO.idmetrica
                        INNER JOIN mfcgt.dobjetivo as OBJETIVO on OBJETIVO.id=METRICA.idobjetivo
                        INNER JOIN mfcgt.dplataforma PLATAFORMA ON PLATAFORMA.id = OBJETIVO.idplataforma
                        INNER JOIN mfcgt.mfcasignacion ASIGNACION on ASIGNACION.idmarca = MARCA.id 
                        where
                        ASIGNACION.idusuario = {}
                        AND date_format(str_to_date(IMPLEMENTACIONES.multiplestiposb,'%m/%d/%Y'),'%Y-%m-%d')  > '{}'
                        and IMPLEMENTACIONES.multiplestiposg is not null and IMPLEMENTACIONES.id !=(98936)
                        group by IMPLEMENTACIONES.ID
                        ;
                    """.format(idusuario,hoy,idusuario,hoy,idusuario,hoy)))
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
                        End = datetime.strptime(row['EndDate'], "%d/%m/%Y")
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
            exp = ''
            return campaings

        except Exception as e:
            exp = e
            print(e)
            return 'error:' + str(exp), 201
        finally:
            db.session.close()
            print(datetime.now())
            


class GetReporteCliente(Resource):
    #@jwt_required
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
            data = db.session.query( func.concat(models.mfc.id, models.mfc.idversion).label('id'),models.mfc.id.label('idflow') ,models.mfc.estado,models.mfc.nombre,models.mfc.anioimplementacion,
            models.dpais.nombre.label('paisimplementar'), models.mfc.paisfacturar, models.mfc.paisimplementar, models.mfc.idversion).join(models.mfc,
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

class MisFLowsAprobadosPorUsuario(Resource):
    def get(self,idusuario):
        try:
            if idusuario == '1':
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
            data = db.session.query( func.concat(models.mfc.id, models.mfc.idversion).label('id'),models.mfc.id.label('idflow') ,models.mfc.estado,models.mfc.nombre,models.mfc.anioimplementacion,
            models.dpais.nombre.label('paisimplementar'), models.mfc.paisfacturar, models.mfc.paisimplementar, models.mfc.idversion).join(
                models.mfc,models.mfc.paisimplementar == models.dpais.id).join(
                models.mfcasignacion,models.mfc.idmarca == models.mfcasignacion.idmarca
                ).filter(
                models.mfcasignacion.idusuario == idusuario,models.mfc.anioimplementacion==2020).order_by(desc(func.ifnull(models.mfc.fechaing,models.mfc.fechamod))).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())
class MisCampanas(Resource):
    def get(self,flowid,versionid):
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
            query = db.session.query('id', 'idversion', 'nombre', 'nombreversion', 'fechainicio', 'fechafin', 'costo', 'costoplataforma','producto','descripcion')
            query = query.from_statement(text("""
                  select c.id,c.idversion,c.nombre,c.nombreversion,c.fechainicio, c.fechafin , sum(distinct d.costo) costo,product.nombre producto, c.descripcion,
                    (
                        select sum(da.Cost) from dailycampaing da
                        inner join Campaings ca on ca.CampaingID = da.CampaingID
                        inner join mfcgt.mfccompradiaria com on  ca.Campaingname = com.multiplestiposg
                        inner join mfcgt.mfccampana m on m.id = com.idcampana
                        where m.id = c.id
                    ) costoplataforma
                    from mfcgt.mfccampana c
                    inner join mfcgt.mfccompradiaria d on d.idcampana = c.id
                    inner join mfcgt.dproducto product on product.id = c.idproducto
                    where c.idmfc = {} and c.idversionmfc = {}
                    group by c.id;
                    """.format(flowid,versionid)))

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
            query = db.session.query('id', 'nombre', 'fecha_inicio_mfc', 'fecha_fin_mfc','costo_mfc', 'costo_pl','Plataforma','Version','Objetivo','Medio','odc','Presupuesto')
            query = query.from_statement(text("""
                  select cd.id, cd.multiplestiposg nombre, cd.multiplestiposa fecha_inicio_mfc,cd.multiplestiposb fecha_fin_mfc,
                    cd.costo costo_mfc,sum(da.Cost) costo_pl,PLATAFORMA.nombre as Plataforma,cd.multiplestiposd as Version,
					OBJETIVO.nombre as Objetivo, MEDIO.nombre Medio, cd.odc, cd.idpresupuesto Presupuesto
                    from mfcgt.mfccompradiaria cd
                    left join dailycampaing da on cd.id = da.CampaignIDMFC
                    INNER JOIN mfcgt.dformatodigital as FORMATO on FORMATO.id=cd.idformatodigital
					INNER JOIN mfcgt.danuncio as ANUNCIO on ANUNCIO.id=FORMATO.idanuncio
					INNER JOIN mfcgt.dmetrica as METRICA on METRICA.id=ANUNCIO.idmetrica
					INNER JOIN mfcgt.dobjetivo as OBJETIVO on OBJETIVO.id=METRICA.idobjetivo
					INNER JOIN mfcgt.dplataforma as PLATAFORMA on PLATAFORMA.id=OBJETIVO.idplataforma	
					INNER JOIN mfcgt.dsubmedio as SUBMEDIO on SUBMEDIO.id=PLATAFORMA.idsubmedio
					INNER JOIN mfcgt.dmedio as MEDIO on MEDIO.id=SUBMEDIO.idmedio
					INNER JOIN mfcgt.dtipomedio as TIPOMEDIO on TIPOMEDIO.id=MEDIO.idtipomedio
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

class PutLineaImplementacion(Resource):
    def put(self,idLinea,ODC,Presupuesto):
        try:
            a = models.mfccompradiaria.query.filter(models.mfccompradiaria.id==idLinea).first()
            a.odc = ODC
            a.idpresupuesto = Presupuesto
            db.session.commit()
            return 'ODC y Presupuesto Actualizado exitosamente', 201
        except Exception as e:
            print(e)
            return 'No se realizo la Actualizacion', 400
        finally:
            db.session.close()
            


class GetResults_Campaings(Resource):
    @jwt_required
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

class GetLocalMedia(Resource):
    @jwt_required
    def get(self):
        try:
            lm = LocalMediaReportsSchema()
            lm = LocalMediaReportsSchema(many=True)
            data = db.session.query(LocalMedia).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())     


class PostLocalMedia(Resource):
    #@jwt_required
    def post(self,usuario_id):
        try:
            content = request.json
            for result in content:
                if result == '0':
                    continue
                else:
                    #print(len(content[result]))
                    if len(content[result]) > 0:
                        old = models.LocalMediaReports.query.filter(LocalMediaReports.IDMFC==int(content[result][0]),
                        LocalMediaReports.ReportDate == int(content[result][3]), LocalMediaReports.State != 3 ).first()
                        if old == None:
                            idmfc = content[result][0]
                            odc = content[result][1]
                            orden = content[result][2]
                            reportdate = content[result][3]
                            adname = str(content[result][8])
                            unicost = content[result][9]                    
                            impressions = content[result][10]
                            clicks = content[result][11]
                            reach = content[result][12]
                            videowachestat75 = content[result][13]
                            listens = content[result][14]
                            conversions = content[result][15]
                            ctr = content[result][16]
                            landingpageviews = content[result][17]
                            uniqueviews = content[result][18]
                            timeonpage = content[result][19]
                            follows = content[result][20]
                            navigation = content[result][21]
                            tamano =  len(content[result])
                            print(tamano)
                            if tamano < 22:
                                sendmessage = content[result][23]
                                openmessage = content[result][24]
                            else:
                                sendmessage = 0
                                openmessage = 0
                            createduser =  int(usuario_id)

                            a = LocalMediaReports(adname,idmfc,reportdate,unicost,odc,orden,None,reach,impressions,clicks,
                            videowachestat75,listens,conversions,ctr,landingpageviews,uniqueviews,timeonpage,None,
                            follows,navigation,sendmessage,openmessage,createduser)
                            db.session.add(a)
                        else:
                            mensaje = 'Campaña: ' + str(content[result][0]) + ' ya fue cargada en la semana:' + str(content[result][3])
                            return mensaje, 200    
                    else:
                        continue
                    
            db.session.commit()
            return 'Formulario ingresado correctamente',201
        except Exception as e:
            print(e)
        finally:
            db.session.close()
    def put(self):
        try:
            content = request.json
            id = content['id']
            a = LocalMediaReports.query.filter(LocalMediaReports.ID==id).first()
            a.ADName = content['ADName']
            a.ReportDate = content['ReportDate']
            a.UniCost = content['UnitCost']
            a.ODC = content['ODC']
            a.Orden = content['Orden']
            a.BudgetUsed = content['BudgetUsed']
            a.Reach = content['Reach']
            a.Impressions = content['Impressions']
            a.Clicks = content['Clicks']
            a.Videowachestat75 = content['Videowachesat75']
            a.Listens = content['Listens']
            a.Conversions = content['Conversions']
            a.CTR = content['CTR']
            a.Landingpageviews = content['Landingpageviews']
            a.Uniqueviews = content['UniqueViews']
            a.TimeOnPage = content['TimeOnPage']
            a.TypePublication = content['TypePublication']
            a.Follows = content['Follows']
            a.Navigation = content['Navigation']
            
            a.UpdatedUser = content['CreatedUser']
            db.session.commit()
            return 'Medio local actualizado correctamente Correctamente', 201
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class GetLocalMedia(Resource):
    @jwt_required
    def get(self,id):
        try:
            content = request.json
            lm = LocalMediaReportsSchema()
            lm = LocalMediaReportsSchema(many=True)
            data = db.session.query(LocalMediaReports).filter(LocalMediaReports.ID==id).all()
            result = lm.dump(data)
            result = jsonify(result)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close() 
class CambioLocalMedia(Resource):
    @jwt_required
    def post(self,id,estado,idusuario):
        try:
            
            a = models.LocalMediaReports.query.filter(models.LocalMediaReports.ID==id).first()
            a.State = estado
            a.UpdatedUser = idusuario
            if estado == '3':
                usuario_correo = models.UsuarioOmgGT.query.filter(models.UsuarioOmgGT.id == a.CreatedUser).first()
                compra_diaria = models.mfccompradiaria.query.filter(models.mfccompradiaria.id == a.IDMFC).first()
                content = request.json
                a.Description = content['Description']
                msg = Message( 
                                'Hola ' + usuario_correo.nombre, 
                                sender ='support@wolvisor.com', 
                                recipients = [usuario_correo.email] 
                            ) 
                msg.body = 'La campaña: ' 
                #mail.send(msg) 
            db.session.commit()
            return 'Medio local actualizado correctamente Correctamente', 201
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class GetLocalMediaxMarca(Resource):
    @jwt_required
    def get(self,idmarca):
        try:
            cshema = LocalMediaReportsSchema()
            cshema = LocalMediaReportsSchema(many=True)
            
            query = db.session.query('ID','Nombre Anuncio','Orden','ReportDate','Nombre Campaña','UnitCost','State')
            query = query.from_statement(text("""
            select distinct LOCALM.ID, LOCALM.ADName 'Nombre Anuncio',CAMPANA.nombre 'Nombre Campaña' ,
            LOCALM.Orden,date_format(LOCALM.ReportDate,'%M-%d') ReportDate,LOCALM.ADName,LOCALM.UnitCost,LOCALM.State 
            from MediaPlatformsReports.LocalMedia LOCALM
            inner JOIN mfcgt.mfccompradiaria as IMPLEMENTACIONES on LOCALM.IDMFC=IMPLEMENTACIONES.id
            INNER JOIN mfcgt.mfccampana as CAMPANA on CAMPANA.id=IMPLEMENTACIONES.idcampana and CAMPANA.idversion=IMPLEMENTACIONES.idversion
            INNER JOIN mfcgt.mfc as FLOW on FLOW.id=CAMPANA.idmfc and FLOW.idversion=CAMPANA.idversionmfc
            INNER JOIN mfcgt.dmarca as MARCA on MARCA.id=FLOW.idmarca
            WHERE MARCA.id = {};
            """.format(idmarca)))
            result = cshema.dump(query)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class GetLocalMediaxUsuario(Resource):
    #@jwt_required
    def get(self,idusuario):
        try:
            result = None
            user = UsuarioOmgGT.query.filter(UsuarioOmgGT.id==idusuario).first()
            if user.idpuesto == 1029:
                cshema = LocalMediaReportsSchema()
                cshema = LocalMediaReportsSchema(many=True)
                
                query = db.session.query('ID','IDMFC','Presupuesto','Nombre Anuncio','Orden','ReportDate','Nombre Campaña','UnitCost','State','Medio','Objetivo','Marca')
                query = query.from_statement(text("""
                select distinct LOCALM.ID,IMPLEMENTACIONES.ID IDMFC,LOCALM.ODC 'Orden' , LOCALM.ADName 'Nombre Anuncio',
                CLIENTE.nombre Medio,MARCA.nombre Marca,OBJETIVO.nombre Objetivo,CAMPANA.nombre 'Nombre Campaña' ,LOCALM.Orden 'Presupuesto'
                ,STR_TO_DATE(CONCAT('2021',LOCALM.ReportDate,' MONDAY'), '%X%V %W') ReportDate
                ,LOCALM.ADName,LOCALM.UnitCost,LOCALM.State 
                from MediaPlatformsReports.LocalMedia LOCALM
                inner JOIN mfcgt.mfccompradiaria as IMPLEMENTACIONES on LOCALM.IDMFC=IMPLEMENTACIONES.id
                INNER JOIN mfcgt.mfccampana as CAMPANA on CAMPANA.id=IMPLEMENTACIONES.idcampana and CAMPANA.idversion=IMPLEMENTACIONES.idversion
                INNER JOIN mfcgt.mfc as FLOW on FLOW.id=CAMPANA.idmfc and FLOW.idversion=CAMPANA.idversionmfc
                INNER JOIN mfcgt.dmarca as MARCA on MARCA.id=FLOW.idmarca
                INNER JOIN mfcgt.dcliente as CLIENTE on CLIENTE.id=MARCA.idcliente
                INNER JOIN mfcgt.dformatodigital as FORMATO on FORMATO.id=IMPLEMENTACIONES.idformatodigital
                INNER JOIN mfcgt.danuncio as ANUNCIO on ANUNCIO.id=FORMATO.idanuncio
                INNER JOIN mfcgt.dmetrica as METRICA on METRICA.id=ANUNCIO.idmetrica
                INNER JOIN mfcgt.dobjetivo as OBJETIVO on OBJETIVO.id=METRICA.idobjetivo
                INNER JOIN mfcgt.dplataforma as PLATAFORMA on PLATAFORMA.id=OBJETIVO.idplataforma
                
                order by CreatedDate desc
                limit 200;
                """))
                result = cshema.dump(query)
            else:
                cshema = LocalMediaReportsSchema()
                cshema = LocalMediaReportsSchema(many=True)
                
                query = db.session.query('ID','IDMFC','Presupuesto','Nombre Anuncio','Orden','ReportDate','Nombre Campaña','UnitCost','State','Medio','Objetivo','Marca','CampanaId','FlowId')
                query = query.from_statement(text("""
                select distinct LOCALM.ID,IMPLEMENTACIONES.ID IDMFC,LOCALM.ODC 'Orden' , LOCALM.ADName 'Nombre Anuncio',
                CLIENTE.nombre Medio,MARCA.nombre Marca,OBJETIVO.nombre Objetivo,CAMPANA.nombre 'Nombre Campaña' ,LOCALM.Orden 'Presupuesto'
                ,STR_TO_DATE(CONCAT('2021',LOCALM.ReportDate,' MONDAY'), '%X%V %W') ReportDate
                ,LOCALM.ADName,LOCALM.UnitCost,LOCALM.State, CAMPANA.id CampanaId, FLOW.id FlowId
                from MediaPlatformsReports.LocalMedia LOCALM
                inner JOIN mfcgt.mfccompradiaria as IMPLEMENTACIONES on LOCALM.IDMFC=IMPLEMENTACIONES.id
                INNER JOIN mfcgt.mfccampana as CAMPANA on CAMPANA.id=IMPLEMENTACIONES.idcampana and CAMPANA.idversion=IMPLEMENTACIONES.idversion
                INNER JOIN mfcgt.mfc as FLOW on FLOW.id=CAMPANA.idmfc and FLOW.idversion=CAMPANA.idversionmfc
                INNER JOIN mfcgt.dmarca as MARCA on MARCA.id=FLOW.idmarca
                INNER JOIN mfcgt.dcliente as CLIENTE on CLIENTE.id=MARCA.idcliente
                INNER JOIN mfcgt.dformatodigital as FORMATO on FORMATO.id=IMPLEMENTACIONES.idformatodigital
                INNER JOIN mfcgt.danuncio as ANUNCIO on ANUNCIO.id=FORMATO.idanuncio
                INNER JOIN mfcgt.dmetrica as METRICA on METRICA.id=ANUNCIO.idmetrica
                INNER JOIN mfcgt.dobjetivo as OBJETIVO on OBJETIVO.id=METRICA.idobjetivo
                INNER JOIN mfcgt.dplataforma as PLATAFORMA on PLATAFORMA.id=OBJETIVO.idplataforma
                order by CreatedDate desc
                limit 100;
                """))
                result = cshema.dump(query)
            
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())

class GetLocalMediaCount(Resource):
    #@jwt_required
    def get(self,idusuario):
        try:
            cshema = LocalMediaReportsCountSchema()
            cshema = LocalMediaReportsCountSchema(many=True)
            
            query = db.session.query('Por Revisar','Aprobados','Rechazados')
            query = query.from_statement(text("""
            select 
                (select distinct count(LOCALM.ID) 
                        from MediaPlatformsReports.LocalMedia LOCALM
						inner JOIN mfcgt.mfccompradiaria as IMPLEMENTACIONES on LOCALM.IDMFC=IMPLEMENTACIONES.id
						INNER JOIN mfcgt.mfccampana as CAMPANA on CAMPANA.id=IMPLEMENTACIONES.idcampana and CAMPANA.idversion=IMPLEMENTACIONES.idversion
						INNER JOIN mfcgt.mfc as FLOW on FLOW.id=CAMPANA.idmfc and FLOW.idversion=CAMPANA.idversionmfc
						INNER JOIN mfcgt.dmarca as MARCA on MARCA.id=FLOW.idmarca
						INNER JOIN mfcgt.dcliente as CLIENTE on CLIENTE.id=MARCA.idcliente
						INNER JOIN mfcgt.dformatodigital as FORMATO on FORMATO.id=IMPLEMENTACIONES.idformatodigital
						INNER JOIN mfcgt.danuncio as ANUNCIO on ANUNCIO.id=FORMATO.idanuncio
						INNER JOIN mfcgt.dmetrica as METRICA on METRICA.id=ANUNCIO.idmetrica
						INNER JOIN mfcgt.dobjetivo as OBJETIVO on OBJETIVO.id=METRICA.idobjetivo
						INNER JOIN mfcgt.dplataforma as PLATAFORMA on PLATAFORMA.id=OBJETIVO.idplataforma
						INNER JOIN mfcgt.mfcasignacionmedio as ASIGNACION on ASIGNACION.idsubmedio = PLATAFORMA.idsubmedio
                        WHERE ASIGNACION.idusuario = {} and State = 1
                    ) as 'Por Revisar',
                (select distinct count(LOCALM.ID) 
                        from MediaPlatformsReports.LocalMedia LOCALM
						inner JOIN mfcgt.mfccompradiaria as IMPLEMENTACIONES on LOCALM.IDMFC=IMPLEMENTACIONES.id
						INNER JOIN mfcgt.mfccampana as CAMPANA on CAMPANA.id=IMPLEMENTACIONES.idcampana and CAMPANA.idversion=IMPLEMENTACIONES.idversion
						INNER JOIN mfcgt.mfc as FLOW on FLOW.id=CAMPANA.idmfc and FLOW.idversion=CAMPANA.idversionmfc
						INNER JOIN mfcgt.dmarca as MARCA on MARCA.id=FLOW.idmarca
						INNER JOIN mfcgt.dcliente as CLIENTE on CLIENTE.id=MARCA.idcliente
						INNER JOIN mfcgt.dformatodigital as FORMATO on FORMATO.id=IMPLEMENTACIONES.idformatodigital
						INNER JOIN mfcgt.danuncio as ANUNCIO on ANUNCIO.id=FORMATO.idanuncio
						INNER JOIN mfcgt.dmetrica as METRICA on METRICA.id=ANUNCIO.idmetrica
						INNER JOIN mfcgt.dobjetivo as OBJETIVO on OBJETIVO.id=METRICA.idobjetivo
						INNER JOIN mfcgt.dplataforma as PLATAFORMA on PLATAFORMA.id=OBJETIVO.idplataforma
						INNER JOIN mfcgt.mfcasignacionmedio as ASIGNACION on ASIGNACION.idsubmedio = PLATAFORMA.idsubmedio
                        WHERE ASIGNACION.idusuario = {} and State = 2
                    ) as 'Aprobados',
                    (select distinct count(LOCALM.ID) 
                        from MediaPlatformsReports.LocalMedia LOCALM
						inner JOIN mfcgt.mfccompradiaria as IMPLEMENTACIONES on LOCALM.IDMFC=IMPLEMENTACIONES.id
						INNER JOIN mfcgt.mfccampana as CAMPANA on CAMPANA.id=IMPLEMENTACIONES.idcampana and CAMPANA.idversion=IMPLEMENTACIONES.idversion
						INNER JOIN mfcgt.mfc as FLOW on FLOW.id=CAMPANA.idmfc and FLOW.idversion=CAMPANA.idversionmfc
						INNER JOIN mfcgt.dmarca as MARCA on MARCA.id=FLOW.idmarca
						INNER JOIN mfcgt.dcliente as CLIENTE on CLIENTE.id=MARCA.idcliente
						INNER JOIN mfcgt.dformatodigital as FORMATO on FORMATO.id=IMPLEMENTACIONES.idformatodigital
						INNER JOIN mfcgt.danuncio as ANUNCIO on ANUNCIO.id=FORMATO.idanuncio
						INNER JOIN mfcgt.dmetrica as METRICA on METRICA.id=ANUNCIO.idmetrica
						INNER JOIN mfcgt.dobjetivo as OBJETIVO on OBJETIVO.id=METRICA.idobjetivo
						INNER JOIN mfcgt.dplataforma as PLATAFORMA on PLATAFORMA.id=OBJETIVO.idplataforma
						INNER JOIN mfcgt.mfcasignacionmedio as ASIGNACION on ASIGNACION.idsubmedio = PLATAFORMA.idsubmedio
                        WHERE ASIGNACION.idusuario = {} and State = 3
                    ) as 'Rechazados'
            from MediaPlatformsReports.LocalMedia LOCALM limit 1;
            """.format(idusuario,idusuario,idusuario)))
            result = cshema.dump(query)
            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())              

class GetPuesto(Resource):
    @jwt_required
    def get(self,idusuario):
        try:
            user = UsuarioOmgGT.query.filter(UsuarioOmgGT.id==idusuario).first()
            if user.idpuesto == 1029:
                return False
            else:
                return True
        except Exception as e:
            print(e)
        finally:
            db.session.close() 

class PostCSV(Resource):
    def post(self):
        if 'file' not in request.files:
            return 'No esta el archvio Archvio',500
        else:
            data = request.files['errores.csv']
        print('hola')
        return 'Archvio',201


class Visistas(Resource):
    def get(self,IP):
        hoy = datetime.now().strftime("%Y-%m-%d")
        if Visitias_Sitio.query.filter(Visitias_Sitio.IP == IP, Visitias_Sitio.date > hoy ).count() > 0:
            valor = random.randrange(2,4)
            return {'ganador': False,'mensaje':valor},201
        else:
            nueva_visita = Visitias_Sitio(IP,datetime.now())
            db.session.add(nueva_visita)
            db.session.commit()
            contador = Visitias_Sitio.query.filter(Visitias_Sitio.date > hoy).count()
            if contador == 5 or contador == 10 or contador == 15 or contador == 20 or contador == 25 or contador == 30 or contador == 35 or contador == 40 or contador == 45 or contador == 50:
                return {'ganador': True,'mensaje':1},201
            else:
                valor = random.randrange(2,4)
                return {'ganador': False, 'mensaje':valor},201        
        return {'ganador': False},201
    def post(self,IP):
        try:
            content = request.json
            user_old = usuarios_promocion_Sitio.query.filter((usuarios_promocion_Sitio.CUI == content['CUI']) |
             (usuarios_promocion_Sitio.Email == content['Email'])).first()
            if user_old is not None:
                return {'result': 'error'},201
            user = usuarios_promocion_Sitio(content['Nombre'],content['Apellido'],
            content['CUI'],content['Email'],content['Direccion'],content['telefono'],datetime.now())
            db.session.add(user)
            db.session.commit()
            return {'result': 'success'},201
        except Exception as e:
            return {'result': 'error'},401

class Visistas_post(Resource):
    def post(self,IP,Tipo):
        try:
            content = request.json
            if Tipo == 'normal':
                user_old = usuarios_promocion_Sitio.query.filter((usuarios_promocion_Sitio.CUI == content['CUI']) |
                (usuarios_promocion_Sitio.Email == content['Email'])).first()
                if user_old is not None:
                    return {'result': 'error'},201
                user = usuarios_promocion_Sitio(content['Nombre'],content['Apellido'],
                content['CUI'],content['Email'],content['Direccion'],content['telefono'],datetime.now())
                db.session.add(user)
                db.session.commit()
            elif Tipo == 'camisas':
                user_old = usuarios_promocion_barca_Sitio.query.filter((usuarios_promocion_barca_Sitio.CUI == content['CUI']) |
                (usuarios_promocion_Sitio.Email == content['Email'])).first()
                if user_old is not None:
                    return {'result': 'error'},201
                user = usuarios_promocion_barca_Sitio(content['Nombre'],content['Apellido'],
                content['CUI'],content['Email'],content['Direccion'],content['telefono'],datetime.now())
                db.session.add(user)
                db.session.commit()
            return {'result': 'success'},201
        except Exception as e:
            return {'result': 'error'},401
        
class Correos(Resource):
    def post(self):
        try:
            content = request.json
            msg = Message( 

                'Certificado Parrilleros Victoria ' , 
                sender ='support@wolvisor.com', 
                recipients = [content['email']] 
            ) 
            msg.html = """
                <b>Felicidades {}</b>
                <img src="https://drive.google.com/uc?export=view&id=1hYEOxm4mplhNu5zepKdLv609lczITGno" alt="Parrilleros"> 
            """.format(content['name'])
            msg.attach = content['certificate'] 
            mail.send(msg)
            return {'error': False},201
        except Exception as e:
            return {'result': True},200


class Preguntas_barca(Resource):
    #@jwt_required
    def post(self,IP):
        try:
            hoy = datetime.now().strftime("%Y-%m-%d")
            if Visitias_Sitio.query.filter(Visitias_Sitio.IP == IP, Visitias_Sitio.date > hoy ).count() > 0:
    
                return {'result': 'ip no valida'},201
            else:
                nueva_visita = Visitias_Sitio(IP,datetime.now())
                #db.session.add(nueva_visita)
                #db.session.commit()
                content = request.json
                randdash = np.random.choice(range(1,9), 5, replace=False)
                json_preguntas = []
                for i,x in enumerate(randdash):
                    if x == 1:
                        pregunta = {
                            'Pregunta': str(i+1) + '.¿En qué año se fundó el FC Barcelona?',
                            'respuesta1':'1809',
                            'respuesta2':'1899',
                            'respuesta3':'1918',
                            'respuesta4':'1900',
                        }
                    elif x == 2:
                        pregunta = {
                            'Pregunta': str(i+1) + '.¿Con qué entrenador ganó el FC Barcelona su primera copa de Europa?',
                            'respuesta1':'Josep Guardiala',
                            'respuesta2':'Frank Rijkaard',
                            'respuesta3':'Johan Cruyff',
                            'respuesta4':'Louis Van Gaal',
                        }
                    elif x == 3:
                        pregunta = {
                            'Pregunta': str(i+1) + '.¿Cuál era el dorsal del legendario J Cruyff?',
                            'respuesta1':'14',
                            'respuesta2':'20',
                            'respuesta3':'10',
                            'respuesta4':'19',
                        }
                    elif x == 4:
                        pregunta = {
                            'Pregunta': str(i+1) + '.¿En el 2021 que cambió de Victoria Frost?',
                            'respuesta1':'Su sabor',
                            'respuesta2':'Su presentación',
                            'respuesta3':'Su microfiltrado en frío',
                            'respuesta4':'Todo lo anterior',
                        }
                    elif x == 5:
                        pregunta = {
                            'Pregunta': str(i+1) + '.¿Cuál es la capacidad del Campo Nou?',
                            'respuesta1':'99,354 Personas',
                            'respuesta2':'89,106 Personas',
                            'respuesta3':'105,000 Personas',
                            'respuesta4':'94,565 Personas',
                        }
                    elif x == 6:
                        pregunta = {
                            'Pregunta': str(i+1) + '.¿Cuántas Copas del Rey ha ganado el FCB?',
                            'respuesta1':'31',
                            'respuesta2':'24',
                            'respuesta3':'27',
                            'respuesta4':'22',
                        }
                    elif x == 7:
                        pregunta = {
                            'Pregunta': str(i+1) + '.¿Quién es el máximo goleador de la historia del FCB?',
                            'respuesta1':'Leo Messi',
                            'respuesta2':"Samuel Eto'o",
                            'respuesta3':'César Rodriguez',
                            'respuesta4':'J. Cruyff',
                        }
                    elif x == 8:
                        pregunta = {
                            'Pregunta': str(i+1) + '.¿Cuál es el premio de calidad internacional que ganó Victoria Frost?',
                            'respuesta1':'Monde Selection Gran Oro',
                            'respuesta2':'Monde Selection Silver',
                            'respuesta3':'Monde Selection Cobre',
                            'respuesta4':'Monde Selection Oro',
                        }
                    elif x == 9:
                        pregunta = {
                            'Pregunta': str(i+1) + '.¿La Nueva Fórmula de Victoria Frost tiene?',
                            'respuesta1':'Más color',
                            'respuesta2':'Más espuma',
                            'respuesta3':'Más olor',
                            'respuesta4':'Más sabor, más refrescante',
                        }
                    json_preguntas.append(pregunta)
                
                return json_preguntas,200
        except Exception as e:
            return {'result': True},200

class RespuestasPreguntas_barca(Resource):
    #@jwt_required
    def post(self):
        try:
            content = request.json
            if len(content) < 5:
                return {'ganador': False},200
            for result in content:
                result_sp = result['pregunta'].split('.',2)
                if result_sp[1] == '¿En qué año se fundó el FC Barcelona?':
                    if result['respuesta'] != '1899':
                        return {'ganador': False},200
                elif result_sp[1] == '¿Con qué entrenador ganó el FC Barcelona su primera copa de Europa?':
                    if result['respuesta'] != 'Johan Cruyff':
                        return {'ganador': False},200
                elif result_sp[1] == '¿Cuál era el dorsal del legendario J Cruyff?':
                    if result['respuesta'] != '14':
                        return {'ganador': False},200
                elif result_sp[1] == '¿En qué año se lanzó al mercado Victoria Frost?':
                    if result['respuesta'] != '2008':
                        return {'ganador': False},200
                elif result_sp[1] == '¿En el 2021 que cambió de Victoria Frost?':
                    if result['respuesta'] != 'Todo lo anterior':
                        return {'ganador': False},200
                elif result_sp[1] == '¿Cuál es la capacidad del Campo Nou?':
                    if result['respuesta'] != '99,354 Personas':
                        return {'ganador': False},200
                elif result_sp[1] == '¿Cuántas Copas del Rey ha ganado el FCB?':
                    if result['respuesta'] != '31':
                        return {'ganador': False},200
                elif result_sp[1] == '¿Quién es el máximo goleador de la historia del FCB?':
                    if result['respuesta'] != 'Leo Messi':
                        return {'ganador': False},200
                elif result_sp[1] == '¿Cuál es el premio de calidad internacional que ganó Victoria Frost?':
                    if result['respuesta'] != 'Monde Selection Silver':
                        return {'ganador': False},200
                elif result_sp[1] == '¿La Nueva Fórmula de Victoria Frost tiene?':
                    if result['respuesta'] != 'Más sabor, más refrescante':
                        return {'ganador': False},200
                else:
                    return {'ganador': False},200
            return {'ganador': True},200
        except Exception as e:
            return {'error': True},200

        

class PostTonaLight(Resource):
    def post(self):
        try:
            content = request.json
            user_old = usuarios_promocion_tonalight.query.filter((usuarios_promocion_tonalight.CUI == content['CUI']) |
             (usuarios_promocion_tonalight.Email == content['Email'])).first()
            if user_old is not None:
                return {'result': 'error'},201
            codigo = ''.join(random.choice('0123456789ABCDEF') for i in range(7))
            user = usuarios_promocion_tonalight(content['Nombre'],content['Apellido'],
            content['CUI'],content['Email'],content['telefono'],codigo,datetime.now(),0)
            db.session.add(user)
            db.session.commit()
            content = request.json
            msg = Message( 

                'Tona Light' , 
                sender ='Cerveza Tona', 
                recipients = [content['Email']] 
            ) 
            msg.html = """
                <img src="https://cervezatona.com/assets/img/To%C3%B1a-header.png" alt="tona" width="500" height="600">
                <br>
                <h3 sytle="color:black">
                <b>Felicidades {}</b> Te has ganado 2 cervezas Toña Light para probar <br> el nuevo sabor de Nicaragua <br> </h3>
                <h2>Código: {} </h2><br> 
                <h4>

                Puedes canjear tu premio en cualquier SuperExpress y AMPM. <br>
                Recuerda llevar tus 2 botellas retornables vacías para canjear tu premio.<br>
                Fecha de caducidad 30/12/2021. <br> 
                Si tienes un problema con tu canje, comunícate al correo: sac@ccn.com.ni.
                </h4>
                <img src="https://cervezatona.com/assets/img/To%C3%B1a-footer.png" alt="tona" width="500" >
            """.format(content['Nombre'],codigo)
            mail.send(msg)
            return {'codigo': codigo},201
        except Exception as e:
            return {'result': 'error'},401
    def put(self):
        try:
            content = request.json
            a = usuarios_promocion_tonalight.query.filter(usuarios_promocion_tonalight.codigo==content["CODIGO"],
            usuarios_promocion_tonalight.CUI==content['CUI']).first()
            if a == None:
                return { 'success':False,'result': 'Codigo no existe'},201
            if a.state == 1:
                return {'success':False,'result': 'Codigo ya Canjeado'},201
            a.tienda = content['TIENDA']
            a.date_premio = datetime.now()
            a.state = 1
            db.session.commit()
            return {'success':True, 'result':'Codigo Canjeado Exitosamente'}, 201
        except Exception as e:
            print(e)
            return 'Error al canjear el codigo', 400
        finally:
            db.session.close()
            pass            
### Mis Flows
##
## Se tiene que agregar cada ruta a la aplicacion, ruta -> class
##

#Bitacora
api.add_resource(PostCSV, '/archvio')
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
api.add_resource(MisFLowsAprobadosPorUsuario, '/FlowsUsuario/<string:idusuario>')
api.add_resource(MisCampanas, '/Flows/Campana/<string:flowid>&<string:versionid>')
api.add_resource(MisLineasImplementadas, '/Flows/LineaImp/<string:campanaid>')
api.add_resource(PutLineaImplementacion, '/Flows/LineaImp/<string:idLinea>&<string:ODC>&<string:Presupuesto>')
api.add_resource(GetResults_Campaings, '/Reports/<string:idMarca>')
api.add_resource(PostLocalMedia, '/Reports/LocalMedia/<string:usuario_id>')
api.add_resource(GetLocalMedia, '/Reports/LocalMedia/<string:id>')
api.add_resource(GetPuesto, '/Reports/TipoUsuario/<string:idusuario>')
api.add_resource(GetLocalMediaxMarca, '/Reports/LocalMediaxMarca/<string:idmarca>')
api.add_resource(GetLocalMediaxUsuario, '/Reports/LocalMediaxUsuario/<string:idusuario>')
api.add_resource(GetLocalMediaCount, '/Reports/LocalMediaCount/<string:idusuario>')
api.add_resource(CambioLocalMedia, '/Reports/LocalMediaState/<string:id>&<string:estado>&<string:idusuario>')
#Actualizacion Datos
api.add_resource(Actualizacion_Datos.GetMetricsCampaing, '/DatosReportes/<string:IDMFC>&<string:Mes>')
api.add_resource(Actualizacion_Datos.UpdateMetricsCamps, '/DatosReportes/')
#Promocion Victoria Frost
api.add_resource(Visistas, '/api/Frost/promocion/<string:IP>')
api.add_resource(Visistas_post, '/api/Frost/promocion/<string:IP>&<string:Tipo>')
api.add_resource(Preguntas_barca, '/api/Frost/preguntas/<string:IP>')
api.add_resource(RespuestasPreguntas_barca, '/api/Frost/preguntas/2')
api.add_resource(Correos, '/email')
api.add_resource(PostTonaLight, '/api/tonalight')
#Promocion Vicorita Clasica Día del

if __name__ == '__main__':
    JWTManager(app)
    app.run(debug=True,port=5050)