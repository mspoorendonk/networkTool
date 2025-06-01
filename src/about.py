"""
About window

"""

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class AboutDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle('About')

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setGeometry(QRect(150, 250, 341, 32))
        #self.buttonBox.setOrientation(Qt.Horizontal)
        #self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(QLabel(
            "This program is written by Marc Spoorendonk, 2021. There was no tool available that showed\n"
            + "the status of the network in one glance in a visually pleasing way. So I decided to\n"
            + "write one as a hobbies project. It is a nice opportunity to get some PyQtChart\n"
            + "experience along the way.\n\nLet me know if you like it or when you have some suggestions.\n"))
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.buttonBox.accepted.connect(self.accept)

        self.activateWindow()
        # self.resize(400, 700)

    def accept(self):
        print('accept')
        self.hide()
