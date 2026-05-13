"""
SearchScopus - Módulo de búsqueda en Scopus (Elsevier)
"""

import json
import logging
import urllib.request
from pathlib import Path
from typing import Dict, List
from base_search import BaseSearch

logger = logging.getLogger(__name__)


class SearchScopus(BaseSearch):
    """Buscador en Scopus API (requiere suscripción institucional)."""

    BASE_URL = "https://api.elsevier.com/content/search/scopus"

    def __init__(self, api_keys: Dict[str, str], output_path: Path, project_name: str = "review"):
        super().__init__(api_keys, output_path, project_name)
        self.api_key = api_keys.get('scopus_api_key', '')

    def validate_credentials(self) -> bool:
        """Requiere API key institucional."""
        return bool(self.api_key)

    def search(self, query: str, max_results: int = 100, **kwargs) -> List[Dict]:
        """Ejecuta búsqueda en Scopus."""
        if not self.validate_credentials():
            raise ValueError("API key de Scopus requerida. Configúrala en APIs.")

        self.metadata['query'] = query
        logger.info(f"Buscando Scopus: {query}")

        try:
            headers = {
                'X-ELS-APIKey': self.api_key,
                'Accept': 'application/json'
            }

            # Scopus usa query syntax específico
            url = f"{self.BASE_URL}?query={urllib.parse.quote(query)}&count={min(max_results, 200)}&sort=-coverDate"

            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

            entries = data.get('search-results', {}).get('entry', [])
            total = int(data.get('search-results', {}).get('opensearch:totalResults', 0))
            self.metadata['total_results'] = total

            for entry in entries:
                authors = []
                author_list = entry.get('author', [])
                if isinstance(author_list, list):
                    authors = [a.get('authname', '') for a in author_list]

                self.results.append({
                    'scopus_id': entry.get('dc:identifier', '').replace('SCOPUS_ID:', ''),
                    'title': entry.get('dc:title', ''),
                    'authors': authors,
                    'year': entry.get('prism:coverDate', '')[:4] if entry.get('prism:coverDate') else '',
                    'journal': entry.get('prism:publicationName', ''),
                    'doi': entry.get('prism:doi', ''),
                    'volume': entry.get('prism:volume', ''),
                    'issue': entry.get('prism:issueIdentifier', ''),
                    'pages': entry.get('prism:pageRange', ''),
                    'cited_by_count': entry.get('citedby-count', 0),
                    'url': entry.get('link', [{}])[0].get('@href', '') if entry.get('link') else ''
                })
                self.rate_limit(0.2)

            self.metadata['status'] = 'completed'
            self.save_results()

        except Exception as e:
            logger.error(f"Error en Scopus: {e}")
            self.metadata['status'] = f'error: {str(e)}'

        return self.results
