from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Usuario import usuario
from Solicitudes import solicitud
from Constantes import URL

_STYLE = """
QDialog {
    background-color: #F1F5F9;
}
QLabel {
    color: #374151;
    font-family: Arial;
    font-size: 13px;
}
QLabel#lbl_titulo {
    color: #0F172A;
    font-size: 16px;
    font-weight: bold;
}
QLineEdit, QDateTimeEdit {
    background-color: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #1E293B;
    min-height: 20px;
}
QLineEdit:focus, QDateTimeEdit:focus {
    border: 1.5px solid #7C3AED;
}
QPushButton {
    background-color: #7C3AED;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
    font-family: Arial;
    min-height: 36px;
}
QPushButton:hover { background-color: #6D28D9; }
QPushButton:pressed { background-color: #5B21B6; }
QPushButton#btn_cancelar { background-color: #475569; }
QPushButton#btn_cancelar:hover { background-color: #334155; }
"""

class Comision(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.pantalla_principal = parent
        self.setWindowTitle("Registrar salida por comisión")
        self.setFixedSize(420, 300)
        self.setStyleSheet(_STYLE)
        self.componentes()

    def componentes(self):
        root = QVBoxLayout()
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(12)

        self.stack = QStackedWidget()

        # --- Página 0: formulario de solicitud ---
        page0 = QWidget()
        p0 = QVBoxLayout(page0)
        p0.setContentsMargins(0, 0, 0, 0)
        p0.setSpacing(12)

        titulo = QLabel("Registrar Comisión")
        titulo.setObjectName('lbl_titulo')
        p0.addWidget(titulo)

        p0.addWidget(QLabel('Hora de regreso'))
        self.fecha_hora_input = QDateTimeEdit(self)
        self.fecha_hora_input.setDateTime(QDateTime.currentDateTime())
        self.fecha_hora_input.setCalendarPopup(True)
        p0.addWidget(self.fecha_hora_input)

        p0.addWidget(QLabel('Razón de salida'))
        self.razon_input = QLineEdit()
        self.razon_input.setPlaceholderText('Describa la razón de salida')
        p0.addWidget(self.razon_input)

        p0.addSpacing(4)
        btn = QPushButton('Solicitar comisión')
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.solicitar_comision)
        p0.addWidget(btn)
        self.stack.addWidget(page0)

        # --- Página 1: espera de aprobación del supervisor ---
        page1 = QWidget()
        p1 = QVBoxLayout(page1)
        p1.setContentsMargins(0, 0, 0, 0)
        p1.setSpacing(12)
        p1.setAlignment(Qt.AlignCenter)

        self.espera_label = QLabel('Esperando aprobación del supervisor...')
        self.espera_label.setAlignment(Qt.AlignCenter)
        self.espera_label.setWordWrap(True)
        p1.addWidget(self.espera_label)

        cancelar_boton = QPushButton('Cancelar')
        cancelar_boton.setObjectName('btn_cancelar')
        cancelar_boton.setCursor(Qt.PointingHandCursor)
        cancelar_boton.clicked.connect(self._cancelar_espera)
        p1.addWidget(cancelar_boton)
        self.stack.addWidget(page1)

        root.addWidget(self.stack)
        self.setLayout(root)

    def solicitar_comision(self) -> None:
        razon = self.razon_input.text().strip()
        if not razon:
            QMessageBox.warning(self, 'Atención', 'Ingrese una razón de salida.')
            return

        self._razon = razon
        self._fecha_hora_regreso = self.fecha_hora_input.dateTime()
        ahora_qdt = QDateTime.currentDateTime()
        self._hora_solicitud = ahora_qdt

        data = {
            'ID_EMPRESA': usuario.personal.ID_EMPRESA,
            'NOMBRE_PERSONAL': "{0} {1}".format(usuario.personal.NOMBRE, usuario.personal.APELLIDO_PATERNO),
            'RAZON': razon,
            'HORA_SOLICITUD': ahora_qdt.toString('yyyy-MM-dd hh:mm:ss'),
            'HORA_REGRESO': self._fecha_hora_regreso.toString('yyyy-MM-dd hh:mm:ss'),
        }
        url = URL + '/comision/solicitar/' + usuario.personal.ID_PERSONAL
        estado, respuesta = solicitud("POST", url, json=data)
        if not estado:
            QMessageBox.warning(self, 'Error', respuesta.get('mensaje', 'No se pudo enviar la solicitud'))
            return

        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._consultar_estado_comision)
        self._poll_timer.start(3000)
        self.stack.setCurrentIndex(1)

    def _consultar_estado_comision(self) -> None:
        url = URL + '/comision/estado/' + usuario.personal.ID_PERSONAL
        estado, respuesta = solicitud("GET", url)
        if not estado:
            return
        estado_solicitud = respuesta.get('datos', {}).get('ESTADO')
        if estado_solicitud == 'aceptado':
            self._poll_timer.stop()
            self._grabar_justificacion()
            # La ausencia sólo se permite hasta la hora de regreso; luego se reanuda la verificación de cámara.
            self.pantalla_principal.registrar_comision(self._razon, self._fecha_hora_regreso)
            self.pantalla_principal._resetear_ausencia()
            usuario.estado = False
            QMessageBox.information(self, 'Aprobado', 'El supervisor aceptó su solicitud de comisión.')
            self.close()
        elif estado_solicitud == 'rechazado':
            self._poll_timer.stop()
            QMessageBox.warning(self, 'Rechazado', 'El supervisor rechazó la solicitud de comisión.')
            self.close()

    def _grabar_justificacion(self) -> None:
        data = {
            'ID_EMPRESA':          usuario.personal.ID_EMPRESA,
            'ID_PERSONAL':         usuario.personal.ID_PERSONAL,
            'TIPO_JUSTIFICACION':  'Salida por comisión',
            'FECHA_HORA_REGISTRO': self._hora_solicitud.toString('yyyy-MM-dd hh:mm:ss'),
            'FECHA_HORA_RETORNO':  self._fecha_hora_regreso.toString('yyyy-MM-dd hh:mm:ss'),
            'DESCRIPCION':         self._razon,
            'ID_JUSTIFICACION':    None,
        }
        estado, respuesta = solicitud("POST", URL + '/grabar_justifica', json=data)
        if not estado:
            QMessageBox.warning(self, 'Error', respuesta.get('mensaje', 'No se pudo registrar la justificación'))

    def _cancelar_espera(self) -> None:
        if hasattr(self, '_poll_timer'):
            self._poll_timer.stop()
        self.close()