import soundcard as sc
import soundfile as sf
import numpy as np
import librosa
import threading
import os
import warnings
import time

class FishBiteDetector():
    def __init__(self):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        reference_dir = os.path.join(project_root, "data", "fishing_data", "fishing_sequences")
        self.reference_sounds = []
        self.sample_rate = None
        
        for file in os.listdir(reference_dir):
            if file.endswith(".wav"):
                sound_file = os.path.join(reference_dir, file)
                sound_data, sample_rate = librosa.load(sound_file)
                sound_data = librosa.util.normalize(sound_data)
                self.reference_sounds.append((sound_data, file))  # Store both sound_data and file_name
                print(f"Loaded reference sound file: {sound_file}")
                
                if self.sample_rate is None:
                    self.sample_rate = sample_rate
        
        self.on_sound_cue_recognized = None
        self.is_running = True
        self.audio_thread = None
        self.buffer_size = int(self.sample_rate * 1.0)  # Buffer size of 1 second

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

    #two steps i can do to increase the comparison 
    #We gather audio files that represent the sound cue we want to detect. These audio files serve as training examples for the system.
    #Audio Enhancement: Apply audio enhancement techniques to the recorded audio segments before similarity comparison. This can include noise reduction, equalization, or filtering to emphasize the relevant frequencies of the sound cue. By improving the signal-to-noise ratio and reducing the impact of background noise, you can enhance the accuracy of the sound cue detection.
    
    def _record_and_detect_audio(self):
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=self.sample_rate) as mic:
            print("Starting audio detection from speakers...")

            while self.is_running:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=sc.SoundcardRuntimeWarning)
                    # Record audio from the speakers
                    data = mic.record(numframes=self.buffer_size)
                    audio_segment = data[:, 0]  # Use only the first channel

                    # Process the audio data
                    similarity, file_name = self._compute_similarity(audio_segment)
                    if similarity is not None:
                        print(f"Similarity: {similarity:.2f}, File: {file_name}")

                        threshold = 0.8
                        if similarity >= threshold:
                            print(f"Fish bite detected! Similarity: {similarity:.2f}, File: {file_name}")
                            if self.on_sound_cue_recognized:
                                self.on_sound_cue_recognized(similarity)  # Pass the similarity value to the callback

                # Sleep for 1 second before the next iteration
                if self.is_running:
                    time.sleep(1)

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