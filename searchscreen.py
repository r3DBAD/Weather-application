import sys
import os
import requests
import datetime
from geopy.geocoders import Nominatim
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QGraphicsBlurEffect, QMessageBox, QComboBox, 
    QCompleter
)
from PyQt6.QtGui import (QFontDatabase, QPixmap, QIcon)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QStringListModel

@staticmethod
def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

api_key_path = resource_path("api.txt")
try:
    with open(api_key_path, "r") as f:
        api_key_from_conf = f.read().strip()
except Exception:
    api_key_from_conf = ""

USERNAME_GEONAMES = 'r3dbad'

class SearchScreen(QWidget):
    language_changed = pyqtSignal(str)
    weather_data_ready = pyqtSignal(dict) 
    forecast_data_ready = pyqtSignal(dict)  
    
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.current_language = "RU"  
        self.translations = {
            "RU": {
                "greeting_morning": "Доброе утро!",
                "greeting_day": "Добрый день!",
                "greeting_evening": "Добрый вечер!",
                "greeting_night": "Доброй ночи!",
                "placeholder": "Введите город или нажмите на кнопку геолокации",
                "location_error": "Не удалось определить местоположение",
                "weather_error": "Ошибка",
                "error_city_not_found": "Город не найден",
                "no_internet": "Нет подключения к интернету",
                "api_error": "Ошибка API",
                "invalid_city": "Введите корректное название города",
                "any_error":"Ошибка при поиске городов"
            },
            "EN": {
                "greeting_morning": "Good morning!",
                "greeting_day": "Good afternoon!",
                "greeting_evening": "Good evening!",
                "greeting_night": "Good night!",
                "placeholder": "Enter city or click location button",
                "location_error": "Failed to detect location",
                "weather_error": "Error",
                "error_city_not_found": "City not found",
                "no_internet": "No internet connection",
                "api_error": "API error",
                "invalid_city": "Please enter a valid city name",
                "any_error":"Error by searching cities"
            }
        }
        
        self.init_ui()
        self.language_changed.connect(self.update_texts)
        
    def init_ui(self):
        container_widget = QWidget(self)
        layout = QVBoxLayout(container_widget)

        font_path = resource_path(os.path.join('sources/fonts/', 'try-clother.ttf'))
        font_id = QFontDatabase.addApplicationFont(font_path)
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
            color: Aqua;
            font-family: {font_family};
            font-weight: bold;
            background: transparent;
        """)
        self.title_label.setMinimumHeight(200)

        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        input_layout = QHBoxLayout()
        input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.location_input = QLineEdit(self)
        self.update_placeholder_text()
        self.location_input.setFixedWidth(700)

        input_layout.addWidget(self.location_input)

        layout.addLayout(input_layout)
        layout.addStretch(1)

        self.setLayout(layout)

        self.location_button = QPushButton(self)
        location_icon_path = resource_path(os.path.join('sources/icons/', 'location.png'))
        self.location_button.setIcon(QIcon(location_icon_path))
        self.location_button.setIconSize(QSize(50, 50)) 
        self.location_button.setFixedSize(60, 60) 
        self.location_button.setStyleSheet("border: none; background: transparent;")
        self.location_button.clicked.connect(self.set_location_from_ip)
        self.location_button.setParent(self)  
        self.location_button.show()


        self.language_combo = QComboBox(self)
        self.language_combo.addItem("RU")
        self.language_combo.addItem("EN")
        self.language_combo.setFixedSize(80, 30)
        self.language_combo.setCurrentText(self.current_language)
        self.language_combo.currentTextChanged.connect(self.change_language)

        self.completer_model = QStringListModel()
        self.setup_completer()
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.fetch_cities_api)
       
        self.location_input.textChanged.connect(self.on_text_edited)
        self.location_input.returnPressed.connect(self.on_city_entered)

    def setup_completer(self):
        self.completer = QCompleter()
        self.completer.setModel(self.completer_model)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setMaxVisibleItems(8)
        self.completer.popup().setStyleSheet("""
                QListView {
                    background: rgba(40, 40, 40, 0.95);
                    color: white;
                    border: 1px solid #555;
                    font-size: 16px;
                    padding: 4px;
                }
                QListView::item {
                    padding: 6px;
                    border-bottom: 1px solid #333;
                }
                    QListView::item:hover {
                    background: #555;
                }""")
        
        self.location_input.setCompleter(self.completer)

    def on_text_edited(self, text):
        self.search_timer.stop()
        if len(text.strip()) >= 3:
            self.search_timer.start(200)  
        else:
            self.completer_model.setStringList([])  

    def fetch_cities_api(self):
        search_text = self.location_input.text().strip()
        if len(search_text) < 3:
            self.completer_model.setStringList([])
            return

        try:
            url = "http://api.geonames.org/searchJSON"
            params = {
                'name_startsWith': search_text,
                'maxRows': 15,
                'username': USERNAME_GEONAMES,
                'lang': 'ru' if self.current_language == 'RU' else 'en',
                'cities': 'cities5000',
                'featureClass': 'P',
                'orderby': 'population',
                'style': 'FULL'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if "geonames" not in data:
                raise ValueError("Invalid response format")
                
            cities = []
            geonames = data.get('geonames', [])
            current_lang = self.current_language.lower()
            
            for city in geonames:
                if not isinstance(city, dict):
                    continue
                    
                if city.get('population', 0) <= 10000:
                    continue
                    
                country = city.get('countryName', '')
                name_in_lang = None
                
                for names in city.get("alternateNames", []):
                    if not isinstance(names, dict):
                        continue
                    if names.get("lang") == current_lang:
                        name_in_lang = names.get('name')
                        if name_in_lang:
                            break
                
                if not name_in_lang:
                    name_in_lang = city.get('name', '')
                
                if name_in_lang:
                    city_str = f"{name_in_lang}, {country}" if country else name_in_lang
                    cities.append(city_str)
            
            self.completer_model.setStringList(cities[:10])
            
        except Exception as e:
            self.show_error("any_error")
            

    def change_language(self, language):
        self.current_language = language
        self.language_changed.emit(language)
        self.update_texts()

    def update_texts(self):
        _, greeting = self.set_bg()
        self.title_label.setText(greeting)
        self.update_placeholder_text()
        
    def update_placeholder_text(self):
        lang = self.current_language
        self.location_input.setPlaceholderText(self.translations[lang]["placeholder"])

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

        lang = self.current_language
        translations = self.translations[lang]

        if 6 <= hour < 12:
            time_day = 'morning'
            greeting = translations["greeting_morning"]
        elif 12 <= hour < 18:
            time_day = 'day'
            greeting = translations["greeting_day"]
        elif 18 <= hour < 22:
            time_day = 'evening'
            greeting = translations["greeting_evening"]
        else:
            time_day = 'evening'
            greeting = translations["greeting_night"]

        bg_image =  resource_path(os.path.join('sources/backgrounds/', f'{season}_{time_day}.jpg'))
        return bg_image, greeting
    
    def get_current_location(self):
        try:
            response = requests.get("https://ipinfo.io/json", timeout=5)
            data = response.json()
            loc = data.get("loc", "")
            
            if not loc:
                return None
                
            latitude, longitude = loc.split(",")
            geolocator = Nominatim(user_agent="weather_app")
            location = geolocator.reverse((latitude, longitude), 
                                         language="ru" if self.current_language == 'RU' else "en")
            
            address = location.raw.get("address", {})
            return address.get("city") or address.get("town") or address.get("village")
            
        except (requests.exceptions.RequestException, Exception):
            return None
        
        
    def show_error(self, error_key):
        lang = self.current_language
        QMessageBox.warning(self, 
                          self.translations[lang]["weather_error"],
                          self.translations[lang][error_key])

    def set_location_from_ip(self):
        try:
            if city := self.get_current_location():
                self.location_input.setText(city)
                self.location_input.setFocus()
            else:
                self.show_error("location_error")
        except Exception:
            self.show_error("location_error")

    def resizeEvent(self, event):
        self.background_label.setGeometry(self.rect())
        self.location_button.move(self.width() - 80, self.height() - 80)
        self.language_combo.move(20, self.height() - 60)

    def on_city_entered(self):
        city = self.location_input.text().strip()
        if not city:
            self.show_error("invalid_city")
            return

        try:
            weather = self.fetch_weather(city)
            forecast = self.fetch_week_weather(city)
            
            if weather and forecast:
                self.stacked_widget.setCurrentIndex(1)
            else:
                self.show_error("error_city_not_found")
                
        except requests.exceptions.RequestException:
            self.show_error("no_internet")
        except Exception:
            self.show_error("api_error")


    def fetch_weather(self, city):
        if not api_key_from_conf:
            self.show_error("api_error")
            return None

        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key_from_conf}&units=metric&lang={'ru' if self.current_language == 'RU' else 'en'}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("cod") != 200:
                return None
                
            weather_data = {
                "city": data["name"],
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind": data["wind"]["speed"],
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"]
            }
            
            self.weather_data_ready.emit(weather_data)
            return weather_data
            
        except Exception:
            return None

    def fetch_week_weather(self, city):
        if not api_key_from_conf:
            return None

        try:
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key_from_conf}"
            geo_response = requests.get(geo_url, timeout=10)
            geo_data = geo_response.json()

            if not geo_data:
                return None
                
            lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
            
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=metric&exclude=hourly,minutely&appid={api_key_from_conf}&lang={'ru' if self.current_language == 'RU' else 'en'}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            forecast_data = {
                "city": city,
                "current": {
                    "temp": data["current"]["temp"],
                    "feels_like": data["current"]["feels_like"],
                    "humidity": data["current"]["humidity"],
                    "wind": data["current"]["wind_speed"],
                    "description": data["current"]["weather"][0]["description"],
                    "icon": data["current"]["weather"][0]["icon"]
                },
                "daily": []
            }
            
            for day in data["daily"][:7]:
                day_data = {
                    "date": datetime.datetime.fromtimestamp(day["dt"]).strftime("%d.%m"),
                    "day_name": datetime.datetime.fromtimestamp(day["dt"]).strftime("%A"),
                    "temp_day": day["temp"]["day"],
                    "temp_night": day["temp"]["night"],
                    "description": day["weather"][0]["description"],
                    "icon": day["weather"][0]["icon"],
                    "humidity": day["humidity"],
                    "wind": day["wind_speed"]
                }
                forecast_data["daily"].append(day_data)
            
            self.forecast_data_ready.emit(forecast_data)
            return forecast_data
            
        except Exception:
            return None