from PyQt5 import QtWidgets, QtCore

from months import Months

QDialog = QtWidgets.QDialog
QLabel = QtWidgets.QLabel
QPushButton, QSpinBox, QComboBox = (
    QtWidgets.QPushButton,
    QtWidgets.QSpinBox,
    QtWidgets.QComboBox
)

Qt = QtCore.Qt


class EditorWindow(QDialog):
    def __init__(self, day, month, year, parent=None):
        super().__init__(parent)
        self.day = day
        self.month = month
        self.year = year
        self.initUi()
    
    def initUi(self):
        linfo = QLabel('info', self)
        linfo.setText('{}, {}, {}'.format(
            self.day,
            Months(self.month).name,
            self.year
        ))
