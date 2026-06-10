import cv2
import base64
import psutil
import socket
import requests
import pyautogui
import numpy as np

from array import array
from Constantes import URL_IP

class Manager():
    def __init__(self) -> None:
        self.nombre_pc = None
        self.ip_privada = None
        self.ip_publica = None
    
    def capturar_pantalla(self):
        captura = pyautogui.screenshot()
        imagen = cv2.cvtColor(np.array(captura), cv2.COLOR_RGB2BGR)
        buffer = cv2.imencode('.png', imagen)[1]
        encoded = base64.b64encode(buffer)
        decoded = encoded.decode('utf-8')
        return decoded
    
    def detectar_programas(self, programas: array):
        temp = []
        for p in psutil.process_iter():
            try:
                if p.name() in programas:
                    temp.append(p.name())
            except psutil.Error:
                pass
        return temp
    
    def conseguir_metadatos(self):
        self.nombre_pc = socket.gethostname()
        self.ip_privada = socket.gethostbyname(self.nombre_pc)
        self.ip_publica = requests.get(URL_IP).text