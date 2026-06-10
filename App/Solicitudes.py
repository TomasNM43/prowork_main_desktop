import requests
from requests.exceptions import Timeout, RequestException

def solicitud(method: str, url: str, json: dict = None, timeout: int = None) -> tuple:
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=json, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, json=json, timeout=timeout)
        else:
            return False, {'mensaje': "Método HTTP no soportado"}

        # Verificar el código de estado HTTP
        if response.status_code == 200:
            try:
                r = response.json()
                if r.get('exito', False):
                    return True, r
                else:
                    return False, r
            except ValueError:
                return False, {'mensaje': "Respuesta del servidor no es un JSON válido"}
        else:
            return False, {'mensaje': f"Error HTTP {response.status_code}"}

    except Timeout:
        return False, {'mensaje': "Error con el servicio web"}
    except RequestException as e:
        return False, {'mensaje': str(e)}
