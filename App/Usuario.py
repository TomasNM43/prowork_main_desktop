import Constantes

from Solicitudes import solicitud
from collections import namedtuple

class Usuario():
    def __init__(self) -> None:
        self.personal = None
        self.asistencia = None
        self.parametros = None
        self.programas = []
        self.estado = False
        self.justificado = False
        self.comision = False
        self.ausente = False
        self.refrigerio = False
        self.timestap_inicio = None
        self.timestap_fin = None
        self.minutos_ausentes = 0
    
    def obtener_parametros(self):
        url = Constantes.URL + '/parametros/{0}'.format(self.personal.ID_EMPRESA)
        estado, respuesta = solicitud("GET", url)
        if estado:
            diccionario = respuesta['datos']
            self.parametros = namedtuple("Parametros", diccionario.keys())(*diccionario.values())
            return True
        else:
            return False

    def obtener_programas(self):
        url = Constantes.URL + '/programas/{0}'.format(self.personal.ID_PERSONAL)
        estado, respuesta = solicitud("GET", url)
        if estado:
            data = respuesta['datos']
            for i in data:
                self.programas.append(i['TIPO_HERRAMIENTA'])
            return True
        else:
            return False

usuario = Usuario()