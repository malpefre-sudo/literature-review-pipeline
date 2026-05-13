"""
Utils - Funciones utilitarias compartidas para el pipeline de literatura
"""

import re
import json
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """Limpia un string para usar como nombre de archivo."""
    return "".join(c if c.isalnum() or c in ('_', '-', ' ') else '_' for c in name).strip()


def generate_query_from_concepts(
    concepts: Dict[str, List[str]],
    within_operator: str = "OR",
    between_operator: str = "AND",
    use_parentheses: bool = True
) -> str:
    """Genera una query booleana a partir de conceptos."""
    parts = []
    for concept_name, terms in concepts.items():
        if not terms:
            continue
        if use_parentheses:
            part = f"({' {within_operator} ".join(terms)})"
        else:
            part = f" {' {within_operator} ".join(terms)}"
        parts.append(part)

    return f" {' {between_operator} ".join(parts)


def merge_results(results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Combina resultados de múltiples fuentes."""
    merged = {
        'metadata': {
            'sources': [],
            'total_results': 0,
            'merged_at': None
        },
        'results': []
    }

    seen_dois = set()
    seen_pmids = set()
    seen_titles = set()

    for result_data in results_list:
        source = result_data.get('metadata', {}).get('source', 'unknown')
        merged['metadata']['sources'].append(source)

        for item in result_data.get('results', []):
            # Deduplicación por DOI
            doi = item.get('doi', '').lower()
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)

            # Deduplicación por PMID
            pmid = item.get('pmid', '')
            if pmid and pmid in seen_pmids:
                continue
            if pmid:
                seen_pmids.add(pmid)

            # Deduplicación por título (hash normalizado)
            title = item.get('title', '').lower().strip()
            if title:
                title_hash = hashlib.md5(title.encode()).hexdigest()
                if title_hash in seen_titles:
                    continue
                seen_titles.add(title_hash)

            item['_source'] = source
            merged['results'].append(item)

    merged['metadata']['total_results'] = len(merged['results'])
    from datetime import datetime
    merged['metadata']['merged_at'] = datetime.now().isoformat()

    return merged


def export_to_csv(data: List[Dict], filepath: Path) -> None:
    """Exporta resultados a CSV."""
    import csv
    if not data:
        return

    keys = set()
    for item in data:
        keys.update(item.keys())
    keys = sorted(keys)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)


def export_to_bibtex(data: List[Dict], filepath: Path) -> None:
    """Exporta resultados a BibTeX (simplificado)."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for i, item in enumerate(data):
            key = f"ref{i+1}"
            f.write(f"@article{{{key},\n")
            f.write(f"  title = {{{item.get('title', '')}}},\n")
            f.write(f"  author = {{{' and '.join(item.get('authors', []))}}},\n")
            f.write(f"  year = {{{item.get('year', item.get('publication_year', ''))}}},\n")
            f.write(f"  journal = {{{item.get('journal', item.get('venue', ''))}}},\n")
            if item.get('doi'):
                f.write(f"  doi = {{{item.get('doi')}}},\n")
            if item.get('pmid'):
                f.write(f"  pmid = {{{item.get('pmid')}}},\n")
            f.write("}\n\n")
