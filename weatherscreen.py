from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QGraphicsBlurEffect, QMessageBox, QComboBox, QCompleter
)
from PyQt6.QtGui import QFontDatabase, QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal,QTimer, QStringListModel

class ShowWeather(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        

