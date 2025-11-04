from dataclasses import field, dataclass
from typing import List


@dataclass
class Definition:
    index: int
    text: str
    examples: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)