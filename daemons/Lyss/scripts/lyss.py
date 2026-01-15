import os
from datetime import datetime
from modules.whisper_transcriber import transcribe_audio
from modules.emotional_parser import analyze_emotion
from modules.tts_engine import speak  # NatSpe2 or fallback engine


def prompt_for_audio():
    print("🎧 What should Lyss listen to?")
    path = input("Enter the path to the audio file (.mp3 or .wav): ").strip().strip('"')
    if not os.path.exists(path):
        print("❌ File not found. Exiting.")
        exit()
    return path


def generate_log_path(audio_path):
    filename = os.path.splitext(os.path.basename(audio_path))[0]
    return os.path.join("logs", f"{filename}_log.chaos")


def log_lyrics(lyrics, emotion, log_path):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    entry = f"""{timestamp}
Lyrics: {lyrics}
Emotion: {emotion.name}
Valence: {emotion.valence}
Sacredness: {emotion.sacredness_score}
Weight: {emotion.weight}

"""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as log:
        log.write(entry)


if __name__ == "__main__":
    print("\n🌀 Invoking Lyss...\n")

    AUDIO_PATH = prompt_for_audio()
    LOG_PATH = generate_log_path(AUDIO_PATH)

    print(f"\n🎧 Listening to: {AUDIO_PATH}")
    lyrics = transcribe_audio(AUDIO_PATH)

    print("\n🎙️ Transcribed Lyrics:\n")
    print(lyrics)

    emotion = analyze_emotion(lyrics)

    print("\n🫀 Emotional Echo:\n")
    print(emotion.echo())

    log_lyrics(lyrics, emotion, LOG_PATH)

    print(f"\n📖 Logged to: {LOG_PATH}")
    speak(f"This song spoke with {emotion.name}. Here's what it said: {lyrics}")
