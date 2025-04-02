import requests
import datetime
from geopy.geocoders import Nominatim
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QGraphicsBlurEffect, QMessageBox, QComboBox, QCompleter
)
from PyQt6.QtGui import QFontDatabase, QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal,QTimer, QStringListModel
class SearchScreen(QWidget):
    language_changed = pyqtSignal(str)  
    
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
                "location_error": "Не удалось определить местоположение"
            },
            "EN": {
                "greeting_morning": "Good morning!",
                "greeting_day": "Good afternoon!",
                "greeting_evening": "Good evening!",
                "greeting_night": "Good night!",
                "placeholder": "Enter city or click location button",
                "location_error": "Failed to detect location"
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
                }
""")
        
        self.location_input.setCompleter(self.completer)

    def on_text_edited(self, text):
        self.search_timer.stop()
        if len(text.strip()) >= 2:
            self.search_timer.start(300)  
        else:
            self.completer_model.setStringList([])  

    def fetch_cities_api(self):
        search_text = self.location_input.text()
        if len(search_text) < 2:
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
            if 'geonames' in data:
                for city in data['geonames']:
                    if city.get('population', 0) > 10000:
                        name = city.get('name', '')
                        country = city.get('countryName', '')
                        if name:
                            cities.append(f"{name}, {country}" if country else name)
            
            self.completer_model.setStringList(cities[:10])
            
        except Exception as e:
            print(f"API error: {e}")
            

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