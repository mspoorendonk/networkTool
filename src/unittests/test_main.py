#from logging import NullHandler
#from unittest import TestCase
from main import *
#import os
#from time import sleep
#from threading import Thread

#dataStore = 0

class TestSound(TestCase):
    def testSound(self):
        QtMultimedia.QSound(os.path.join('resources', 'slowdown.wav')).play()
        sleep(2)

    def testSound2(self):
        QtMultimedia.QSound.play('slowdown.wav')
        sleep(2)

    def testSound3(self):
        url = QtCore.QUrl.fromLocalFile(os.path.join('resources', 'slowdown.wav'))
        content = QtMultimedia.QMediaContent(url)
        player = QtMultimedia.QMediaPlayer()
        player.setMedia(content)
        player.setVolume(50)
        player.play()
        sleep(2)


class TestMainWindow(TestCase):
    def fireUpUi(self):
        app = QApplication(sys.argv)
        self.app = app
        self.app.setStyle('Fusion')
        
        self.win = MainWindow()
        app.exec()

    def setUp(self):
        #global dataStore
        #dataStore = DataStore()
        Thread(target=self.fireUpUi).start()
        sleep(4)
        

    def tearDown(self):
        self.app.deleteLater()

    def test_start_pings(self):
        self.win.startPings()
        sleep(15)
        self.win.stop.emit()

    def test_start_ookla(self):
        self.win.startOokla()
        sleep(15)
        self.win.stop.emit()

    def test_start_iperf_upload(self):
        self.fail()

    def test_start_iperf_down(self):
        self.fail()

    def test_start_iperf_bidirectional(self):
        self.fail()

    def test_start_iperf_alternating(self):
        self.fail()

    def test_clear(self):
        self.win.clear()
        self.fail()

    def test_export(self):
        self.win.export()
        #self.fail()
