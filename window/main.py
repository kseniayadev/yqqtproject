import datetime
from calendar import Calendar

from PyQt5 import QtCore, QtSql, QtWidgets

from db import DatabaseError, conn
from months import Months
from window.editor import EditorWindow
from window.info import InfoWindow

QWidget, QMainWindow, QDialog = (
    QtWidgets.QWidget,
    QtWidgets.QMainWindow,
    QtWidgets.QDialog
)
QLabel, QTableWidget = QtWidgets.QLabel, QtWidgets.QTableWidget
QPushButton, QSpinBox, QComboBox = (
    QtWidgets.QPushButton,
    QtWidgets.QSpinBox,
    QtWidgets.QComboBox
)
QTableWidgetItem, QAbstractItemView = (
    QtWidgets.QTableWidgetItem,
    QtWidgets.QAbstractItemView
)
QVBoxLayout, QHBoxLayout, QFormLayout = (
    QtWidgets.QVBoxLayout,
    QtWidgets.QHBoxLayout,
    QtWidgets.QFormLayout
)
QMenuBar = QtWidgets.QMenuBar

Qt, QEvent = QtCore.Qt, QtCore.QEvent

QItemSelectionModel = QtCore.QItemSelectionModel

QSqlQuery = QtSql.QSqlQuery


class MainWidget(QWidget):
    calendar = Calendar()
    maxYear = datetime.MAXYEAR
    minYear = datetime.MINYEAR

    class SelectMonthDialog(QDialog):
        def __init__(self, parent=None, flags=Qt.Dialog):
            super().__init__(parent, flags)
            self.initUi()

        def initUi(self):
            today = datetime.date.today()
            eyear = QSpinBox()
            eyear.setMinimum(MainWidget.minYear)
            eyear.setMaximum(MainWidget.maxYear)
            eyear.setValue(today.year)
            self.eyear = eyear
            emonth = QComboBox()
            emonth.addItems((month.name for month in Months))
            emonth.setEditable(False)
            emonth.setInsertPolicy(0)
            emonth.setCurrentIndex(today.month - 1)
            self.emonth = emonth
            form = QFormLayout()
            form.addRow('&Month: ', emonth)
            form.addRow('&Year: ', eyear)
            bok = QPushButton('&OK')
            bok.clicked.connect(self.accept)
            bcancel = QPushButton('&Cancel')
            bcancel.clicked.connect(self.reject)
            hbox = QHBoxLayout()
            hbox.addWidget(bok)
            hbox.addWidget(bcancel)
            vbox = QVBoxLayout()
            vbox.addLayout(form)
            vbox.addLayout(hbox)
            self.setLayout(vbox)

    def __init__(self, parent=None):
        super().__init__(parent)
        today = datetime.date.today()
        self.month = today.month
        self.year = today.year
        self.initUi()

    def initUi(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        bprevious = QPushButton('<')
        bprevious.clicked.connect(self.previousMonth)
        bnext = QPushButton('>')
        bnext.clicked.connect(self.nextMonth)
        bdate = QPushButton('Date')
        bdate.clicked.connect(self.selectMonth)
        hbox.addWidget(bprevious)
        hbox.addWidget(bdate)
        hbox.addWidget(bnext)
        vbox.addLayout(hbox)
        tcalendar = QTableWidget()
        self.info = InfoWindow()
        self.tcalendar = tcalendar
        self.bprevious = bprevious
        self.bnext = bnext
        self.bdate = bdate
        vbox.addWidget(tcalendar)
        vbox.addWidget(self.info)
        self.setLayout(vbox)
        self.initCalendar()

    def eventFilter(self, source, event):
        if (event.type() == QEvent.MouseButtonDblClick and
                event.buttons() == Qt.LeftButton and
                source is self.tcalendar.viewport()):
            item = self.tcalendar.itemAt(event.pos())
            if item is not None:
                if item.text() != '':
                    item = item.text()
                    if ':' in item:
                        item = item[:item.index(':')]
                    self.openEditor(int(item))
        return super().eventFilter(source, event)

    def initCalendar(self):
        tcalendar = self.tcalendar
        tcalendar.setColumnCount(7)
        tcalendar.setHorizontalHeaderLabels((
            'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'San'
        ))
        tcalendar.setRowCount(6)
        tcalendar.setVerticalHeaderLabels(map(str, range(1, 7)))
        tcalendar.setEditTriggers(QAbstractItemView.NoEditTriggers)
        selection = QItemSelectionModel(tcalendar.model())
        tcalendar.setSelectionModel(selection)
        tcalendar.viewport().installEventFilter(self)
        self.updateCalendar()

    def updateCalendar(self):
        tcalendar = self.tcalendar
        days = self.calendar.monthdayscalendar(self.year, self.month)
        for y in range(6):
            for x in range(7):
                tcalendar.setItem(y, x, QTableWidgetItem(''))
        self.info.clear()
        for y, row in enumerate(days):
            for x, item in enumerate(row):
                if item == 0:
                    item = ''
                else:
                    if not conn.isOpen():
                        if not conn.open():
                            raise DatabaseError
                    query = QSqlQuery(conn)
                    query.prepare('SELECT price, count, category FROM outgones WHERE\
                        (day = {} and month = {} and year = {})'.format(
                            item, self.month, self.year
                    ))
                    query.exec_()
                    if not query.isSelect():
                        raise DatabaseError
                    s = 0
                    query.first()
                    while query.isValid():
                        val = query.value('price') * query.value('count')
                        s += val
                        self.info.addData(query.value('category'), val)
                        query.next()
                    if s == 0:
                        item = str(item)
                    else:
                        item = '{}: {}'.format(item, round(s, 2))
                    conn.close()
                tcalendar.setItem(
                    y, x,
                    QTableWidgetItem(item)
                )
        tcalendar.resizeColumnsToContents()
        tcalendar.resizeRowsToContents()
        month = Months(self.month).name
        year = str(self.year)
        self.bdate.setText('{}, {}'.format(month, year))
        w = sum(tcalendar.columnWidth(i) for i in range(7)) + 33
        h = sum(tcalendar.rowHeight(i) for i in range(7)) + 198
        self.resize(w, h)
        self.parent().setFixedSize(w, h)

    def nextMonth(self):
        month = self.month
        year = self.year
        if month == 12:
            if year + 1 <= self.maxYear:
                self.month = 1
                self.year += 1
        else:
            self.month += 1
        self.updateCalendar()

    def previousMonth(self):
        month = self.month
        year = self.year
        if month == 1:
            if year - 1 >= self.minYear:
                self.month = 12
                self.year -= 1
        else:
            self.month -= 1
        self.updateCalendar()

    def selectMonth(self):
        dialog = MainWidget.SelectMonthDialog()
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.month = dialog.emonth.currentIndex() + 1
            self.year = dialog.eyear.value()
            self.updateCalendar()

    def openEditor(self, day, month=None, year=None):
        if month is None:
            month = self.month
        if year is None:
            year = self.year
        editor = EditorWindow(day, month, year)
        editor.exec_()


class MainWindow(QMainWindow):
    def __init__(self, parent=None, flags=Qt.Window):
        super().__init__(parent, flags)
        self.setCentralWidget(MainWidget(self))
        self.setMenuBar(QMenuBar())
        self.setWindowTitle('Controller of outgoes')
        self.show()
