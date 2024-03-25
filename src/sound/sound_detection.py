import numpy as np
import librosa

class FishBiteDetector:
    def __init__(self, game_window_title):
        self.game_window_title = game_window_title
        sound_file = "..\\..\\data\\fishing_data\\fishing_sequences\\fishOnTheHook_cue.wav"
        self.sound_data, self.sample_rate = librosa.load(sound_file)
        self.sound_data = librosa.util.normalize(self.sound_data)
        
        print(f"Loaded sound file: {sound_file}")
        print(f"Sound data shape: {self.sound_data.shape}")
        print(f"Sample rate: {self.sample_rate}")

    def detect_fish_bite(self):
        # Placeholder for fish bite detection logic
        return False

    def _compute_similarity(self, audio_segment):
        # Normalize the audio segment
        audio_segment = librosa.util.normalize(audio_segment)

        # Compute the cross-correlation between the audio segment and the fish bite sound
        correlation = np.correlate(audio_segment, self.sound_data, mode='valid')
        similarity = np.max(correlation) / np.sqrt(np.sum(audio_segment ** 2) * np.sum(self.sound_data ** 2))

        return similarity