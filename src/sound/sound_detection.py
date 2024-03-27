import soundcard as sc
import soundfile as sf
import numpy as np
import librosa
import threading

class FishBiteDetector:
    def __init__(self):
        sound_file = "..\\..\\data\\fishing_data\\fishing_sequences\\fishOnTheHook_cue.wav"
        self.sound_data, self.sample_rate = librosa.load(sound_file)
        self.sound_data = librosa.util.normalize(self.sound_data)
        self.on_sound_cue_recognized = None
        
        print(f"Loaded sound file: {sound_file}")
        print(f"Sound data shape: {self.sound_data.shape}")
        print(f"Sample rate: {self.sample_rate}")
        
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

    def _record_and_detect_audio(self):
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=self.sample_rate) as mic:
            print("Starting audio detection from speakers...")

            while self.is_running:
                # Record audio from the speakers
                data = mic.record(numframes=self.buffer_size)
                audio_segment = data[:, 0]  # Use only the first channel

                # Process the audio data
                similarity = self._compute_similarity(audio_segment)
                if similarity is not None:
                    print(f"Similarity: {similarity:.2f}")

                    threshold = 0.8
                    if similarity >= threshold:
                        print(f"Fish bite detected! Similarity: {similarity:.2f}")
                        if self.on_sound_cue_recognized:
                            self.on_sound_cue_recognized()
                
                # Repeat the check multiple times within the same buffer
                num_repeats = 5  # Adjust this value as needed
                for _ in range(num_repeats):
                    data = mic.record(numframes=self.buffer_size // num_repeats)
                    audio_segment = data[:, 0]
                    similarity = self._compute_similarity(audio_segment)
                    if similarity is not None and similarity >= threshold:
                        print(f"Fish bite detected! Similarity: {similarity:.2f}")
                        if self.on_sound_cue_recognized:
                            self.on_sound_cue_recognized()

        print("Audio detection stopped.")

    def _compute_similarity(self, audio_segment):
        try:
            audio_segment = librosa.util.normalize(audio_segment)
            
            # Ensure the lengths of audio_segment and sound_data match
            if len(audio_segment) < len(self.sound_data):
                # Pad audio_segment with zeros to match the length of sound_data
                audio_segment = np.pad(audio_segment, (0, len(self.sound_data) - len(audio_segment)), mode='constant')
            elif len(audio_segment) > len(self.sound_data):
                # Truncate audio_segment to match the length of sound_data
                audio_segment = audio_segment[:len(self.sound_data)]
            
            # Compute cross-correlation using FFT
            correlation = np.fft.irfft(np.fft.rfft(audio_segment) * np.conj(np.fft.rfft(self.sound_data)))
            
            # Find the maximum correlation value and its index
            max_correlation = np.max(correlation)
            max_index = np.argmax(correlation)
            
            # Compute the similarity score
            similarity = max_correlation / np.sqrt(np.sum(audio_segment ** 2) * np.sum(self.sound_data ** 2))
            
            return similarity
        except Exception as e:
            print(f"Error in similarity computation: {str(e)}")
            return 0.0  # Return a default value (e.g., 0.0) in case of an error