import soundcard as sc
import soundfile as sf
import numpy as np
import librosa
import threading
import os
import warnings
import time
from scipy.signal import butter, sosfilt
import noisereduce as nr

class FishBiteDetector():
    def __init__(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        reference_dir = os.path.join(project_root, "data", "fishing_data", "fishing_sequences")
        self.reference_sounds = []
        self.sample_rate = None
        self.clear_sound_data = None
        
        # Load the clear sound file
        clear_sound_file = os.path.join(reference_dir, "fOTH_cue_water1.wav")
        clear_sound_data, sample_rate = librosa.load(clear_sound_file)
        
        if self.sample_rate is None:
            self.sample_rate = sample_rate
        elif self.sample_rate != sample_rate:
            raise ValueError("Inconsistent sample rates between clear sound file and reference sound files.")
        
        self.clear_sound_data = clear_sound_data
        
        for file in os.listdir(reference_dir):
            if file.endswith(".wav") and file != "fOTH_cue_clear1.wav":
                sound_file = os.path.join(reference_dir, file)
                sound_data, sample_rate = librosa.load(sound_file)
                
                if sample_rate != self.sample_rate:
                    raise ValueError("Inconsistent sample rates among reference sound files.")
                
                sound_data = self._preprocess_audio(sound_data, self.clear_sound_data)  # Preprocess the reference sound
                self.reference_sounds.append((sound_data, file))
                print(f"Loaded reference sound file: {sound_file}")

        if self.sample_rate is None:
            raise ValueError("No valid reference sound files found.")

        self.on_sound_cue_recognized = None
        self.is_running = True
        self.audio_thread = None
        self.buffer_size = int(self.sample_rate * 0.5)  # Buffer size

    def start_detection(self):
        self.is_running = True
        self.audio_thread = threading.Thread(target=self._record_and_detect_audio)
        self.audio_thread.start()

    def stop_detection(self):
        self.is_running = False
        if self.audio_thread:
            self.audio_thread.join()

    def record_audio(self, duration, output_file):
        print(f"Recording audio for {duration} seconds...")
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=self.sample_rate) as mic:
            data = mic.record(numframes=int(self.sample_rate * duration))
            sf.write(file=output_file, data=data[:, 0], samplerate=self.sample_rate)
        print(f"Recorded audio saved to: {output_file}")

    def _record_and_detect_audio(self):
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=self.sample_rate) as mic:
            print("Starting audio detection from speakers...")

            while self.is_running:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=sc.SoundcardRuntimeWarning)
                    # Record audio from the speakers
                    data = mic.record(numframes=self.buffer_size)
                    audio_segment = data[:, 0]  # Use only the first channel
                
                    # Preprocess the incoming audio
                    preprocessed_audio = self._preprocess_audio(audio_segment, self.clear_sound_data)
                
                    # Process the preprocessed audio data
                    similarity, file_name = self._compute_similarity(preprocessed_audio)
                    if similarity is not None:
                        print(f"Similarity: {similarity:.2f}, File: {file_name}")

                        threshold = 0.4
                        if similarity >= threshold:
                            print(f"Fish bite detected! Similarity: {similarity:.2f}, File: {file_name}")
                            if self.on_sound_cue_recognized:
                                self.on_sound_cue_recognized(similarity)  # Pass the similarity value to the callback

            print("Audio detection stopped.")

            print("Audio detection stopped.")

    def _compute_similarity(self, audio_segment):
        try:
            audio_segment = librosa.util.normalize(audio_segment)
            
            max_similarity = 0.0
            max_file_name = ""
            
            for reference_sound, file_name in self.reference_sounds:
                # Ensure the lengths of audio_segment and reference_sound match
                if len(audio_segment) < len(reference_sound):
                    # Pad audio_segment with zeros to match the length of reference_sound
                    audio_segment = np.pad(audio_segment, (0, len(reference_sound) - len(audio_segment)), mode='constant')
                elif len(audio_segment) > len(reference_sound):
                    # Truncate audio_segment to match the length of reference_sound
                    audio_segment = audio_segment[:len(reference_sound)]
                
                # Compute cross-correlation using FFT
                correlation = np.fft.irfft(np.fft.rfft(audio_segment) * np.conj(np.fft.rfft(reference_sound)))
                
                # Find the maximum correlation value
                max_correlation = np.max(correlation)
                
                # Compute the similarity score
                similarity = max_correlation / np.sqrt(np.sum(audio_segment ** 2) * np.sum(reference_sound ** 2))
                
                # Update the maximum similarity and corresponding file name
                if similarity > max_similarity:
                    max_similarity = similarity
                    max_file_name = file_name
            
            return max_similarity, max_file_name
        except Exception as e:
            print(f"Error in similarity computation: {str(e)}")
            return 0.0, ""  # Return a default similarity of 0.0 and an empty file name in case of an error
        
    def _preprocess_audio(self, audio_data, sound_cue_data=None):
        # Apply adaptive noise reduction
        noise_reduced_audio = self._reduce_noise(audio_data, sound_cue_data)
        
        # Apply normalization
        normalized_audio = librosa.util.normalize(noise_reduced_audio)
        
        # Check for non-finite values
        if not np.isfinite(normalized_audio).all():
            print("Warning: Non-finite values encountered in audio data. Skipping preprocessing.")
            return audio_data
        
        # Apply filtering (e.g., bandpass filter)
        filtered_audio = self._apply_bandpass_filter(normalized_audio)
        
        return filtered_audio

    def _reduce_noise(self, audio_data, sound_cue_data):
        # Find the portion of audio that doesn't contain the sound cue
        sound_cue_length = len(sound_cue_data)
        audio_length = len(audio_data)
        
        if audio_length <= sound_cue_length:
            # If the audio segment is shorter than or equal to the sound cue length,
            # use the entire audio segment for noise reduction
            noise_reduced_audio = nr.reduce_noise(audio_data, sr=self.sample_rate)
        else:
            # Find the portion of audio that doesn't contain the sound cue
            cross_correlation = np.correlate(audio_data, sound_cue_data, mode='valid')
            sound_cue_end_index = np.argmax(cross_correlation) + sound_cue_length
            
            if sound_cue_end_index < audio_length:
                # Use the portion of audio after the sound cue for noise reduction
                noise_sample = audio_data[sound_cue_end_index:]
            else:
                # If the sound cue ends at the end of the audio segment,
                # use the entire audio segment for noise reduction
                noise_sample = audio_data
            
            # Apply noise reduction
            noise_reduced_audio = nr.reduce_noise(audio_data, y_noise=noise_sample, sr=self.sample_rate)

        return noise_reduced_audio

    def _apply_bandpass_filter(self, audio_data, low_freq=500, high_freq=2000):
        # Define the filter parameters
        order = 5
        nyquist_freq = 0.5 * self.sample_rate
        low = low_freq / nyquist_freq
        high = high_freq / nyquist_freq
        
        # Design the bandpass filter
        sos = butter(order, [low, high], btype='band', output='sos')
        
        # Apply the filter to the audio data
        audio_filtered = sosfilt(sos, audio_data)
        
        return audio_filtered