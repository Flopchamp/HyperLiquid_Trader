# Hyperliquid Multi-Account Trader

A robust, GUI-based multi-account trading system for Hyperliquid, built with Python 3.x and PyQt6.

## Features
- Manage up to 10 accounts with independent configuration
- Asynchronous trading with the Hyperliquid Python SDK
- Dynamic SL/TP logic, order splitting, and copy trading
- Embedded TradingView chart with chart-click trading
- Secure API key management via `.env` or `config/settings.json`
- Modular, scalable, and Windows-compatible

## Setup
1. **Clone the repository**
2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
3. **Configure API keys:**
   - Preferred: Create a `.env` file in the project root:
     ```
     API_KEY_1=your_api_key_1
     API_SECRET_1=your_api_secret_1
     # ... up to API_KEY_10, API_SECRET_10
     ```
   - Or edit `config/settings.json` with your account info.
4. **Run the app:**
   ```
   python main.py
   ```

## Usage
- Use the GUI to select accounts, set order parameters, and place trades.
- Use the TradingView chart for visual trading and SL/TP/entry selection.
- Use the master account selector for copy trading.

## Testing
- Tests are located in the `tests/` directory (see below for scaffold).
- Run tests with:
  ```
  pytest
  ```

## Project Structure
- `main.py` — App entry point
- `ui/` — PyQt6 GUI components
- `core/` — Trading logic, order splitting, copy trading
- `utils/` — Config loading, validation, helpers
- `config/` — API key and settings storage
- `assets/` — Styles and icons

## Requirements
- Python 3.10+
- PyQt6, PyQt6-WebEngine, hyperliquid, python-dotenv

## License
MIT
