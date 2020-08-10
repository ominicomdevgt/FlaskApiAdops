from flask import Flask, request
import models
import sys
from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy,time
from flask_marshmallow import Marshmallow
from datetime import datetime, timedelta
from app import app, db
from sqlalchemy.sql import func,text, desc
from models import rCampaingMetrics
class GetMetricsCampaing(Resource):
    #@jwt_required
    def get(self,IDMFC,Mes):
        try:
            cshema = models.rCampaingMetricsSchema()
            cshema = models.rCampaingMetricsSchema(many=True)
            query = db.session.query('Cliente','Marca', 'MFC', 'ID Campaña', 'Campaña', 'Fecha Inicio', 'Fecha Fin','Objetivo','ID Nomenclatura',
            'Nomenclatura', 'Medio','Inversion Planificada', 'KPI Planificado', 'Costo','Alcance','Frecuencia','Impresiones','Clicks','Video 75', 'Conversiones',
            'Descargas', 'KPI', 'id', 'Engagements')
            query = query.from_statement(text("""
            SELECT distinct CLIENTE.nombre Cliente, MARCA.nombre Marca, METRICAS.CampaignIDMFC MFC, CAMPANA.id 'ID Campaña', CAMPANA.nombre 'Campaña', 
						date_format(ifnull( CAMP.StartDate,str_to_date(IMPLEMENTACIONES.multiplestiposa,'%m/%d/%Y')),'%d/%m/%Y') 'Fecha Inicio',
                        date_format(str_to_date(IMPLEMENTACIONES.multiplestiposb,'%m/%d/%Y'),'%d/%m/%Y') 'Fecha Fin',
                        OBJETIVO.nombre Objetivo, IMPLEMENTACIONES.id 'ID Nomenclatura', CAMP.Campaingname Nomenclatura, PLATAFORMA.Nombre Medio,
                        ifnull(IMPLEMENTACIONES.costo,ifnull(IMPLEMENTACIONES.multiplescostosb,IMPLEMENTACIONES.bonificacion))  'Inversion Planificada',
                        SUBSTRING_INDEX (SUBSTRING_INDEX(CAMP.Campaingname, '_', 14),'_',-1) 'KPI Planificado',
                        METRICAS.Cost Costo, METRICAS.Reach Alcance, METRICAS.Frequency Frecuencia , METRICAS.Impressions Impresiones, METRICAS.Clicks,
                        METRICAS.Videowachesat75 'Video 75', METRICAS.Conversions Conversiones, METRICAS.AppInstalls Descargas, METRICAS.Result KPI, METRICAS.id, METRICAS.Postengagements Engagements
						from MediaPlatformsReports.CampaingMetrics METRICAS
						INNER JOIN MediaPlatformsReports.Campaings CAMP ON CAMP.CampaingID = METRICAS.CampaingID
						LEFT JOIN MediaPlatformsReports.Accounts ACCOUNTS on CAMP.AccountsID = ACCOUNTS.AccountsID
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
                        INNER JOIN mfcgt.dplataforma as PLATAFORMA on PLATAFORMA.id=OBJETIVO.idplataforma                      
                        WHERE METRICAS.CampaignIDMFC = {} and METRICAS.Week = {};""".format(IDMFC,Mes)))
            result = cshema.dump(query)


            return result
        except Exception as e:
            print(e)
        finally:
            db.session.close()
            print(datetime.now())


class UpdateMetricsCamps(Resource):
    def put(self):
        try:
            json_data = request.get_json(force=True)
            Cost = json_data['Cost']
            Reach = json_data['Reach']
            Postengagements = json_data['Postengagements']
            AppInstalls = json_data['AppInstalls']
            Clicks = json_data['Clicks']
            Impressions = json_data['Impressions']
            Frequency = json_data['Frequency']
            Conversions = json_data['Conversions']
            Videowachesat75 = json_data['Videowachesat75']
            id = json_data['id']
            user_mod = json_data['user']
            objetive = json_data['Objetivo']
            Metric = rCampaingMetrics.query.filter(rCampaingMetrics.id==id).first()
            Metric.Cost = Cost
            Metric.Reach = Reach
            Metric.Clicks = Clicks
            Metric.Postengagements = Postengagements
            Metric.AppInstalls = AppInstalls
            Metric.Impressions = Impressions
            Metric.Frequency = Frequency
            Metric.Conversions = Conversions
            Metric.Videowachesat75 = Videowachesat75
            Metric.UserMod = user_mod
            Metric.UpdateDate = datetime.now()
            if objetive == 'TRAFICO':
                Metric.Result = Clicks
            elif objetive == 'ALCANCE':
                Metric.Result = Reach
            elif objetive == 'AWARENESS':
                Metric.Result = Impressions
            elif objetive == 'DESCARGA':
                Metric.Result = AppInstalls
            elif objetive == 'INTERACCION':
                Metric.Result = Postengagements
            elif objetive == 'REPRODUCCION':
                Metric.Result = Videowachesat75
            elif objetive == 'CONVERSION':
                Metric.Result = Conversions    
            db.session.commit()
            return 'Account Ingresado Correctamente', 201
        except Exception as e:
            print(e)
            return 'Account no Ingresada', 400
        finally:
            db.session.close()
            print(datetime.now())