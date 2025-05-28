# main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.hyperliquid_sniper import HyperliquidSniper

def main():
    print("Starting Hyperliquid Sniper UI...")
    app = QApplication(sys.argv)
    window = HyperliquidSniper()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
