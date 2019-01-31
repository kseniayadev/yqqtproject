from PyQt5 import QtWidgets, QtCore, QtSql

from window.info import InfoWindow
from months import Months
from db import conn, DatabaseError
from categories import Categories

QDialog = QtWidgets.QDialog
QLabel = QtWidgets.QLabel
QVBoxLayout, QHBoxLayout, QFormLayout = (
    QtWidgets.QVBoxLayout,
    QtWidgets.QHBoxLayout,
    QtWidgets.QFormLayout
)
QPushButton, QDoubleSpinBox, QSpinBox, QComboBox, QLineEdit = (
    QtWidgets.QPushButton,
    QtWidgets.QDoubleSpinBox,
    QtWidgets.QSpinBox,
    QtWidgets.QComboBox,
    QtWidgets.QLineEdit
)
QTreeWidget, QTreeWidgetItem = (
    QtWidgets.QTreeWidget,
    QtWidgets.QTreeWidgetItem
)

Qt = QtCore.Qt

QSqlQuery = QtSql.QSqlQuery


class EditorWindow(QDialog):
    def __init__(self, day, month, year, parent=None):
        super().__init__(parent)
        self.day = day
        self.month = month
        self.year = year
        self.categories = dict()
        self.initUi()
        self.update()

    def initUi(self):
        form = QFormLayout()
        self.ename = QLineEdit()
        form.addRow('Name:', self.ename)
        self.ecategory = QComboBox()
        self.ecategory.addItems((category.name for category in Categories))
        self.ecategory.setEditable(False)
        self.ecategory.setInsertPolicy(0)
        form.addRow('Category:', self.ecategory)
        self.eprice = QDoubleSpinBox()
        self.eprice.setMaximum(1000000.0)
        self.eprice.setMinimum(0.0)
        form.addRow('Price:', self.eprice)
        self.ecount = QSpinBox()
        self.ecount.setMinimum(1)
        self.ecount.setMaximum(1000000)
        self.ecount.setValue(1)
        form.addRow('Count:', self.ecount)
        self.badd = QPushButton("&Add")
        self.badd.clicked.connect(self.add)
        self.tree = QTreeWidget()
        self.tree.header().hide()
        self.info = InfoWindow()
        vbox = QVBoxLayout()
        vbox.addWidget(self.tree)
        vbox.addLayout(form)
        vbox.addWidget(self.badd)
        vbox.addWidget(self.info)
        self.setLayout(vbox)
        self.setWindowTitle('{}, {}, {}'.format(
            self.day,
            Months(self.month).name,
            self.year
        ))

    def update(self):
        self.info.clear()
        if not conn.isOpen():
            if not conn.open():
                raise DatabaseError
        query = QSqlQuery(conn)
        query.prepare('SELECT name, price, count, category FROM outgones WHERE\
            (day = {} and month = {} and year = {})'.format(
                self.day, self.month, self.year
        ))
        query.exec_()
        if not query.isSelect():
            raise DatabaseError
        query.first()
        while query.isValid():
            name = query.value('name')
            price = query.value('price')
            count = query.value('count')
            category = query.value('category')
            if category not in self.categories:
                parent = QTreeWidgetItem(self.tree)
                parent.setText(0, Categories(category).name)
                self.categories[category] = parent
            parent = self.categories[category]
            child = QTreeWidgetItem(parent)
            child.setText(
                0,
                '{}:  {}x{} = {}'.format(name, price, count, price * count)
            )
            self.info.addData(category, price * count)
            query.next()

    def add(self):
        name = self.ename.text()
        if len(name) == 0:
            return
        category = self.ecategory.currentIndex()
        price = self.eprice.value()
        count = self.ecount.value()
        if not conn.isOpen():
            if not conn.open():
                raise DatabaseError
        query = QSqlQuery(conn)
        query.exec_(
            'INSERT INTO outgones VALUES (\
            "{}", {}, {}, {}, {}, {}, {});'.format(
                name, self.day, self.month, self.year,
                category, price, count
            )
        )
        self.update()
