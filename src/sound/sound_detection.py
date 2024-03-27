import wave
import numpy as np
import librosa
import pyaudio
import threading
from collections import deque

class FishBiteDetector:
    def __init__(self, game_window_title):
        self.game_window_title = game_window_title
        sound_file = "..\\..\\data\\fishing_data\\fishing_sequences\\fishOnTheHook_cue.wav"
        self.sound_data, self.sample_rate = librosa.load(sound_file)
        self.sound_data = librosa.util.normalize(self.sound_data)
        self.on_sound_cue_recognized = None
        
        print(f"Loaded sound file: {sound_file}")
        print(f"Sound data shape: {self.sound_data.shape}")
        print(f"Sample rate: {self.sample_rate}")
        
        self.is_running = True
        self.audio_thread = None
        self.device_index = None
        self.buffer_size = int(self.sample_rate * 1.0)  # Buffer size of 1 second
        self.ring_buffer = deque(maxlen=self.buffer_size)

    def stop_detection(self):
        self.is_running = False
        if self.audio_thread:
            self.audio_thread.join()

    def list_audio_devices(self):
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        
        print("Available audio input devices:")
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"Device index: {i}")
                print(f"Device name: {device_info['name']}")
                print(f"Device sample rate: {device_info['defaultSampleRate']}")
                print("---")

        p.terminate()

    def detect_fish_bite(self):
        # No need to record audio here, as it's already being recorded continuously
        # in the _record_and_detect_audio method
        return False
    
    def save_recorded_audio(self, output_file):
        audio_data = np.concatenate(self.audio_frames)
        
        # Convert audio data to int16 format
        audio_data = (audio_data * 32767).astype(np.int16)

        # Write audio data to WAV file
        with wave.open(output_file, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 16-bit audio
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())

        print(f"Recorded audio saved to: {output_file}")

    def _record_and_detect_audio(self, output_file, sample_rate=44100, channels=1):
        p = pyaudio.PyAudio()
        chunk_size = 1024

        if self.device_index is None:
            print("No audio input device specified. Please provide a valid device index.")
            return

        try:
            # Open the audio stream with the selected device
            stream = p.open(format=pyaudio.paFloat32,
                            channels=channels,
                            rate=sample_rate,
                            input=True,
                            input_device_index=self.device_index,
                            frames_per_buffer=chunk_size)

            print(f"Starting audio detection on device: {p.get_device_info_by_index(self.device_index)['name']}")

            self.audio_frames = []

            while self.is_running:
                data = stream.read(chunk_size)
                audio_segment = np.frombuffer(data, dtype=np.float32)

                # Append audio segment to the ring buffer
                self.ring_buffer.extend(audio_segment)

                # Append audio segment to the list of frames
                self.audio_frames.append(audio_segment)

                # Check if the buffer has enough data for processing
                if len(self.ring_buffer) == self.buffer_size:
                    # Convert the ring buffer to a numpy array
                    audio_data = np.array(self.ring_buffer)

                    # Process the audio data
                    similarity = self._compute_similarity(audio_data)
                    if similarity is not None:
                        print(f"Similarity: {similarity:.2f}")

                        threshold = 0.8
                        if similarity >= threshold:
                            print(f"Fish bite detected! Similarity: {similarity:.2f}")
                            if self.on_sound_cue_recognized:
                                self.on_sound_cue_recognized()

            stream.stop_stream()
            stream.close()
            p.terminate()

            # Save the recorded audio to a file
            self.save_recorded_audio(output_file)

            print("Audio detection stopped.")

        except OSError as e:
            print(f"Error occurred while opening the audio stream: {str(e)}")
            print("Please check the audio device settings and ensure the selected device is valid.")
        
    def start_detection(self, device_index, output_file):
        self.device_index = device_index
        self.is_running = True
        self.audio_thread = threading.Thread(target=self._record_and_detect_audio, args=(output_file,))
        self.audio_thread.start()

    def _compute_similarity(self, audio_segment):        
        try:
            audio_segment = librosa.util.normalize(audio_segment)
            correlation = np.correlate(audio_segment, self.sound_data, mode='valid')
            similarity = np.max(correlation) / np.sqrt(np.sum(audio_segment ** 2) * np.sum(self.sound_data ** 2))
            return similarity
        except Exception as e:
            print(f"Error in similarity computation: {str(e)}")
            return 0.0  # Return a default value (e.g., 0.0) in case of an error