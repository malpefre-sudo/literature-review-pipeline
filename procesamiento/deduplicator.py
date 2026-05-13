"""
Deduplicator - Motor de deduplicación de referencias bibliográficas
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class Deduplicator:
    """Deduplica referencias de múltiples fuentes usando múltiples estrategias."""

    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.seen_dois = set()
        self.seen_pmids = set()
        self.seen_pmcids = set()
        self.seen_hashes = set()
        self.duplicates = []
        self.unique_results = []

    def _normalize_title(self, title: str) -> str:
        """Normaliza título para comparación."""
        return re.sub(r'[^\w\s]', '', title.lower().strip())

    def _title_similarity(self, title1: str, title2: str) -> float:
        """Calcula similitud entre dos títulos."""
        if not title1 or not title2:
            return 0.0
        return SequenceMatcher(None, 
            self._normalize_title(title1), 
            self._normalize_title(title2)
        ).ratio()

    def _get_fingerprint(self, item: Dict) -> str:
        """Genera fingerprint único del artículo."""
        # Prioridad: DOI > PMID > PMCID > Title+Year+FirstAuthor
        if item.get('doi'):
            return f"doi:{item['doi'].lower()}"
        if item.get('pmid'):
            return f"pmid:{item['pmid']}"
        if item.get('pmcid'):
            return f"pmcid:{item['pmcid']}"

        # Fallback: combinación de título + año + primer autor
        title = self._normalize_title(item.get('title', ''))
        year = str(item.get('year', item.get('publication_year', '')))
        authors = item.get('authors', [])
        first_author = authors[0].split()[-1] if authors else ''

        fingerprint = f"{title}|{year}|{first_author}"
        return hashlib.md5(fingerprint.encode()).hexdigest()

    def deduplicate(self, results: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict]]:
        """
        Deduplica una lista de resultados.

        Returns:
            (unique_results, duplicates)
        """
        self.unique_results = []
        self.duplicates = []

        for item in results:
            is_duplicate = False

            # 1. Verificar DOI
            doi = item.get('doi', '').lower()
            if doi and doi in self.seen_dois:
                is_duplicate = True
            elif doi:
                self.seen_dois.add(doi)

            # 2. Verificar PMID
            pmid = item.get('pmid', '')
            if not is_duplicate and pmid and pmid in self.seen_pmids:
                is_duplicate = True
            elif pmid:
                self.seen_pmids.add(pmid)

            # 3. Verificar PMCID
            pmcid = item.get('pmcid', '')
            if not is_duplicate and pmcid and pmcid in self.seen_pmcids:
                is_duplicate = True
            elif pmcid:
                self.seen_pmcids.add(pmcid)

            # 4. Verificar fingerprint
            if not is_duplicate:
                fp = self._get_fingerprint(item)
                if fp in self.seen_hashes:
                    is_duplicate = True
                else:
                    self.seen_hashes.add(fp)

            # 5. Verificar similitud de título con artículos únicos ya aceptados
            if not is_duplicate:
                title = item.get('title', '')
                for unique in self.unique_results:
                    if self._title_similarity(title, unique.get('title', '')) > self.similarity_threshold:
                        is_duplicate = True
                        break

            if is_duplicate:
                item['_duplicate_reason'] = 'identifier_match_or_similar_title'
                self.duplicates.append(item)
            else:
                self.unique_results.append(item)

        logger.info(f"Deduplicación: {len(self.unique_results)} únicos, {len(self.duplicates)} duplicados")
        return self.unique_results, self.duplicates

    def save_deduplication_report(self, output_path: Path) -> None:
        """Guarda reporte de deduplicación."""
        report = {
            'summary': {
                'total_input': len(self.unique_results) + len(self.duplicates),
                'unique': len(self.unique_results),
                'duplicates': len(self.duplicates),
                'deduplication_rate': len(self.duplicates) / (len(self.unique_results) + len(self.duplicates)) if (len(self.unique_results) + len(self.duplicates)) > 0 else 0
            },
            'unique_results': self.unique_results,
            'duplicates': self.duplicates
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Reporte guardado: {output_path}")
