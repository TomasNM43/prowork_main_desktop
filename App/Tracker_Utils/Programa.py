class Programa:
    def __init__(self, nombre, timestamp):
        self.nombre = nombre
        self.timestamp = timestamp

    def serialize(self):
        return {
            'nombre' : self.nombre,
            'timestamp' : self.tiempo_json()
        }
    
    def tiempo_json(self):
        tiempo_lista = []
        for time in self.timestamp:
            tiempo_lista.append(time.serialize())
        return tiempo_lista