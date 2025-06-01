from time import sleep
from threading import Thread
from PyQt6 import QtCore, uic, QtMultimedia
import pytest
from src.main import MainWindow, QApplication
import os
import logging

#dataStore = 0

# Sound tests as plain functions

def test_sound():
    url = QtCore.QUrl.fromLocalFile(os.path.join('resources', 'slowdown.wav'))
    player = QtMultimedia.QMediaPlayer()
    player.setSource(url)
    player.play()
    sleep(2)

def test_sound2():
    url = QtCore.QUrl.fromLocalFile('resources/slowdown.wav')
    player = QtMultimedia.QMediaPlayer()
    player.setSource(url)
    player.play()
    sleep(2)

def test_sound3():
    url = QtCore.QUrl.fromLocalFile(os.path.join('resources', 'slowdown.wav'))
    player = QtMultimedia.QMediaPlayer()
    player.setSource(url)
    player.play()
    sleep(2)

# Pytest fixture for MainWindow
@pytest.fixture(scope="module")
def main_window():
    # Uncomment below for terminal log messages
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # You can control the logging level
    logging.getLogger().setLevel(logging.DEBUG)  

    app = QApplication([])
    app.setStyle('Fusion')
    win = MainWindow()
    yield win
    win.close()
    app.quit()

# MainWindow tests as plain functions

def test_start_pings(main_window):
    main_window.startPings()
    for _ in range(120):  # 120 * 0.1s = 12 seconds
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()

def test_start_ookla(main_window):
    main_window.startOokla()
    for _ in range(120):  # 120 * 0.1s = 12 seconds
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()

def test_start_iperf_upload(main_window):
    main_window.startIperfUpload()
    for _ in range(120):
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()

def test_start_iperf_down(main_window):
    main_window.startIperfDown()
    for _ in range(120):
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()

def test_start_iperf_bidirectional(main_window):
    main_window.startIperfBidirectional()
    for _ in range(120):
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()

def test_start_iperf_alternating(main_window):
    main_window.startIperfAlternating()
    for _ in range(120):
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()

def test_clear(main_window):
    main_window.clear()
    # Optionally add assertions here

def test_export(main_window):
    main_window.export()
    # Optionally add assertions here
