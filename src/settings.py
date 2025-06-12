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
        self.initUI()

    def initUI(self):

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

        cb1.setCurrentText(self.settings.value('ping_host_1'))
        cb2.setCurrentText(self.settings.value('ping_host_2'))

        layout.addRow(QLabel("first hop"), QLabel(getFirstHop(), toolTip="Autodetected. In case of wifi this is the router."))
        layout.addRow(QLabel("host1"), cb1)
        layout.addRow(QLabel("host2"), cb2)

        formGroupBox = QGroupBox("Ping hosts")
        formGroupBox.setLayout(layout)

        self.pingSize = QLineEdit()
        self.pingSize.setText(self.settings.value('ping_size', '1024'))
        self.pingSize.setToolTip('The size of the ping packets. The default is 1024 bytes.')

        layout2 = QFormLayout()
        layout2.addRow(QLabel('ping size'), self.pingSize)

        # Add tone settings
        self.toneComboBox = QComboBox(self)
        self.toneComboBox.addItems(['muted', 'ping1', 'pingFirstHop', 'iperfUp', 'iperfDown', 'ooklaUp', 'ooklaDown'])
        self.toneComboBox.setCurrentText(self.settings.value('tone_series', 'muted'))
        self.toneComboBox.setToolTip('The series to which the tone will be attached. The tone will be high when the bandwith is high or the latency is low.')
        layout2.addRow(QLabel('Tone'), self.toneComboBox)

        # Add setting for maximum bandwidth, set the default to 1000Mbps
        self.maxBandwidth = QLineEdit()
        self.maxBandwidth.setText(self.settings.value('max_bandwidth', '1000'))
        self.maxBandwidth.setToolTip('The maximum bandwidth in Mbps. The tone will be high when the bandwidth is close to this value.')
        layout2.addRow(QLabel('Max bandwidth'), self.maxBandwidth)

        # Add setting for maximum latency, set the default to 100ms
        self.maxLatency = QLineEdit()
        self.maxLatency.setText(self.settings.value('max_latency', '100'))
        self.maxLatency.setToolTip('The maximum latency in ms. The tone will be low when the latency is close to this value.')
        layout2.addRow(QLabel('Max latency'), self.maxLatency)

        # Put all the settings in a vertical layout
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
        self.settings.setValue('tone_series', self.toneComboBox.currentText())
        self.settings.setValue('max_bandwidth', self.maxBandwidth.text())
        self.settings.setValue('max_latency', self.maxLatency.text())
        self.hide()

    def reject(self, yes=True):
        print('reject')
        self.hide()