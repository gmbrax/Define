from typing import List, Dict, Optional, Tuple

from define.utils import ServiceBase, APIClient
from define.models import Entry, Definition, Pronunciation


class ThesaurusService(ServiceBase):
    """Service para processar thesaurus Merriam-Webster"""

    def __init__(self, parent):
        super().__init__(parent)
        self.api_client = APIClient()

    # ========== PUBLIC METHODS ==========

    def fetch_and_process(self, word: str) -> Optional[Tuple[List[Entry], List[Entry]]]:
        """
        Busca e processa palavra APENAS no thesaurus (modo standalone -t).

        Args:
            word: Palavra a buscar

        Returns:
            Tuple com (main_entries, sub_entries) ou None se não encontrar
        """
        raw_data = self._fetch_thesaurus_data(word)

        if not raw_data or not any(isinstance(e, dict) for e in raw_data):
            return None

        return self._process_thesaurus_entries(raw_data, word)

    def enrich_entries(self, word: str, entries: List[Entry]) -> None:
        """
        Enriquece entradas IN-PLACE com dados do thesaurus (modo default).

        Esta função modifica os objetos Entry diretamente, adicionando
        synonyms, antonyms e related words de cada definition.

        Args:
            word: Palavra a buscar no thesaurus
            entries: Lista de Entry objects a serem enriquecidos (modificados in-place)

        Returns:
            None - modifica entries diretamente
        """
        raw_data = self._fetch_thesaurus_data(word)

        if not raw_data:
            return  # Early return se não achar dados

        # Enriquece cada entrada IN-PLACE
        for entry in entries:
            self._enrich_entry(entry, raw_data)

    # ========== PRIVATE FETCH HELPER ==========

    def _fetch_thesaurus_data(self, word: str) -> Optional[List[Dict]]:
        """
        Busca dados brutos do thesaurus API.

        Helper reutilizado por fetch_and_process() e enrich_entries().

        Args:
            word: Palavra a buscar

        Returns:
            Lista de dicts com dados do thesaurus, ou None se falhar
        """
        # Pega config
        config = self._ServiceBase__parent.config
        thes_key = config.get_data("THESAURUS KEY")
        thes_url = config.get_data("Thesaurus URL")

        if not thes_key or not thes_url:
            return None

        # Monta URL
        url = f"{thes_url[list(thes_url.keys())[0]]}{word}?key={thes_key[list(thes_key.keys())[0]]}"

        # Busca dados via APIClient
        return self.api_client.fetch(url, f"thes_{word}")

    # ========== PROCESSING METHODS ==========

    def _process_thesaurus_entries(self, raw_data: List[Dict], query_word: str) -> Tuple[List[Entry], List[Entry]]:
        """
        Processa dados brutos do thesaurus em Entry objects.

        Args:
            raw_data: Dados brutos do API
            query_word: Palavra buscada (para determinar main vs sub entries)

        Returns:
            Tuple com (main_entries, sub_entries)
        """
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
        """
        Cria Entry object a partir de dados do thesaurus.

        Args:
            thes_entry: Dict com dados de uma entrada do thesaurus
            query_word: Palavra buscada

        Returns:
            Entry object completo
        """
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
        """
        Extrai pronúncias de uma entrada.

        Args:
            entry: Dict com dados da entrada

        Returns:
            Lista de Pronunciation objects
        """
        prons = entry.get('hwi', {}).get('prs', [])
        return [Pronunciation(text=p.get('mw', '')) for p in prons if 'mw' in p]

    def _extract_thesaurus_definitions(self, thes_entry: Dict) -> List[Definition]:
        """
        Extrai todas as definições de uma entrada do thesaurus.

        Args:
            thes_entry: Dict com dados da entrada

        Returns:
            Lista de Definition objects
        """
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
        """
        Cria Definition a partir de um sense do thesaurus.

        Args:
            sense: Dict com dados do sense
            index: Índice da definição (para numeração)

        Returns:
            Definition object
        """
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

    # ========== ENRICHMENT METHODS ==========

    def _enrich_entry(self, entry: Entry, raw_thesaurus: List[Dict]) -> None:
        """
        Enriquece uma entrada IN-PLACE com dados do thesaurus.

        Args:
            entry: Entry object a ser modificado
            raw_thesaurus: Dados brutos do thesaurus API
        """
        # Filtra por part of speech
        thes_entry = self._filter_by_pos(raw_thesaurus, entry.part_of_speech)

        if not thes_entry:
            return

        # Enriquece cada definição IN-PLACE
        for i, definition in enumerate(entry.definitions):
            thes_sense = self._get_sense_by_index(thes_entry, i)
            if thes_sense:
                self._merge_into_definition(definition, thes_sense)

    def _filter_by_pos(self, thesaurus_data: List[Dict], pos: str) -> Optional[Dict]:
        """
        Filtra entry do thesaurus por part of speech.

        Args:
            thesaurus_data: Lista de entries do thesaurus
            pos: Part of speech a buscar

        Returns:
            Entry correspondente ou None
        """
        for entry in thesaurus_data:
            entry_pos = entry.get('fl', '').lower()
            if entry_pos == pos.lower():
                return entry

        # Fallback: retorna primeiro entry
        return thesaurus_data[0] if thesaurus_data else None

    def _get_sense_by_index(self, thes_entry: Dict, sense_index: int) -> Optional[Dict]:
        """
        Pega sense do thesaurus pelo índice.

        Args:
            thes_entry: Entry do thesaurus
            sense_index: Índice do sense desejado

        Returns:
            Dict com dados do sense ou None
        """
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

    def _merge_into_definition(self, definition: Definition, thes_sense: Dict) -> None:
        """
        Combina dados do thesaurus com definição existente IN-PLACE.

        Args:
            definition: Definition object a ser modificado
            thes_sense: Sense do thesaurus com syn/ant/rel
        """
        # Extrai do thesaurus
        thes_syns = self._extract_word_list(thes_sense, 'syn_list')
        thes_rels = self._extract_word_list(thes_sense, 'rel_list')
        thes_ants = self._extract_word_list(thes_sense, 'ant_list')

        # Merge e deduplica IN-PLACE
        definition.synonyms = list(set(definition.synonyms + thes_syns))
        definition.related = list(set(definition.related + thes_rels))
        definition.antonyms = list(set(definition.antonyms + thes_ants))

    # ========== UTILITY METHODS ==========

    def _extract_word_list(self, sense: Dict, list_key: str) -> List[str]:
        """
        Extrai lista de palavras (syn/rel/ant) de um sense.

        Args:
            sense: Dict com dados do sense
            list_key: Chave da lista ('syn_list', 'rel_list', 'ant_list')

        Returns:
            Lista de palavras
        """
        words = []
        groups = sense.get(list_key, [])

        for group in groups:
            for wdobj in group:
                if isinstance(wdobj, dict) and "wd" in wdobj:
                    words.append(wdobj["wd"])

        return words

    def _is_only_punctuation(self, text: str) -> bool:
        """
        Verifica se texto contém apenas pontuação/espaços.

        Args:
            text: Texto a verificar

        Returns:
            True se só tiver pontuação/espaços, False caso contrário
        """
        import string
        return all(c in string.punctuation + string.whitespace for c in text)