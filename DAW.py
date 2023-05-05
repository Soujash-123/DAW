import numpy as np
import scipy.io.wavfile as wavfile
import scipy.signal as signal
import librosa

class DAW:
    def __init__(self):
        self.tracks = []
        self.sample_rate = None
        self.channels = None
    
    def add_track(self, filename):
        rate, data = wavfile.read(filename)
        self.tracks.append(data)
        if self.sample_rate is None:
            self.sample_rate = rate
            self.channels = data.shape[1]
    
    def upload_track(self, data, sample_rate):
        self.tracks.append(data)
        if self.sample_rate is None:
            self.sample_rate = sample_rate
            self.channels = data.shape[1]
    
    def save(self, filename):
        data = np.zeros((len(self.tracks[0]), self.channels))
        for track in self.tracks:
            data += track
        data /= len(self.tracks)
        wavfile.write(filename, self.sample_rate, data.astype(np.int16))
    
    def increase_volume(self, factor):
        for i in range(len(self.tracks)):
            self.tracks[i] *= factor
    
    def decrease_volume(self, factor):
        for i in range(len(self.tracks)):
            self.tracks[i] /= factor
    
    def denoise(self, window_size=4096, threshold=0.1):
        for i in range(len(self.tracks)):
            track = self.tracks[i]
            for j in range(self.channels):
                channel = track[:, j]
                noise = np.abs(signal.medfilt(np.abs(channel), window_size) - np.abs(channel))
                mask = noise < threshold * np.max(noise)
                channel[mask] = 0
    
    def add_reverb(self, decay=0.5, delay=0.1):
        impulse_response = np.zeros(int(self.sample_rate * delay))
        impulse_response[0] = 1
        impulse_response = signal.lfilter([1], [1, -decay], impulse_response)
        for i in range(len(self.tracks)):
            self.tracks[i] = signal.convolve(self.tracks[i], impulse_response)

# Example usage
if __name__ == '__main__':
    # Load audio data from file
    data, sample_rate = librosa.load('new_track.wav', sr=44100, mono=False)

    # Create DAW instance and upload track
    daw = DAW()
    daw.upload_track(data, sample_rate)

    # Apply effects and save mixed track
    daw.increase_volume(2)
    daw.denoise()
    daw.add_reverb()
    daw.save('mixed.wav')