import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QFont, QPainter, QIcon, QColor, QLinearGradient, QBrush, QPalette
from PyQt6.QtCore import Qt, QPointF, QSize
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

class ShowWeather(QWidget):
    def __init__(self, stacked_widget, search_screen):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.search_screen = search_screen
        self.init_ui()
        # search_screen.language_changed.connect(self.update_translations)
        search_screen.weather_data_ready.connect(self.update_current_weather)
        search_screen.forecast_data_ready.connect(self.update_forecast)
        # lang = self.current_language
        # self.translations = {
        #     "EN": {
        #         "feelslike": "Feels like:",
        #         "wind":"Wind:",
        #         "hum":"Hunidity:",
        #         "tempforweek":"Temperature for a week",
        #         "temp":"Temperature (°C)"
        #     },
        #     "RU" : {
        #         "feelslike": "Ощущается:",
        #         "wind":"Ветер:",
        #         "hum":"Влажность:",
        #         "tempforweek":"Температура на неделю",
        #         "temp":"Температура (°C)"
        #     }
        # }
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(30, 80, 150))
        gradient.setColorAt(1, QColor(15, 40, 75))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 10)
        
        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon('sources/icons/home.png'))
        self.back_button.setIconSize(QSize(30, 30))
        self.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        top_row.addWidget(self.back_button)
        
        self.location_label = QLabel("Город")
        self.location_label.setFont(QFont('Arial', 18, QFont.Weight.Bold))
        self.location_label.setStyleSheet("color: white;")
        top_row.addWidget(self.location_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.date_label = QLabel(datetime.datetime.now().strftime("%d %B %Y"))
        self.date_label.setFont(QFont('Arial', 14))
        self.date_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        top_row.addWidget(self.date_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(top_row)

        current_weather_frame = QFrame()
        current_weather_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 10px;
            }
        """)
        current_layout = QHBoxLayout(current_weather_frame)
        current_layout.setContentsMargins(5, 5, 5, 5)
        
        self.current_temp_label = QLabel("--°C")
        self.current_temp_label.setFont(QFont('Arial', 42, QFont.Weight.Bold))
        self.current_temp_label.setStyleSheet("color: white;")
        current_layout.addWidget(self.current_temp_label, alignment=Qt.AlignmentFlag.AlignLeft)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("color: rgba(255, 255, 255, 0.3);")
        current_layout.addWidget(separator)
        
        params_layout = QVBoxLayout()
        params_layout.setSpacing(8)
        
        self.weather_desc_label = QLabel("--")
        self.weather_desc_label.setFont(QFont('Arial', 14, QFont.Weight.Medium))
        self.weather_desc_label.setStyleSheet("color: white;")
        
        self.feels_like_label = QLabel("Ощущается: --°C")
        self.feels_like_label.setFont(QFont('Arial', 12))
        self.feels_like_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        self.wind_label = QLabel("Ветер: -- м/с")
        self.wind_label.setFont(QFont('Arial', 12))
        self.wind_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        self.humidity_label = QLabel("Влажность: --%")
        self.humidity_label.setFont(QFont('Arial', 12))
        self.humidity_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        for label in [self.weather_desc_label, self.feels_like_label, 
                     self.wind_label, self.humidity_label]:
            params_layout.addWidget(label)
        
        current_layout.addLayout(params_layout)
        main_layout.addWidget(current_weather_frame)

        weekly_frame = QFrame()
        weekly_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 6px;
            }
        """)
        weekly_layout = QHBoxLayout(weekly_frame)
        weekly_layout.setSpacing(5)
        weekly_layout.setContentsMargins(5, 5, 5, 5)
        
        self.daily_widgets = []
        for i in range(7):
            day_frame = QFrame()
            day_frame.setStyleSheet("""
                QFrame {
                    background: transparent;
                }
                QFrame:hover {
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 10px;
                }
            """)
            day_layout = QVBoxLayout(day_frame)
            day_layout.setSpacing(5)
            day_layout.setContentsMargins(5, 5, 5, 5)
            
            day_name = QLabel("--")
            day_name.setFont(QFont('Arial', 12, QFont.Weight.Bold))
            day_name.setStyleSheet("color: white;")
            day_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            day_temp = QLabel("--/--°C")
            day_temp.setFont(QFont('Arial', 12))
            day_temp.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
            day_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            day_desc = QLabel("--")
            day_desc.setFont(QFont('Arial', 10))
            day_desc.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
            day_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            day_layout.addWidget(day_name)
            day_layout.addWidget(day_temp)
            day_layout.addWidget(day_desc)
            
            weekly_layout.addWidget(day_frame)
            self.daily_widgets.append((day_name, day_temp, day_desc))
        
        main_layout.addWidget(weekly_frame, stretch=1)

        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 10px;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setStyleSheet("background: transparent;")
        chart_layout.addWidget(self.chart_view)
        
        main_layout.addWidget(chart_frame, stretch=2)
        
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
    
