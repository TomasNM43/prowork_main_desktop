from __future__ import print_function

import sys
import time
import json
import datetime

from os import system
from PyQt5.QtCore import *

from AppLogger import get_logger
from Tracker_Utils.Lista import Lista
from Tracker_Utils.Tiempo import Tiempo
from Tracker_Utils.Programa import Programa

_log = get_logger(__name__)

if sys.platform in ['Windows', 'win32', 'cygwin']:
    import win32gui
    #import uiautomation as auto
#elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
    #from Foundation import *
    #from AppKit import NSWorkspace

class Tracker(QThread):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.hilo_activo = None

    def run(self):
        self.hilo_activo = True
        _log.info("Tracker.run() iniciado")

        active_window_name = ""
        activity_name = ""
        start_time = datetime.datetime.now()
        activeList = Lista([])
        first_time = True
        try:
            activeList.initialize_me()
        except Exception:
            _log.warning("No se pudo cargar programas.json, se inicia lista vacía")

        while self.hilo_activo:
            try:
                if sys.platform not in ['linux', 'linux2']:
                    new_window_name = self.get_active_window()
                if active_window_name != new_window_name:
                    activity_name = active_window_name
                    if not first_time:
                        end_time = datetime.datetime.now()
                        time_entry = Tiempo(start_time, end_time, 0, 0, 0, 0)
                        time_entry._get_specific_times()
                        exists = False
                        for programa in activeList.programa:
                            if programa.nombre == activity_name:
                                exists = True
                                programa.timestamp.append(time_entry)
                        if not exists:
                            programa = Programa(active_window_name, [time_entry])
                            activeList.programa.append(programa)
                        with open('programas.json', 'w') as json_file:
                            json.dump(activeList.serialize(), json_file, indent=4, sort_keys=True)
                            start_time = datetime.datetime.now()
                    first_time = False
                    active_window_name = new_window_name
            except Exception:
                _log.error("Error en ciclo Tracker", exc_info=True)

    def get_active_window(self):
        _active_window_name = None
        if sys.platform in ['Windows', 'win32', 'cygwin']:
            window = win32gui.GetForegroundWindow()
            _active_window_name = win32gui.GetWindowText(window)
        elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
            _active_window_name = (NSWorkspace.sharedWorkspace()
                                .activeApplication()['NSApplicationName'])
        return _active_window_name
    
    def stop(self):
        self.hilo_activo = False
        self.quit()