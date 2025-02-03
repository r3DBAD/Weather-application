import requests
import matplotlib
import sys
from PyQt6.QtCore import QSize,Qt
from PyQt6.QtWidgets import QApplication,QWidget,QMainWindow,QPushButton,QLabel

class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(1280,720))
        self.setWindowTitle('Weather moon')
        header = QLabel('Выберите город')
app = QApplication(sys.argv)
wind = WeatherApp()
wind.show()
app.exec()