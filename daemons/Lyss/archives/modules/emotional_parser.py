from modules.chaos_emotion import CHAOSemote

def analyze_emotion(lyrics):
    text = lyrics.lower()

    if any(word in text for word in ["love", "light", "hope"]):
        return CHAOSemote.HOPE
    if any(word in text for word in ["rain", "lost", "grief", "alone"]):
        return CHAOSemote.GRIEF
    if any(word in text for word in ["fire", "rage", "burn"]):
        return CHAOSemote.ANGER
    if any(word in text for word in ["numb", "quiet", "mute"]):
        return CHAOSemote.NUMB
    if any(word in text for word in ["glory", "sky", "stars", "divine"]):
        return CHAOSemote.AWE
    if any(word in text for word in ["shame", "regret", "mistake"]):
        return CHAOSemote.SHAME

    return CHAOSemote.LONGING  # Default fallback
