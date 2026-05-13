"""
SearchSemanticScholar - Módulo de búsqueda en Semantic Scholar
"""

import json
import logging
import urllib.request
from pathlib import Path
from typing import Dict, List
from base_search import BaseSearch

logger = logging.getLogger(__name__)


class SearchSemanticScholar(BaseSearch):
    """Buscador en Semantic Scholar API."""

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_keys: Dict[str, str], output_path: Path, project_name: str = "review"):
        super().__init__(api_keys, output_path, project_name)
        self.api_key = api_keys.get('semantic_scholar_api_key', '')

    def validate_credentials(self) -> bool:
        """API key opcional pero recomendada."""
        return True  # Permite búsqueda sin key (límites más bajos)

    def search(self, query: str, max_results: int = 100, **kwargs) -> List[Dict]:
        """Ejecuta búsqueda en Semantic Scholar."""
        self.metadata['query'] = query
        logger.info(f"Buscando Semantic Scholar: {query}")

        try:
            fields = "title,authors,year,abstract,externalIds,venue,citationCount,openAccessPdf"
            url = f"{self.BASE_URL}/paper/search?query={urllib.parse.quote(query)}&limit={min(max_results, 100)}&fields={fields}"

            headers = {}
            if self.api_key:
                headers['x-api-key'] = self.api_key

            req = urllib.request.Request(url, headers=headers)

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())

            papers = data.get('data', [])
            total = data.get('total', 0)
            self.metadata['total_results'] = total

            for paper in papers:
                external_ids = paper.get('externalIds', {})
                self.results.append({
                    'paper_id': paper.get('paperId', ''),
                    'title': paper.get('title', ''),
                    'authors': [a.get('name', '') for a in paper.get('authors', [])],
                    'year': paper.get('year', ''),
                    'venue': paper.get('venue', ''),
                    'abstract': paper.get('abstract', ''),
                    'doi': external_ids.get('DOI', ''),
                    'pmid': external_ids.get('PubMed', ''),
                    'citations': paper.get('citationCount', 0),
                    'open_access_pdf': paper.get('openAccessPdf', {}).get('url', ''),
                    'url': f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}"
                })
                self.rate_limit(0.1 if self.api_key else 1.0)

            self.metadata['status'] = 'completed'
            self.save_results()

        except Exception as e:
            logger.error(f"Error en Semantic Scholar: {e}")
            self.metadata['status'] = f'error: {str(e)}'

        return self.results
