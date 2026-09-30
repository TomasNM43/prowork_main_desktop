# Runtime hook: parcha face_recognition_models para apuntar a sys._MEIPASS
# cuando la app corre desde un bundle de PyInstaller.
import sys
import os

if hasattr(sys, '_MEIPASS'):
    import face_recognition_models

    _models_dir = os.path.join(sys._MEIPASS, 'face_recognition_models', 'models')

    face_recognition_models.pose_predictor_model_location = \
        lambda: os.path.join(_models_dir, 'shape_predictor_68_face_landmarks.dat')
    face_recognition_models.pose_predictor_five_point_model_location = \
        lambda: os.path.join(_models_dir, 'shape_predictor_5_face_landmarks.dat')
    face_recognition_models.face_recognition_model_location = \
        lambda: os.path.join(_models_dir, 'dlib_face_recognition_resnet_model_v1.dat')
    face_recognition_models.cnn_face_detector_model_location = \
        lambda: os.path.join(_models_dir, 'mmod_human_face_detector.dat')
