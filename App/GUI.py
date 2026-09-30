import time
from urllib.parse import quote
from collections import namedtuple
from Constantes import *
from PyQt5.QtGui import *
from Camara import Camara
from PyQt5.QtCore import *
from Usuario import usuario
from Manager import Manager
from PyQt5.QtWidgets import *
from Solicitudes import solicitud
from Dialogs.Comision import Comision
from Dialogs.Actividades import Actividades
from Dialogs.Justificaciones import Justificaciones
from Tracker import Tracker

class GUI(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(TEXTO_TITULO_VENTANA)
        self.resize(ANCHO_VENTANA, ALTO_VENTANA)
        if True:
            usuario.obtener_parametros()
            usuario.obtener_programas()
            self.componentes_visuales()
            self.componentes_funcionales()
        else:
            QMessageBox.warning(self, 'Error', "Error inicializando aplicación, consulte con su supervisor")

    def componentes_visuales(self) -> None:
        widget = QWidget(self)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Panel izquierdo — Cámara
        cam_widget = QWidget()
        cam_widget.setStyleSheet("background-color: #000000;")
        cam_inner = QVBoxLayout(cam_widget)
        cam_inner.setContentsMargins(8, 8, 8, 8)
        cam_inner.setAlignment(Qt.AlignCenter)
        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setStyleSheet("border: 2px solid #1E293B; background-color: #111827;")
        self.video_label.setAlignment(Qt.AlignCenter)
        cam_inner.addWidget(self.video_label)
        cam_inner.addStretch()
        main_layout.addWidget(cam_widget, stretch=1)

        # Panel derecho — Controles
        right = QWidget()
        right.setFixedWidth(300)
        right.setStyleSheet("background-color: #1E293B;")
        self.layout_gui = QVBoxLayout(right)
        self.layout_gui.setContentsMargins(20, 24, 20, 24)
        self.layout_gui.setSpacing(10)

        # Info de usuario
        nombre = f"{usuario.personal.NOMBRE} {usuario.personal.APELLIDO_PATERNO}"
        lbl_nombre = QLabel(nombre)
        lbl_nombre.setStyleSheet("color: #F8FAFC; font-size: 15px; font-weight: bold; font-family: Arial;")
        lbl_nombre.setWordWrap(True)
        self.layout_gui.addWidget(lbl_nombre)

        lbl_cargo = QLabel(usuario.personal.CARGO)
        lbl_cargo.setStyleSheet("color: #94A3B8; font-size: 12px; font-family: Arial;")
        self.layout_gui.addWidget(lbl_cargo)

        lbl_area = QLabel(usuario.personal.AREA)
        lbl_area.setStyleSheet("color: #94A3B8; font-size: 12px; font-family: Arial;")
        self.layout_gui.addWidget(lbl_area)

        self.lbl_tard = QLabel()
        self.lbl_tard.setStyleSheet(
            "color: #FCA5A5; font-size: 12px; font-weight: bold; font-family: Arial;"
            "background-color: #450A0A; border-radius: 4px; padding: 3px 6px;"
        )
        self.lbl_tard.hide()
        self.layout_gui.addWidget(self.lbl_tard)
        self._actualizar_tardanza()

        # Indicador de estado de jornada
        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(10, 10)
        self.status_dot.setStyleSheet("background-color: #475569; border-radius: 5px;")
        status_row.addWidget(self.status_dot)
        self.status_text = QLabel("Jornada no iniciada")
        self.status_text.setStyleSheet("color: #64748B; font-size: 11px; font-family: Arial;")
        status_row.addWidget(self.status_text)
        status_row.addStretch()
        self.layout_gui.addLayout(status_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #334155; border: none; max-height: 1px; margin: 4px 0;")
        self.layout_gui.addWidget(sep)

        # Fecha y hora
        self.fecha_hora_label = QLabel()
        self.fecha_hora_label.setStyleSheet(
            "color: #F8FAFC; font-size: 30px; font-weight: bold; font-family: Arial;"
        )
        self.fecha_hora_label.setAlignment(Qt.AlignCenter)
        self.layout_gui.addWidget(self.fecha_hora_label)

        self.sesion_label = QLabel("Sesión: —")
        self.sesion_label.setStyleSheet("color: #64748B; font-size: 11px; font-family: Arial;")
        self.sesion_label.setAlignment(Qt.AlignCenter)
        self.layout_gui.addWidget(self.sesion_label)
        self.sesion_inicio_ts = None

        # Minutos improductivos
        self.minutos_improductivos_label = QLabel("Minutos Improductivos: 0")
        self.minutos_improductivos_label.setStyleSheet(
            "color: #FCD34D; font-size: 12px; font-weight: bold; font-family: Arial;"
            "background-color: #451A03; border-radius: 4px; padding: 5px 8px;"
        )
        self.minutos_improductivos_label.setAlignment(Qt.AlignCenter)
        self.layout_gui.addWidget(self.minutos_improductivos_label)

        self.layout_gui.addStretch()

        # Separador y etiqueta de acciones
        sep_acc = QFrame()
        sep_acc.setFrameShape(QFrame.HLine)
        sep_acc.setStyleSheet("background-color: #334155; border: none; max-height: 1px;")
        self.layout_gui.addWidget(sep_acc)
        lbl_acciones = QLabel("ACCIONES")
        lbl_acciones.setStyleSheet(
            "color: #475569; font-size: 10px; font-weight: bold; font-family: Arial; letter-spacing: 1px;"
        )
        self.layout_gui.addWidget(lbl_acciones)

        # Plantilla de estilo para botones
        _btn = (
            "QPushButton {{ color: white; border: none; border-radius: 6px; "
            "padding: 10px 16px; font-size: 13px; font-weight: bold; font-family: Arial; "
            "background-color: {bg}; min-height: 36px; }} "
            "QPushButton:hover {{ background-color: {hv}; }} "
            "QPushButton:pressed {{ background-color: {pr}; }} "
            "QPushButton:disabled {{ background-color: #334155; color: #64748B; }}"
        )

        self.iniciar_boton = QPushButton(TEXTO_BOTON_INICIAR)
        self.iniciar_boton.setStyleSheet(_btn.format(bg='#16A34A', hv='#15803D', pr='#166534'))
        self.iniciar_boton.setCursor(Qt.PointingHandCursor)
        self.iniciar_boton.clicked.connect(self.iniciar_jornada)
        self.layout_gui.addWidget(self.iniciar_boton)

        self.finalizar_boton = QPushButton(TEXTO_BOTON_FINALIZAR)
        self.finalizar_boton.setStyleSheet(_btn.format(bg='#DC2626', hv='#B91C1C', pr='#991B1B'))
        self.finalizar_boton.setCursor(Qt.PointingHandCursor)
        self.finalizar_boton.clicked.connect(self.finalizar_jornada)
        self.finalizar_boton.setEnabled(False)
        self.layout_gui.addWidget(self.finalizar_boton)

        self.refrigerio_boton = QPushButton("Iniciar refrigerio")
        self.refrigerio_boton.setStyleSheet(_btn.format(bg='#D97706', hv='#B45309', pr='#92400E'))
        self.refrigerio_boton.setCursor(Qt.PointingHandCursor)
        self.refrigerio_boton.clicked.connect(self.evento_refrigerios)
        self.refrigerio_boton.setEnabled(False)
        self.layout_gui.addWidget(self.refrigerio_boton)

        self.justificar_boton = QPushButton(TEXTO_BOTON_JUSTIFICAR)
        self.justificar_boton.setStyleSheet(_btn.format(bg='#2563EB', hv='#1D4ED8', pr='#1E40AF'))
        self.justificar_boton.setCursor(Qt.PointingHandCursor)
        self.justificar_boton.clicked.connect(self.evento_justificaciones)
        self.justificar_boton.setEnabled(False)
        self.layout_gui.addWidget(self.justificar_boton)

        self.comision_boton = QPushButton("Comisión")
        self.comision_boton.setStyleSheet(_btn.format(bg='#7C3AED', hv='#6D28D9', pr='#5B21B6'))
        self.comision_boton.setCursor(Qt.PointingHandCursor)
        self.comision_boton.clicked.connect(self.evento_comision)
        self.comision_boton.setEnabled(False)
        self.layout_gui.addWidget(self.comision_boton)

        self.actividades_boton = QPushButton("Actividades")
        self.actividades_boton.setStyleSheet(_btn.format(bg='#0891B2', hv='#0E7490', pr='#155E75'))
        self.actividades_boton.setCursor(Qt.PointingHandCursor)
        self.actividades_boton.clicked.connect(self.evento_actividades)
        self.actividades_boton.setEnabled(False)
        self.layout_gui.addWidget(self.actividades_boton)

        main_layout.addWidget(right)
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def componentes_funcionales(self) -> None:
        # Manager -> Controles
        self.manager = Manager()
        self.manager.conseguir_metadatos()

        # Camara -> Image
        self.camara = Camara()
        self.camara.start()
        self.camara.ImageUpdate.connect(self.ImageUpdateSlot)

        # Tracker -> Programas (se inicia recién al comenzar la jornada, ver iniciar_jornada)
        self.tracker = Tracker()

        self._ts_ausencia = None  # timestamp cuando desaparece la cara
        self._ts_sin_cara = None   # timestamp del primer frame sin cara (período de gracia)
        self._ts_ausencia_last_tick = None  # último tick para acumulación incremental
        self._minutos_ultimo_update = 0  # último entero de minutos sincronizado con el servidor
        self._notif_inicio_refrig = False  # evita repetir el aviso durante el mismo minuto
        self._notif_fin_refrig = False

        # Timer 1 segundo
        timer_1s = QTimer(self)
        timer_1s.timeout.connect(self.timer_1s)
        timer_1s.start(1000)

        # Verificación -> Timer
        self.verificar_timer = QTimer(self)
        self.verificar_timer.timeout.connect(self.verificar_asistencia)
        # self.verificar_timer.start(int(usuario.parametros.VERIFICACION_EVENTO_MINUTOS) * 60000)

        # Actualización -> Timer
        actualizacion_timer = QTimer(self)
        actualizacion_timer.timeout.connect(self.actualizar_minutos_improductivos)
        # actualizacion_timer.start(int(usuario.parametros.ACTUALIZACION_MINUTOS_IMPRODUCTIVOS)  * 60000)

        # Avances -> Timer
        avances_timer = QTimer(self)
        avances_timer.timeout.connect(self.mandar_avances)
        # avances_timer.start(int(usuario.parametros.VERIFICACION_AVANCE_MINUTOS) * 60000)

        # Programas -> Timer
        programas_timer = QTimer(self)
        programas_timer.timeout.connect(self.verificacion_programas)
        programas_timer.start(1 * 60000)

        # Supervisión -> Timer (captura periódica de cámara y pantalla)
        self.supervision_timer = QTimer(self)
        self.supervision_timer.timeout.connect(self.evento_supervision)
        self.supervision_timer.start(SUPERVISION_INTERVALO_MINUTOS * 60000)
    
    def timer_1s(self) -> None:
        self.mostrar_fecha_hora()
        self._actualizar_sesion()
        if self.sesion_inicio_ts is not None:
            self._verificar_presencia_camara()
            if (usuario.asistencia is not None
                    and usuario.asistencia.HORA_INICIO_REFRIGERIO_PRG != ''
                    and usuario.asistencia.HORA_FIN_REFRIGERIO_PRG != ''):
                self.verificar_refrigerios()

    def _actualizar_sesion(self) -> None:
        if self.sesion_inicio_ts is not None:
            elapsed = int(time.time() - self.sesion_inicio_ts)
            h, rem = divmod(elapsed, 3600)
            m, s = divmod(rem, 60)
            self.sesion_label.setText(f"Sesión: {h:02d}:{m:02d}:{s:02d}")

    _GRACE_SECONDS = 5  # segundos sin cara antes de contar como ausencia

    def _verificar_presencia_camara(self) -> None:
        if not usuario.estado:  # no contar ausencia durante refrigerio u otras pausas
            return
        if not self.camara.ubicacion_cara:
            if self._ts_sin_cara is None:
                self._ts_sin_cara = time.time()
            if self._ts_ausencia is None and (time.time() - self._ts_sin_cara) >= self._GRACE_SECONDS:
                self._ts_ausencia = self._ts_sin_cara
                self._ts_ausencia_last_tick = self._ts_ausencia
                self._minutos_ultimo_update = int(usuario.minutos_ausentes)
                self.status_dot.setStyleSheet("background-color: #EF4444; border-radius: 5px;")
                self.status_text.setText("No detectado en cámara")
            elif self._ts_ausencia is not None:
                now = time.time()
                usuario.minutos_ausentes += (now - self._ts_ausencia_last_tick) / 60
                self._ts_ausencia_last_tick = now
                self.minutos_improductivos_label.setText("Minutos Improductivos: {}".format(int(usuario.minutos_ausentes)))
                if int(usuario.minutos_ausentes) > self._minutos_ultimo_update:
                    self._minutos_ultimo_update = int(usuario.minutos_ausentes)
                    self._sincronizar_minutos()
        else:
            self._ts_sin_cara = None
            self.status_dot.setStyleSheet("background-color: #22C55E; border-radius: 5px;")
            self.status_text.setText("Jornada activa")
            if self._ts_ausencia is not None:
                now = time.time()
                usuario.minutos_ausentes += (now - self._ts_ausencia_last_tick) / 60
                total_minutos_ausencia = (now - self._ts_ausencia) / 60
                self._ts_ausencia = None
                self._ts_ausencia_last_tick = None
                self.minutos_improductivos_label.setText("Minutos Improductivos: {}".format(int(usuario.minutos_ausentes)))
                self._sincronizar_minutos()
                intervalo = int(usuario.parametros.VERIFICACION_EVENTO_MINUTOS or 5)
                if total_minutos_ausencia >= intervalo:
                    self.grabar_evento(ID_EVENTO_AUSENTE,
                        DESCRIPCION_EVENTO_AUSENTE.format(intervalo),
                        now, self.camara.get_frame())

    def ImageUpdateSlot(self, Image) -> None:
        self.video_label.setPixmap(QPixmap.fromImage(Image))

    def _actualizar_tardanza(self) -> None:
        tardanza_min = None
        if usuario.asistencia is not None:
            tardanza_min = getattr(usuario.asistencia, 'TARDANZA', None)
        if tardanza_min:
            horas, mins = divmod(int(tardanza_min), 60)
            texto_tard = f"Tardanza: {horas}h {mins}m" if horas else f"Tardanza: {mins}m"
            self.lbl_tard.setText(texto_tard)
            self.lbl_tard.show()
        else:
            self.lbl_tard.hide()

    def grabar_evento(self, id_evento: str, descripcion_evento: str, tiempo: float, prueba: str, captura_pc: str = None):
        if captura_pc is None:
            captura_pc = self.manager.capturar_pantalla()
        json = {
                "ID_EVENTO": id_evento,
                "DESCRIPCION_EVENTO": descripcion_evento,
                "HORA_REGISTRO": time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(tiempo)),
                "ID_PERSONAL": usuario.personal.ID_PERSONAL,
                "ID_EMPRESA": usuario.personal.ID_EMPRESA,
                "PRUEBA": prueba,
                "CAPTURA_PC": captura_pc,
                "NOMBRE_PC": self.manager.nombre_pc,
                "IP_PRIVADA": self.manager.ip_privada,
                "IP_PUBLICA": self.manager.ip_publica}
        estado, _ = solicitud("POST", URL + '/evento', json)
        if estado:
            return True
        else:
            return False

    def mostrar_fecha_hora(self) -> None:
        self.fecha_hora_label.setText(QDateTime.currentDateTime().toString('dd/MM/yyyy \n hh:mm:ss'))

    def _mostrar_aviso(self, titulo: str, mensaje: str) -> None:
        # No modal: si la persona aún no regresó no hay quién cierre el diálogo,
        # y un QMessageBox modal (exec_) detiene el timer_1s hasta que se cierra.
        aviso = QMessageBox(QMessageBox.Information, titulo, mensaje, QMessageBox.Ok, self)
        aviso.setWindowModality(Qt.NonModal)
        aviso.setAttribute(Qt.WA_DeleteOnClose)
        aviso.show()

    def verificar_refrigerios(self) -> None:
        hora_actual = QDateTime.currentDateTime().toString('hh:mm')
        if hora_actual >= usuario.asistencia.HORA_INICIO_REFRIGERIO_PRG:
            if not self._notif_inicio_refrig:
                self._notif_inicio_refrig = True
                usuario.estado = False
                usuario.hora_inicio_refrigerio = QDateTime.currentDateTime()
                self.refrigerio_boton.setEnabled(True)
                self._mostrar_aviso('Importante', 'Inicio de hora de refrigerio programada')
                self.grabar_evento(ID_EVENTO_INICIO_REFRIGERIO, DESCRIPCION_EVENTO_INICIO_REFRIGERIO, time.time(), self.camara.get_frame())
        else:
            self._notif_inicio_refrig = False

        if hora_actual >= usuario.asistencia.HORA_FIN_REFRIGERIO_PRG:
            if not self._notif_fin_refrig:
                self._notif_fin_refrig = True
                usuario.estado = True
                self.refrigerio_boton.setEnabled(False)
                self._mostrar_aviso('Importante', 'Fin de hora de refrigerio programada')
                self.grabar_evento(ID_EVENTO_FIN_REFRIGERIO, DESCRIPCION_EVENTO_FIN_REFRIGERIO, time.time(), self.camara.get_frame())
                url = URL + '/refrigerio/inicia/{0}'.format(usuario.personal.ID_PERSONAL)
                solicitud("PUT", url)
        else:
            self._notif_fin_refrig = False
    
    def iniciar_jornada(self) -> None:
        json_data = {
            'ID_PERSONAL': usuario.personal.ID_PERSONAL
        }
        url = URL + f'/asistencia/inicia'
        estado, respuesta = solicitud("POST", url, json=json_data)
        if estado:
            usuario.estado = True
            self.sesion_inicio_ts = time.time()
            self.status_dot.setStyleSheet("background-color: #22C55E; border-radius: 5px;")
            self.status_text.setText("Jornada activa")
            datos_asistencia = respuesta.get('datos') if isinstance(respuesta, dict) else None
            if isinstance(datos_asistencia, dict):
                actual = usuario.asistencia._asdict() if usuario.asistencia is not None else {}
                actual.update(datos_asistencia)
                usuario.asistencia = namedtuple("Asistencia", actual.keys())(*actual.values())
                self._actualizar_tardanza()
            if not self.tracker.isRunning():
                self.tracker.start()
            self.grabar_evento(ID_EVENTO_INICIA, DESCRIPCION_EVENTO_INICIA, time.time(), self.camara.get_frame())
            self.iniciar_boton.setEnabled(False)
            self.finalizar_boton.setEnabled(True)
            self.justificar_boton.setEnabled(True)
            self.comision_boton.setEnabled(True)
            self.actividades_boton.setEnabled(True)
            self.obtener_minutos_improductivos()
        else:
            QMessageBox.warning(self, 'Error', respuesta['mensaje'])
        
    def finalizar_jornada(self) -> None:
        if self.grabar_evento(ID_EVENTO_FINALIZA, DESCRIPCION_EVENTO_FINALIZA, time.time(), self.camara.get_frame()):
            url = URL + '/asistencia/finaliza/{0}'.format(usuario.personal.ID_PERSONAL)
            estado, respuesta = solicitud("PUT", url)
            if estado:
                self.status_dot.setStyleSheet("background-color: #EF4444; border-radius: 5px;")
                self.status_text.setText("Jornada finalizada")
                self.sesion_inicio_ts = None
                self.camara.stop()
                self.tracker.stop()
                self.close()
            else:
                QMessageBox.warning(self, 'Error', respuesta['mensaje'])
    
    def evento_refrigerios(self) -> None:
        if not usuario.refrigerio:
            url = URL + '/refrigerio/inicia/{0}'.format(usuario.personal.ID_PERSONAL)
            estado, respuesta = solicitud("PUT", url)
            if estado:
                usuario.refrigerio = True
                usuario.hora_inicio_refrigerio = QDateTime.currentDateTime()
                self.refrigerio_boton.setText("Finalizar refrigerio")
                self.grabar_evento(ID_EVENTO_INICIO_REFRIGERIO, DESCRIPCION_EVENTO_INICIO_REFRIGERIO, time.time(), self.camara.get_frame())
            else:
                QMessageBox.warning(self, 'Error', respuesta['mensaje'])
        else:
            url = URL + '/refrigerio/finaliza/{0}'.format(usuario.personal.ID_PERSONAL)
            estado, respuesta = solicitud("PUT", url)
            if estado:
                usuario.refrigerio = False
                self.grabar_evento(ID_EVENTO_FIN_REFRIGERIO, DESCRIPCION_EVENTO_FIN_REFRIGERIO, time.time(), self.camara.get_frame())
                self.layout_gui.removeWidget(self.refrigerio_boton)
                self.refrigerio_boton = None
            else:
                QMessageBox.warning(self, 'Error', respuesta['mensaje'])
    
    def evento_justificaciones(self):
        jutificacion_ventana = Justificaciones(self)
        jutificacion_ventana.show()

    def registrar_justificacion(self, id, justificacion):
        self.grabar_evento(ID_EVENTO_JUSTIFICADO, DESCRIPCION_EVENTO_JUSTIFICADO + justificacion, time.time(), self.camara.get_frame())

    def evento_supervision(self) -> None:
        if usuario.estado:
            self.grabar_evento(ID_EVENTO_SUPERVISION, DESCRIPCION_EVENTO_SUPERVISION, time.time(), self.camara.get_frame())

    def registrar_comision(self, razon, fecha_hora_regreso: QDateTime):
        self.grabar_evento(ID_EVENTO_COMISION, DESCRIPCION_EVENTO_COMISION + razon, time.time(), self.camara.get_frame())
        ms_restantes = QDateTime.currentDateTime().msecsTo(fecha_hora_regreso)
        if ms_restantes > 0:
            QTimer.singleShot(ms_restantes, self.finalizar_comision)

    def finalizar_comision(self):
        self._resetear_ausencia()
        usuario.estado = True

    def evento_comision(self):
        comision_ventana = Comision(self)
        comision_ventana.show()

    def evento_actividades(self):
        actividades_ventana = Actividades(self)
        actividades_ventana.show()

    def verificar_asistencia(self):
        if not usuario.justificado and usuario.estado and not self.camara.ubicacion_cara and usuario.timestap_inicio is None:
            self.verificar_timer.setInterval(1000)
            usuario.timestap_inicio = time.time()
        elif not usuario.justificado and usuario.estado and self.camara.ubicacion_cara and usuario.timestap_inicio is not None:
            usuario.timestap_fin = time.time()
            horas, rem = divmod(usuario.timestap_fin - usuario.timestap_inicio, 3600)
            minutos, segundos = divmod(rem, 60)
            print("{:0>2}:{:0>2}:{:05.2f}".format(int(horas), int(minutos), segundos))

            usuario.minutos_ausentes += minutos
            usuario.timestap_inicio = None
            self.verificar_timer.setInterval(int(usuario.parametros.VERIFICACION_EVENTO_MINUTOS)  * 60000)
            self.actualizar_minutos_improductivos()
            if int(minutos) >= int(usuario.parametros.VERIFICACION_EVENTO_MINUTOS):
                if self.grabar_evento(ID_EVENTO_AUSENTE, DESCRIPCION_EVENTO_AUSENTE.format(usuario.parametros.VERIFICACION_EVENTO_MINUTOS), usuario.timestap_inicio, self.camara.get_frame()):
                    QMessageBox.information(self, 'Importante', 'Evento de ausencia enviado')
                else:
                    QMessageBox.warning(self, 'Error', 'No se pudo enviar el evento')
    
    def _resetear_ausencia(self):
        self._ts_sin_cara = None
        self._ts_ausencia = None
        self._ts_ausencia_last_tick = None
        self._minutos_ultimo_update = int(usuario.minutos_ausentes)

    def _sincronizar_minutos(self):
        url = URL + '/minutos/improductivos/{0}/{1}'.format(usuario.personal.ID_PERSONAL, int(usuario.minutos_ausentes))
        solicitud("PUT", url)

    def aplicar_descuento_refrigerio(self, minutos: int) -> None:
        if minutos <= 0:
            return
        usuario.minutos_ausentes = max(usuario.minutos_ausentes - minutos, 0)
        self.minutos_improductivos_label.setText("Minutos Improductivos: {0}".format(int(usuario.minutos_ausentes)))
        self._minutos_ultimo_update = int(usuario.minutos_ausentes)
        self._sincronizar_minutos()

    def obtener_minutos_improductivos(self):
        fecha_inicio = quote(time.strftime('%d-%m-%y', time.localtime(self.sesion_inicio_ts)))
        url = URL + '/minutos/improductivos/{0}/{1}'.format(usuario.personal.ID_PERSONAL, fecha_inicio)
        estado, respuesta = solicitud("GET", url)
        if estado:
            minutos = respuesta['datos'].get('MINUTOS_IMPRODUCTIVOS', 0) or 0
            usuario.minutos_ausentes = float(minutos)
            self.minutos_improductivos_label.setText("Minutos Improductivos: {}".format(int(usuario.minutos_ausentes)))

    def actualizar_minutos_improductivos(self):
        self.minutos_improductivos_label.setText("Minutos Improductivos: {0}".format(int(usuario.minutos_ausentes)))
        url = URL + '/minutos/improductivos/{0}/{1}'.format(usuario.personal.ID_PERSONAL, int(usuario.minutos_ausentes))
        estado, respuesta = solicitud("PUT", url)
        if estado:
            QMessageBox.information(self, 'Importante', respuesta['mensaje'])
        else:
            QMessageBox.warning(self, 'Error', respuesta['mensaje'])
    
    def mandar_avances(self):
        if usuario.estado:
            if self.grabar_evento(ID_EVENTO_AVANCE, DESCRIPCION_EVENTO_AVANCE, time.time(), self.camara.get_frame()):
                QMessageBox.information(self, 'Importante', 'Avance enviado')
            else:
                QMessageBox.warning(self, 'Error', 'No se pudo enviar el avance')

    def verificacion_programas(self):
        programas = self.manager.detectar_programas(usuario.programas)
        paginas = self.manager.detectar_paginas(usuario.paginas)
        detectados = programas + paginas
        if len(detectados) > 0 and usuario.estado:
            descripcion = '{}: {}'.format(DESCRIPCION_EVENTO_PROGRAMAS, ', '.join(detectados))
            if self.grabar_evento(ID_EVENTO_PROGRAMAS, descripcion, time.time(), self.camara.get_frame()):
                if len(detectados) == 1:
                    QMessageBox.warning(self, 'Error', 'El siguiente programa se ha detectado: {0}'.format(detectados[0]))
                else:
                    QMessageBox.warning(self, 'Error', 'Se detectaron múltiples programas en uso')
            else:
                QMessageBox.warning(self, 'Error', 'No se pudo enviar el evento')

    def closeEvent(self, a0: QCloseEvent) -> None:
        try:
            solicitud("DELETE", f"{URL}/streaming/{usuario.personal.ID_PERSONAL}")
        except Exception:
            pass
        return super().closeEvent(a0)