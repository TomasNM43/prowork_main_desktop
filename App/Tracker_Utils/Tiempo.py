class Tiempo:
    def __init__(self, tiempo_inicio, tiempo_fin, dias, horas, minutos, segundos):
        self.tiempo_inicio = tiempo_inicio
        self.tiempo_fin = tiempo_fin
        self.total_time = tiempo_fin - tiempo_inicio
        self.dias = dias
        self.horas = horas
        self.minutos = minutos
        self.segundos = segundos
    
    def _get_specific_times(self):
        self.dias, self.segundos = self.total_time.days, self.total_time.seconds
        self.horas = self.dias * 24 + self.segundos // 3600
        self.minutos = (self.segundos % 3600) // 60
        self.segundos = self.segundos % 60

    def serialize(self):
        return {
            'tiempo_inicio' : self.tiempo_inicio.strftime("%Y-%m-%d %H:%M:%S"),
            'tiempo_fin' : self.tiempo_fin.strftime("%Y-%m-%d %H:%M:%S"),
            'dias' : self.dias,
            'horas' : self.horas,
            'minutos' : self.minutos,
            'segundos' : self.segundos
        }