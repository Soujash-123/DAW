import sys
import os
import pyaudio
import wave
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QComboBox, QLabel

class AudioStudio(QWidget):
    def __init__(self):
        super().__init__()

        # Define audio recording parameters
        self.chunk = 1024
        self.sample_format = pyaudio.paInt16
        self.channels = 2
        self.fs = 44100
        self.seconds = 5

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

        # Define the GUI components
        self.record_button = QPushButton('Record')
        self.stop_button = QPushButton('Stop')
        self.filter_button = QPushButton('Apply Filter')
        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems(['None', 'Equalization', 'Compression', 'Reverb'])
        self.file_label = QLabel('No file selected')
        self.file_button = QPushButton('Select File')
        
        # Add the components to the layout
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.record_button)
        hbox1.addWidget(self.stop_button)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.filter_dropdown)
        hbox2.addWidget(self.filter_button)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.file_label)
        hbox3.addWidget(self.file_button)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        self.setLayout(vbox)

        # Connect signals to slots
        self.record_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.filter_button.clicked.connect(self.apply_filter)
        self.file_button.clicked.connect(self.select_file)

        # Set window properties
        self.setWindowTitle('Audio Studio')
        self.setGeometry(100, 100, 400, 200)

    def start_recording(self):
        self.stream = self.p.open(format=self.sample_format,
                    channels=self.channels,
                    rate=self.fs,
                    frames_per_buffer=self.chunk,
                    input=True)
        self.frames = []
        for i in range(0, int(self.fs / self.chunk * self.seconds)):
            data = self.stream.read(self.chunk)
            self.frames.append(data)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        # Save recorded audio to a file
        wf = wave.open("recording.wav", "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b"".join(self.frames))
        wf.close()
        self.file_label.setText('recording.wav')

    def stop_recording(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def apply_filter(self):
        filter_type = self.filter_dropdown.currentText()
        if filter_type == 'None':
            return
        elif filter_type == 'Equalization':
            # Apply equalization filter
            if self.file_label.text() == 'No file selected':
                file_path = 'recording.wav'
            else:
                file_path = self.file_label.text()
            os.system(f"ffmpeg -i {file_path} -af equalizer=f=1000:width_type=h:width=50:g=-10 output.wav")
            if self.file_label.text() == 'No file selected':
                self.file_label.setText('output.wav')
        elif filter_type == 'Compression':
            # Apply compression filter
            if self.file_label.text() == 'No file selected':
                file_path = 'recording.wav'
            else:
                file_path = self.file_label.text()
            os.system(f"ffmpeg -i {file_path} -af compand=attacks=0:decays=0:points=-80/-80|-40/-10|0/-10|20/-10:soft-knee=10:volume=-40dB output.wav")
            if self.file_label.text() == 'No file selected':
                self.file_label.setText('output.wav')
        elif filter_type == 'Reverb':
            # Apply reverb filter
            if self.file_label.text() == 'No file selected':
                file_path = 'recording.wav'
            else:
                file_path = self.file_label.text()
            os.system(f"ffmpeg -i {file_path} -af aecho=0.8:0.9:1000:0.3 output.wav")
            if self.file_label.text() == 'No file selected':
                self.file_label.setText('output.wav')
    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Audio File', os.getcwd(), 'Audio Files (*.wav;*.mp3;*.ogg)')
        self.file_label.setText(file_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    studio = AudioStudio()
    studio.show()
    sys.exit(app.exec_())
