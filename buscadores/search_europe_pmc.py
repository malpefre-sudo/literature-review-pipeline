"""
SearchEuropePMC - Módulo de búsqueda en Europe PMC
"""

import json
import logging
import urllib.request
from pathlib import Path
from typing import Dict, List
from base_search import BaseSearch

logger = logging.getLogger(__name__)


class SearchEuropePMC(BaseSearch):
    """Buscador en Europe PMC REST API."""

    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def __init__(self, api_keys: Dict[str, str], output_path: Path, project_name: str = "review"):
        super().__init__(api_keys, output_path, project_name)
        self.email = api_keys.get('entrez_email', '')

    def validate_credentials(self) -> bool:
        """No requiere key, pero email es recomendado."""
        return True

    def search(self, query: str, max_results: int = 100, **kwargs) -> List[Dict]:
        """Ejecuta búsqueda en Europe PMC."""
        self.metadata['query'] = query
        logger.info(f"Buscando Europe PMC: {query}")

        try:
            # Europe PMC usa query syntax similar a PubMed
            url = f"{self.BASE_URL}?query={urllib.parse.quote(query)}&pageSize={min(max_results, 1000)}&format=json&resultType=core"

            headers = {
                'User-Agent': f'LiteratureReviewBot/1.0 (mailto:{self.email})' if self.email else 'LiteratureReviewBot/1.0'
            }

            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

            items = data.get('resultList', {}).get('result', [])
            total = data.get('hitCount', 0)
            self.metadata['total_results'] = total

            for item in items:
                self.results.append({
                    'pmid': item.get('pmid', ''),
                    'pmcid': item.get('pmcid', ''),
                    'doi': item.get('doi', ''),
                    'title': item.get('title', ''),
                    'authors': [a.get('fullName', '') for a in item.get('authorList', {}).get('author', [])],
                    'journal': item.get('journalTitle', ''),
                    'year': item.get('pubYear', ''),
                    'abstract': item.get('abstractText', ''),
                    'is_open_access': item.get('isOpenAccess', 'N') == 'Y',
                    'url': f"https://europepmc.org/article/MED/{item.get('pmid', '')}" if item.get('pmid') else ''
                })
                self.rate_limit(0.3)

            self.metadata['status'] = 'completed'
            self.save_results()

        except Exception as e:
            logger.error(f"Error en Europe PMC: {e}")
            self.metadata['status'] = f'error: {str(e)}'

        return self.results
