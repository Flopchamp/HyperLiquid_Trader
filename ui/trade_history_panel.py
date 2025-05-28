from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class TradeHistoryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.label = QLabel("Trade History & Analytics")
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.label)
        layout.addWidget(self.text_edit)

    def add_trade(self, trade_info: str):
        self.text_edit.append(trade_info)

    def clear_history(self):
        self.text_edit.clear()
