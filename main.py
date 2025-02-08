import sys
import requests
import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout, QStackedWidget
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class HomeScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.title_label = QLabel("Weather App")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Arial", 20))
        layout.addWidget(self.title_label)
        
        self.location_input = QLineEdit(self)
        self.location_input.setPlaceholderText("Введите город или нажмите на 'Моё местоположение'")
        layout.addWidget(self.location_input)
        
        self.button_layout = QHBoxLayout()
        
        self.get_weather_btn = QPushButton("Погода сейчас")
        self.get_weather_btn.clicked.connect(self.show_weather)
        self.button_layout.addWidget(self.get_weather_btn)
        
        self.get_week_weather_btn = QPushButton("Прогноз на неделю")
        self.get_week_weather_btn.clicked.connect(self.show_week_weather)
        self.button_layout.addWidget(self.get_week_weather_btn)
        
        self.use_location_btn = QPushButton("Моё местоположение")
        self.use_location_btn.clicked.connect(self.set_location_from_ip)
        self.button_layout.addWidget(self.use_location_btn)
        
        layout.addLayout(self.button_layout)
        
    def show_weather(self):
        city = self.location_input.text()
        if not city:
            QMessageBox.warning(self, "Ошибка", "Введите горд или используйте кнопку местоположения")
            return
        self.stacked_widget.weather_screen.fetch_weather(city)
        self.stacked_widget.setCurrentIndex(1)
        
    def show_week_weather(self):
        city = self.location_input.text()
        if not city:
            QMessageBox.warning(self, "Ошибка", "Введите город или используйте кнопку местоположения")
            return
        self.stacked_widget.week_weather_screen.fetch_week_weather(city)
        self.stacked_widget.setCurrentIndex(2)
        
    def set_location_from_ip(self):
        city = self.get_current_location()
        if city:
            self.location_input.setText(city)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить местоположение")
    
    def get_current_location(self):
        try:
            response = requests.get("https://ipinfo.io")
            data = response.json()
            return data.get("city", "")
        except:
            return ""


class WeatherScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.weather_result = QLabel("Здесь будет погода")
        self.weather_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weather_result.setFont(QFont("Arial", 14))
        self.weather_result.setWordWrap(True)
        layout.addWidget(self.weather_result)
        
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(self.back_button)
    
    def fetch_weather(self, city):
        api_key = ""
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        try:
            response = requests.get(url)
            data = response.json()
            if data["cod"] != 200:
                raise ValueError(data["message"])
            temp = data["main"]["temp"]
            weather = data["weather"][0]["description"]
            city_name = data["name"]
            self.weather_result.setText(f"Город: {city_name}\nТемпература: {temp}°C\nПогода: {weather.capitalize()}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


class WeekWeatherScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.forecast_result = QLabel("Здесь будет прогноз")
        self.forecast_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.forecast_result.setFont(QFont("Arial", 14))
        self.forecast_result.setWordWrap(True)
        layout.addWidget(self.forecast_result)
        
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(self.back_button)
    
    def fetch_week_weather(self, city):
        api_key = ""
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
        try:
            geo_response = requests.get(geo_url)
            geo_data = geo_response.json()
            if not geo_data:
                raise ValueError("Город не найден")
            lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=metric&exclude=hourly&appid={api_key}"
            response = requests.get(url)
            data = response.json()
            if "daily" not in data:
                raise ValueError("Ошибка загрузки данных")
            forecast = "Прогноз на неделю:\n"
            for day in data["daily"]:
                date = datetime.datetime.fromtimestamp(day["dt"]).strftime("%A, %d %B")
                temp_day = day["temp"]["day"]
                temp_night = day["temp"]["night"]
                weather_desc = day["weather"][0]["description"]
                forecast += f"{date}: День {temp_day}°C, Ночь {temp_night}°C, {weather_desc.capitalize()}\n"
            self.forecast_result.setText(forecast)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))


class WeatherApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1280, 720)
        self.home_screen = HomeScreen(self)
        self.weather_screen = WeatherScreen(self)
        self.week_weather_screen = WeekWeatherScreen(self)
        self.addWidget(self.home_screen)
        self.addWidget(self.weather_screen)
        self.addWidget(self.week_weather_screen)
        self.setCurrentIndex(0)
        
        with open("style.qss", "r") as file:
            self.setStyleSheet(file.read())

app = QApplication(sys.argv)
window = WeatherApp()
window.show()
sys.exit(app.exec())