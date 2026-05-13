"""
ExportManager - Exportación a formatos de gestores bibliográficos

Formatos soportados:
- RIS (Zotero, Mendeley, EndNote, RefWorks)
- BibTeX (LaTeX, JabRef, Zotero)
- CSV (Excel, Google Sheets)
- JSON (interoperabilidad)
"""

import re
import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ExportManager:
    """Exporta referencias bibliográficas a múltiples formatos."""

    def __init__(self, output_path: Path):
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def _parse_name(self, full_name: str) -> Tuple[str, str]:
        """Parsea nombre completo en (apellido, nombre)."""
        parts = full_name.strip().split()
        if len(parts) == 1:
            return parts[0], ""
        elif len(parts) == 2:
            return parts[1], parts[0]
        else:
            # Última palabra como apellido, resto como nombre
            return parts[-1], " ".join(parts[:-1])

    def to_ris(self, articles: List[Dict], filename: str = "references.ris") -> Path:
        """
        Exporta a formato RIS (tagged format).
        Compatible con Zotero, Mendeley, EndNote, RefWorks.

        Tags RIS usados:
        TY - Tipo de referencia
        TI - Título
        AU - Autor (uno por línea)
        T2 - Título secundario (journal)
        PY - Año
        VL - Volumen
        IS - Issue
        SP - Página inicial
        EP - Página final
        DO - DOI
        SN - ISSN/ISBN
        AB - Abstract
        UR - URL
        KW - Palabras clave
        ER - Fin de registro
        """
        lines = []

        for article in articles:
            # Determinar tipo
            ref_type = self._get_ris_type(article)
            lines.append(f"TY  - {ref_type}")

            # Título
            title = article.get('title', '')
            if title:
                lines.append(f"TI  - {title}")

            # Autores
            authors = article.get('authors', [])
            if not authors and article.get('author'):
                authors = article.get('author', [])

            for author in authors:
                if isinstance(author, dict):
                    name = author.get('fullName') or f"{author.get('given', '')} {author.get('family', '')}".strip()
                else:
                    name = str(author)
                if name:
                    lines.append(f"AU  - {name}")

            # Journal / Venue
            journal = (article.get('journal') or article.get('venue') or 
                      article.get('source') or article.get('journalTitle', ''))
            if journal:
                lines.append(f"T2  - {journal}")

            # Año
            year = article.get('year') or article.get('publication_year') or article.get('pubYear', '')
            if year:
                lines.append(f"PY  - {year}")

            # Volumen
            volume = article.get('volume', '')
            if volume:
                lines.append(f"VL  - {volume}")

            # Issue
            issue = article.get('issue', '')
            if issue:
                lines.append(f"IS  - {issue}")

            # Páginas
            pages = article.get('pages', '')
            if pages:
                if '-' in pages:
                    sp, ep = pages.split('-', 1)
                    lines.append(f"SP  - {sp.strip()}")
                    lines.append(f"EP  - {ep.strip()}")
                else:
                    lines.append(f"SP  - {pages}")

            # DOI
            doi = article.get('doi', '')
            if doi:
                lines.append(f"DO  - {doi}")

            # PMID
            pmid = article.get('pmid', '')
            if pmid:
                lines.append(f"AN  - {pmid}")  # Accession Number

            # Abstract
            abstract = article.get('abstract', '')
            if abstract:
                # RIS requiere que el abstract no tenga saltos de línea
                abstract_clean = abstract.replace('
', ' ').replace('', ' ')
                lines.append(f"AB  - {abstract_clean}")

            # URL
            url = article.get('url', '')
            if url:
                lines.append(f"UR  - {url}")

            # Keywords (si existen)
            keywords = article.get('keywords', [])
            if isinstance(keywords, list):
                for kw in keywords:
                    lines.append(f"KW  - {kw}")

            # Fin de registro
            lines.append("ER  - ")
            lines.append("")  # Línea en blanco entre registros

        # Escribir archivo
        output_file = self.output_path / filename
        ris_content = "
".join(lines)
        output_file.write_text(ris_content, encoding='utf-8')

        logger.info(f"RIS exportado: {output_file} ({len(articles)} referencias)")
        return output_file

    def to_bibtex(self, articles: List[Dict], filename: str = "references.bib") -> Path:
        """
        Exporta a formato BibTeX.
        Compatible con LaTeX, JabRef, Zotero.
        """
        lines = []

        for i, article in enumerate(articles):
            # Generar clave única
            first_author = ""
            if article.get('authors'):
                first_author = str(article['authors'][0]).split()[-1] if article['authors'] else ""
            year = str(article.get('year', article.get('publication_year', '0000')))
            cite_key = f"{first_author.lower()}{year}{i+1}" if first_author else f"ref{i+1}"
            cite_key = re.sub(r'[^a-zA-Z0-9]', '', cite_key)

            entry_type = self._get_bibtex_type(article)

            lines.append(f"@{entry_type}{{{cite_key},")

            # Campos
            fields = []

            if article.get('title'):
                fields.append(f"  title = {{{article['title']}}}")

            # Autores en formato BibTeX: Apellido, Nombre and Apellido, Nombre
            authors = article.get('authors', [])
            if authors:
                bibtex_authors = []
                for author in authors:
                    if isinstance(author, dict):
                        name = (f"{author.get('family', '')}, {author.get('given', '')}".strip(', '))
                    else:
                        parts = str(author).split()
                        if len(parts) > 1:
                            name = f"{parts[-1]}, {' '.join(parts[:-1])}"
                        else:
                            name = str(author)
                    bibtex_authors.append(name)
                fields.append(f"  author = {{{' and '.join(bibtex_authors)}}}")

            if article.get('year') or article.get('publication_year'):
                y = article.get('year') or article.get('publication_year')
                fields.append(f"  year = {{{y}}}")

            journal = (article.get('journal') or article.get('venue') or 
                      article.get('source') or article.get('journalTitle', ''))
            if journal:
                fields.append(f"  journal = {{{journal}}}")

            if article.get('volume'):
                fields.append(f"  volume = {{{article['volume']}}}")

            if article.get('issue') or article.get('number'):
                fields.append(f"  number = {{{article.get('issue', article.get('number', ''))}}}")

            if article.get('pages'):
                fields.append(f"  pages = {{{article['pages']}}}")

            if article.get('doi'):
                fields.append(f"  doi = {{{article['doi']}}}")

            if article.get('pmid'):
                fields.append(f"  pmid = {{{article['pmid']}}}")

            if article.get('abstract'):
                abstract_clean = article['abstract'].replace('
', ' ')
                fields.append(f"  abstract = {{{abstract_clean}}}")

            if article.get('url'):
                fields.append(f"  url = {{{article['url']}}}")

            lines.extend(fields)
            lines.append("}")
            lines.append("")

        output_file = self.output_path / filename
        output_file.write_text("
".join(lines), encoding='utf-8')

        logger.info(f"BibTeX exportado: {output_file} ({len(articles)} referencias)")
        return output_file

    def to_csv(self, articles: List[Dict], filename: str = "references.csv") -> Path:
        """Exporta a CSV para Excel/Google Sheets."""
        if not articles:
            logger.warning("No hay artículos para exportar a CSV")
            return None

        # Recolectar todas las columnas posibles
        all_keys = set()
        for article in articles:
            all_keys.update(article.keys())

        # Columnas preferidas en orden
        preferred = [
            'title', 'authors', 'year', 'publication_year', 'journal', 'venue', 
            'source', 'doi', 'pmid', 'pmcid', 'volume', 'issue', 'pages', 
            'abstract', 'url', 'cited_by_count', 'references_count', '_source'
        ]

        fieldnames = []
        for key in preferred:
            if key in all_keys:
                fieldnames.append(key)

        # Añadir columnas restantes
        for key in sorted(all_keys):
            if key not in fieldnames and not key.startswith('_'):
                fieldnames.append(key)

        output_file = self.output_path / filename

        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for article in articles:
                row = {}
                for key in fieldnames:
                    value = article.get(key, '')
                    # Convertir listas a strings
                    if isinstance(value, list):
                        value = '; '.join(str(v) for v in value)
                    row[key] = value
                writer.writerow(row)

        logger.info(f"CSV exportado: {output_file} ({len(articles)} referencias)")
        return output_file

    def to_json(self, articles: List[Dict], filename: str = "references.json") -> Path:
        """Exporta a JSON estructurado."""
        data = {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'count': len(articles),
                'source': 'Literature Review Pipeline'
            },
            'references': articles
        }

        output_file = self.output_path / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"JSON exportado: {output_file} ({len(articles)} referencias)")
        return output_file

    def export_all(self, articles: List[Dict], base_filename: str = "references") -> Dict[str, Path]:
        """
        Exporta a todos los formatos disponibles.

        Returns:
            Dict con paths de cada formato exportado
        """
        results = {}

        try:
            results['ris'] = self.to_ris(articles, f"{base_filename}.ris")
        except Exception as e:
            logger.error(f"Error exportando RIS: {e}")

        try:
            results['bibtex'] = self.to_bibtex(articles, f"{base_filename}.bib")
        except Exception as e:
            logger.error(f"Error exportando BibTeX: {e}")

        try:
            results['csv'] = self.to_csv(articles, f"{base_filename}.csv")
        except Exception as e:
            logger.error(f"Error exportando CSV: {e}")

        try:
            results['json'] = self.to_json(articles, f"{base_filename}.json")
        except Exception as e:
            logger.error(f"Error exportando JSON: {e}")

        logger.info(f"Exportación completada: {len(results)} formatos")
        return results

    def _get_ris_type(self, article: Dict) -> str:
        """Determina el tipo RIS apropiado."""
        article_type = article.get('type', '').lower()
        if 'review' in article_type:
            return 'JREV'
        elif 'book' in article_type:
            return 'BOOK'
        elif 'chapter' in article_type:
            return 'CHAP'
        elif 'conference' in article_type:
            return 'CONF'
        else:
            return 'JOUR'  # Journal article (default)

    def _get_bibtex_type(self, article: Dict) -> str:
        """Determina el tipo BibTeX apropiado."""
        article_type = article.get('type', '').lower()
        if 'review' in article_type:
            return 'article'
        elif 'book' in article_type:
            return 'book'
        elif 'chapter' in article_type:
            return 'incollection'
        elif 'conference' in article_type:
            return 'inproceedings'
        else:
            return 'article'
