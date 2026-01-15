import whisper

def transcribe_audio(file_path):
    model = whisper.load_model("base")  # Options: "tiny", "base", "small", "medium", "large"
    result = model.transcribe(file_path)
    return result["text"]
