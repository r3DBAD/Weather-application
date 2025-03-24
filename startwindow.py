from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox)
from PyQt6.QtCore import Qt



class StartWindow(QWidget):
    def __init__(self,stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        with open("style.qss", "r") as file:
            self.setStyleSheet(file.read())

        main_layout = QVBoxLayout()

        self.language_combo = QComboBox()
        self.language_combo.addItem("Русский")
        self.language_combo.addItem("English")

        main_layout.addStretch()
        main_layout.addWidget(self.language_combo, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

        self.next_button = QPushButton("Далее")

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.next_button)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        self.next_button.clicked.connect(self.on_next_button_clicked)

    def on_next_button_clicked(self):
        selected_language = self.language_combo.currentText()
        print(f"Выбранный язык: {selected_language}")
        self.stacked_widget.setCurrentIndex(1)

        