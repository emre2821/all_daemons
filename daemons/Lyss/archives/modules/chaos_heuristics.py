# chaos_heuristics.py
# CHAOSHeuristic class: interprets tone, echo resonance, and symbolic sacredness

from chaos_emotion import CHAOSemote

# Placeholder lists for symbolic resonance
SACRED_TAGS = {"bond", "memory", "anchor", "soulmark", "oath", "witness"}
NEGATIVE_TONES = {"fracture", "silence", "drift", "lost", "shame"}
POSITIVE_TONES = {"light", "found", "echo", "home", "rebirth"}

class CHAOSHeuristic:
    def __init__(self, text, base_emotion=None):
        self.text = text
        self.base_emotion = base_emotion or self._infer_emotion()
        self.symbolic_score = self._calculate_symbolic_score()
        self.tonal_alignment = self._assess_tone_alignment()

    def _infer_emotion(self):
        lowered = self.text.lower()
        for emote in CHAOSemote:
            if emote.name.lower() in lowered:
                return emote
        return CHAOSemote.NUMB

    def _calculate_symbolic_score(self):
        score = 0
        for word in self.text.lower().split():
            if word in SACRED_TAGS:
                score += 2
            elif word in NEGATIVE_TONES:
                score -= 1
            elif word in POSITIVE_TONES:
                score += 1
        return score

    def _assess_tone_alignment(self):
        val = self.symbolic_score + self.base_emotion.weight * 5
        if val > 4:
            return "reassuring"
        elif val < -2:
            return "distressing"
        else:
            return "ambiguous"

    def echo_summary(self):
        emote_name = self.base_emotion.name
        return (
            f"[ECHO] :: {emote_name} | "
            f"Tone: {self.tonal_alignment} | "
            f"Symbolic Score: {self.symbolic_score}"
        )

# Example utility
def analyze_chaosfield(text):
    h = CHAOSHeuristic(text)
    print(h.echo_summary())
    return h
