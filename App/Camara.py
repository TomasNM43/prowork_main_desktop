import cv2
import base64
import threading
import requests as _requests
import face_recognition

from AppLogger import get_logger
from Constantes import STREAMING_SECRET, URL, URL_WEB
from PyQt5.QtGui import *
from PyQt5.QtCore import *


_log = get_logger(__name__)
_id_personal_stream = None
_streaming_activo   = False
_frame_counter      = 0

class Camara(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hilo_activo = None
        self.ubicacion_cara = []

    def run(self):
        self.hilo_activo = True
        _log.info("Camara.run() iniciado")

        # Intentar con DirectShow primero, luego backend por defecto
        Capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not Capture.isOpened():
            _log.warning("CAP_DSHOW no disponible, usando backend por defecto")
            Capture = cv2.VideoCapture(0)

        if not Capture.isOpened():
            _log.error("No se pudo abrir ninguna cámara")
            return

        _log.info("Cámara abierta correctamente")

        while self.hilo_activo:
            ret, self.frame = Capture.read()
            if ret:
                if _streaming_activo and _id_personal_stream:
                    global _frame_counter
                    _frame_counter += 1
                    if _frame_counter % 3 == 0:
                        _, buf = cv2.imencode('.jpg', self.frame,
                                             [cv2.IMWRITE_JPEG_QUALITY, 60])
                        frame_bytes = buf.tobytes()
                        if _frame_counter == 3:
                            _log.info(f"Streaming iniciado → id={_id_personal_stream} url={URL_WEB}")
                        def _push(data):
                            try:
                                resp = _requests.post(
                                    f"{URL_WEB}/ProWork/ProWork_Personal/ReceiveFrame?idPersonal={_id_personal_stream}",
                                    data=data,
                                    headers={
                                        "Content-Type": "application/octet-stream",
                                        "X-Stream-Secret": STREAMING_SECRET
                                    },
                                    timeout=1
                                )
                                if _frame_counter % 30 == 0:
                                    _log.info(f"Frame #{_frame_counter} enviado — HTTP {resp.status_code}")
                            except Exception as e:
                                _log.warning(f"Error enviando frame #{_frame_counter}: {e}")
                        threading.Thread(target=_push, args=(frame_bytes,), daemon=True).start()
                elif _frame_counter == 0 and not _streaming_activo:
                    pass  # streaming aún no solicitado, sin log
                # --- face_recognition (fallos no deben cortar el video) ---
                try:
                    frame_reducido = cv2.resize(self.frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_frame_reducido = frame_reducido[:, :, ::-1]
                    self.ubicacion_cara = face_recognition.face_locations(rgb_frame_reducido)
                except Exception as e:
                    _log.error(f"face_recognition error: {e}", exc_info=True)
                    self.ubicacion_cara = []

                # --- Convertir frame a QImage y emitir ---
                try:
                    Image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    FlippedImage = cv2.flip(Image, 1)
                    h, w, ch = FlippedImage.shape
                    bytes_per_line = ch * w
                    ConvertToQtFormat = QImage(
                        FlippedImage.tobytes(), w, h, bytes_per_line,
                        QImage.Format_RGB888
                    )
                    Pic = ConvertToQtFormat.scaled(1015, 1015, Qt.KeepAspectRatio)
                    self.ImageUpdate.emit(Pic)
                except Exception as e:
                    _log.error(f"QImage/emit error: {e}", exc_info=True)

        Capture.release()
        _log.info("Cámara liberada")
    
    def get_frame(self):
        buffer = cv2.imencode('.png', self.frame)[1]
        encoded = base64.b64encode(buffer)
        decoded = encoded.decode('utf-8')
        return decoded

    def stop(self):
        self.hilo_activo = False
        self.quit()