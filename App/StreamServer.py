from flask import Flask, Response
import threading
import cv2

_flask_app = Flask(__name__)
_frame_actual = None
_lock = threading.Lock()

def actualizar_frame(frame):
    global _frame_actual
    with _lock:
        _frame_actual = frame.copy()

def _generar():
    while True:
        with _lock:
            if _frame_actual is None:
                continue
            _, buf = cv2.imencode('.jpg', _frame_actual,
                                  [cv2.IMWRITE_JPEG_QUALITY, 60])
            datos = buf.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + datos + b'\r\n')

@_flask_app.route('/stream')
def stream():
    return Response(_generar(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def iniciar_servidor(puerto=5001):
    _flask_app.run(host='0.0.0.0', port=puerto,
                   threaded=True, use_reloader=False)