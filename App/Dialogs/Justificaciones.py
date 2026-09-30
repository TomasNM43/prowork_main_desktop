import datetime
import time
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
QComboBox, QLineEdit, QDateTimeEdit {
    background-color: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #1E293B;
    min-height: 20px;
}
QComboBox:focus, QLineEdit:focus, QDateTimeEdit:focus { border: 1.5px solid #2563EB; }
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
    _TIPO_DEFAULT  = "Interno"
    _TIPO_PERMISO  = "Permiso"
    _TIPO_COMISION = "Comision"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.pantalla_principal = parent
        self.setWindowTitle("Registrar salida justificada")
        self.setFixedSize(400, 430)
        self.setStyleSheet(_STYLE)
        self.componentes_visuales()

    def componentes_visuales(self) -> None:
        result = self.obtener_justificaciones()
        self.id_justifica, self.descripciones, self.minutos = result if result else ([], [], [])

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

        p0.addWidget(QLabel('Tipo'))
        self.tipo_combobox = QComboBox(self)
        self.tipo_combobox.addItems([self._TIPO_DEFAULT, self._TIPO_PERMISO, self._TIPO_COMISION])
        self.tipo_combobox.currentIndexChanged.connect(self._on_tipo_changed)
        p0.addWidget(self.tipo_combobox)

        # Campos dinámicos según el tipo seleccionado
        self.campos_stack = QStackedWidget()

        # Campos para tipo Default: lista de justificaciones de la empresa
        default_widget = QWidget()
        dw = QVBoxLayout(default_widget)
        dw.setContentsMargins(0, 0, 0, 0)
        dw.setSpacing(8)
        dw.addWidget(QLabel('Justificación'))
        self.justifica_combobox = QComboBox(self)
        self.justifica_combobox.addItems(self.descripciones)
        self.justifica_combobox.activated.connect(
            lambda: self.actualizar_minutos(self.minutos[self.justifica_combobox.currentIndex()])
        )
        dw.addWidget(self.justifica_combobox)
        self.minutos_label = QLabel("Minutos Justificados: {0}".format(self.minutos[0] if self.minutos else 0))
        self.minutos_label.setObjectName('lbl_mins')
        dw.addWidget(self.minutos_label)
        self.campos_stack.addWidget(default_widget)

        # Campos para Permiso / Comisión: descripción libre + hora de retorno
        libre_widget = QWidget()
        lw = QVBoxLayout(libre_widget)
        lw.setContentsMargins(0, 0, 0, 0)
        lw.setSpacing(8)

        self.retorno_refrigerio_checkbox = QCheckBox('Retorno de refrigerio (opcional)')
        self.retorno_refrigerio_checkbox.toggled.connect(self._on_retorno_refrigerio_toggled)
        lw.addWidget(self.retorno_refrigerio_checkbox)

        self.retorno_refrigerio_info = QLabel()
        self.retorno_refrigerio_info.setWordWrap(True)
        self.retorno_refrigerio_info.setVisible(False)
        lw.addWidget(self.retorno_refrigerio_info)

        self.descripcion_label_libre = QLabel('Descripción')
        lw.addWidget(self.descripcion_label_libre)
        self.descripcion_input = QLineEdit(self)
        self.descripcion_input.setPlaceholderText('Describa la razón de salida')
        lw.addWidget(self.descripcion_input)
        self.hora_retorno_label_libre = QLabel('Hora de retorno')
        lw.addWidget(self.hora_retorno_label_libre)
        self.fecha_hora_input = QDateTimeEdit(self)
        self.fecha_hora_input.setDateTime(QDateTime.currentDateTime())
        self.fecha_hora_input.setCalendarPopup(True)
        lw.addWidget(self.fecha_hora_input)
        self.campos_stack.addWidget(libre_widget)

        p0.addWidget(self.campos_stack)
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

        # --- Página 2: Espera de aprobación del supervisor ---
        page2 = QWidget()
        p2 = QVBoxLayout(page2)
        p2.setContentsMargins(0, 0, 0, 0)
        p2.setSpacing(12)
        p2.setAlignment(Qt.AlignCenter)

        self.espera_supervisor_label = QLabel('Esperando aprobación del supervisor...')
        self.espera_supervisor_label.setAlignment(Qt.AlignCenter)
        self.espera_supervisor_label.setWordWrap(True)
        p2.addWidget(self.espera_supervisor_label)

        cancelar_espera_boton = QPushButton('Cancelar')
        cancelar_espera_boton.setObjectName('btn_regreso')
        cancelar_espera_boton.setCursor(Qt.PointingHandCursor)
        cancelar_espera_boton.clicked.connect(self._cancelar_espera_refrigerio)
        p2.addWidget(cancelar_espera_boton)
        self.stack.addWidget(page2)

        root.addWidget(self.stack)
        self.setLayout(root)

    def _on_tipo_changed(self, index: int) -> None:
        self.campos_stack.setCurrentIndex(0 if index == 0 else 1)
        es_permiso = (index == 1)
        self.retorno_refrigerio_checkbox.setVisible(es_permiso)
        if not es_permiso:
            self.retorno_refrigerio_checkbox.setChecked(False)

    def _on_retorno_refrigerio_toggled(self, checked: bool) -> None:
        self.hora_retorno_label_libre.setVisible(not checked)
        self.fecha_hora_input.setVisible(not checked)
        self.retorno_refrigerio_info.setVisible(checked)
        if checked:
            self.descripcion_label_libre.setText('Motivo del recuento')
            self.descripcion_input.setPlaceholderText('Describa por qué solicita el recuento')
            hora_salida = usuario.hora_inicio_refrigerio
            texto_hora = hora_salida.toString('dd/MM/yyyy hh:mm') if hora_salida else 'No registrada'
            self.retorno_refrigerio_info.setText(
                'Salió a refrigerio: {0}\nSe enviará una solicitud a su supervisor para descontar '
                'los minutos improductivos generados por el retraso.'.format(texto_hora)
            )
        else:
            self.descripcion_label_libre.setText('Descripción')
            self.descripcion_input.setPlaceholderText('Describa la razón de salida')

    def obtener_justificaciones(self):
        url = URL + '/justifica/' + usuario.personal.ID_EMPRESA
        id_justifica, descripciones, minutos = [], [], []
        estado, respuesta = solicitud("GET", url)
        if estado:
            for i in respuesta['datos']:
                id_justifica.append(i['ID_JUSTIFICACION'])
                descripciones.append(i['DESCRIPCION'])
                minutos.append(i['MINUTOS_JUSTIFICADOS'])
            return id_justifica, descripciones, minutos
        else:
            QMessageBox.warning(self, 'Error', respuesta['mensaje'])
            return [], [], []

    def actualizar_minutos(self, minutos) -> None:
        self.minutos_label.setText("Minutos Justificados: {0}".format(minutos))

    def registrar_justificacion(self) -> None:
        tipo = self.tipo_combobox.currentText()

        if tipo == self._TIPO_PERMISO and self.retorno_refrigerio_checkbox.isChecked():
            self._solicitar_retorno_refrigerio()
            return

        if tipo == self._TIPO_COMISION:
            self._solicitar_comision()
            return

        ahora = datetime.datetime.now()

        if tipo == self._TIPO_DEFAULT:
            if not self.id_justifica:
                QMessageBox.warning(self, 'Atención', 'No hay justificaciones disponibles.')
                return
            idx = self.justifica_combobox.currentIndex()
            id_justifica = self.id_justifica[idx]
            descripcion = self.descripciones[idx]
            mins = self.minutos[idx]
            fecha_retorno = ahora + datetime.timedelta(minutes=mins)
            segundos_restantes = mins * 60
        else:
            descripcion = self.descripcion_input.text().strip()
            if not descripcion:
                QMessageBox.warning(self, 'Atención', 'Ingrese una descripción.')
                return
            id_justifica = None
            retorno_qt = self.fecha_hora_input.dateTime()
            segundos_restantes = max(QDateTime.currentDateTime().secsTo(retorno_qt), 0)
            fecha_retorno = retorno_qt.toPyDateTime()

        url = URL + '/grabar_justifica'
        data = {
            'ID_EMPRESA':          usuario.personal.ID_EMPRESA,
            'ID_PERSONAL':         usuario.personal.ID_PERSONAL,
            'TIPO_JUSTIFICACION':  "Ausencia justificada",
            'FECHA_HORA_REGISTRO': ahora.strftime("%Y-%m-%d %H:%M:%S"),
            'FECHA_HORA_RETORNO':  fecha_retorno.strftime("%Y-%m-%d %H:%M:%S"),
            'DESCRIPCION':         descripcion,
            'ID_JUSTIFICACION':    id_justifica,
        }

        estado, respuesta = solicitud("POST", url, json=data)
        if not estado:
            QMessageBox.warning(self, 'Error', respuesta.get('mensaje', 'Error al registrar'))
            return

        id_grabado = respuesta.get('datos', {}).get('ID_JUSTIFICACION', id_justifica)

        self.pantalla_principal.registrar_justificacion(id_grabado, descripcion)

        self.pantalla_principal._resetear_ausencia()
        usuario.estado = False

        self._segundos_restantes = segundos_restantes
        self.minutos_restantes_label.setText(str(datetime.timedelta(seconds=self._segundos_restantes)))
        timer = QTimer(self)
        timer.timeout.connect(self._timer_1s)
        timer.start(1000)
        self.stack.setCurrentIndex(1)

    def _timer_1s(self) -> None:
        self._segundos_restantes -= 1
        if self._segundos_restantes <= 0:
            self.regreso()
        else:
            self.minutos_restantes_label.setText(str(datetime.timedelta(seconds=self._segundos_restantes)))

    def regreso(self) -> None:
        self.pantalla_principal._resetear_ausencia()
        usuario.estado = True
        self.close()

    def _solicitar_retorno_refrigerio(self) -> None:
        hora_salida_qdt = usuario.hora_inicio_refrigerio
        if hora_salida_qdt is None:
            QMessageBox.warning(self, 'Atención', 'No se registró la hora de salida a refrigerio.')
            return

        descripcion = self.descripcion_input.text().strip()
        if not descripcion:
            QMessageBox.warning(self, 'Atención', 'Ingrese el motivo del recuento.')
            return

        ahora_qdt = QDateTime.currentDateTime()
        fin_prg = QDateTime(ahora_qdt.date(), QTime.fromString(usuario.asistencia.HORA_FIN_REFRIGERIO_PRG, 'hh:mm'))
        minutos_solicitados = max(fin_prg.secsTo(ahora_qdt) // 60, 0)

        data = {
            'ID_EMPRESA': usuario.personal.ID_EMPRESA,
            'NOMBRE_PERSONAL': "{0} {1}".format(usuario.personal.NOMBRE, usuario.personal.APELLIDO_PATERNO),
            'HORA_SALIDA_REFRIGERIO': hora_salida_qdt.toString('yyyy-MM-dd hh:mm:ss'),
            'HORA_SOLICITUD': ahora_qdt.toString('yyyy-MM-dd hh:mm:ss'),
            'MINUTOS_SOLICITADOS': minutos_solicitados,
            'DESCRIPCION': descripcion,
        }
        url = URL + '/refrigerio/solicitar-retorno/' + usuario.personal.ID_PERSONAL
        estado, respuesta = solicitud("POST", url, json=data)
        if not estado:
            QMessageBox.warning(self, 'Error', respuesta.get('mensaje', 'No se pudo enviar la solicitud'))
            return

        self._minutos_solicitados_refrigerio = minutos_solicitados
        self._descripcion_refrigerio = descripcion
        self._hora_solicitud_refrigerio = ahora_qdt
        self.espera_supervisor_label.setText(
            'Esperando aprobación del supervisor...\nMinutos a descontar: {0}'.format(minutos_solicitados)
        )
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._consultar_estado_retorno_refrigerio)
        self._poll_timer.start(3000)
        self.stack.setCurrentIndex(2)

    def _consultar_estado_retorno_refrigerio(self) -> None:
        url = URL + '/refrigerio/estado-retorno/' + usuario.personal.ID_PERSONAL
        estado, respuesta = solicitud("GET", url)
        if not estado:
            return
        estado_solicitud = respuesta.get('datos', {}).get('ESTADO')
        if estado_solicitud == 'aceptado':
            self._poll_timer.stop()
            self._grabar_justificacion_refrigerio()
            self.pantalla_principal.aplicar_descuento_refrigerio(self._minutos_solicitados_refrigerio)
            self.pantalla_principal.grabar_evento(
                ID_EVENTO_RETORNO_REFRIGERIO_APROBADO,
                DESCRIPCION_EVENTO_RETORNO_REFRIGERIO_APROBADO + " ({0} min)".format(self._minutos_solicitados_refrigerio),
                time.time(), self.pantalla_principal.camara.get_frame()
            )
            QMessageBox.information(self, 'Aprobado', 'El supervisor aceptó su solicitud. Se descontaron los minutos improductivos.')
            self.close()
        elif estado_solicitud == 'rechazado':
            self._poll_timer.stop()
            QMessageBox.warning(self, 'Rechazado', 'El supervisor rechazó la solicitud de retorno de refrigerio.')
            self.close()

    def _grabar_justificacion_refrigerio(self) -> None:
        ahora_qdt = QDateTime.currentDateTime()
        data = {
            'ID_EMPRESA':          usuario.personal.ID_EMPRESA,
            'ID_PERSONAL':         usuario.personal.ID_PERSONAL,
            'TIPO_JUSTIFICACION':  "Retorno de refrigerio tardío aprobado",
            'FECHA_HORA_REGISTRO': self._hora_solicitud_refrigerio.toString('yyyy-MM-dd hh:mm:ss'),
            'FECHA_HORA_RETORNO':  ahora_qdt.toString('yyyy-MM-dd hh:mm:ss'),
            'DESCRIPCION':         'Retorno de refrigerio ({0} min): {1}'.format(
                self._minutos_solicitados_refrigerio, self._descripcion_refrigerio),
            'ID_JUSTIFICACION':    None,
        }
        estado, respuesta = solicitud("POST", URL + '/grabar_justifica', json=data)
        if not estado:
            QMessageBox.warning(self, 'Error', respuesta.get('mensaje', 'No se pudo registrar la justificación'))

    def _cancelar_espera_refrigerio(self) -> None:
        if hasattr(self, '_poll_timer'):
            self._poll_timer.stop()
        self.close()

    def _solicitar_comision(self) -> None:
        descripcion = self.descripcion_input.text().strip()
        if not descripcion:
            QMessageBox.warning(self, 'Atención', 'Ingrese una descripción.')
            return

        self._descripcion_comision = descripcion
        self._fecha_hora_regreso_comision = self.fecha_hora_input.dateTime()
        ahora_qdt = QDateTime.currentDateTime()
        self._hora_solicitud_comision = ahora_qdt

        data = {
            'ID_EMPRESA': usuario.personal.ID_EMPRESA,
            'NOMBRE_PERSONAL': "{0} {1}".format(usuario.personal.NOMBRE, usuario.personal.APELLIDO_PATERNO),
            'RAZON': descripcion,
            'HORA_SOLICITUD': ahora_qdt.toString('yyyy-MM-dd hh:mm:ss'),
            'HORA_REGRESO': self._fecha_hora_regreso_comision.toString('yyyy-MM-dd hh:mm:ss'),
        }
        url = URL + '/comision/solicitar/' + usuario.personal.ID_PERSONAL
        estado, respuesta = solicitud("POST", url, json=data)
        if not estado:
            QMessageBox.warning(self, 'Error', respuesta.get('mensaje', 'No se pudo enviar la solicitud'))
            return

        self.espera_supervisor_label.setText('Esperando aprobación del supervisor...')
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._consultar_estado_comision)
        self._poll_timer.start(3000)
        self.stack.setCurrentIndex(2)

    def _consultar_estado_comision(self) -> None:
        url = URL + '/comision/estado/' + usuario.personal.ID_PERSONAL
        estado, respuesta = solicitud("GET", url)
        if not estado:
            return
        estado_solicitud = respuesta.get('datos', {}).get('ESTADO')
        if estado_solicitud == 'aceptado':
            self._poll_timer.stop()
            self._grabar_justificacion_comision()
            self.pantalla_principal.registrar_comision(self._descripcion_comision, self._fecha_hora_regreso_comision)
            self.pantalla_principal._resetear_ausencia()
            usuario.estado = False
            QMessageBox.information(self, 'Aprobado', 'El supervisor aceptó su solicitud de comisión.')
            self.close()
        elif estado_solicitud == 'rechazado':
            self._poll_timer.stop()
            QMessageBox.warning(self, 'Rechazado', 'El supervisor rechazó la solicitud de comisión.')
            self.close()

    def _grabar_justificacion_comision(self) -> None:
        data = {
            'ID_EMPRESA':          usuario.personal.ID_EMPRESA,
            'ID_PERSONAL':         usuario.personal.ID_PERSONAL,
            'TIPO_JUSTIFICACION':  "Ausencia justificada",
            'FECHA_HORA_REGISTRO': self._hora_solicitud_comision.toString('yyyy-MM-dd hh:mm:ss'),
            'FECHA_HORA_RETORNO':  self._fecha_hora_regreso_comision.toString('yyyy-MM-dd hh:mm:ss'),
            'DESCRIPCION':         self._descripcion_comision,
            'ID_JUSTIFICACION':    None,
        }
        estado, respuesta = solicitud("POST", URL + '/grabar_justifica', json=data)
        if not estado:
            QMessageBox.warning(self, 'Error', respuesta.get('mensaje', 'No se pudo registrar la justificación'))