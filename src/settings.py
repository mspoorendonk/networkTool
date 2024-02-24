"""
Settings window

use qsettings
"""


from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6 import QtCore
from util import getFirstHop

class SettingsDialog(QDialog):

    def __init__(self, parent, settings):
        super().__init__(parent)
        #super().__init__(parent, QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle('Settings')
        self.settings = settings

        layout = QFormLayout()

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setGeometry(QRect(150, 250, 341, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")

        cb1 = QComboBox()
        cb2 = QComboBox()

        self.cb1 = cb1
        self.cb2 = cb2

        for cb in (cb1, cb2):
            cb.addItem("lens.l.google.com")
            cb.addItem("teams.microsoft.com")
            cb.setEditable(True)

        cb1.setCurrentText(parent.settings.value('ping_host_1'))
        cb2.setCurrentText(parent.settings.value('ping_host_2'))

        layout.addRow(QLabel("first hop:"), QLabel(getFirstHop()))
        layout.addRow(QLabel("host1:"), cb1)
        layout.addRow(QLabel("host2:"), cb2)

        formGroupBox = QGroupBox("Ping hosts")
        formGroupBox.setLayout(layout)

        self.pingSize = QLineEdit()
        self.pingSize.setText(parent.settings.value('ping_size', '1024'))

        layout2 = QFormLayout()
        layout2.addRow(QLabel('ping size'), self.pingSize)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(formGroupBox)
        mainLayout.addLayout(layout2)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.activateWindow()
        #self.resize(400, 700)

    def accept(self, yes=True):
        print('accept')
        self.settings.setValue('ping_host_1', self.cb1.currentText())
        self.settings.setValue('ping_host_2', self.cb2.currentText())
        self.settings.setValue('ping_size', self.pingSize.text())
        self.hide()

    def reject(self, yes=True):
        print('reject')
        self.hide()