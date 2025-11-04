import re
from typing import Set, Dict

class TextProcessor:
    """Limpa markup Merriam-Webster"""

    def __init__(self, api_client):
        self.api_client = api_client
        self._resolved_refs: Dict[str, str] = {}

    def clean_text(self, text: str) -> str:
        """Remove markup MW e resolve cross-refs"""
        text = self._resolve_cross_refs(text)
        text = re.sub(r'\{d_link\|([^|}]+)\|[^}]*\}', r'\1', text)
        text = re.sub(r'\{\/?dx[^}]*\}', '', text)
        text = re.sub(r'\{[^}]*\}', '', text)
        return text.strip()

    def _resolve_cross_refs(self, text: str) -> str:
        """Resolve {dxt|...} references"""
        pattern = re.compile(r'\{dxt\|([^}]*)\}')
        refs = self._extract_refs(text, pattern)

        # Resolve refs que ainda não foram resolvidas
        for ref in refs:
            if ref not in self._resolved_refs:
                self._resolved_refs[ref] = self._fetch_ref(ref)

        def replacement(match):
            inner = match.group(1)
            parts = inner.split('|')
            if len(parts) > 1:
                ref_word = parts[1].split(':')[0]
                return self._resolved_refs.get(ref_word, ref_word)
            return inner

        return pattern.sub(replacement, text)

    def _extract_refs(self, text: str, pattern) -> Set[str]:
        """Extrai referências do texto"""
        refs = set()
        for match in pattern.findall(text):
            parts = match.split('|')
            if len(parts) > 1:
                ref_word = parts[1].split(':')[0]
                refs.add(ref_word)
        return refs

    def _fetch_ref(self, ref_word: str) -> str:
        """Busca uma referência via API - precisa ser implementado pelo service"""
        # Isso será chamado pelo DictionaryService que tem acesso ao API
        return ref_word

    def set_ref_resolver(self, resolver_func):
        """Define função para resolver refs (injeção de dependência)"""
        self._fetch_ref = resolver_func