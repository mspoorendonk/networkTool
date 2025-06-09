from time import sleep
from threading import Thread
from PyQt6 import QtCore, uic, QtMultimedia
import pytest
from src.main import MainWindow, QApplication
import os
import logging
from pathlib import Path

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
    for _ in range(60):  # 60 * 0.1s = 6 seconds
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()
    sleep(6) # wait for few seconds to make sure the ookla server is ready for the next run
    QApplication.processEvents() # let the status bar message be processed
    assert main_window.statusBar().currentMessage() == 'ping done'
    # assert that there are at least some values in the series that are > 0
    assert any(value > 0 for value in main_window.dataStore.data['ping1'].value)
    assert any(value > 0 for value in main_window.dataStore.data['pingFirstHop'].value)
    sleep(5)


def test_start_ookla(main_window):
    main_window.startOokla()
    for _ in range(120):  # 120 * 0.1s = 12 seconds
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()
    sleep(2) # wait for few seconds to make sure the ookla server is ready for the next run
    QApplication.processEvents() # let the status bar message be processed
    assert main_window.statusBar().currentMessage() == 'ookla done'
    # assert that there are at least some values in the series that are > 0
    assert any(value > 0 for value in main_window.dataStore.data['ooklaDown'].value)
    assert any(value > 0 for value in main_window.dataStore.data['ooklaUp'].value)

def test_start_iperf_upload(main_window):
    main_window.startIperfUpload()
    for _ in range(120):
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()
    sleep(2) # wait for 2 seconds to make sure the iperf server is ready for the next run
    assert main_window.dataStore.data['iperf_up'].value[-2] > 0
    assert main_window.statusBar().currentMessage() == 'iperf done'

def test_start_iperf_down(main_window):
    main_window.startIperfDown()
    for _ in range(60):
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()
    sleep(6) # wait for 2 seconds to make sure the iperf server is ready for the next run
    QApplication.processEvents() # let the status bar message be processed
    assert main_window.dataStore.data['iperfDown'].value[-3] > 0
    assert main_window.statusBar().currentMessage() == 'iperf done'

def test_start_iperf_bidirectional(main_window):
    main_window.startIperfBidirectional()
    for _ in range(120):
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()
    sleep(6) # wait for 2 seconds to make sure the iperf server is ready for the next run
    QApplication.processEvents() # let the status bar message be processed
    assert main_window.statusBar().currentMessage() == 'iperf done'
    assert any(value > 0 for value in main_window.dataStore.data['iperfUp'].value)
    assert any(value > 0 for value in main_window.dataStore.data['iperfDown'].value)

def test_start_iperf_alternating(main_window):
    main_window.startIperfAlternating()
    for _ in range(240):
        QApplication.processEvents()
        sleep(0.1)
    main_window.stop.emit()
    sleep(15) # wait for 2 seconds to make sure the iperf server is ready for the next run
    QApplication.processEvents() # let the status bar message be processed
    assert main_window.statusBar().currentMessage() == 'iperf done'
    # assert that there are at least some values in the series that are > 0
    assert any(value > 0 for value in main_window.dataStore.data['iperfUp'].value)
    assert any(value > 0 for value in main_window.dataStore.data['iperfDown'].value)

def test_clear(main_window):
    main_window.clear()
    # Assert all series are empty
    for name, series in main_window.dataStore.data.items():
        assert len(series.value) == 0
        assert len(series.timestamp) == 0
        assert len(series.connect) == 0
        assert len(series.comment) == 0
        assert len(series.commentTimestamp) == 0
    # Assert stats labels are reset
    for stats in (main_window.lanStats, main_window.internetStats):
        for label in (
            stats.maxDownLabel, stats.avgDownLabel, stats.minDownLabel, stats.curDownLabel,
            stats.maxUpLabel, stats.avgUpLabel, stats.minUpLabel, stats.curUpLabel
        ):
            assert label.text() == '-'
    # Assert status bar message
    assert main_window.statusBar().currentMessage() == 'Data cleared'

def test_export(main_window, tmp_path, monkeypatch):
    # Patch getMyDocuments to use a temp directory
    import src.util as util

    main_window.dataStore.export(exportFolder = str(tmp_path))
    # Check that a CSV file was created for each series
    for name in main_window.dataStore.data.keys():
        csv_file = tmp_path / f'{name}.csv'
        assert csv_file.exists(), f"{csv_file} does not exist"
