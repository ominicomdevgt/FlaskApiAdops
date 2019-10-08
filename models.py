from app import db,ma


class Bitacora(db.Model):
    __tablename__ = 'bitacora'
    bitacoraID = db.Column(db.Integer, primary_key=True)
    Operacion = db.Column(db.String, unique=True, nullable=False)
    Resultado = db.Column(db.String, unique=True, nullable=False)
    Documento = db.Column(db.String, unique=True, nullable=False)
    CreateDate = db.Column(db.DateTime, unique=True, nullable=False)

class BitacoraSchema(ma.ModelSchema):
    class Meta:
        fields = ('bitacoraID','Operacion','Resultado','Documento','CreateDate')


class Accounts(db.Model):
    __tablename__ = 'Accounts'
    AccountsID = db.Column(db.String, primary_key=True)  # Field name made lowercase.
    Account = db.Column(db.String, unique=True, nullable=False)
    Media = db.Column(db.String, unique=True, nullable=False)
    CreateDate = db.Column(db.DateTime, unique=True, nullable=False)
    Country = db.Column(db.String,  nullable=True)
    def __init__(self, AccountsID, Account, Media,Country):
        self.AccountsID = AccountsID
        self.Account = Account
        self.Media = Media
        self.Country = Country
        

    
class AccountsSchema(ma.ModelSchema):
    class Meta:
        fields = ('AccountsID','Account','Media','CreateDate','Country')


class Dcliente(db.Model):
    __table_args__ = {'schema':'mfcgt'}
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
        fields = ('id','nombre','usering')        

class Dmarca(db.Model):
    __table_args__ = {'schema':'mfcgt'}
    __tablename__ = 'dmarca'
    id = db.Column(db.Integer, primary_key=True)  # Field name made lowercase.
    nombre = db.Column(db.String, unique=True)
    abreviatura = db.Column(db.String, unique=True)
    idcliente = db.Column(db.Integer, db.ForeignKey('mfcgt.dcliente.id'),nullable=False)
    usering = db.Column(db.Integer, unique=True)
    fechaing = db.Column(db.DateTime)
    usermod = db.Column(db.Integer, unique=True)
    fechamod = db.Column(db.DateTime)
    estado = db.Column(db.Integer)
    dmarcaFK = db.relationship('Accountxmarca',backref='dmarca', primaryjoin='Accountxmarca.marca == Dmarca.id')
    dclienteFK = db.relationship('Dcliente',backref='dmarca', primaryjoin='Dcliente.id == Dmarca.idcliente')

    def fullname(self,nombre):
        return self.nombre + " - " + nombre

class DmarcaSchema(ma.ModelSchema):
    class Meta:
        nombre = Dmarca.nombre + Dcliente.nombre
        fields = ("id","fullname","usering","abreviatura")

class Accountxmarca(db.Model):
    __tablename__ = 'accountxmarca'
    idAccountxMarca = db.Column(db.Integer, primary_key=True)  # Field name made lowercase.
    account = db.Column(db.String,db.ForeignKey('Accounts.AccountsID'),nullable=False)
    marca = db.Column(db.Integer, db.ForeignKey('mfcgt.dmarca.id'),nullable=False)
    usering = db.Column(db.Integer, unique=True)
    fechaing = db.Column(db.DateTime)
    usermod = db.Column(db.Integer)
    fechamod = db.Column(db.DateTime)
    def __init__(self, account, marca, usering):
        self.account = account
        self.marca = marca
        self.usering = usering
    

class AccountxMarcaSchema(ma.ModelSchema):  
    class Meta:
        fields = ('idAccountxMarca','AccountID','Medio' , 'marca','nombre')


class Errorscampaings(db.Model):
    __tablename__ = 'ErrorsCampaings'
    iderrorscampaings = db.Column(db.Integer, primary_key=True)
    error = db.Column(db.String,nullable=False)
    comentario = db.Column(db.String,nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    media = db.Column(db.String,nullable=False)
    tipoerrorid = db.Column(db.Integer,nullable=False)
    campaingid = db.Column(db.String,nullable=False)
    usuariovalidacion = db.Column(db.Integer,nullable=False)
    impressions = db.Column(db.Integer,nullable=False)
    createdate = db.Column(db.DateTime,nullable=False)

class ErrorsCampaingsSchema(ma.ModelSchema):
    class Meta:
        fields = ('iderror','idcuenta','cuenta' , 'CampaingID','Camapingname','Error','TipoErrorID','DescripcionError','GrupoError', 'Icono','Comentario','Estado','Media','Fecha','tipousuario', 'plataforma', 'marca','cliente')


class Tiposerrores(db.Model):
    __tablename__ = 'TiposErrores'
    tipoerrorid = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String, nullable=False)
    icono = db.Column(db.String, nullable=False)
    tipousuario = db.Column(db.Integer, nullable=False)
    createdate = db.Column(db.DateTime, nullable=False)

class TipoErroresSchema(ma.ModelSchema):
    class Meta:
        fields = ('tipoerrorid','descripcion','icono' , 'tipousuario')


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
    accountsid = db.Column(db.String,db.ForeignKey('Accounts.AccountsID'), nullable=False)
    createdate = db.Column(db.DateTime, nullable=False)
    startdate = db.Column(db.DateTime, nullable=False)
    enddate = db.Column(db.DateTime, nullable=False)

class CampaingsSchema(ma.ModelSchema):
    class Meta:
        fields = ('campaingid','campaingname','campaignspendinglimit', 'campaigndailybudget', 'campaignlifetimebudget',
        'campaignobjective','campaignstatus','cost','accountsid', 'createdate','startdate', 'enddate')

class CampaingsAM(db.Model):
    __tablename__ = 'CampaingsAM'
    campaingid = db.Column(db.String, primary_key=True)
    campaingname = db.Column(db.String, nullable=False)
    campaingname = db.Column(db.String, nullable=False)
    accountsid = db.Column(db.String,db.ForeignKey('Accounts.AccountsID'), nullable=False)


class CampaingsSchema(ma.ModelSchema):
    class Meta:
        fields = ('campaingid','campaingname','campaignspendinglimit', 'campaigndailybudget', 'campaignlifetimebudget',
        'campaignobjective','campaignstatus','cost','accountsid', 'createdate','startdate', 'enddate')


class ReportSchema(ma.ModelSchema):
    class Meta:
        fields = ('Account', 'Media','Campaingname','CampaingID','Cost','StartDate' ,  'EndDate' ,   'presupuesto',  'objetivo', 'result','State', 'TotalDias', 'DiasServidos','DiasPorservir','ValorEsperado', 'ValorReal','PorcentajeEsperadoV','PorcentajeRealV','KPIEsperado', 'KPIReal','PorcentajeEsperadoK','PorcentajeRealK')


class LocalMedia(db.Model):
    __tablename__ = 'localmedia'
    LocalMediaID  = db.Column(db.Integer, primary_key=True)
    Medio = db.Column(db.String, nullable=False)
    Cliente = db.Column(db.String, nullable=False)
    Pais = db.Column(db.String, nullable=False)
    Campana = db.Column(db.String, nullable=False)
    Nomenclatura = db.Column(db.String, nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date, nullable=False)
    Mes = db.Column(db.String, nullable=False)
    Odc = db.Column(db.String, nullable=False)
    AccountID = db.Column(db.String, nullable=False)
    State = db.Column(db.Integer, nullable=False)

class LocalMediaSchema(ma.ModelSchema):
    class Meta:
        fields = ('LocalMediaID','Medio','Cliente', 'Pais', 'Campana','StartDate','EndDate', 'Mes', 'Odc', 'State')

class DetailLocalMedia(db.Model):
    __tablename__ = 'detaillocalmedia'
    detailID  = db.Column(db.Integer, primary_key=True)
    LocalMediaID = db.Column(db.Integer, nullable=False)
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
        fields = ('StartWeek','EndWeek', 'Nomenclatura', 'Formato','Objetivo','Impresiones', 'Clicks', 'Ctr', 'Consumo')
