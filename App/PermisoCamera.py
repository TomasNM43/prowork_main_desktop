import threading
import time
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal
from Constantes import URL
from Solicitudes import solicitud

class _Senales(QObject):
    mostrar_dialogo = pyqtSignal()

_senales = _Senales()
_id_personal_global = None
_ventana_ref = None
_dialogo_activo = False

def iniciar_polling_permisos(id_personal, ventana_principal):
    global _id_personal_global, _ventana_ref
    _id_personal_global = id_personal
    _ventana_ref = ventana_principal
    _senales.mostrar_dialogo.connect(_mostrar_dialogo)
    hilo = threading.Thread(
        target=_loop_polling, args=(id_personal,), daemon=True)
    hilo.start()

def _loop_polling(id_personal):
    global _dialogo_activo
    while True:
        time.sleep(3)
        try:
            _, resp = solicitud(
                "GET", f"{URL}/streaming/consultar-solicitud/{id_personal}")
            if resp.get("tiene_solicitud") and not _dialogo_activo:
                _dialogo_activo = True
                _senales.mostrar_dialogo.emit()
        except Exception:
            pass

def _mostrar_dialogo():
    global _dialogo_activo
    msg = QMessageBox(_ventana_ref)
    msg.setWindowTitle("Solicitud de acceso a cámara")
    msg.setText(
        "El supervisor solicita ver tu cámara.\n"
        "¿Aceptas compartir tu cámara en este momento?")
    msg.setIcon(QMessageBox.Question)
    btn_aceptar  = msg.addButton("Aceptar",  QMessageBox.AcceptRole)
    btn_rechazar = msg.addButton("Rechazar", QMessageBox.RejectRole)
    msg.exec_()
    acepta = msg.clickedButton() == btn_aceptar
    _dialogo_activo = False
    try:
        solicitud("PUT",
                  f"{URL}/streaming/responder-permiso/{_id_personal_global}",
                  json={"acepta": acepta})
    except Exception:
        pass
    if acepta:
        import Camara
        Camara._streaming_activo = True
