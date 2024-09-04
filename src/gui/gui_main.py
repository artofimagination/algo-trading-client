from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QGridLayout,
    QPushButton,
    QComboBox,
    QLabel
)

from pyqtgraph import GraphicsLayoutWidget
from PyQt5.QtCore import QThread

from backend import Backend, BOT_HELLO, BOT_INTUITION
from gui.candle_chart import CandlestickItems, ExecutedOrderItems
from datetime import datetime


# Main Qt UI window
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.workerThread = QThread(self)
        self.worker = Backend()
        self.worker.signals.error.connect(self.sigint_handler)
        self.worker.signals.finished.connect(self.thread_complete)

        self.setCentralWidget(self._create_main_widget())
        self.resize(800, 600)
        self.showMaximized()
        self.setWindowTitle("Algo trading client")

        self.worker.moveToThread(self.workerThread)
        self.workerThread.finished.connect(self.worker.deleteLater)
        self.workerThread.started.connect(self.worker.run)
        self.workerThread.start()
        self.show()

    def time_axis(self, values, scale, spacing):
        return [datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M') for value in values]

    def _create_main_widget(self):
        main_widget = QWidget()
        main_layout = QGridLayout()
        main_widget.setLayout(main_layout)
        self.candles_historic_plot = GraphicsLayoutWidget()
        self.candles_historic_plot.setViewport(QOpenGLWidget())
        run_button = QPushButton("Run")
        run_button.pressed.connect(self._run)
        download_data_button = QPushButton("Download")
        download_data_button.pressed.connect(self.worker.download)
        bot_selector_label = QLabel("Bot")
        self.bot_selector = QComboBox()
        main_layout.addWidget(self.candles_historic_plot, 0, 0, 1, 4)
        main_layout.addWidget(bot_selector_label, 1, 0, 1, 1)
        main_layout.addWidget(self.bot_selector, 1, 1, 1, 1)
        main_layout.addWidget(run_button, 1, 2, 1, 1)
        main_layout.addWidget(download_data_button, 1, 3, 1, 1)

        self.plot = self.candles_historic_plot.addPlot()
        self.plot.showGrid(x=True, y=True)

        return main_widget

    def _run(self):
        self.worker.run_bot(self.bot_selector.currentText())

    def plot_historic(self):
        self.plot.clear()
        resolution_min = self.worker.bot.resolution_min
        self.plot.getAxis('bottom').setTickSpacing(600 * resolution_min, 1)  # Set tick spacing (86400 seconds = 1 day)
        self.plot.getAxis('bottom').tickStrings = self.time_axis
        data = self.worker.bot.historical_data(None, self.worker.bot.get_start_timestamp())
        data['startTime'] = data['startTime'].astype(int) // 10**9
        data['closeTime'] = data['closeTime'].astype(int) // 10**9
        # Select the first four columns and the new index column
        selected_columns = data[['startTime', 'open', 'high', 'low', 'close']]

        # Convert the selected columns to a list of lists
        data_list = selected_columns.values.tolist()
        candlesticks = CandlestickItems(data_list)
        self.plot.addItem(candlesticks)

        completed_orders = self.worker.bot.completed_orders
        if len(completed_orders) > 0:
            completed_orders['timestamp'] = completed_orders['timestamp'].astype(int) // 10**9
            completed_orders['exec_timestamp'] = completed_orders['exec_timestamp'].astype(int) // 10**9
            # Select the first four columns and the new index column
            selected_columns = completed_orders[['side', 'timestamp', 'start_price', 'exec_timestamp', 'price']]
            data_list = selected_columns.values.tolist()
            order_marking = ExecutedOrderItems(data_list)
            self.plot.addItem(order_marking)

    def closeEvent(self, event):
        """Override of QMainWindow.closeEvent"""
        # Call the function you want before closing
        self.sigint_handler()

    def sigint_handler(self):
        """Terminate UI and the threads appropriately."""
        if self.worker is not None:
            self.worker.stop = True
            self.workerThread.quit()
            self.workerThread.wait()
        print("Exiting app through GUI")
        QApplication.quit()

    def thread_complete(self):
        """Executes tasks on thread completion."""
        print("Worker thread stopped...")
