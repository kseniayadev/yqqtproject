#!/usr/bin/python3

import sys

from PyQt5 import QtWidgets

from window.main import MainWindow

QApplication = QtWidgets.QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())
