from searchscreen import SearchScreen
from weatherscreen import ShowWeather
import sys
from PyQt6.QtWidgets import (QApplication, QStackedWidget)

class WeatherApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Weather4You')
        self.setGeometry(100, 100, 1200, 740)
        self.center()
        self.search_screen = SearchScreen(self)
        self.addWidget(self.search_screen)
        self.weatherscreen = ShowWeather(self,self.search_screen)
        self.addWidget(self.weatherscreen)
        self.setCurrentIndex(0)
        with open("style.qss", "r") as file:
            self.setStyleSheet(file.read())

    def center(self):
        screen = QApplication.primaryScreen()  
        screen_geometry = screen.availableGeometry()  
        window_geometry = self.frameGeometry() 
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

app = QApplication(sys.argv)
window = WeatherApp()
window.show()
app.exec()