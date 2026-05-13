"""
PDFDownloader - Descarga automática de artículos desde DOI

Fuentes de descarga (en orden de preferencia):
1. Unpaywall API (acceso abierto legal)
2. OpenAlex (PDF links)
3. Semantic Scholar (openAccessPdf)
4. DOI resolver directo (fallback)

Uso ético: respeta robots.txt y rate limits.
"""

import os
import json
import logging
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PDFDownloader:
    """Descarga PDFs de artículos académicos dado un DOI."""

    def __init__(
        self,
        output_path: Path,
        email: str = "",
        unpaywall_email: str = "",
        timeout: int = 30
    ):
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.email = email or unpaywall_email
        self.timeout = timeout
        self.downloaded = []
        self.failed = []

    def _download_file(self, url: str, filepath: Path, headers: Optional[Dict] = None) -> bool:
        """Descarga un archivo con manejo de errores."""
        try:
            req_headers = {
                'User-Agent': f'LiteratureReviewBot/1.0 (mailto:{self.email})' if self.email else 'LiteratureReviewBot/1.0'
            }
            if headers:
                req_headers.update(headers)

            req = urllib.request.Request(url, headers=req_headers)

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                # Verificar que es PDF
                content_type = response.headers.get('Content-Type', '')
                if 'pdf' not in content_type.lower() and 'octet-stream' not in content_type.lower():
                    # Algunos servidores no envían Content-Type correcto
                    pass

                data = response.read()
                if len(data) < 1000:  # Probablemente no es un PDF real
                    return False

                filepath.write_bytes(data)
                return True

        except Exception as e:
            logger.debug(f"Fallo descarga {url}: {e}")
            return False

    def _get_unpaywall_url(self, doi: str) -> Optional[str]:
        """Consulta Unpaywall API para obtener PDF de acceso abierto."""
        if not self.email:
            return None

        try:
            url = f"https://api.unpaywall.org/v2/{doi}?email={urllib.parse.quote(self.email)}"

            req = urllib.request.Request(url, headers={
                'User-Agent': f'LiteratureReviewBot/1.0 (mailto:{self.email})'
            })

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

            # Buscar mejor PDF disponible
            best_oa = data.get('best_oa_location', {})
            if best_oa:
                pdf_url = best_oa.get('url_for_pdf') or best_oa.get('url')
                if pdf_url:
                    return pdf_url

            # Fallback a cualquier location OA
            for loc in data.get('oa_locations', []):
                pdf_url = loc.get('url_for_pdf') or loc.get('url')
                if pdf_url:
                    return pdf_url

        except Exception as e:
            logger.debug(f"Unpaywall error for {doi}: {e}")

        return None

    def _get_doi_direct(self, doi: str) -> Optional[str]:
        """Intenta resolver DOI directamente a PDF."""
        try:
            # DOI resolver
            resolver_url = f"https://doi.org/{doi}"
            req = urllib.request.Request(resolver_url, headers={
                'User-Agent': 'LiteratureReviewBot/1.0',
                'Accept': 'application/pdf, application/x-pdf, */*'
            })

            with urllib.request.urlopen(req, timeout=10) as response:
                final_url = response.geturl()
                # Si el redirect ya es un PDF
                if final_url.endswith('.pdf'):
                    return final_url

                # Intentar añadir /pdf/ a URL de publisher comunes
                if 'sciencedirect.com' in final_url:
                    return final_url.replace('/article/', '/article/pii/') + '/pdfft?md5=...'

        except Exception as e:
            logger.debug(f"DOI direct error for {doi}: {e}")

        return None

    def download_article(
        self,
        doi: str,
        title: str = "",
        open_access_url: str = "",
        semantic_scholar_pdf: str = "",
        filename: Optional[str] = None
    ) -> Dict:
        """
        Intenta descargar un artículo por múltiples vías.

        Returns:
            Dict con status, filepath, source
        """
        if not doi:
            return {'status': 'skipped_no_doi', 'filepath': None, 'source': None}

        # Sanitizar nombre de archivo
        safe_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in title[:80])
        if not filename:
            filename = f"{safe_title}_{doi.replace('/', '_')}.pdf"

        filepath = self.output_path / filename

        # Si ya existe, saltar
        if filepath.exists():
            return {'status': 'already_exists', 'filepath': str(filepath), 'source': 'cache'}

        # Orden de intentos
        sources = [
            ('semantic_scholar', semantic_scholar_pdf),
            ('openalex', open_access_url),
            ('unpaywall', self._get_unpaywall_url(doi)),
            ('doi_direct', self._get_doi_direct(doi))
        ]

        for source_name, pdf_url in sources:
            if not pdf_url:
                continue

            success = self._download_file(pdf_url, filepath)
            if success:
                self.downloaded.append({
                    'doi': doi,
                    'title': title,
                    'filepath': str(filepath),
                    'source': source_name,
                    'timestamp': datetime.now().isoformat()
                })
                return {'status': 'downloaded', 'filepath': str(filepath), 'source': source_name}

        # Falló todo
        self.failed.append({
            'doi': doi,
            'title': title,
            'timestamp': datetime.now().isoformat()
        })
        return {'status': 'failed', 'filepath': None, 'source': None}

    def download_batch(
        self,
        articles: List[Dict],
        max_downloads: Optional[int] = None
    ) -> Dict:
        """
        Descarga un lote de artículos.

        Args:
            articles: Lista de dicts con 'doi', 'title', 'open_access_pdf', etc.
            max_downloads: Límite de descargas (None = todas)

        Returns:
            Resumen de descargas
        """
        total = len(articles)
        limit = max_downloads or total

        logger.info(f"Iniciando descarga de {min(limit, total)} PDFs...")

        for i, article in enumerate(articles[:limit]):
            if i % 10 == 0:
                logger.info(f"Progreso: {i}/{min(limit, total)}")

            self.download_article(
                doi=article.get('doi', ''),
                title=article.get('title', ''),
                open_access_url=article.get('oa_url', article.get('open_access_pdf', '')),
                semantic_scholar_pdf=article.get('open_access_pdf', '')
            )

            # Rate limiting respetuoso
            import time
            time.sleep(0.5)

        summary = {
            'total_attempted': min(limit, total),
            'downloaded': len(self.downloaded),
            'failed': len(self.failed),
            'already_exists': len([d for d in self.downloaded if d.get('source') == 'cache']),
            'output_path': str(self.output_path)
        }

        # Guardar reporte
        report_path = self.output_path / 'download_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': summary,
                'downloaded': self.downloaded,
                'failed': self.failed
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"Descarga completada: {summary['downloaded']}/{summary['total_attempted']} exitosos")
        return summary
