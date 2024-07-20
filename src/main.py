import sys

from PyQt5.QtWidgets import QApplication
from gui.gui_main import MainWindow

if __name__ == "__main__":
    # --no-sandbox is only required when running in docker as root
    sys.argv.append('--no-sandbox')
    app = QApplication(sys.argv)
    window = MainWindow()

    sys.exit(app.exec_())
