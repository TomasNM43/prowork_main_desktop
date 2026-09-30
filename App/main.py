import sys

# Logging debe inicializarse ANTES de cualquier otro import de la app
from AppLogger import setup_logging, get_logger
setup_logging()
_log = get_logger('main')

from GUI import GUI
from Login import Login
from PyQt5.QtWidgets import *

if __name__ == '__main__':
    _log.info("QApplication iniciada")
    App = QApplication(sys.argv)
    try:
        login = Login()
        if login.exec() == 1:
            _log.info("Login exitoso, abriendo GUI principal")
            main = GUI()
            main.show()
            sys.exit(App.exec())
        else:                                                                                                   
            _log.info("Login cancelado")
    except Exception:
        _log.critical("Error crítico en arranque", exc_info=True)
        raise