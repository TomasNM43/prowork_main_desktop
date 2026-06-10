from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Usuario import usuario

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
"""

class Comision(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.pantalla_principal = parent
        self.setWindowTitle("Registrar salida por comisión")
        self.setFixedSize(420, 260)
        self.setStyleSheet(_STYLE)
        self.componentes()

    def componentes(self):
        root = QVBoxLayout()
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(12)

        titulo = QLabel("Registrar Comisión")
        titulo.setObjectName('lbl_titulo')
        root.addWidget(titulo)

        root.addWidget(QLabel('Hora de regreso'))
        self.fecha_hora_input = QDateTimeEdit(self)
        self.fecha_hora_input.setDateTime(QDateTime.currentDateTime())
        self.fecha_hora_input.setCalendarPopup(True)
        root.addWidget(self.fecha_hora_input)

        root.addWidget(QLabel('Razón de salida'))
        self.razon_input = QLineEdit()
        self.razon_input.setPlaceholderText('Describa la razón de salida')
        root.addWidget(self.razon_input)

        root.addSpacing(4)
        btn = QPushButton('Registrar comisión')
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.registrar_comision)
        root.addWidget(btn)

        self.setLayout(root)

    def registrar_comision(self):
        self.pantalla_principal.registrar_comision(self.razon_input.text())
        # Añadir cambio de timer
        # self.pantalla_principal.verificar_timer.setInterval(X)
        usuario.estado = False
        self.close()