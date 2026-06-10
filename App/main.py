import sys

from GUI import GUI
from Login import Login
from PyQt5.QtWidgets import *

if __name__ == '__main__':
    App = QApplication(sys.argv)
    login = Login()
    if login.exec() == 1:
        main = GUI()
        main.show()
        sys.exit(App.exec())