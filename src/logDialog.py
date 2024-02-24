
"""
Log window

"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class LogDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent, Qt.WindowCloseButtonHint)

        self.setWindowTitle('Log')

        logLabel = QLabel(self)

