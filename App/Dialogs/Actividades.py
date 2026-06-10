from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Constantes import *
from Usuario import usuario
from Solicitudes import solicitud

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
QLabel#lbl_desc {
    color: #1E293B;
    font-size: 13px;
    background-color: #E2E8F0;
    border-radius: 4px;
    padding: 6px 10px;
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
QComboBox:focus { border: 1.5px solid #0891B2; }
QLineEdit {
    background-color: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #1E293B;
    min-height: 20px;
}
QLineEdit:focus { border: 1.5px solid #0891B2; }
QCheckBox {
    color: #374151;
    font-size: 13px;
    font-family: Arial;
    spacing: 6px;
}
QPushButton {
    background-color: #0891B2;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: bold;
    font-family: Arial;
    min-height: 36px;
}
QPushButton:hover { background-color: #0E7490; }
QPushButton:pressed { background-color: #155E75; }
QPushButton#btn_refrescar { background-color: #475569; }
QPushButton#btn_refrescar:hover { background-color: #334155; }
"""

class Actividades(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Actividades")
        self.setFixedSize(480, 320)
        self.setStyleSheet(_STYLE)
        self.componentes()
        self.listar_actividades()

    def componentes(self):
        root = QVBoxLayout()
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(12)

        titulo = QLabel("Actividades asignadas")
        titulo.setObjectName('lbl_titulo')
        root.addWidget(titulo)

        root.addWidget(QLabel('Seleccionar actividad'))
        self.actividades_combobox = QComboBox(self)
        root.addWidget(self.actividades_combobox)

        self.descripcion_label = QLabel()
        self.descripcion_label.setObjectName('lbl_desc')
        self.descripcion_label.setWordWrap(True)
        root.addWidget(self.descripcion_label)

        # Estado y avance en fila
        row = QHBoxLayout()
        row.setSpacing(16)

        estado_col = QVBoxLayout()
        estado_col.setSpacing(4)
        estado_col.addWidget(QLabel('Completada'))
        self.estado = QCheckBox()
        estado_col.addWidget(self.estado)
        row.addLayout(estado_col)

        avance_col = QVBoxLayout()
        avance_col.setSpacing(4)
        avance_col.addWidget(QLabel('Avance'))
        self.avance_input = QLineEdit()
        self.avance_input.setPlaceholderText('% de avance')
        avance_col.addWidget(self.avance_input)
        row.addLayout(avance_col, stretch=1)

        root.addLayout(row)
        root.addStretch()

        btns = QHBoxLayout()
        btns.setSpacing(10)
        refrescar_boton = QPushButton('Refrescar')
        refrescar_boton.setObjectName('btn_refrescar')
        refrescar_boton.setCursor(Qt.PointingHandCursor)
        refrescar_boton.clicked.connect(self.listar_actividades)
        btns.addWidget(refrescar_boton)
        guardar_boton = QPushButton('Guardar')
        guardar_boton.setCursor(Qt.PointingHandCursor)
        guardar_boton.clicked.connect(self.guardar)
        btns.addWidget(guardar_boton)
        root.addLayout(btns)

        self.setLayout(root)
    
    def listar_actividades(self):
        def actualizar_datos(descripcion, estado, avance):
            self.descripcion_label.setText("Descripcion: {0}".format(descripcion))
            self.estado.setChecked(estado)
            self.avance_input.setPlaceholderText(avance)
        url = URL + '/actividades/' + usuario.personal.ID_PERSONAL
        estado, respuesta = solicitud("GET", url)
        actividades = []
        descripciones = []
        estados = []
        avance = []
        if estado:
            data = respuesta['datos']
            for i in data:
                actividades.append(i['TITULO_ACTIVIDAD'])
                descripciones.append(i['DESCRIPCION_ACTIVIDAD'])
                if i['ESTADO_ACTIVIDAD'] == "Pendiente":
                    estados.append(False)
                else:
                    estados.append(True)
                avance.append(i['AVANCE_ACTIVIDAD'])
            self.actividades_combobox.clear()
            self.actividades_combobox.addItems(actividades)
            self.descripcion_label.setText("Descripcion: {0}".format(descripciones[0]))
            self.estado.setChecked(estados[0])
            self.avance_input.setPlaceholderText(avance[0])
            self.actividades_combobox.activated.connect(lambda: actualizar_datos(descripciones[self.actividades_combobox.currentIndex()], estados[self.actividades_combobox.currentIndex()], avance[self.actividades_combobox.currentIndex()]))
        else:
            QMessageBox.warning(self, 'Error', respuesta['mensaje'])
    
    def guardar(self):
        self.close()