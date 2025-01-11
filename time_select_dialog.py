from PyQt5.QtWidgets import QDialog, QVBoxLayout, QRadioButton, QPushButton, QHBoxLayout, QLineEdit, QGroupBox, QFormLayout
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QIntValidator, QRegExpValidator
import json



class TimeSelectDialog(QDialog):
    def __init__(self, network_manager):
        super().__init__()
        self.network_manager = network_manager
        self.setWindowTitle('Ustawienia Gry')
        layout = QVBoxLayout(self)

        # Grupa przycisków radiowych do wyboru trybu gry
        mode_layout = QHBoxLayout()
        self.mode_group = QGroupBox("Tryb Gry:")
        self.mode_buttons = []
        modes = [("1 Gracz", "1P"), ("2 Graczy", "2P"), ("AI", "AI")]
        for text, mode in modes:
            radio_button = QRadioButton(text)
            self.mode_buttons.append((radio_button, mode))
            mode_layout.addWidget(radio_button)

        self.mode_buttons[0][0].setChecked(True)  # Domyślnie zaznacz pierwszą opcję
        self.mode_group.setLayout(mode_layout)
        layout.addWidget(self.mode_group)

        # Pola do ustawienia adresu IP i portu
        network_layout = QFormLayout()
        self.ip_line_edit = QLineEdit()
        self.port_line_edit = QLineEdit()

        # Walidatory dla pól
        ip_regex = QRegExp("((2[0-4]\\d|25[0-5]|[01]?\\d\\d?)\\.){3}(2[0-4]\\d|25[0-5]|[01]?\\d\\d?)")
        port_validator = QIntValidator(1, 65535)
        ip_validator = QRegExpValidator(ip_regex)

        self.ip_line_edit.setValidator(ip_validator)
        self.port_line_edit.setValidator(port_validator)

        network_layout.addRow("Adres IP:", self.ip_line_edit)
        network_layout.addRow("Port:", self.port_line_edit)
        layout.addLayout(network_layout)

        # Opcje czasu startowego
        self.radio_buttons = []
        times = [("1 minuta", 60), ("3 minuty", 180), ("5 minut", 300)]
        for text, value in times:
            radio_button = QRadioButton(f"{text} + 3s za ruch")
            self.radio_buttons.append((radio_button, value))  # Zapisz wartość czasu razem z przyciskiem
            layout.addWidget(radio_button)

        self.radio_buttons[0][0].setChecked(True)  # Domyślnie zaznacz pierwszą opcję

        # Przycisk do potwierdzenia wyboru
        self.confirm_button = QPushButton('Rozpocznij grę', self)
        self.confirm_button.clicked.connect(self.save_settings_and_close)
        layout.addWidget(self.confirm_button)

    def selected_time(self):
        for button, value in self.radio_buttons:
            if button.isChecked():
                return value

    def selected_mode(self):
        for button, mode in self.mode_buttons:
            if button.isChecked():
                return mode

    def get_network_settings(self):
        return self.ip_line_edit.text(), self.port_line_edit.text()

    def save_settings_and_close(self):
        # Zbierz wszystkie wybrane ustawienia
        mode = self.selected_mode()
        ip, port = self.get_network_settings()
        time = self.selected_time()

        # Zapisz ustawienia do pliku JSON
        settings = {
            "mode": mode,
            "ip": ip,
            "port": port,
            "time": time
        }

        with open("game_settings.json", "w") as json_file:
            json.dump(settings, json_file, indent=4)

        # Zamknij okno dialogowe
        self.accept()

        self.start_game_based_on_mode(mode, ip, port, time)

    def start_game_based_on_mode(self, mode, ip, port, time):
        if mode == "2P":
            if ip:  # Start as client
                self.network_manager.start_client(ip, port)
            else:  # Start as server
                self.network_manager.start_server(port)
        self.accept()