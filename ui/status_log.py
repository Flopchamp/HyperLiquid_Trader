from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class StatusLog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel("Status Log")
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.label)
        layout.addWidget(self.text_edit)

    def append(self, message: str):
        self.text_edit.append(message)
