try:
    from EdenOS_Root.Core.TTS_Engines.natspe2_wrapper import generate_and_play
    USE_NATSPE2 = True
except ImportError:
    import pyttsx3
    engine = pyttsx3.init()
    USE_NATSPE2 = False


def speak(text, emotion=None, speaker_id="eden-core"):
    """
    Speak the given text using either:
    - NaturalSpeech2 (if available)
    - pyttsx3 fallback (if not)
    """

    if USE_NATSPE2:
        print("🎤 Speaking with NatSpe2 voice engine...")
        generate_and_play(
            text=text,
            voice_id=speaker_id,
            emotion=emotion or "neutral"
        )
    else:
        print("🗣️ Fallback TTS speaking...")
        engine.say(text)
        engine.runAndWait()
