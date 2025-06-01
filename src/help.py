"""
Help window

"""

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class HelpDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle('Help')

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setGeometry(QRect(150, 250, 341, 32))
        self.buttonBox.setObjectName("buttonBox")

        help_text = (
            "<b>Network Tool Help</b><br><br>"
            "<b>Bandwidth</b> is the maximum rate of data transfer across a network, measured in megabits per second (Mbps). Higher bandwidth means more data can be sent or received per second.\n<br><br>"
            "<b>Ping</b> measures the round-trip time for messages sent from your computer to another host and back, in milliseconds (ms). Lower ping means less delay and a more responsive connection.\n<br><br>"
            "<b>LAN Bandwidth Test (iperf)</b>:<br>"
            "To test your local network (LAN) speed, you need to run an <b>iperf server</b> on one machine in your network. This application will automatically search for the iperf server in your subnet.\n<br>"
            "<ul>"
            "<li>Download and run <b>iperf3</b> on another computer in your LAN.</li>"
            "<li>Start the server with: <code>iperf3 -s</code></li>"
            "<li>Then, use this tool to run the LAN bandwidth test.</li>"
            "</ul>"
            "If no server is found, make sure the firewall allows iperf3 and both computers are on the same subnet.\n<br><br>"
            "<b>Internet Bandwidth Test (Ookla)</b>:<br>"
            "This test uses the Ookla Speedtest CLI to measure your internet speed.\n<br><br>"
            "For more information, see the documentation or contact the author."
        )

        mainLayout = QVBoxLayout()
        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setText(help_text)
        label.setWordWrap(True)
        mainLayout.addWidget(label)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.buttonBox.accepted.connect(self.accept)

        self.activateWindow()
        # self.resize(500, 700)

    def accept(self):
        print('accept')
        self.hide()
