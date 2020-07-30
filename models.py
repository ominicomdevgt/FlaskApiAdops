from app import db, ma


class Bitacora(db.Model):
    __tablename__ = 'bitacora'
    bitacoraID = db.Column(db.Integer, primary_key=True)
    Operacion = db.Column(db.String, unique=True, nullable=False)
    Resultado = db.Column(db.String, unique=True, nullable=False)
    Documento = db.Column(db.String, unique=True, nullable=False)
    CreateDate = db.Column(db.DateTime, unique=True, nullable=False)



class BitacoraSchema(ma.ModelSchema):
    class Meta:
        fields = ('bitacoraID', 'Operacion',
                  'Resultado', 'Documento', 'CreateDate')


class Accounts(db.Model):
    __tablename__ = 'Accounts'
    # Field name made lowercase.
    AccountsID = db.Column(db.String, primary_key=True)
    Account = db.Column(db.String, unique=True, nullable=False)
    Media = db.Column(db.String, unique=True, nullable=False)
    CreateDate = db.Column(db.DateTime, unique=True, nullable=False)
    Country = db.Column(db.String,  nullable=True)
    State = db.Column(db.Integer, nullable=False)

    def __init__(self, AccountsID, Account, Media, Country):
        self.AccountsID = AccountsID
        self.Account = Account
        self.Media = Media
        self.Country = Country


class AccountsSchema(ma.ModelSchema):
    class Meta:
        fields = ('AccountsID', 'Account', 'Media', 'CreateDate', 'Country')


class Dcliente(db.Model):
    __table_args__ = {'schema': 'mfcgt'}
    __tablename__ = 'dcliente'
    id = db.Column(db.Integer, primary_key=True)  # Field name made lowercase.
    nombre = db.Column(db.String, unique=True)
    abreviatura = db.Column(db.String, unique=True)
    idagencia = db.Column(db.Integer, unique=True)
    optimizacion = db.Column(db.Integer)
    comision = db.Column(db.Integer)
    colorcliente = db.Column(db.String)
    colormfc = db.Column(db.String)
    usering = db.Column(db.Integer)
    fechaing = db.Column(db.DateTime)
    usermod = db.Column(db.Integer)
    fechamod = db.Column(db.DateTime)
    estado = db.Column(db.Integer)


class DclienteSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'nombre', 'usering')


class Dmarca(db.Model):
    __table_args__ = {'schema': 'mfcgt'}
    __tablename__ = 'dmarca'
    id = db.Column(db.Integer, primary_key=True)  # Field name made lowercase.
    nombre = db.Column(db.String, unique=True)
    abreviatura = db.Column(db.String, unique=True)
    idcliente = db.Column(db.Integer, db.ForeignKey(
        'mfcgt.dcliente.id'), nullable=False)
    usering = db.Column(db.Integer, unique=True)
    fechaing = db.Column(db.DateTime)
    usermod = db.Column(db.Integer, unique=True)
    fechamod = db.Column(db.DateTime)
    estado = db.Column(db.Integer)

    def fullname(self, nombre):
        return self.nombre + " - " + nombre


class DmarcaSchema(ma.ModelSchema):
    class Meta:
        nombre = Dmarca.nombre + Dcliente.nombre
        fields = ("id", "fullname", "usering", "abreviatura")


class ResuladsBrand(db.Model):
    __tablename__ = 'Result_brands'
    # Field name made lowercase.
    idResult = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    MarcaID = db.Column(db.Integer)
    status = db.Column(db.Integer)


class Accountxmarca(db.Model):
    __tablename__ = 'accountxmarca'
    # Field name made lowercase.
    idAccountxMarca = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String)
    marca = db.Column(db.Integer)
    usering = db.Column(db.Integer, unique=True)
    fechaing = db.Column(db.DateTime)
    usermod = db.Column(db.Integer)
    fechamod = db.Column(db.DateTime)

    def __init__(self, accounts, marcas, userings):
        self.account = accounts
        self.marca = marcas
        self.usering = userings



class AccountxMarcaSchema(ma.ModelSchema):
    class Meta:
        fields = ('idAccountxMarca', 'AccountID', 'Medio', 'marca', 'nombre')


class Errorscampaings(db.Model):
    __tablename__ = 'ErrorsCampaings'
    iderrorscampaings = db.Column(db.Integer, primary_key=True)
    error = db.Column(db.String, nullable=False)
    comentario = db.Column(db.String, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    media = db.Column(db.String, nullable=False)
    tipoerrorid = db.Column(db.Integer, nullable=False)
    campaingid = db.Column(db.String, nullable=False)
    usuariovalidacion = db.Column(db.Integer, nullable=False)
    impressions = db.Column(db.Integer, nullable=False)
    createdate = db.Column(db.DateTime, nullable=False)
    UsuarioOmitir = db.Column(db.Integer, nullable=False)

    def __init__(self, Estado):
        self.estado = Estado


class ErrorsCampaingsSchema(ma.ModelSchema):
    class Meta:
        fields = ('iderror', 'idcuenta', 'cuenta', 'CampaingID', 'Camapingname', 'Error', 'TipoErrorID', 'DescripcionError',
                  'GrupoError', 'Icono', 'Comentario', 'Estado', 'Media', 'Fecha', 'tipousuario', 'plataforma', 'marca', 'cliente')


class ErrorsCampaingsCountSchema(ma.ModelSchema):
    class Meta:
        fields = ('totales', 'totalinversion', 'totalnomeclatura',
                  'totalpaises', 'ordenesdecompra', 'errorconsumo')


class Tiposerrores(db.Model):
    __tablename__ = 'TiposErrores'
    tipoerrorid = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String, nullable=False)
    icono = db.Column(db.String, nullable=False)
    tipousuario = db.Column(db.Integer, nullable=False)
    createdate = db.Column(db.DateTime, nullable=False)


class TipoErroresSchema(ma.ModelSchema):
    class Meta:
        fields = ('tipoerrorid', 'descripcion', 'icono', 'tipousuario')


class Campaings(db.Model):
    __tablename__ = 'Campaings'
    campaingid = db.Column(db.String, primary_key=True)
    campaingname = db.Column(db.String, nullable=False)
    campaignspendinglimit = db.Column(db.Float, nullable=False)
    campaigndailybudget = db.Column(db.Float, nullable=False)
    campaignlifetimebudget = db.Column(db.Float, nullable=False)
    campaignobjective = db.Column(db.String, nullable=False)
    campaignstatus = db.Column(db.String, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    accountsid = db.Column(db.String, db.ForeignKey(
        'Accounts.AccountsID'), nullable=False)
    createdate = db.Column(db.DateTime, nullable=False)
    startdate = db.Column(db.DateTime, nullable=False)
    enddate = db.Column(db.DateTime, nullable=False)


class CampaingsSchema(ma.ModelSchema):
    class Meta:
        fields = ('campaingid', 'campaingname', 'campaignspendinglimit', 'campaigndailybudget', 'campaignlifetimebudget',
                  'campaignobjective', 'campaignstatus', 'cost', 'accountsid', 'createdate', 'startdate', 'enddate')


class CampaingsAM(db.Model):
    __tablename__ = 'CampaingsAM'
    campaingid = db.Column(db.String, primary_key=True)
    campaingname = db.Column(db.String, nullable=False)
    campaingname = db.Column(db.String, nullable=False)
    accountsid = db.Column(db.String, db.ForeignKey(
        'Accounts.AccountsID'), nullable=False)


class CampaingsSchema(ma.ModelSchema):
    class Meta:
        fields = ('campaingid', 'campaingname', 'campaignspendinglimit', 'campaigndailybudget', 'campaignlifetimebudget',
                  'campaignobjective', 'campaignstatus', 'cost', 'accountsid', 'createdate', 'startdate', 'enddate')


class CostSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'cost')


class ReportSchema(ma.ModelSchema):
    class Meta:
        fields = ('Account', 'idcliente', 'CampaingID', 'Marca', 'idmarca', 'Media', 'Campaingname', 'InversionConsumida', 'KPIPlanificado', 'StartDate',  'EndDate', 'mes',   'PresupuestoPlan',  'KPI', 'KPIConsumido', 'State', 'TotalDias', 'DiasEjecutados', 'DiasPorservir',
                  'PresupuestoEsperado', 'PorcentajePresupuesto', 'PorcentajeEsperadoV', 'PorcentajeRealV', 'KPIEsperado', 'PorcentajeKPI', 'PorcentajeEsperadoK', 'PorcentajeRealK', 'EstadoKPI', 'EstadoPresupuesto', 'abr', 'CostoPorResultadoR', 'CostoPorResultadoP')


class LocalMedia(db.Model):
    __tablename__ = 'localmedia'
    LocalMediaID = db.Column(db.Integer, primary_key=True)
    Medio = db.Column(db.String, nullable=False)
    Cliente = db.Column(db.String, nullable=False)
    Pais = db.Column(db.String, nullable=False)
    Campana = db.Column(db.String, nullable=False)
    Nomenclatura = db.Column(db.String, nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)
    Mes = db.Column(db.String, nullable=False)
    ODC = db.Column(db.String, nullable=False)
    AccountID = db.Column(db.String, nullable=False)
    State = db.Column(db.String, nullable=False)


class LocalMediaSchema(ma.ModelSchema):
    class Meta:
        fields = ('LocalMediaID', 'Medio', 'Cliente', 'Pais',
                  'Campana', 'StartDate', 'EndDate', 'Mes', 'ODC', 'State')


class DetailLocalMedia(db.Model):
    __tablename__ = 'detaillocalmedia'
    detailID = db.Column(db.Integer, primary_key=True)
    LocalMediaID = db.Column(db.Integer, db.ForeignKey(
        'loalmedia.LocalMediaID'), nullable=False)
    StartWeek = db.Column(db.Date, nullable=False)
    EndWeek = db.Column(db.Date, nullable=False)
    Nomenclatura = db.Column(db.String, nullable=False)
    Formato = db.Column(db.String, nullable=False)
    Objetivo = db.Column(db.String, nullable=False)
    Impresiones = db.Column(db.Integer, nullable=False)
    Clicks = db.Column(db.Integer, nullable=False)
    Ctr = db.Column(db.Integer, nullable=False)
    Consumo = db.Column(db.Float, nullable=False)


class DetailLocalMediaSchema(ma.ModelSchema):
    class Meta:
        fields = ('detailID', 'StartWeek', 'EndWeek', 'Nomenclatura',
                  'Formato', 'Objetivo', 'Impresiones', 'Clicks', 'Ctr', 'Consumo')


class Results_campaings(db.Model):
    __tablename__ = 'Results_Campaings'
    idResult = db.Column(db.Integer, primary_key=True)
    Url = db.Column(db.String, nullable=False)
    CampaingID = db.Column(db.String, nullable=False)
    Status = db.Column(db.Integer, nullable=False)
    CreateDate = db.Column(db.DateTime, nullable=False)
    Description = db.Column(db.String, nullable=False)
    idMarca= db.Column(db.Integer, nullable=False)

    def __init__(self, idResult, Url, CampaingID , Status, Description,idMarca):
        self.idResult = idResult
        self.Url = Url
        self.CampaingID = CampaingID
        self.Status = Status
        self.Description = Description
        self.idMarca = idMarca


class Results_campaingsSchema(ma.ModelSchema):
    class Meta:
        fields = ('idResult', 'Url', 'CampaingID', 'Status','Description', 'idMarca')


class LeadAdsCampaings(db.Model):
    __tablename__ = 'LeadAdsCampaings'
    idLeadAdsCampaings = db.Column(db.Integer, primary_key=True)
    CampaingID = db.Column(db.String, nullable=False)
    Nombre = db.Column(db.String, nullable=False)
    Apellido = db.Column(db.String, nullable=False)
    Telefono = db.Column(db.Integer, nullable=False)
    Email = db.Column(db.String, nullable=False)
    NIT = db.Column(db.String, nullable=False)
    DPI = db.Column(db.String, nullable=False)
    Plataforma = db.Column(db.String, nullable=False)
    Medio = db.Column(db.String, nullable=False)
    Fuente = db.Column(db.String, nullable=False)
    Ubicacion = db.Column(db.String, nullable=False)
    Producto = db.Column(db.String, nullable=False)
    CreateDate = db.Column(db.DateTime, nullable=False)

    def __init__(self, CampaingID, Nombre, Telefono, NIT, DPI, Email,Ubicacion, Plataforma,  Producto):
        self.CampaingID = CampaingID
        self.Nombre = Nombre
        self.Telefono = Telefono
        self.NIT = NIT
        self.DPI = DPI
        self.Email = Email
        self.Ubicacion = Ubicacion
        self.Plataforma = Plataforma
        self.Producto = Producto

class LeadAdsCampaingsSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'CampaingID', 'Nombre', 'Telefono', 'Email', 'NIT', 'DPI', 'Plataforma', 'Ubicacion', 'Producto','CreateDate', 'EstadoDpi', 'EstadoTelefono', 'EstadoEmail', 'EstadoGeneral')


class Invitados(db.Model):
    __tablename__ = 'Invitados'
    idUsuario = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    idmarca = db.Column(db.Integer, nullable=False)
    idcliente = db.Column(db.Integer, nullable=False)


class InvitadosSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'username', 'password', 'firstName', 'lastName')


class mfcaprobacion(db.Model):
    __table_args__ = {'schema': 'mfcgt'}
    __tablename__ = 'mfcaprobacion'
    id = db.Column(db.Integer, primary_key=True)
    idmfc = db.Column(db.Integer, db.ForeignKey(
        'mfcgt.mfc.id'), nullable=False)
    asunto = db.Column(db.String, nullable=False)
    mensaje = db.Column(db.String, nullable=False)
    emailstatus = db.Column(db.String, nullable=False)
    campana = db.Column(db.String, nullable=False)
    versioncampana = db.Column(db.String, nullable=False)
    tiposmedio = db.Column(db.String, nullable=False)
    medio = db.Column(db.String, nullable=False)
    mes = db.Column(db.String, nullable=False)
    datos = db.Column(db.String, nullable=False)
    usering = db.Column(db.Integer, nullable=False)
    fechaing = db.Column(db.DateTime, nullable=False)
    usermod = db.Column(db.DateTime, nullable=False)
    fechamod = db.Column(db.String, nullable=False)


class aprobacionSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'idmfc', 'datos', 'estado','nombre')


class mfc(db.Model):
    __table_args__ = {'schema': 'mfcgt'}
    __tablename__ = 'mfc'
    id = db.Column(db.Integer, primary_key=True)
    idversion = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String, nullable=False)
    idmarca = db.Column(db.Integer, db.ForeignKey(
        'mfcgt.dmarca.id'), nullable=False)
    idagencia = db.Column(db.Integer, nullable=False)
    moneda = db.Column(db.String, nullable=False)
    aprobado = db.Column(db.Integer, nullable=False)
    aprobadopor = db.Column(db.Integer, nullable=False)
    cancelado = db.Column(db.Integer, nullable=False)
    canceladopor = db.Column(db.Integer, nullable=False)
    fechacancelado = db.Column(db.DateTime, nullable=False)
    paisfacturar = db.Column(db.Integer, nullable=False)
    paisimplementar = db.Column(db.Integer, nullable=False)
    anioimplementacion = db.Column(db.Integer, nullable=False)
    usering = db.Column(db.Integer, nullable=False)
    fechaing = db.Column(db.DateTime, nullable=False)
    usermod = db.Column(db.DateTime, nullable=False)
    fechamod = db.Column(db.String, nullable=False)
    estado = db.Column(db.Integer, nullable=False)


class mfcSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'idversion', 'nombre',
                  'paisfacturar', 'paisimplementar', 'estado')


class mfccampana(db.Model):
    __table_args__ = {'schema': 'mfcgt'}
    __tablename__ = 'mfccampana'
    id = db.Column(db.Integer, primary_key=True)
    idversion = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String, nullable=False)
    nombreversion = db.Column(db.String, nullable=False)
    color = db.Column(db.String, nullable=False)
    idmfc = db.Column(db.Integer, db.ForeignKey(
        'mfcgt.mfc.id'), nullable=False)
    idversionmfc = db.Column(db.Integer, nullable=False)
    idproducto = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.String, nullable=False)
    fechainicio = db.Column(db.DateTime, nullable=False)
    fechafin = db.Column(db.DateTime, nullable=False)
    usering = db.Column(db.Integer, nullable=False)
    fechaing = db.Column(db.DateTime, nullable=False)
    usermod = db.Column(db.DateTime, nullable=False)
    fechamod = db.Column(db.String, nullable=False)
    estado = db.Column(db.Integer, nullable=False)


class campanaSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'idversion', 'nombre', 'nombreversion', 'fechainicio','costo',
                  'costoplataforma', 'fechafin', 'paisfacturar', 'paisimplementar', 'estado')


class mfccompradiaria(db.Model):
    __table_args__ = {'schema': 'mfcgt'}
    __tablename__ = 'mfccompradiaria'
    id = db.Column(db.Integer, primary_key=True)
    idcampana = db.Column(db.Integer, nullable=False)
    idversion = db.Column(db.Integer, nullable=False)
    idformato = db.Column(db.Integer, nullable=False)
    idformatodigital = db.Column(db.Integer, nullable=False)
    costo = db.Column(db.Float, nullable=False)
    bonificacion = db.Column(db.Float, nullable=False)
    cobertura_publicacion = db.Column(db.String, nullable=False)
    observaciones = db.Column(db.String, nullable=False)
    multiplestiposa = db.Column(db.String, nullable=False)
    multiplestiposb = db.Column(db.String, nullable=False)
    multiplestiposc = db.Column(db.String, nullable=False)
    multiplestiposd = db.Column(db.String, nullable=False)
    multiplestipose = db.Column(db.String, nullable=False)
    multiplestiposf = db.Column(db.String, nullable=False)
    multiplestiposg = db.Column(db.String, nullable=False)
    multiplestiposh = db.Column(db.String, nullable=False)
    multiplescostosa = db.Column(db.Float, nullable=False)
    multiplescostosb = db.Column(db.Float, nullable=False)
    multiplescostosc = db.Column(db.Float, nullable=False)
    multiplescostosd = db.Column(db.Float, nullable=False)
    multiplescostose = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    enero = db.Column(db.String, nullable=False)
    febrero = db.Column(db.String, nullable=False)
    marzo = db.Column(db.String, nullable=False)
    abril = db.Column(db.String, nullable=False)
    mayo = db.Column(db.String, nullable=False)
    junio = db.Column(db.String, nullable=False)
    julio = db.Column(db.String, nullable=False)
    agosto = db.Column(db.String, nullable=False)
    septiembre = db.Column(db.String, nullable=False)
    octubre = db.Column(db.String, nullable=False)
    noviembre = db.Column(db.String, nullable=False)
    diciembre = db.Column(db.String, nullable=False)
    odc = db.Column(db.String, nullable=False)
    idraiz = db.Column(db.Integer, nullable=False)
    idpresupuesto = db.Column(db.Integer, nullable=False)
    aprobado = db.Column(db.Integer, nullable=False)
    usering = db.Column(db.Integer, nullable=False)
    fechaing = db.Column(db.DateTime, nullable=False)
    usermod = db.Column(db.DateTime, nullable=False)
    fechamod = db.Column(db.String, nullable=False)
    estado = db.Column(db.Integer, nullable=False)


class compradiariaSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'nombre', 'fecha_inicio_mfc', 'fecha_fin_mfc', 'fecha_inicio_pl','fecha_fin_pl',
                  'costo_mfc', 'costo_pl')


class dpais(db.Model):
    __table_args__ = {'schema': 'mfcgt'}
    __tablename__ = 'dpais'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    codigo  = db.Column(db.Integer, nullable=False)
    usering = db.Column(db.Integer, nullable=False)
    fechaing = db.Column(db.DateTime, nullable=False)
    usermod = db.Column(db.DateTime, nullable=False)
    fechamod = db.Column(db.String, nullable=False)
    estado = db.Column(db.Integer, nullable=False)


class rCampaings(db.Model):
    __table_args__ = {'schema': 'MediaPlatformsReports'}
    __tablename__ = 'Campaings'
    campaingid = db.Column(db.String, primary_key=True)
    campaingname = db.Column(db.String, nullable=False)
    campaignspendinglimit = db.Column(db.Float, nullable=False)
    campaigndailybudget = db.Column(db.Float, nullable=False)
    campaignlifetimebudget = db.Column(db.Float, nullable=False)
    campaignobjective = db.Column(db.String, nullable=False)
    campaignstatus = db.Column(db.String, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    accountsid = db.Column(db.String, nullable=False)
    createdate = db.Column(db.DateTime, nullable=False)
    startdate = db.Column(db.DateTime, nullable=False)
    enddate = db.Column(db.DateTime, nullable=False)


class rCampaingsSchema(ma.ModelSchema):
    class Meta:
        fields = ('campaingid', 'campaingname', 'campaignspendinglimit', 'campaigndailybudget', 'campaignlifetimebudget',
                  'campaignobjective', 'campaignstatus', 'cost', 'accountsid', 'createdate', 'startdate', 'enddate')


class rCampaingMetrics(db.Model):
    __table_args__ = {'schema': 'MediaPlatformsReports'}
    __tablename__ = 'CampaingMetrics'
    id = db.Column(db.Integer, primary_key=True)  # Field name made lowercase.
    Reach = db.Column(db.Integer)
    Frequency = db.Column(db.Float)
    Cost = db.Column(db.Float)
    Clicks = db.Column(db.Integer)
    Percentofbudgetused = db.Column(db.Float)
    Impressions = db.Column(db.Integer)
    #CampaingID = db.Column(db.String)
    CampaingID = db.Column(db.String, db.ForeignKey(
        'MediaPlatformsReports.Campaings.campaingid'), nullable=False)
    CreateDate = db.Column(db.DateTime)
    ReportType = db.Column(db.Integer)
    Result = db.Column(db.Float)
    Postengagements = db.Column(db.Float)
    Estimatedadrecalllift = db.Column(db.Float)
    Videowachesat75 = db.Column(db.Float)
    ThruPlay = db.Column(db.Float)
    Conversions = db.Column(db.Integer)
    Objetive = db.Column(db.String)
    CampaignIDMFC = db.Column(db.Integer)
    AppInstalls = db.Column(db.Integer)
    KPICost = db.Column(db.Float)
    CloseData = db.Column(db.Integer)
    Week = db.Column(db.Integer)
    UserMod = db.Column(db.String)
    UpdateDate = db.Column(db.DateTime)

class rCampaingMetricsSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'Nomenclatura', 'Cost', 'Frequency', 'Reach', 'Postengagements', 'Impressions', 'Clicks', 'Videowachesat75'
        , 'Conversions', 'AppInstalls', 'KPI')