"""
SearchCrossRef - Módulo de búsqueda en CrossRef
"""

import json
import logging
import urllib.request
from pathlib import Path
from typing import Dict, List
from base_search import BaseSearch

logger = logging.getLogger(__name__)


class SearchCrossRef(BaseSearch):
    """Buscador en CrossRef API (sin API key requerida)."""

    BASE_URL = "https://api.crossref.org/works"

    def __init__(self, api_keys: Dict[str, str], output_path: Path, project_name: str = "review"):
        super().__init__(api_keys, output_path, project_name)
        self.email = api_keys.get('entrez_email', '')  # Usar email para polite pool

    def validate_credentials(self) -> bool:
        """No requiere credenciales."""
        return True

    def search(self, query: str, max_results: int = 100, **kwargs) -> List[Dict]:
        """Ejecuta búsqueda en CrossRef."""
        self.metadata['query'] = query
        logger.info(f"Buscando CrossRef: {query}")

        try:
            headers = {
                'User-Agent': f'LiteratureReviewBot/1.0 (mailto:{self.email})' if self.email else 'LiteratureReviewBot/1.0'
            }

            url = f"{self.BASE_URL}?query={urllib.parse.quote(query)}&rows={min(max_results, 1000)}&sort=relevance"

            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

            items = data.get('message', {}).get('items', [])
            total = data.get('message', {}).get('total-results', 0)
            self.metadata['total_results'] = total

            for item in items:
                authors = []
                for author in item.get('author', []):
                    name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                    if name:
                        authors.append(name)

                self.results.append({
                    'doi': item.get('DOI', ''),
                    'title': item.get('title', [''])[0] if isinstance(item.get('title'), list) else item.get('title', ''),
                    'authors': authors,
                    'published': item.get('published-print', item.get('published-online', {})).get('date-parts', [['']])[0],
                    'journal': item.get('container-title', [''])[0] if isinstance(item.get('container-title'), list) else '',
                    'type': item.get('type', ''),
                    'url': item.get('URL', ''),
                    'references_count': item.get('references-count', 0),
                    'cited_by_count': item.get('is-referenced-by-count', 0)
                })
                self.rate_limit(0.2)

            self.metadata['status'] = 'completed'
            self.save_results()

        except Exception as e:
            logger.error(f"Error en CrossRef: {e}")
            self.metadata['status'] = f'error: {str(e)}'

        return self.results
