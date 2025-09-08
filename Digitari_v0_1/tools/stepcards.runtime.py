
# minimal, dependency-free runtime for Step Cards
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class Card:
    id: str
    statement: str
    why: str = ""
    effort: str = "S"  # XS|S|M|L
    timebox_min: int = 5
    blocker: str = ""
    on_success: Optional[str] = None
    on_abort: Optional[str] = None

@dataclass
class Deck:
    name: str
    cards: Dict[str, Card]
    entry: str

class StepRunner:
    def __init__(self, deck: Deck):
        self.deck = deck
        self.ptr = deck.entry
        self.log: List[str] = []

    def current(self) -> Card:
        return self.deck.cards[self.ptr]

    def start(self):
        c = self.current()
        self.log.append(f"START {c.id}: {c.statement}")

    def succeed(self):
        c = self.current()
        self.log.append(f"OK {c.id}")
        if c.on_success and c.on_success in self.deck.cards:
            self.ptr = c.on_success
        else:
            self.ptr = ""  # end

    def abort(self):
        c = self.current()
        self.log.append(f"ABORT {c.id}")
        if c.on_abort and c.on_abort in self.deck.cards:
            self.ptr = c.on_abort
        else:
            self.ptr = ""  # end


