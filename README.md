# Rust Fishing Bot

This repository contains a Rust Fishing Bot that automates the fishing process in the game Rust. The bot utilizes computer vision, machine learning, and audio processing techniques to detect fish bites, analyze fishing rod movements, and interact with the game.

**Important Notes:**
- This project was made for a bachelor's thesis.
- There is no model nor data provided in this repository, thus making it not useful for people looking for a functioning tool.
- This project is done for educational purposes only.

## Features

- Automated fishing in Rust
- Fish bite detection using audio processing
- Fishing rod movement analysis using computer vision
- Machine learning model for predicting fishing tension
- Game interaction and control

## Requirements

- Python 3.x
- OpenCV
- TensorFlow
- Keras
- scikit-learn
- soundcard
- soundfile
- librosa
- noisereduce
- pyautogui

## Data Collection

The `src/collect_data.py` script can be used to collect fishing data by recording the game screen and audio. The collected data can be used for training and testing the machine learning models.

## Machine Learning

The `src/ml` directory contains scripts for data preprocessing, model training, and model evaluation. The trained models are used by the fishing bot to predict the fishing tension based on the captured game frames.

## Bot Functionality

The `src/bot` directory contains the main functionality of the fishing bot, including fish bite detection, fish caught detection, and game interaction.

## Sound Processing

The `src/sound` directory contains scripts for audio processing, including fish bite detection using sound cues.

## Video Processing

The `src/video` directory contains scripts for video processing, including fish movement detection and fishing rod shake analysis.

## Contributing

As this project was created for a bachelor's thesis and is for educational purposes only, contributions are not actively sought. However, if you have any suggestions or feedback, feel free to open an issue.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- The Rust game developers for creating an engaging fishing minigame.
- The open-source community for providing valuable libraries and tools.
- The bachelor's thesis supervisor for guidance and support throughout the project.

Please note that this repository does not contain the trained models or the dataset used in the project. The purpose of this repository is to showcase the code and techniques used in the development of the Rust Fishing Bot as part of a bachelor's thesis.