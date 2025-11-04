from typing import List, Dict, Optional, Tuple

from define.utils import ServiceBase, APIClient
from define.models import Entry, Definition, Pronunciation


class ThesaurusService(ServiceBase):
    """Service para processar thesaurus Merriam-Webster"""

    def __init__(self, parent):
        super().__init__(parent)
        self.api_client = APIClient()

    def fetch_and_process(self, word: str) -> Optional[Tuple[List[Entry], List[Entry]]]:
        """Busca e processa palavra APENAS no thesaurus (modo standalone)"""
        # Pega config
        config = self._ServiceBase__parent.config
        thes_key = config.get_data("THESAURUS KEY")
        thes_url = config.get_data("Thesaurus URL")

        if not thes_key or not thes_url:
            return None

        # Monta URL
        url = f"{thes_url[list(thes_url.keys())[0]]}{word}?key={thes_key[list(thes_key.keys())[0]]}"

        # Busca dados
        raw_data = self.api_client.fetch(url, f"thes_{word}")

        if not raw_data or not any(isinstance(e, dict) for e in raw_data):
            return None

        # Processa entradas do thesaurus
        return self._process_thesaurus_entries(raw_data, word)

    def fetch_and_enrich(self, word: str, entries: List[Entry]) -> List[Entry]:
        """Busca thesaurus e enriquece entradas existentes (modo enrich)"""
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

    def _process_thesaurus_entries(self, raw_data: List[Dict], query_word: str) -> Tuple[List[Entry], List[Entry]]:
        """Processa entradas do thesaurus como Entry objects"""
        main_entries = []
        sub_entries = []

        for thes_entry in raw_data:
            if not isinstance(thes_entry, dict):
                continue

            processed = self._create_entry_from_thesaurus(thes_entry, query_word)

            if processed.is_main_entry:
                main_entries.append(processed)
            else:
                sub_entries.append(processed)

        return main_entries, sub_entries

    def _create_entry_from_thesaurus(self, thes_entry: Dict, query_word: str) -> Entry:
        """Cria Entry object a partir de dados do thesaurus"""
        headword = thes_entry.get('hwi', {}).get('hw', '').replace('*', '')
        hwi_hw = headword.lower()
        is_main = hwi_hw == query_word.lower()

        # Extrai definições do thesaurus
        definitions = self._extract_thesaurus_definitions(thes_entry)

        # Monta short_summary a partir das definições
        short_summary = []
        for definition in definitions[:3]:  # Pega até 3 definições
            if definition.synonyms:
                short_summary.append(f"Synonyms: {', '.join(definition.synonyms[:5])}")

        return Entry(
            headword=headword,
            homonym_num=thes_entry.get('hom', ''),
            part_of_speech=thes_entry.get('fl', ''),
            pronunciations=self._extract_pronunciations(thes_entry),
            etymology='',  # Thesaurus não tem etimologia
            definitions=definitions,
            short_summary=short_summary,
            is_main_entry=is_main
        )

    def _extract_pronunciations(self, entry: Dict) -> List[Pronunciation]:
        """Extrai pronúncias"""
        prons = entry.get('hwi', {}).get('prs', [])
        return [Pronunciation(text=p.get('mw', '')) for p in prons if 'mw' in p]

    def _extract_thesaurus_definitions(self, thes_entry: Dict) -> List[Definition]:
        """Extrai definições do thesaurus"""
        definitions = []
        count = 0

        for def_block in thes_entry.get('def', []):
            for sseq_block in def_block.get('sseq', []):
                for sense_tuple in sseq_block:
                    if sense_tuple[0] == 'sense':
                        sense = sense_tuple[1]
                        definitions.append(self._create_definition_from_sense(sense, count))
                        count += 1

        return definitions

    def _create_definition_from_sense(self, sense: Dict, index: int) -> Definition:
        """Cria Definition a partir de um sense do thesaurus"""
        # Extrai texto da definição (se houver)
        text_parts = []
        for dt_item in sense.get('dt', []):
            if dt_item[0] == 'text':
                # Remove markup básico
                text = dt_item[1].strip()
                text = text.lstrip(':').strip()
                # Filtra pontuação isolada
                if text and not self._is_only_punctuation(text):
                    text_parts.append(text)

        # Se não achou texto, usa os sinônimos como descrição
        if not text_parts:
            synonyms = self._extract_word_list(sense, 'syn_list')
            if synonyms:
                # Usa primeiros sinônimos como descrição
                definition_text = f"synonymous with: {', '.join(synonyms[:3])}"
            else:
                definition_text = f"[Thesaurus entry {index + 1}]"
        else:
            definition_text = ' '.join(text_parts)

        return Definition(
            index=index + 1,
            text=definition_text,
            examples=[],  # Thesaurus geralmente não tem exemplos
            synonyms=self._extract_word_list(sense, 'syn_list'),
            related=self._extract_word_list(sense, 'rel_list'),
            antonyms=self._extract_word_list(sense, 'ant_list')
        )

    def _is_only_punctuation(self, text: str) -> bool:
        """Verifica se texto é apenas pontuação/espaços"""
        import string
        return all(c in string.punctuation + string.whitespace for c in text)

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