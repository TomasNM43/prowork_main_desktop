import json

from Tracker_Utils.Tiempo import Tiempo
from dateutil import parser
from Tracker_Utils.Programa import Programa

class Lista:
    def __init__(self, programa):
        self.programa = programa
    
    def initialize_me(self):
        lista = Lista([])
        with open('programas.json', 'r') as f:
            data = json.load(f)
            lista = Lista(
                programa = self.obtener_programas(data)
            )
        return lista
    
    def obtener_programas(self, data):
        lista = []
        for programa in data['programa']:
            lista.append(
                Programa(
                    nombre = programa['nombre'],
                    timestamp = self.obtener_timestamp(programa),
                )
            )
        self.programa = lista
        return lista
    
    def obtener_timestamp(self, data):
        lista = []
        for timestamp in data['timestamp']:
            lista.append(
                Tiempo(
                    tiempo_inicio = parser.parse(timestamp['tiempo_inicio']),
                    tiempo_fin = parser.parse(timestamp['tiempo_fin']),
                    dias = timestamp['dias'],
                    horas = timestamp['horas'],
                    minutos = timestamp['minutos'],
                    segundos = timestamp['segundos'],
                )
            )
        self.timestamp = lista
        return lista
    
    def serialize(self):
        return {
            'programa' : self.generar_json()
        }
    
    def generar_json(self):
        programa_ = []
        for p in self.programa:
            programa_.append(p.serialize())
        
        return programa_