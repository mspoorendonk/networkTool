import sys
import sounddevice as sd
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QSlider, QPushButton
from PyQt6.QtCore import QTimer, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.frequency = 440
        self.phase = 0
        self.sample_rate = 44100
        self.is_playing = False
        
        self.initUI()
        self.start_audio()
        self.setup_sensor()
        
    def initUI(self):
        self.setWindowTitle('Simple Continuous Tone')
        self.setGeometry(100, 100, 400, 150)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.freq_label = QLabel('Frequency: 440 Hz')
        layout.addWidget(self.freq_label)
        
        # Start/Stop button
        self.play_button = QPushButton('Start')
        self.play_button.clicked.connect(self.toggle_audio)
        layout.addWidget(self.play_button)
        
        # Slider for manual control
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Orientation.Horizontal)  # Horizontal
        self.slider.setRange(200, 2000)
        self.slider.setValue(440)
        self.slider.valueChanged.connect(self.change_frequency)
        layout.addWidget(self.slider)
        
    def audio_callback(self, outdata, frames, time, status):
        """Generate continuous sine wave with phase continuity"""
        if not self.is_playing:
            outdata.fill(0)  # Output silence when not playing
            return
            
        for i in range(frames):
            outdata[i] = 0.3 * math.sin(self.phase)
            # Increment phase based on current frequency
            self.phase += 2 * math.pi * self.frequency / self.sample_rate
            # Keep phase in reasonable range to prevent overflow
            if self.phase > 2 * math.pi:
                self.phase -= 2 * math.pi
            
    def start_audio(self):
        """Start continuous audio stream"""
        self.stream = sd.OutputStream(
            callback=self.audio_callback,
            channels=1,
            samplerate=self.sample_rate,
            dtype='float32'
        )
        self.stream.start()
        
    def toggle_audio(self):
        """Toggle audio playback on/off"""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_button.setText('Stop')
        else:
            self.play_button.setText('Start')
        
    def change_frequency(self, freq):
        """Change the frequency of the continuous tone"""
        self.frequency = freq
        self.freq_label.setText(f'Frequency: {freq} Hz')
        
    def setup_sensor(self):
        """Simulate sensor readings"""
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.read_sensor)
        self.sensor_timer.start(50)  # 20Hz updates
        self.counter = 0
        
    def read_sensor(self):
        """Replace this with your actual sensor reading"""
        sensor_value = 500 + 300 * math.sin(self.counter * 0.1)
        self.counter += 1
        
        # Update frequency based on sensor
        self.change_frequency(int(sensor_value))
        
    def closeEvent(self, event):
        self.stream.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())