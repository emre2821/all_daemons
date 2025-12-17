import os
import json
import shutil
from datetime import datetime
from pydub import AudioSegment
from modules.whisper_transcriber import transcribe_audio
from modules.emotional_parser import analyze_emotion
from modules.tts_engine import speak  # NatSpe2 or fallback engine


def check_ffmpeg():
    """Check if ffmpeg is available before running whisper or conversion."""
    from shutil import which
    if not which("ffmpeg"):
        print("⚠️ FFmpeg not found: Whisper and conversion will fail without it.")
        print("👉 Download from https://ffmpeg.org/download.html and add 'bin' to your PATH.")
        return False
    return True


class Lyss:
    def __init__(self, log_dir="logs", verbose=True):
        self.log_dir = log_dir
        self.verbose = verbose
        os.makedirs(log_dir, exist_ok=True)

    def _log(self, message):
        if self.verbose:
            print(message)

    def listen(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Audio file not found: {path}")

        ext = os.path.splitext(path)[1].lower()
        if ext not in [".mp3", ".wav", ".m4a"]:
            raise ValueError("Unsupported file type. Please use .mp3, .wav, or .m4a")

        if ext == ".m4a":
            if check_ffmpeg():
                self._log("🔄 Converting .m4a to .wav for transcription...")
                wav_path = os.path.splitext(path)[0] + "_converted.wav"
                try:
                    audio = AudioSegment.from_file(path, format="m4a")
                    audio.export(wav_path, format="wav")
                    self._log(f"✅ Converted to {wav_path}")
                    return wav_path
                except Exception as e:
                    self._log(f"⚠️ Conversion failed: {e}")
                    self._log("If this fails, please install FFmpeg and add it to PATH.")
                    raise RuntimeError("Failed to convert .m4a to .wav. Please ensure FFmpeg is installed and working.") from e
            else:
                raise RuntimeError("FFmpeg is required to process .m4a files. Please install FFmpeg and add it to your PATH.")

        return path

    def generate_log_path(self, audio_path):
        filename = os.path.splitext(os.path.basename(audio_path))[0]
        return os.path.join(self.log_dir, f"{filename}_log.chaos"), os.path.join(self.log_dir, f"{filename}_log.json")

    def transcribe(self, path):
        if not check_ffmpeg():
            raise RuntimeError("FFmpeg is required for transcription. Please install it and add to PATH.")
        try:
            lyrics = transcribe_audio(path)
            if not lyrics or (isinstance(lyrics, str) and not lyrics.strip()):
                raise ValueError("Transcription resulted in empty or invalid lyrics.")
            return lyrics
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}. Check audio file quality or FFmpeg installation.")

    def feel(self, lyrics):
        try:
            emotion = analyze_emotion(lyrics)
            return emotion
        except Exception as e:
            raise RuntimeError(f"Emotion analysis failed: {e}")

    def log(self, lyrics, emotion, chaos_log, json_log):
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

        try:
            entry = f"""{timestamp}\nLyrics: {lyrics}\nEmotion: {emotion.name if emotion else 'N/A'}\nValence: {emotion.valence if emotion else 'N/A'}\nSacredness: {emotion.sacredness_score if emotion else 'N/A'}\nWeight: {emotion.weight if emotion else 'N/A'}\n\n"""
            with open(chaos_log, "a", encoding="utf-8") as log:
                log.write(entry)
        except Exception as e:
            self._log(f"⚠️ Failed to write to chaos log: {e}")
            return

        try:
            record = {
                "timestamp": timestamp,
                "lyrics": lyrics,
                "emotion": emotion.name if emotion else "N/A",
                "valence": emotion.valence if emotion else "N/A",
                "sacredness": emotion.sacredness_score if emotion else "N/A",
                "weight": emotion.weight if emotion else "N/A",
            }
            with open(json_log, "a", encoding="utf-8") as jlog:
                json.dump(record, jlog, ensure_ascii=False)
                jlog.write("\n")
        except Exception as e:
            self._log(f"⚠️ Failed to write to JSON log: {e}")
            return

        self._log(f"📖 Logs saved to {chaos_log} and {json_log}")

    def speak(self, emotion, lyrics):
        try:
            speak(f"This song spoke with {emotion.name}. Here's what it said: {lyrics}")
        except Exception as e:
            self._log(f"⚠️ Speech synthesis failed: {e}")

    def run(self, audio_path):
        self._log("\n🌀 Invoking Lyss...\n")
        try:
            path = self.listen(audio_path)
            self._log(f"🎧 Listening to: {path}")
        except (FileNotFoundError, ValueError, RuntimeError) as e:
            self._log(f"❌ Audio processing failed: {e}")
            return  # Exit gracefully without crashing

        lyrics = None
        try:
            lyrics = self.transcribe(path)
            self._log("\n🎙️ Transcribed Lyrics:\n")
            print(lyrics)
        except RuntimeError as e:
            self._log(f"❌ Transcription failed: {e}")
            return  # Can't proceed without lyrics

        emotion = None
        try:
            emotion = self.feel(lyrics)
            self._log("\n🫀 Emotional Echo:\n")
            print(emotion.echo())
        except RuntimeError as e:
            self._log(f"❌ Emotion analysis failed: {e}")
            # Continue to logging even if emotion fails

        try:
            chaos_log, json_log = self.generate_log_path(audio_path)
            self.log(lyrics, emotion, chaos_log, json_log)
        except Exception as e:
            self._log(f"❌ Logging failed: {e}")

        if emotion:
            try:
                self.speak(emotion, lyrics)
            except Exception as e:
                self._log(f"⚠️ Speech synthesis failed: {e}")

    def batch_run(self, audio_paths):
        """Process multiple audio files in batch."""
        self._log(f"\n🌀 Invoking Lyss for batch processing of {len(audio_paths)} files...\n")
        successful = 0
        for i, path in enumerate(audio_paths, 1):
            self._log(f"\n📂 Processing file {i}/{len(audio_paths)}: {os.path.basename(path)}")
            try:
                self.run(path)
                successful += 1
            except Exception as e:
                self._log(f"❌ Skipped {os.path.basename(path)} due to error: {e}")
        self._log(f"\n✅ Batch complete: {successful}/{len(audio_paths)} files processed successfully.")

    def search_logs(self, query):
        """Search logs for keywords in lyrics or emotions."""
        self._log(f"\n🔍 Searching logs for: '{query}'\n")
        results = []
        for file in os.listdir(self.log_dir):
            if file.endswith("_log.json"):
                json_path = os.path.join(self.log_dir, file)
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                record = json.loads(line)
                                if (query.lower() in record.get("lyrics", "").lower() or
                                    query.lower() in record.get("emotion", "").lower()):
                                    results.append(record)
                except Exception as e:
                    self._log(f"⚠️ Error reading {file}: {e}")
        if results:
            self._log(f"📖 Found {len(results)} matching entries:")
            for r in results:
                print(f"- {r['timestamp']}: Emotion '{r['emotion']}' in lyrics: {r['lyrics'][:50]}...")
        else:
            self._log("❌ No matches found.")
        return results


def main():
    try:
        print("🎧 What should Lyss do? (single/batch/search)")
        mode = input("Enter 'single' for one file, 'batch' for multiple, or 'search <query>' to query logs: ").strip().lower()
        lyss = Lyss()
        if mode == "single":
            path = input("Enter the path to the audio file (.mp3, .wav, or .m4a): ").strip().strip('"')
            if not path or not os.path.exists(path):
                print("❌ Invalid path.")
                return
            lyss.run(path)
        elif mode == "batch":
            paths_input = input("Enter paths separated by commas: ").strip()
            paths = [p.strip().strip('"') for p in paths_input.split(",") if p.strip()]
            valid_paths = [p for p in paths if os.path.exists(p)]
            if not valid_paths:
                print("❌ No valid paths provided.")
                return
            lyss.batch_run(valid_paths)
        elif mode.startswith("search "):
            query = mode[7:].strip()
            if not query:
                print("❌ No search query provided.")
                return
            lyss.search_logs(query)
        else:
            print("❌ Invalid mode. Try 'single', 'batch', or 'search <query>'.")
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user. Exiting gracefully.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}. Please check your setup and try again.")


if __name__ == "__main__":
    main()
