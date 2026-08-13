import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Maquina(db.Model):
    __tablename__ = 'maquinas'
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    serial = db.Column(db.String(50), default='')
    estado = db.Column(db.String(50), default='Operativa')
    ubicacion = db.Column(db.String(100), default='')
    notas = db.Column(db.Text, default='')

    def to_dict(self, paciente_actual=None):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'serial': self.serial,
            'estado': self.estado,
            'ubicacion': self.ubicacion,
            'notas': self.notas,
            'paciente_actual': paciente_actual,
        }


class Registro(db.Model):
    __tablename__ = 'registros'
    id = db.Column(db.String(10), primary_key=True)
    fecha = db.Column(db.String(10), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    cedula = db.Column(db.String(30), default='')
    sexo = db.Column(db.String(1), default='')
    edad = db.Column(db.Integer, nullable=True)
    lesion = db.Column(db.String(200), default='')
    direccion = db.Column(db.String(300), default='')
    tel1 = db.Column(db.String(100), default='')
    tel2 = db.Column(db.String(100), default='')
    dr_refiere = db.Column(db.String(200), default='')
    ars = db.Column(db.String(100), default='Privado')
    maquina = db.Column(db.String(10), default='')
    estatus = db.Column(db.String(20), default='Activo')
    motivo = db.Column(db.String(300), default='')
    facturacion = db.Column(db.Float, default=0)
    saldo_pendiente = db.Column(db.Float, default=0)
    modo_uso = db.Column(db.String(100), default='')
    condicion_salida = db.Column(db.String(100), default='')
    condicion_retorno = db.Column(db.String(100), default='')
    parametros = db.Column(db.Text, default='')
    notas = db.Column(db.Text, default='')
    proxima_colocacion = db.Column(db.String(10), nullable=True)
    notas_seguimiento = db.Column(db.Text, default='')
    fecha_retiro = db.Column(db.String(10), nullable=True)
    observaciones_retiro = db.Column(db.Text, default='')
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    productos = db.Column(db.Text, default='[]')
    fotos = db.Column(db.Text, default='[]')

    def to_dict(self):
        return {
            'id': self.id,
            'fecha': self.fecha,
            'nombre': self.nombre,
            'cedula': self.cedula,
            'sexo': self.sexo,
            'edad': self.edad,
            'lesion': self.lesion,
            'direccion': self.direccion,
            'tel1': self.tel1,
            'tel2': self.tel2,
            'dr_refiere': self.dr_refiere,
            'ars': self.ars,
            'maquina': self.maquina,
            'estatus': self.estatus,
            'motivo': self.motivo,
            'facturacion': self.facturacion,
            'saldo_pendiente': self.saldo_pendiente or 0,
            'modo_uso': self.modo_uso,
            'condicion_salida': self.condicion_salida,
            'condicion_retorno': self.condicion_retorno,
            'parametros': self.parametros,
            'notas': self.notas,
            'proxima_colocacion': self.proxima_colocacion,
            'notas_seguimiento': self.notas_seguimiento,
            'fecha_retiro': self.fecha_retiro,
            'observaciones_retiro': self.observaciones_retiro,
            'lat': self.lat,
            'lng': self.lng,
            'productos': json.loads(self.productos or '[]'),
            'fotos': json.loads(self.fotos or '[]'),
        }


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.String(10), primary_key=True)
    user = db.Column(db.String(50), unique=True, nullable=False)
    pass_ = db.Column('pass', db.Text, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), default='')
    rol = db.Column(db.String(20), default='usuario')
    activo = db.Column(db.Boolean, default=True)

    def to_dict(self, include_pass=False):
        d = {
            'id': self.id,
            'user': self.user,
            'nombre': self.nombre,
            'email': self.email or '',
            'rol': self.rol,
            'activo': self.activo,
        }
        if include_pass:
            d['pass'] = self.pass_
        return d


class PacienteMaster(db.Model):
    __tablename__ = 'pacientes_master'
    nombre = db.Column(db.String(200), primary_key=True)
    datos = db.Column(db.Text, default='{}')


class Consentimiento(db.Model):
    __tablename__ = 'consentimientos'
    id = db.Column(db.String(10), primary_key=True)
    fecha_firma = db.Column(db.String(10), nullable=False)   # YYYY-MM-DD
    nombre = db.Column(db.String(200), nullable=False)
    cedula = db.Column(db.String(30), default='')
    edad = db.Column(db.Integer, nullable=True)
    direccion = db.Column(db.String(300), default='')
    telefono = db.Column(db.String(100), default='')
    medico = db.Column(db.String(200), default='')
    centro_salud = db.Column(db.String(200), default='')
    firmado = db.Column(db.Boolean, default=False)
    notas = db.Column(db.Text, default='')

    def to_dict(self):
        return {
            'id': self.id,
            'fecha_firma': self.fecha_firma,
            'nombre': self.nombre,
            'cedula': self.cedula,
            'edad': self.edad,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'medico': self.medico,
            'centro_salud': self.centro_salud,
            'firmado': self.firmado,
            'notas': self.notas,
        }


class Config(db.Model):
    __tablename__ = 'config'
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text, default='')

    def to_dict(self):
        return json.loads(self.datos or '{}')
