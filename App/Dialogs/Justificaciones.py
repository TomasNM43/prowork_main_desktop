import datetime
from Solicitudes import solicitud
from PyQt5.QtWidgets import *
from Usuario import usuario
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Constantes import *

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
QLabel#lbl_mins {
    color: #1D4ED8;
    font-size: 13px;
    font-weight: bold;
    background-color: #DBEAFE;
    border-radius: 4px;
    padding: 4px 10px;
}
QLabel#lbl_countdown {
    color: #0F172A;
    font-size: 52px;
    font-weight: bold;
    font-family: Arial;
}
QComboBox {
    background-color: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #1E293B;
    min-height: 20px;
}
QComboBox:focus { border: 1.5px solid #2563EB; }
QPushButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
    font-family: Arial;
    min-height: 36px;
}
QPushButton:hover { background-color: #1D4ED8; }
QPushButton:pressed { background-color: #1E40AF; }
QPushButton#btn_regreso { background-color: #475569; }
QPushButton#btn_regreso:hover { background-color: #334155; }
"""

class Justificaciones(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.pantalla_principal = parent
        self.setWindowTitle("Registrar salida justificada")
        self.setFixedSize(400, 300)
        self.setStyleSheet(_STYLE)
        self.componentes_visuales()

    def componentes_visuales(self) -> None:
        self.id_justifica, self.descripciones, self.minutos = self.obtener_justificaciones()

        root = QVBoxLayout()
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(0)

        self.stack = QStackedWidget()

        # --- Página 0: Selección ---
        page0 = QWidget()
        p0 = QVBoxLayout(page0)
        p0.setContentsMargins(0, 0, 0, 0)
        p0.setSpacing(12)

        titulo = QLabel("Registrar Justificación")
        titulo.setObjectName('lbl_titulo')
        p0.addWidget(titulo)

        p0.addWidget(QLabel('Tipo de justificación'))
        self.justifica_combobox = QComboBox(self)
        self.justifica_combobox.addItems(self.descripciones)
        self.justifica_combobox.activated.connect(
            lambda: self.actualizar_minutos(self.minutos[self.justifica_combobox.currentIndex()])
        )
        p0.addWidget(self.justifica_combobox)

        self.minutos_label = QLabel("Minutos Justificados: {0}".format(self.minutos[0]))
        self.minutos_label.setObjectName('lbl_mins')
        p0.addWidget(self.minutos_label)
        p0.addStretch()

        self.justificar_boton = QPushButton('Justificar')
        self.justificar_boton.setCursor(Qt.PointingHandCursor)
        self.justificar_boton.clicked.connect(self.registrar_justificacion)
        p0.addWidget(self.justificar_boton)
        self.stack.addWidget(page0)

        # --- Página 1: Conteo regresivo ---
        page1 = QWidget()
        p1 = QVBoxLayout(page1)
        p1.setContentsMargins(0, 0, 0, 0)
        p1.setSpacing(12)
        p1.setAlignment(Qt.AlignCenter)

        lbl_espera = QLabel("Tiempo restante")
        lbl_espera.setAlignment(Qt.AlignCenter)
        p1.addWidget(lbl_espera)

        self.minutos_restantes_label = QLabel("00:00:00")
        self.minutos_restantes_label.setObjectName('lbl_countdown')
        self.minutos_restantes_label.setAlignment(Qt.AlignCenter)
        p1.addWidget(self.minutos_restantes_label)

        self.regreso_boton = QPushButton("Regresar")
        self.regreso_boton.setObjectName('btn_regreso')
        self.regreso_boton.setCursor(Qt.PointingHandCursor)
        self.regreso_boton.clicked.connect(self.regreso)
        p1.addWidget(self.regreso_boton)
        self.stack.addWidget(page1)

        root.addWidget(self.stack)
        self.setLayout(root)

    def obtener_justificaciones(self) -> None:
        url = URL + '/justifica/' + usuario.personal.ID_INSTITUCION
        id_justifica = []
        descripciones = []
        minutos = []
        estado, respuesta = solicitud("GET", url)

        if estado:
            data = respuesta['datos']
            for i in data:
                id_justifica.append(i['ID_JUSTIFICACION'])
                descripciones.append(i['DESCRIPCION'])
                minutos.append(i['MINUTOS_JUSTIFICADOS'])
            return id_justifica, descripciones, minutos
        else:
            QMessageBox.warning(self, 'Error', respuesta['mensaje'])
    
    def actualizar_minutos(self, minutos):
        self.minutos_label.setText("Minutos Justificados: {0}".format(minutos))

    def registrar_justificacion(self):
        self.pantalla_principal.registrar_justificacion(
            self.id_justifica[self.justifica_combobox.currentIndex()],
            self.descripciones[self.justifica_combobox.currentIndex()]
        )
        self.minutos_inicial = self.minutos[self.justifica_combobox.currentIndex()] * 60
        self.minutos_actuales = self.minutos_inicial

        timer_1s = QTimer(self)
        timer_1s.timeout.connect(self.timer_1s)
        timer_1s.start(1000)

        self.stack.setCurrentIndex(1)
        usuario.estado = False

    def timer_1s(self):
        self.minutos_actuales -= 1
        if self.minutos_actuales == 0:
            self.regreso()
        else:
            self.minutos_restantes_label.setText(str(datetime.timedelta(seconds=self.minutos_actuales)))

    def regreso(self):
        minutos_finales = int((self.minutos_inicial - self.minutos_actuales)/60)
        usuario.minutos_ausentes += minutos_finales
        self.pantalla_principal.actualizar_minutos_improductivos()
        usuario.estado = True
        self.close()