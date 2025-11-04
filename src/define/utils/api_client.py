from requests import request
from typing import Optional, Dict, Any, List

class APIClient:
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def fetch(self, url: str, cache_key: str) -> Optional[List[Dict]]:

        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            resp = request("GET", url)

            if resp.status_code != 200 or not resp.text.strip():
                self._cache[cache_key] = None
                return None

            data = resp.json()


            if isinstance(data, list) and data and isinstance(data[0], dict):
                self._cache[cache_key] = data
                return data

            self._cache[cache_key] = None
            return None

        except Exception:
            self._cache[cache_key] = None
            return None