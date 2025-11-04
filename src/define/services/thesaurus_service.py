from typing import List, Dict, Optional

from define.utils import ServiceBase, APIClient
from define.models import Entry, Definition


class ThesaurusService(ServiceBase):
    """Service para processar thesaurus Merriam-Webster"""

    def __init__(self, parent):
        super().__init__(parent)
        self.api_client = APIClient()

    def fetch_and_enrich(self, word: str, entries: List[Entry]) -> List[Entry]:
        """Busca thesaurus e enriquece entradas"""
        # Pega config
        config = self._ServiceBase__parent.config
        thes_key = config.get_data("THESAURUS KEY")
        thes_url = config.get_data("Thesaurus URL")

        if not thes_key or not thes_url:
            return entries

        # Monta URL
        url = f"{thes_url[list(thes_url.keys())[0]]}{word}?key={thes_key[list(thes_key.keys())[0]]}"

        # Busca dados
        raw_data = self.api_client.fetch(url, f"thes_{word}")

        if not raw_data:
            return entries

        # Enriquece cada entrada
        for entry in entries:
            self._enrich_entry(entry, raw_data)

        return entries

    def _enrich_entry(self, entry: Entry, raw_thesaurus: List[Dict]):
        """Enriquece uma entrada com dados do thesaurus"""
        # Filtra por part of speech
        thes_entry = self._filter_by_pos(raw_thesaurus, entry.part_of_speech)

        if not thes_entry:
            return

        # Enriquece cada definição
        for i, definition in enumerate(entry.definitions):
            thes_sense = self._get_sense_by_index(thes_entry, i)
            if thes_sense:
                self._merge_into_definition(definition, thes_sense)

    def _filter_by_pos(self, thesaurus_data: List[Dict], pos: str) -> Optional[Dict]:
        """Filtra entry por part of speech"""
        for entry in thesaurus_data:
            entry_pos = entry.get('fl', '').lower()
            if entry_pos == pos.lower():
                return entry

        # Fallback
        return thesaurus_data[0] if thesaurus_data else None

    def _get_sense_by_index(self, thes_entry: Dict, sense_index: int) -> Optional[Dict]:
        """Pega sense pelo índice"""
        defs = thes_entry.get('def', [])
        current_index = 0

        for def_block in defs:
            for sseq_block in def_block.get('sseq', []):
                for sense_tuple in sseq_block:
                    if sense_tuple[0] == 'sense':
                        if current_index == sense_index:
                            return sense_tuple[1]
                        current_index += 1

        return None

    def _merge_into_definition(self, definition: Definition, thes_sense: Dict):
        """Combina thesaurus com definição"""
        # Extrai do thesaurus
        thes_syns = self._extract_word_list(thes_sense, 'syn_list')
        thes_rels = self._extract_word_list(thes_sense, 'rel_list')
        thes_ants = self._extract_word_list(thes_sense, 'ant_list')

        # Merge e deduplica
        definition.synonyms = list(set(definition.synonyms + thes_syns))
        definition.related = list(set(definition.related + thes_rels))
        definition.antonyms = list(set(definition.antonyms + thes_ants))

    def _extract_word_list(self, sense: Dict, list_key: str) -> List[str]:
        """Extrai lista de palavras"""
        words = []
        groups = sense.get(list_key, [])

        for group in groups:
            for wdobj in group:
                if isinstance(wdobj, dict) and "wd" in wdobj:
                    words.append(wdobj["wd"])

        return words