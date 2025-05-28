from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot

class ChartBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.on_chart_event = None  # Callback for chart events

    @pyqtSlot(str, float)
    def chartClicked(self, marker_type, price):
        if self.on_chart_event:
            self.on_chart_event(marker_type, price)

class ChartView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        self.webview = QWebEngineView()
        layout.addWidget(self.webview)

        # Set up QWebChannel bridge
        self.channel = QWebChannel()
        self.bridge = ChartBridge()
        self.channel.registerObject('chartBridge', self.bridge)
        self.webview.page().setWebChannel(self.channel)

        # Example: connect to a callback (parent/main window should set this)
        # self.bridge.on_chart_event = self.handle_chart_event

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
        </head>
        <body>
            <div style="margin-bottom:10px;">
                <label for="markerType">Set marker type: </label>
                <select id="markerType">
                    <option value="entry">Entry</option>
                    <option value="sl">Stop Loss</option>
                    <option value="tp1">Take Profit 1</option>
                    <option value="tp2">Take Profit 2</option>
                    <option value="tp3">Take Profit 3</option>
                    <option value="tp4">Take Profit 4</option>
                    <option value="tp5">Take Profit 5</option>
                </select>
            </div>
            <div id="tradingview_chart" style="height:600px;"></div>
            <script type="text/javascript">                
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    window.chartBridge = channel.objects.chartBridge;
                });
                new TradingView.widget({
                    "container_id": "tradingview_chart",
                    "width": "100%",
                    "height": "600",
                    "symbol": "BINANCE:BTCUSDT",
                    "interval": "5",
                    "timezone": "Etc/UTC",
                    "theme": "dark",
                    "style": "1",
                    "locale": "en",
                    "toolbar_bg": "#f1f3f6",
                    "enable_publishing": false,
                    "allow_symbol_change": true,
                    "hide_legend": false,
                    "save_image": false,
                    "container_id": "tradingview_chart",
                    "studies": [],
                    "overrides": {}
                });
                // Listen for mouse clicks on the chart area
                document.getElementById('tradingview_chart').addEventListener('click', function(e) {
                    if (window.chartBridge) {
                        var markerType = document.getElementById('markerType').value;
                        // In production, get price from chart API at click position
                        // For demo, use a random price
                        var price = Math.random() * 70000 + 10000;
                        window.chartBridge.chartClicked(markerType, price);
                    }
                });
            </script>
        </body>
        </html>
        """

        self.webview.setHtml(html)
