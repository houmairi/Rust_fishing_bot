import numpy as np
import librosa
import os
import pyaudio
import win32gui

class FishBiteDetector:
    def __init__(self, game_window_title):
        self.game_window_title = game_window_title
        sound_file = "..\\..\\data\\fishing_data\\fishing_sequences\\fishOnTheHook_cue.wav"
        self.sound_data, self.sample_rate = librosa.load(sound_file)
        self.sound_data = librosa.util.normalize(self.sound_data)

    def detect_fish_bite(self):
        # Check if the game window is active
        window_handle = win32gui.FindWindow(None, self.game_window_title)
        if window_handle == 0:
            return False

        # Capture the game's audio stream
        audio_segment = self.capture_game_audio()

        # Compute the similarity between the audio segment and the fish bite sound
        similarity = self._compute_similarity(audio_segment)

        # Check if the similarity exceeds a predefined threshold
        threshold = 0.8  # Adjust this value based on your testing
        if similarity >= threshold:
            return True
        else:
            return False

    def capture_game_audio(self):
        chunk = 1024
        sample_format = pyaudio.paFloat32
        channels = 1
        sample_rate = self.sample_rate
        capture_duration = 1  # Capture audio for 1 second

        p = pyaudio.PyAudio()
        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk)

        frames = []
        for _ in range(0, int(sample_rate / chunk * capture_duration)):
            data = stream.read(chunk)
            frames.append(np.frombuffer(data, dtype=np.float32))

        stream.stop_stream()
        stream.close()
        p.terminate()

        audio_segment = np.concatenate(frames)
        return audio_segment

    def _compute_similarity(self, audio_segment):
        # Normalize the audio segment
        audio_segment = librosa.util.normalize(audio_segment)

        # Compute the cross-correlation between the audio segment and the fish bite sound
        correlation = np.correlate(audio_segment, self.sound_data, mode='valid')
        similarity = np.max(correlation) / np.sqrt(np.sum(audio_segment ** 2) * np.sum(self.sound_data ** 2))

        return similarity