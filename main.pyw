#!/usr/bin/python3

import sys

from PyQt5 import QtWidgets

from window.main import MainWindow
import db

QApplication = QtWidgets.QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db.init()
    win = MainWindow()
    sys.exit(app.exec_())
