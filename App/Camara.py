import cv2
import base64
import face_recognition

from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Camara(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hilo_activo = None
        self.ubicacion_cara = []

    def run(self):
        self.hilo_activo = True
        Capture = cv2.VideoCapture(0)
        while self.hilo_activo:
            ret, self.frame = Capture.read()
            if ret:
                frame_reducido = cv2.resize(self.frame, (0, 0), fx=0.25, fy=0.25)
                rgb_frame_reducido = frame_reducido[:, :, ::-1]
                self.ubicacion_cara = face_recognition.face_locations(rgb_frame_reducido)

                Image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                FlippedImage = cv2.flip(Image, 1)
                ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0],
                                           QImage.Format_RGB888)
                Pic = ConvertToQtFormat.scaled(1015, 1015, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Pic)
    
    def get_frame(self):
        buffer = cv2.imencode('.png', self.frame)[1]
        encoded = base64.b64encode(buffer)
        decoded = encoded.decode('utf-8')
        return decoded

    def stop(self):
        self.hilo_activo = False
        self.quit()