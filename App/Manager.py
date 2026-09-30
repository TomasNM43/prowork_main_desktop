import cv2
import re
import sys
import base64
import psutil
import socket
import requests
import pyautogui
import numpy as np

from array import array
from Constantes import URL_IP

try:
    if sys.platform.startswith("win"):
        import win32gui
    else:
        win32gui = None
except ImportError:
    win32gui = None

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
        programas_normalizados = {
            str(programa).strip().lower()
            for programa in programas
        }
        temp = []
        for p in psutil.process_iter():
            try:
                nombre_proceso = p.name()
                if nombre_proceso.lower() in programas_normalizados:
                    temp.append(nombre_proceso)
            except psutil.Error:
                pass
        return temp

    def detectar_paginas(self, paginas: array):
        """Detecta si alguna de las páginas registradas está abierta, buscando su dominio
        entre los títulos de las ventanas visibles (ej. pestañas del navegador)."""
        if win32gui is None or not paginas:
            return []

        titulos = []

        def _acumular_titulo(hwnd, acumulador):
            if win32gui.IsWindowVisible(hwnd):
                titulo = win32gui.GetWindowText(hwnd)
                if titulo:
                    acumulador.append(titulo.lower())
            return True

        try:
            win32gui.EnumWindows(_acumular_titulo, titulos)
        except Exception:
            return []

        texto_ventanas = ' | '.join(titulos)
        detectadas = []
        for pagina in paginas:
            clave = self._extraer_clave_pagina(pagina)
            if clave and clave in texto_ventanas:
                detectadas.append(pagina)
        return detectadas

    @staticmethod
    def _extraer_clave_pagina(pagina: str) -> str:
        valor = str(pagina).strip().lower()
        valor = re.sub(r'^https?://', '', valor)
        valor = re.sub(r'^www\.', '', valor)
        valor = valor.split('/')[0]
        dominio = valor.split('.')[0]
        return dominio
    
    def conseguir_metadatos(self):
        self.nombre_pc = socket.gethostname()
        self.ip_privada = socket.gethostbyname(self.nombre_pc)
        self.ip_publica = requests.get(URL_IP).text