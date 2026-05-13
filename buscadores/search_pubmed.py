"""
SearchPubMed - Módulo de búsqueda en PubMed vía NCBI E-utilities
"""

import json
import logging
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional
from base_search import BaseSearch

logger = logging.getLogger(__name__)


class SearchPubMed(BaseSearch):
    """Buscador en PubMed usando NCBI E-utilities."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, api_keys: Dict[str, str], output_path: Path, project_name: str = "review"):
        super().__init__(api_keys, output_path, project_name)
        self.email = api_keys.get('entrez_email', '')
        self.api_key = api_keys.get('ncbi_api_key', '')
        self.base_params = {
            'email': self.email,
            'tool': 'litreview_pipeline'
        }
        if self.api_key:
            self.base_params['api_key'] = self.api_key

    def validate_credentials(self) -> bool:
        """Requiere email de Entrez."""
        return bool(self.email)

    def search(self, query: str, max_results: int = 100, **kwargs) -> List[Dict]:
        """Ejecuta búsqueda en PubMed."""
        if not self.validate_credentials():
            raise ValueError("Email de Entrez requerido. Configúralo en APIs.")

        self.metadata['query'] = query
        logger.info(f"Buscando PubMed: {query}")

        try:
            # Step 1: ESearch - obtener IDs
            search_params = {
                **self.base_params,
                'db': 'pubmed',
                'term': query,
                'retmax': min(max_results, 10000),
                'retmode': 'json',
                'sort': 'relevance'
            }

            url = f"{self.BASE_URL}/esearch.fcgi?" + urllib.parse.urlencode(search_params)

            with urllib.request.urlopen(url, timeout=30) as response:
                search_data = json.loads(response.read().decode())

            id_list = search_data.get('esearchresult', {}).get('idlist', [])
            total_count = int(search_data.get('esearchresult', {}).get('count', 0))

            self.metadata['total_results'] = total_count
            logger.info(f"PubMed: {total_count} resultados totales, {len(id_list)} a descargar")

            if not id_list:
                self.metadata['status'] = 'completed_empty'
                return []

            # Step 2: ESummary - obtener metadatos
            summary_params = {
                **self.base_params,
                'db': 'pubmed',
                'id': ','.join(id_list),
                'retmode': 'json'
            }

            summary_url = f"{self.BASE_URL}/esummary.fcgi?" + urllib.parse.urlencode(summary_params)

            with urllib.request.urlopen(summary_url, timeout=60) as response:
                summary_data = json.loads(response.read().decode())

            # Procesar resultados
            results = summary_data.get('result', {})
            for pmid in id_list:
                if pmid in results and pmid != 'uids':
                    article = results[pmid]
                    self.results.append({
                        'pmid': pmid,
                        'title': article.get('title', ''),
                        'authors': [a.get('name', '') for a in article.get('authors', [])],
                        'source': article.get('source', ''),
                        'pubdate': article.get('pubdate', ''),
                        'doi': article.get('elocationid', '').replace('doi: ', '') if article.get('elocationid', '').startswith('doi:') else '',
                        'abstract': None,  # Requiere EFetch para abstract completo
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    })
                self.rate_limit(0.34 if self.api_key else 1.0)  # NCBI rate limits

            self.metadata['status'] = 'completed'
            self.save_results()

        except Exception as e:
            logger.error(f"Error en PubMed: {e}")
            self.metadata['status'] = f'error: {str(e)}'

        return self.results
