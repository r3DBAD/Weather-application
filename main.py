import sys
import os
import requests
import datetime
from geopy.geocoders import Nominatim
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QStackedWidget, QGraphicsBlurEffect,QMessageBox
)
from PyQt6.QtGui import QFontDatabase, QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize

class WeatherApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Weather4You')
        self.setGeometry(100, 100, 1280, 720)
        container_widget = QWidget(self)
        layout = QVBoxLayout(container_widget)

        font_id = QFontDatabase.addApplicationFont("sources/fonts/try-clother.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"

        self.image_path, greeting = self.set_bg()

        self.background_label = QLabel(self)
        pixmap = QPixmap(self.image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.background_label.setScaledContents(True)
        self.blur_effect = QGraphicsBlurEffect(self)
        self.blur_effect.setBlurRadius(5)
        self.background_label.setGraphicsEffect(self.blur_effect)

        self.title_label = QLabel(greeting, self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"""
            font-size: 72px;
            color: white;
            font-family: {font_family};
            font-weight: bold;
            background: transparent;
        """)
        self.title_label.setMinimumHeight(200)

        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        input_layout = QHBoxLayout()
        input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.location_input = QLineEdit(self)
        self.location_input.setPlaceholderText("Введите город или нажмите на кнопку геолокации")
        self.location_input.setFixedWidth(700)
        input_layout.addWidget(self.location_input)

        layout.addLayout(input_layout)
        layout.addStretch(1)

        self.addWidget(container_widget)
        self.location_button = QPushButton(self)
        self.location_button.setIcon(QIcon("sources/icons/location.png"))  
        self.location_button.setIconSize(QSize(50, 50)) 
        self.location_button.setFixedSize(60, 60)  
        self.location_button.setStyleSheet("border: none; background: transparent;")
        self.location_button.clicked.connect(self.set_location_from_ip)
        self.location_button.setParent(self)  
        self.location_button.show()  
        with open("style.qss", "r") as file:
            self.setStyleSheet(file.read())

    def set_bg(self):
        now = datetime.datetime.now()
        month = now.month
        hour = now.hour

        if month in [12, 1, 2]:
            season = 'winter'
        elif month in [3, 4, 5]:
            season = 'spring'
        elif month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'autumn'

        if 6 <= hour < 12:
            time_day = 'morning'
            greeting = 'Доброе утро!'
        elif 12 <= hour < 18:
            time_day = 'day'
            greeting = 'Добрый день!'
        elif 18 <= hour < 22:
            time_day = 'evening'
            greeting = 'Добрый вечер!'
        else:
            time_day = 'evening'
            greeting = 'Доброй ночи!'

        bg_image = f'sources/backgrounds/{season}_{time_day}.jpg'
        return bg_image, greeting

    def get_current_location(self):
        try:
            response = requests.get("https://ipinfo.io/json", timeout=5)
            data = response.json()
            loc = data.get("loc", "")  
            if not loc:
                return ""

            latitude, longitude = loc.split(",")  
            geolocator = Nominatim(user_agent="weather_app")
            location = geolocator.reverse((latitude, longitude), language="ru")

            if location and "city" in location.raw["address"]:
                return location.raw["address"]["city"]
            return ""
        
        except Exception as e:
            print("Ошибка:", e)
            return ""

    def set_location_from_ip(self):
        city = self.get_current_location()
        if city:
            self.location_input.setText(city)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить местоположение")

    def resizeEvent(self, event):
        self.background_label.setGeometry(self.rect())
        self.location_button.move(self.width() - 80, self.height() - 80)

app = QApplication(sys.argv)
window = WeatherApp()
window.show()
sys.exit(app.exec())