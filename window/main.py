from PyQt5 import QtWidgets, QtCore

QWidget, QMainWindow = QtWidgets.QWidget, QtWidgets.QMainWindow
QLabel = QtWidgets.QLabel
QMenuBar = QtWidgets.QMenuBar

Qt = QtCore.Qt

class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUi()
    
    def initUi(self):
        QLabel('Test', self)
    


class MainWindow(QMainWindow):
    def __init__(self, parent=None, flags=Qt.Window):
        super().__init__(parent, flags)
        self.setCentralWidget(MainWidget(self))
        self.setMenuBar(QMenuBar())
        self.setWindowTitle('Controller of outgoes')
        self.show()
