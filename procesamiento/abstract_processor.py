"""
AbstractProcessor - Evaluación de relevancia de abstracts

Estrategias de filtrado:
1. Keyword matching (obligatorio + excluyente)
2. Scoring por frecuencia de términos relevantes
3. (Opcional) NLP con transformers para clasificación zero-shot
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import Counter
from datetime import datetime

logger = logging.getLogger(__name__)


class AbstractProcessor:
    """Procesa abstracts para evaluar relevancia respecto a criterios definidos."""

    def __init__(
        self,
        required_keywords: List[str] = None,
        exclusion_keywords: List[str] = None,
        scoring_weights: Optional[Dict[str, float]] = None,
        relevance_threshold: float = 0.3
    ):
        """
        Args:
            required_keywords: Términos que DEBEN aparecer (inclusión obligatoria)
            exclusion_keywords: Términos que SI aparecen descartan el artículo
            scoring_weights: Pesos por categoría de términos para scoring
            relevance_threshold: Puntaje mínimo para considerar relevante
        """
        self.required_keywords = [k.lower() for k in (required_keywords or [])]
        self.exclusion_keywords = [k.lower() for k in (exclusion_keywords or [])]
        self.scoring_weights = scoring_weights or {}
        self.relevance_threshold = relevance_threshold
        self.results = []

    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para comparación."""
        if not text:
            return ""
        return re.sub(r'[^\w\s]', ' ', text.lower())

    def _check_required(self, text: str) -> Tuple[bool, List[str]]:
        """Verifica si todos los términos requeridos están presentes."""
        text_norm = self._normalize_text(text)
        found = []
        for kw in self.required_keywords:
            # Soporte para frases exactas y palabras sueltas
            if ' ' in kw:
                if kw in text_norm:
                    found.append(kw)
            else:
                words = text_norm.split()
                if kw in words:
                    found.append(kw)

        # Al menos uno de cada "grupo" requerido (si hay grupos separados por ;)
        # Por simplicidad: todos los required deben estar
        all_present = len(found) == len(self.required_keywords) if self.required_keywords else True
        return all_present, found

    def _check_exclusion(self, text: str) -> Tuple[bool, List[str]]:
        """Verifica si hay términos excluyentes."""
        text_norm = self._normalize_text(text)
        found = []
        for kw in self.exclusion_keywords:
            if ' ' in kw:
                if kw in text_norm:
                    found.append(kw)
            else:
                if kw in text_norm.split():
                    found.append(kw)

        has_exclusion = len(found) > 0
        return has_exclusion, found

    def _calculate_score(self, text: str) -> float:
        """Calcula score de relevancia basado en pesos."""
        if not self.scoring_weights:
            return 1.0  # Sin pesos, todo pasa si cumple required

        text_norm = self._normalize_text(text)
        words = text_norm.split()
        word_counts = Counter(words)

        total_score = 0.0
        total_weight = 0.0

        for category, terms in self.scoring_weights.items():
            if isinstance(terms, dict):
                # Formato: {"términos": ["a", "b"], "weight": 2.0}
                category_terms = terms.get('terms', [])
                weight = terms.get('weight', 1.0)
            else:
                # Formato simple: lista de términos, peso 1.0
                category_terms = terms if isinstance(terms, list) else [terms]
                weight = 1.0

            category_score = 0
            for term in category_terms:
                term_lower = term.lower()
                count = word_counts.get(term_lower, 0)
                if count > 0:
                    category_score += min(count, 3)  # Cap en 3 para no saturar

            # Normalizar por número de términos en categoría
            if len(category_terms) > 0:
                category_score = category_score / len(category_terms)

            total_score += category_score * weight
            total_weight += weight

        if total_weight > 0:
            return total_score / total_weight
        return 0.0

    def process_article(self, article: Dict) -> Dict:
        """
        Procesa un artículo y determina relevancia.

        Args:
            article: Dict con 'title', 'abstract', 'doi', etc.

        Returns:
            Dict enriquecido con 'relevance_score', 'is_relevant', 'reasons'
        """
        title = article.get('title', '')
        abstract = article.get('abstract', '')
        full_text = f"{title} {abstract}"

        result = {
            **article,
            'processed_at': datetime.now().isoformat(),
            'relevance_score': 0.0,
            'is_relevant': False,
            'filter_reasons': []
        }

        # 1. Verificar exclusiones primero
        has_exclusion, excluded_terms = self._check_exclusion(full_text)
        if has_exclusion:
            result['is_relevant'] = False
            result['filter_reasons'].append(f"EXCLUDED: {', '.join(excluded_terms)}")
            return result

        # 2. Verificar requeridos
        has_required, required_found = self._check_required(full_text)
        if not has_required and self.required_keywords:
            result['is_relevant'] = False
            missing = set(self.required_keywords) - set(required_found)
            result['filter_reasons'].append(f"MISSING_REQUIRED: {', '.join(missing)}")
            return result

        # 3. Calcular score
        score = self._calculate_score(full_text)
        result['relevance_score'] = round(score, 3)

        # 4. Determinar relevancia
        if score >= self.relevance_threshold:
            result['is_relevant'] = True
            result['filter_reasons'].append(f"PASS: score {score:.3f} >= threshold {self.relevance_threshold}")
        else:
            result['is_relevant'] = False
            result['filter_reasons'].append(f"LOW_SCORE: {score:.3f} < threshold {self.relevance_threshold}")

        return result

    def process_batch(self, articles: List[Dict]) -> Dict:
        """
        Procesa un lote de artículos.

        Returns:
            Dict con 'relevant', 'excluded', 'low_score', 'summary'
        """
        relevant = []
        excluded = []
        low_score = []
        missing_abstract = []

        for article in articles:
            if not article.get('abstract') and not article.get('title'):
                missing_abstract.append(article)
                continue

            processed = self.process_article(article)

            if any("EXCLUDED" in r for r in processed['filter_reasons']):
                excluded.append(processed)
            elif any("MISSING_REQUIRED" in r for r in processed['filter_reasons']):
                excluded.append(processed)
            elif not processed['is_relevant']:
                low_score.append(processed)
            else:
                relevant.append(processed)

        summary = {
            'total_processed': len(articles),
            'relevant': len(relevant),
            'excluded': len(excluded),
            'low_score': len(low_score),
            'missing_abstract': len(missing_abstract),
            'relevance_rate': len(relevant) / len(articles) if articles else 0
        }

        logger.info(f"Filtrado completado: {summary['relevant']}/{summary['total_processed']} relevantes")

        return {
            'summary': summary,
            'relevant': relevant,
            'excluded': excluded,
            'low_score': low_score,
            'missing_abstract': missing_abstract
        }

    def save_results(self, output_path: Path, batch_results: Dict) -> None:
        """Guarda resultados del filtrado."""
        output_path.mkdir(parents=True, exist_ok=True)

        # Guardar relevantes
        with open(output_path / 'articles_relevant.json', 'w', encoding='utf-8') as f:
            json.dump(batch_results['relevant'], f, indent=2, ensure_ascii=False)

        # Guardar excluidos
        with open(output_path / 'articles_excluded.json', 'w', encoding='utf-8') as f:
            json.dump(batch_results['excluded'], f, indent=2, ensure_ascii=False)

        # Guardar reporte
        with open(output_path / 'filtering_report.json', 'w', encoding='utf-8') as f:
            json.dump({
                'summary': batch_results['summary'],
                'parameters': {
                    'required_keywords': self.required_keywords,
                    'exclusion_keywords': self.exclusion_keywords,
                    'scoring_weights': self.scoring_weights,
                    'relevance_threshold': self.relevance_threshold
                }
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"Resultados guardados en: {output_path}")
