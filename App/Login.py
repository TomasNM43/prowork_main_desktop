import threading
import Camara
import PermisoCamera
import Constantes
import Versiones
from datetime import datetime

from Usuario import usuario
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Solicitudes import solicitud
from collections import namedtuple

_STYLE = """
QDialog {
    background-color: #F1F5F9;
}
QLabel {
    color: #1E293B;
    font-family: Arial;
    font-size: 13px;
}
QLabel#lbl_titulo {
    color: #FFFFFF;
    font-size: 26px;
    font-weight: bold;
}
QLabel#lbl_subtitulo {
    color: #CBD5E1;
    font-size: 11px;
}
QLineEdit {
    background-color: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #1E293B;
    min-height: 20px;
}
QLineEdit:focus {
    border: 1.5px solid #2563EB;
}
QPushButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
    font-family: Arial;
    min-height: 38px;
}
QPushButton:hover {
    background-color: #1D4ED8;
}
QPushButton:pressed {
    background-color: #1E40AF;
}
QCheckBox {
    color: #64748B;
    font-size: 11px;
    font-family: Arial;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1.5px solid #CBD5E1;
    border-radius: 3px;
    background: white;
}
QCheckBox::indicator:checked {
    background-color: #2563EB;
    border-color: #2563EB;
}
QLabel#lbl_error {
    color: #DC2626;
    font-size: 12px;
    background-color: #FEF2F2;
    border: 1px solid #FCA5A5;
    border-radius: 4px;
    padding: 6px 8px;
}
"""

class Login(QDialog):
    _ANCHO = 420
    _ALTO_BASE = 530

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('ProWork — Iniciar Sesión')
        self.setFixedSize(self._ANCHO, self._ALTO_BASE)
        self.setStyleSheet(_STYLE)
        self.componentes_visuales()
        geo = QApplication.primaryScreen().availableGeometry()
        self.move(geo.center() - self.rect().center())

    def componentes_visuales(self) -> None:
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Cabecera oscura
        header = QWidget()
        header.setFixedHeight(160)
        header.setStyleSheet("background-color: #0F172A;")
        h_layout = QVBoxLayout(header)
        h_layout.setAlignment(Qt.AlignCenter)
        h_layout.setSpacing(4)

        badge = QLabel('PW')
        badge.setFixedSize(54, 54)
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(
            "background-color: #2563EB; color: white; font-size: 19px; "
            "font-weight: bold; font-family: Arial; border-radius: 27px;"
        )
        h_layout.addWidget(badge, alignment=Qt.AlignHCenter)

        titulo = QLabel('ProWork')
        titulo.setObjectName('lbl_titulo')
        titulo.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(titulo)
        subtitulo = QLabel('Sistema de Control de Asistencia')
        subtitulo.setObjectName('lbl_subtitulo')
        subtitulo.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(subtitulo)
        root.addWidget(header)

        # Formulario
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(44, 28, 44, 28)
        form_layout.setSpacing(6)

        form_layout.addWidget(QLabel('Empresa'))
        self.empresa_input = QLineEdit()
        self.empresa_input.setPlaceholderText('Ingrese su empresa')
        form_layout.addWidget(self.empresa_input)

        form_layout.addSpacing(6)
        form_layout.addWidget(QLabel('Usuario'))
        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText('Ingrese su usuario')
        form_layout.addWidget(self.usuario_input)

        form_layout.addSpacing(6)
        form_layout.addWidget(QLabel('Contraseña'))
        self.contra_input = QLineEdit()
        self.contra_input.setPlaceholderText('Ingrese su contraseña')
        self.contra_input.setEchoMode(QLineEdit.Password)
        self.contra_input.returnPressed.connect(self.validar_usuario)
        form_layout.addWidget(self.contra_input)

        mostrar_cb = QCheckBox('Mostrar contraseña')
        mostrar_cb.setCursor(Qt.PointingHandCursor)
        mostrar_cb.toggled.connect(
            lambda checked: self.contra_input.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )
        form_layout.addWidget(mostrar_cb)

        self.error_label = QLabel()
        self.error_label.setObjectName('lbl_error')
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        form_layout.addWidget(self.error_label)

        form_layout.addSpacing(8)
        btn = QPushButton('Iniciar Sesión')
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.validar_usuario)
        form_layout.addWidget(btn)

        root.addWidget(form_container)
        self.setLayout(root)
        self.setTabOrder(self.empresa_input, self.usuario_input)
        self.setTabOrder(self.usuario_input, self.contra_input)
        self.setTabOrder(self.contra_input, btn)

    def validar_usuario(self) -> None:
        self.error_label.hide()
        self.setFixedHeight(self._ALTO_BASE)
        json = {
            'ID_EMPRESA': self.empresa_input.text(),
            'USUARIO': self.usuario_input.text(),
            'PASSWORD_PERSONAL': self.contra_input.text()
        }
        print(json)
        url = Constantes.URL + '/personal'
        estado, respuesta = solicitud("POST", url, json, 10)
        print(estado, respuesta)
        if estado:
            if 'datos' in respuesta:
                diccionario = respuesta['datos']
                asistencia_dict = respuesta.get('asistencia') or {}
                asistencia = asistencia_dict.get('FECHA_HORA_FIN_REAL')
                print(asistencia)
                fecha_hora = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
                if asistencia:
                    if asistencia > fecha_hora:
                        permitido, aviso = Versiones.verificar_version()
                        if not permitido:
                            self._mostrar_error(aviso)
                            return
                        if aviso:
                            QMessageBox.information(self, 'Actualización disponible', aviso)
                        Versiones.registrar_version(diccionario.get('ID_PERSONAL'), diccionario.get('ID_EMPRESA'))
                        usuario.personal = namedtuple("Personal", diccionario.keys())(*diccionario.values())
                        if asistencia_dict:
                            usuario.asistencia = namedtuple("Asistencia", asistencia_dict.keys())(*asistencia_dict.values())
                        Camara._id_personal_stream = usuario.personal.ID_PERSONAL
                        PermisoCamera.iniciar_polling_permisos(
                            usuario.personal.ID_PERSONAL,
                            self.parent()
                        )
                        QMessageBox.information(self, 'Éxito', f"Bienvenido '{usuario.personal.NOMBRE}'")
                        self.accept()
                    else:
                        self._mostrar_error("Asistencia no válida para el día de hoy.")
                else:
                    self._mostrar_error("No se encontró asistencia programada para hoy.")
            else:
                self._mostrar_error(respuesta.get('mensaje', 'Credenciales incorrectas.'))
        else:
            QMessageBox.warning(self, 'Error de conexión', respuesta.get('mensaje', 'No se pudo conectar al servidor.'))

    def _mostrar_error(self, mensaje: str) -> None:
        self.error_label.setText(mensaje)
        self.error_label.show()
        self._ajustar_alto()

    def _ajustar_alto(self) -> None:
        # El diálogo crece lo necesario para que el mensaje de error se vea completo
        self.layout().activate()
        alto = max(self._ALTO_BASE, self.layout().totalHeightForWidth(self._ANCHO))
        self.setFixedHeight(alto)


#20481
#120220000010
#123456