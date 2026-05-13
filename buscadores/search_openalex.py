"""
SearchOpenAlex - Módulo de búsqueda en OpenAlex
"""

import json
import logging
import urllib.request
from pathlib import Path
from typing import Dict, List
from base_search import BaseSearch

logger = logging.getLogger(__name__)


class SearchOpenAlex(BaseSearch):
    """Buscador en OpenAlex API."""

    BASE_URL = "https://api.openalex.org/works"

    def __init__(self, api_keys: Dict[str, str], output_path: Path, project_name: str = "review"):
        super().__init__(api_keys, output_path, project_name)
        self.email = api_keys.get('openalex_email', api_keys.get('entrez_email', ''))

    def validate_credentials(self) -> bool:
        """No requiere key. Email opcional para polite pool."""
        return True

    def search(self, query: str, max_results: int = 100, **kwargs) -> List[Dict]:
        """Ejecuta búsqueda en OpenAlex."""
        self.metadata['query'] = query
        logger.info(f"Buscando OpenAlex: {query}")

        try:
            # OpenAlex usa search syntax diferente
            mailto = f"&mailto={urllib.parse.quote(self.email)}" if self.email else ""
            url = f"{self.BASE_URL}?search={urllib.parse.quote(query)}&per-page={min(max_results, 200)}{mailto}"

            headers = {
                'User-Agent': f'LiteratureReviewBot/1.0 (mailto:{self.email})' if self.email else 'LiteratureReviewBot/1.0'
            }

            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

            items = data.get('results', [])
            total = data.get('meta', {}).get('count', 0)
            self.metadata['total_results'] = total

            for item in items:
                authors = []
                for authorship in item.get('authorships', []):
                    author = authorship.get('author', {})
                    name = author.get('display_name', '')
                    if name:
                        authors.append(name)

                ids = item.get('ids', {})

                self.results.append({
                    'openalex_id': item.get('id', ''),
                    'title': item.get('display_name', ''),
                    'authors': authors,
                    'publication_year': item.get('publication_year', ''),
                    'journal': item.get('host_venue', {}).get('display_name', '') if item.get('host_venue') else '',
                    'doi': ids.get('doi', '').replace('https://doi.org/', '') if ids.get('doi') else '',
                    'pmid': ids.get('pmid', ''),
                    'pmcid': ids.get('pmcid', ''),
                    'abstract': item.get('abstract', ''),
                    'cited_by_count': item.get('cited_by_count', 0),
                    'is_open_access': item.get('open_access', {}).get('is_oa', False),
                    'oa_url': item.get('open_access', {}).get('oa_url', ''),
                    'url': item.get('id', '')
                })
                self.rate_limit(0.1)

            self.metadata['status'] = 'completed'
            self.save_results()

        except Exception as e:
            logger.error(f"Error en OpenAlex: {e}")
            self.metadata['status'] = f'error: {str(e)}'

        return self.results
