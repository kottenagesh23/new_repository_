# Install necessary packages first:
# pip install SpeechRecognition
# pip install rake-nltk
# pip install pyaudio  (for microphone input, optional if you use an audio file)

import speech_recognition as sr
from rake_nltk import Rake
import nltk
from nltk.data import find
import os


def ensure_nltk_data():
    resources = [
        ("corpora/stopwords", "stopwords"),
        ("tokenizers/punkt_tab", "punkt_tab"),
    ]
    for path, pkg in resources:
        try:
            find(path)
        except LookupError:
            nltk.download(pkg, quiet=True)


def speech_to_text_from_wav():
    recognizer = sr.Recognizer()
    print("\nEnter path to a WAV file (or press Enter to skip):")
    wav_path = input("> ").strip().strip('"')
    if not wav_path:
        return None
    if not os.path.isfile(wav_path):
        print("File not found. Falling back to manual input.")
        return None
    try:
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            print("Transcribed from file:", text)
            return text
        except sr.UnknownValueError:
            print("Could not understand audio in file. Falling back to manual input.")
            return None
        except sr.RequestError as e:
            print(f"Speech API error on file: {e}. Falling back to manual input.")
            return None
    except Exception as e:
        print(f"Failed to load WAV file: {e}. Falling back to manual input.")
        return None


def speech_to_keywords_from_mic():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Please speak now...")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
            except Exception:
                pass
            audio_data = recognizer.listen(source)
            print("Recognizing...")
            try:
                text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                print("Could not understand audio. Switching to WAV/manual input.")
                return None
            except sr.RequestError as e:
                print(f"Speech API error: {e}. Switching to WAV/manual input.")
                return None
            print("You said:", text)
            return text
    except AttributeError as e:
        if "Could not find PyAudio" in str(e):
            print("PyAudio not available yet. Switching to WAV/manual input.")
            return None
        print(f"Microphone error: {e}. Switching to WAV/manual input.")
        return None
    except OSError as e:
        print(f"Microphone OS error: {e}. Switching to WAV/manual input.")
        return None
    except Exception as e:
        print(f"Unexpected mic error: {e}. Switching to WAV/manual input.")
        return None


def get_text_input():
    print("\nPlease enter your text manually:")
    return input("> ")


def extract_keywords(text):
    ensure_nltk_data()
    rake = Rake()
    rake.extract_keywords_from_text(text)
    keywords_with_scores = rake.get_ranked_phrases_with_scores()
    print("\nKeywords and scores:")
    for score, keyword in keywords_with_scores:
        print(f"{keyword} ({score})")


if __name__ == "__main__":
    # 1) Try microphone
    transcript = speech_to_keywords_from_mic()

    # 2) If mic unavailable/fails, try WAV file
    if not transcript:
        transcript = speech_to_text_from_wav()

    # 3) If no WAV or failure, fall back to manual input
    if not transcript:
        transcript = get_text_input()

    extract_keywords(transcript)

