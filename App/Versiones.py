import socket

import Constantes
from AppLogger import get_logger
from Solicitudes import solicitud

_log = get_logger('versiones')


def _a_tupla(version: str) -> tuple:
    try:
        return tuple(int(p) for p in str(version).strip().split('.'))
    except ValueError:
        return (0,)


def verificar_version() -> tuple:
    """
    Consulta la última versión publicada en el servidor.
    Devuelve (permitido, mensaje). Solo bloquea si la versión instalada es menor a la
    última y esta está marcada como obligatoria. Si el servidor no responde o no tiene
    el endpoint, no bloquea el inicio de sesión.
    """
    estado, respuesta = solicitud("GET", Constantes.URL + '/version/ultima', timeout=5)
    if not estado:
        _log.warning("No se pudo consultar la última versión: %s", respuesta.get('mensaje'))
        return True, ""

    ultima = respuesta.get('datos') or {}
    version_servidor = ultima.get('VERSION')
    if not version_servidor or _a_tupla(version_servidor) <= _a_tupla(Constantes.VERSION):
        return True, ""

    mensaje = (f"Hay una nueva versión disponible ({version_servidor}). "
               f"Versión instalada: {Constantes.VERSION}.")
    if ultima.get('DESCRIPCION'):
        mensaje += f"\n\n{ultima['DESCRIPCION']}"
    if ultima.get('URL_DESCARGA'):
        mensaje += f"\n\nDescarga: {ultima['URL_DESCARGA']}"
    obligatoria = str(ultima.get('OBLIGATORIA', 0)) in ('1', 'True', 'true')
    return (not obligatoria), mensaje


def registrar_version(id_personal: str, id_empresa: str) -> None:
    """Guarda en la BD la versión que usa este personal. Nunca interrumpe el flujo."""
    try:
        json = {
            'ID_PERSONAL': id_personal,
            'ID_EMPRESA': id_empresa,
            'VERSION': Constantes.VERSION,
            'NOMBRE_PC': socket.gethostname(),
        }
        estado, respuesta = solicitud("POST", Constantes.URL + '/version/registrar', json, 5)
        if not estado:
            _log.warning("No se pudo registrar la versión: %s", respuesta.get('mensaje'))
    except Exception:
        _log.warning("Error registrando la versión", exc_info=True)
