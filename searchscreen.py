import requests
import datetime
from functools import lru_cache
from geopy.geocoders import Nominatim
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QGraphicsBlurEffect, QMessageBox, QComboBox, 
    QCompleter
)
from PyQt6.QtGui import (QFontDatabase, QPixmap, QIcon)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer, QStringListModel

with open("api.txt","r") as f:
    api_key_from_conf = f.read()

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
                "weather_error":"Ошибка"
            },
            "EN": {
                "greeting_morning": "Good morning!",
                "greeting_day": "Good afternoon!",
                "greeting_evening": "Good evening!",
                "greeting_night": "Good night!",
                "placeholder": "Enter city or click location button",
                "location_error": "Failed to detect location",
                "weather_error":"Error"
            }
        }
        
        self.init_ui()
        self.language_changed.connect(self.update_texts)
        
    def init_ui(self):
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
        self.location_button.setIcon(QIcon("sources/icons/location.png"))  
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
            return

        try:
            url = "http://api.geonames.org/searchJSON"
            params = {
                'name_startsWith': search_text,
                'maxRows': 15,
                'username': 'r3dbad',
                'lang': 'ru' if self.current_language == 'RU' else 'en',
                'cities': 'cities5000',
                'featureClass': 'P',
                'orderby': 'population',
                'style': 'FULL'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            cities = []
            geonames = data.get('geonames', [])
            current_lang = self.current_language.lower()
            
            for city in geonames:
                if city.get('population', 0) <= 10000:
                    continue
                    
                country = city.get('countryName', '')
                name_in_lang = None
                
                for names in city.get("alternateNames", []):
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
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
        except (ValueError, KeyError) as e:
            print(f"JSON parsing error: {e}")
            

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

        bg_image = f'sources/backgrounds/{season}_{time_day}.jpg'
        return bg_image, greeting
    
    @lru_cache(maxsize=32)
    def get_current_location(self):
        try:
            response = requests.get("https://ipinfo.io/json", timeout=5)
            data = response.json()
            loc = data.get("loc", "")  
            if not loc:
                return ""

            latitude, longitude = loc.split(",")  
            geolocator = Nominatim(user_agent="weather_app")
            if self.current_language == 'RU':
                location = geolocator.reverse((latitude, longitude), language="ru")
            else:
                location = geolocator.reverse((latitude, longitude), language="en")

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
            lang = self.current_language
            QMessageBox.warning(self, "Error" if lang == "EN" else "Ошибка", 
            self.translations[lang]["location_error"])

    def resizeEvent(self, event):
        self.background_label.setGeometry(self.rect())
        self.location_button.move(self.width() - 80, self.height() - 80)
        self.language_combo.move(20, self.height() - 60)

    def on_city_entered(self):
        city = self.location_input.text().strip()
        if city:
            self.fetch_weather(city)
            self.fetch_week_weather(city)
            self.stacked_widget.setCurrentIndex(1) 

    def fetch_weather(self, city):
        api_key = api_key_from_conf
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang={'ru' if self.current_language == 'RU' else 'en'}"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("cod") != 200:
                error_msg = data.get("message", self.translations[self.current_language]["weather_error"])
                raise ValueError(error_msg)
            
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
            
        except Exception as e:
            QMessageBox.critical(self, 
                               "Error" if self.current_language == "EN" else "Ошибка",
                               str(e))

    def fetch_week_weather(self, city):
        api_key = api_key_from_conf
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
        
        try:
            geo_response = requests.get(geo_url, timeout=10)
            geo_data = geo_response.json()
            
            if not geo_data:
                raise ValueError(self.translations[self.current_language]["location_error"])
            
            lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]
            
           
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=metric&exclude=hourly,minutely&appid={api_key}&lang={'ru' if self.current_language == 'RU' else 'en'}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if "daily" not in data:
                raise ValueError(self.translations[self.current_language]["weather_error"])
            
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
        except Exception as e:
            QMessageBox.critical(self, 
                               "Error" if self.current_language == "EN" else "Ошибка",
                               str(e))