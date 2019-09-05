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

class AccountsSchema(ma.ModelSchema):
    class Meta:
        fields = ('AccountsID','Account','Media','CreateDate')

class Dmarca(db.Model):
    __bind_key__ = 'mfc'
    __tablename__ = 'dmarca'
    id = db.Column(db.Integer, primary_key=True)  # Field name made lowercase.
    nombre = db.Column(db.String, unique=True)
    abreviatura = db.Column(db.String, unique=True)
    idcliente = db.Column(db.Integer, unique=True)
    usering = db.Column(db.Integer, unique=True)
    fechaing = db.Column(db.DateTime)
    usermod = db.Column(db.Integer, unique=True)
    fechamod = db.Column(db.DateTime)
    estado = db.Column(db.Integer)
   
class DmarcaSchema(ma.ModelSchema):
    class Meta:
        fields = ('id','nombre','usering')



class Accountxmarca(db.Model):
    __tablename__ = 'accountxmarca'
    idAccountxMarca = db.Column(db.Integer, primary_key=True)  # Field name made lowercase.
    account = db.Column(db.String, unique=True)
    marca = db.Column(db.Integer, unique=True)
    usering = models.IntegerField( db_column='usering')
    fechaing = models.DateTimeField()
    usermod = models.IntegerField( db_column='usermod', blank=True, null=True)
    fechamod = models.DateTimeField(blank=True, null=True)

    
    class Meta:
        managed = False
        db_table = 'accountxmarca'
        app_label = 'media'