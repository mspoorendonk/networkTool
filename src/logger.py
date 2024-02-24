import sys
from PyQt6 import QtWidgets
import logging

from PyQt6.QtWidgets import QMainWindow



class QTextEditLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit()
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


#class MyDialog(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
class MyDialog(QtWidgets.QDialog):
#class MyDialog(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        logTextBox = QTextEditLogHandler()
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.DEBUG)

        self._button = QtWidgets.QPushButton(self)
        self._button.setText('Test Me')

        layout = QtWidgets.QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget)
        layout.addWidget(self._button)
        self.setLayout(layout)

        # Connect signal to slot
        self._button.clicked.connect(self.test)

    def test(self):
        logging.debug('damn, a bug')
        logging.info('something to remember')
        logging.warning('that\'s not right')
        logging.error('foobar')

if __name__ == '__main__':
    # Uncomment below for terminal log messages
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    app = QtWidgets.QApplication(sys.argv)
    dlg = MyDialog()
    dlg.show()
    dlg.raise_()
    sys.exit(app.exec())