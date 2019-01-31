from PyQt5 import QtWidgets, QtCore

from categories import Categories

QWidget = QtWidgets.QWidget
QLabel = QtWidgets.QLabel
QGridLayout = QtWidgets.QGridLayout

Qt = QtCore.Qt


class InfoWindow(QWidget):
    class InfoLabel(QLabel):
        def __init__(self, name, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.name = name
            self._value = 0
            self.value = 0

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, val):
            try:
                val = float(val)
            except ValueError:
                return
            self._value = val
            self.setText('{}: {}'.format(self.name, val))

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUi()

    def initUi(self):
        self.labels = list()
        grid = QGridLayout()
        for category in Categories:
            label = self.InfoLabel(category.name)
            self.labels.append(label)
            val = category.value
            grid.addWidget(label, val % 6, val // 6)
        label = self.InfoLabel('All')
        self.labels.append(label)
        grid.addWidget(label, 5, 1)
        self.setLayout(grid)
        self.setFixedHeight(120)

    def clear(self):
        for category in range(0, 12):
            self.labels[category].value = 0

    def addData(self, category, val):
        if category not in range(0, 11):
            raise ValueError
        self.labels[category].value += val
        self.labels[-1].value += val
