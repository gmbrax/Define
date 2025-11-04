from dataclasses import dataclass, field
from typing import List

from define.models import Definition, Pronunciation

@dataclass
class Entry:

    headword: str
    homonym_num: str = ""
    part_of_speech: str = ""
    pronunciations: List[Pronunciation] = field(default_factory=list)
    etymology: str = ""
    definitions: List[Definition] = field(default_factory=list)
    short_summary: List[str] = field(default_factory=list)
    is_main_entry: bool = True