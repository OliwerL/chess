from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QDialog

class LogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Log ruchów')
        self.setGeometry(700, 100, 300, 600)  # Możesz dostosować rozmiar i pozycję okna
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)
        self.setLayout(layout)

    @pyqtSlot(str)
    def append_text(self, text):
        self.textEdit.append(text)

    def clear_text(self):
        self.textEdit.clear()
