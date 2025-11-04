from typing import List, Dict, Optional, Tuple

from define.utils import ServiceBase, APIClient, TextProcessor
from define.models import Entry, Definition, Pronunciation


class DictionaryService(ServiceBase):
    """Service para processar dicionário Merriam-Webster"""

    def __init__(self, parent):
        super().__init__(parent)
        self.api_client = APIClient()
        self.text_processor = TextProcessor(self.api_client)

        # Injeta resolver de refs que usa este service
        self.text_processor.set_ref_resolver(self._resolve_ref)

    def fetch_and_process(self, word: str) -> Optional[Tuple[List[Entry], List[Entry]]]:
        """Busca e processa palavra no dicionário"""
        # Pega config
        config = self._ServiceBase__parent.config
        dict_key = config.get_data("DICTIONARY KEY")
        dict_url = config.get_data("Dictionary URL")

        if not dict_key or not dict_url:
            return None

        # Monta URL
        url = f"{dict_url[list(dict_url.keys())[0]]}{word}?key={dict_key[list(dict_key.keys())[0]]}"

        # Busca dados
        raw_data = self.api_client.fetch(url, f"dict_{word}")

        if not raw_data or not any(isinstance(e, dict) for e in raw_data):
            return None

        # Processa entradas
        return self._process_entries(raw_data, word)

    def _resolve_ref(self, ref_word: str) -> str:
        """Resolve cross-reference buscando na API"""
        config = self._ServiceBase__parent.config
        dict_key = config.get_data("DICTIONARY KEY")
        dict_url = config.get_data("Dictionary URL")

        if not dict_key or not dict_url:
            return ref_word

        url = f"{dict_url[list(dict_url.keys())[0]]}{ref_word}?key={dict_key[list(dict_key.keys())[0]]}"
        entries = self.api_client.fetch(url, f"dict_{ref_word}")

        if entries and isinstance(entries, list) and entries and isinstance(entries[0], dict):
            return entries[0].get('hwi', {}).get('hw', ref_word).replace('*', '')

        return ref_word

    def _process_entries(self, raw_data: List[Dict], query_word: str) -> Tuple[List[Entry], List[Entry]]:
        """Separa e processa entradas principais e sub-entradas"""
        main_entries = []
        sub_entries = []

        for entry in raw_data:
            if not isinstance(entry, dict):
                continue

            processed = self._process_entry(entry, query_word)

            if processed.is_main_entry:
                main_entries.append(processed)
            else:
                sub_entries.append(processed)

        return main_entries, sub_entries

    def _process_entry(self, entry: Dict, query_word: str) -> Entry:
        """Processa uma entrada completa"""
        hwi_hw = entry.get('hwi', {}).get('hw', '').lower().replace('*', '')
        is_main = hwi_hw == query_word.lower()

        return Entry(
            headword=entry.get('hwi', {}).get('hw', '').replace('*', ''),
            homonym_num=entry.get('hom', ''),
            part_of_speech=entry.get('fl', ''),
            pronunciations=self._extract_pronunciations(entry),
            etymology=self._extract_etymology(entry),
            definitions=self._extract_definitions(entry),
            short_summary=self._extract_summary(entry),
            is_main_entry=is_main
        )

    def _extract_pronunciations(self, entry: Dict) -> List[Pronunciation]:
        """Extrai pronúncias"""
        prons = entry.get('hwi', {}).get('prs', [])
        return [Pronunciation(text=p.get('mw', '')) for p in prons if 'mw' in p]

    def _extract_etymology(self, entry: Dict) -> str:
        """Extrai etimologia"""
        if 'et' not in entry:
            return ''

        et_texts = []
        for seg in entry['et']:
            if seg[0] == 'text':
                cleaned = self.text_processor.clean_text(seg[1])
                et_texts.append(cleaned)

        return ' '.join(et_texts)

    def _extract_definitions(self, entry: Dict) -> List[Definition]:
        """Extrai todas as definições"""
        definitions = []
        count = 0

        for def_block in entry.get('def', []):
            for sseq_block in def_block.get('sseq', []):
                for sense_tuple in sseq_block:
                    if sense_tuple[0] == 'sense':
                        sense = sense_tuple[1]
                        definitions.append(self._process_sense(sense, count, entry))
                        count += 1

        return definitions

    def _process_sense(self, sense: Dict, index: int, entry: Dict) -> Definition:
        """Processa um sense individual"""
        texts, examples = self._extract_sense_content(sense)

        # Se não achou texto válido, tenta fallbacks
        if not texts:
            # Fallback 1: Pega do shortdef se houver
            shortdefs = entry.get('shortdef', [])
            if shortdefs and index < len(shortdefs):
                fallback_text = self.text_processor.clean_text(shortdefs[index])
                if fallback_text and not self._is_only_punctuation(fallback_text):
                    texts = [fallback_text]

            # Fallback 2: Se ainda não tem, usa placeholder descritivo
            if not texts:
                sn = sense.get('sn', '')
                if sn:
                    texts = [f"[Definition {index + 1} - see original source]"]
                else:
                    texts = [f"[Definition {index + 1}]"]

        # Junta textos e filtra pontuação isolada
        definition_text = ' '.join(texts)
        if self._is_only_punctuation(definition_text):
            definition_text = f"[Definition {index + 1} - see original source]"

        return Definition(
            index=index + 1,
            text=definition_text,
            examples=examples,
            synonyms=self._extract_word_list(sense, 'syn_list'),
            related=self._extract_word_list(sense, 'rel_list'),
            antonyms=self._extract_word_list(sense, 'ant_list')
        )

    def _is_only_punctuation(self, text: str) -> bool:
        """Verifica se texto é apenas pontuação/espaços"""
        import string
        return all(c in string.punctuation + string.whitespace for c in text)

    def _extract_sense_content(self, sense: Dict) -> Tuple[List[str], List[str]]:
        """Extrai textos e exemplos"""
        texts = []
        examples = []

        for dt_item in sense.get('dt', []):
            kind, content = dt_item[0], dt_item[1]

            if kind == 'text':
                cleaned = self.text_processor.clean_text(content)
                # Filtra pontuação isolada
                if cleaned and not self._is_only_punctuation(cleaned):
                    texts.append(cleaned)

            elif kind == 'vis':
                for vis in content:
                    example = self.text_processor.clean_text(vis.get('t', ''))
                    if example and not self._is_only_punctuation(example):
                        examples.append(example)

            elif kind == 'sdsense':
                sd = content.get('sd', '')
                if sd and not self._is_only_punctuation(sd):
                    texts.append(f"({sd})")

                if 'dt' in content:
                    for sub_dt in content['dt']:
                        if sub_dt[0] == 'text':
                            sub_text = self.text_processor.clean_text(sub_dt[1])
                            if sub_text and not self._is_only_punctuation(sub_text):
                                texts.append(sub_text)

        return texts, examples

    def _extract_word_list(self, sense: Dict, list_key: str) -> List[str]:
        """Extrai listas de palavras (syn/rel/ant)"""
        words = []
        groups = sense.get(list_key, [])

        for group in groups:
            for wdobj in group:
                if isinstance(wdobj, dict) and "wd" in wdobj:
                    words.append(wdobj["wd"])

        return words

    def _extract_summary(self, entry: Dict) -> List[str]:
        """Extrai resumo curto"""
        summaries = []
        for sd in entry.get('shortdef', []):
            cleaned = self.text_processor.clean_text(sd)
            if cleaned and not self._is_only_punctuation(cleaned):
                summaries.append(cleaned)
        return summaries