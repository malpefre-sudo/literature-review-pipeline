"""
BibliometricAnalyzer - Análisis bibliométrico y visualización

Genera gráficos y métricas bibliométricas:
- Producción de artículos por año
- Top autores, journals, países
- Red de co-autoría
- Red de co-citación
- Mapa de co-ocurrencia de palabras clave
- Word cloud de términos frecuentes
"""

import json
import logging
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class BibliometricAnalyzer:
    """Analiza referencias bibliográficas y genera visualizaciones."""

    def __init__(self, output_path: Path):
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.articles = []
        self.metrics = {}

    def load_articles(self, articles: List[Dict]) -> None:
        """Carga artículos para análisis."""
        self.articles = articles
        logger.info(f"Cargados {len(articles)} artículos para análisis bibliométrico")

    def load_from_json(self, json_path: Path) -> None:
        """Carga artículos desde archivo JSON."""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'references' in data:
            self.articles = data['references']
        elif 'results' in data:
            self.articles = data['results']
        else:
            self.articles = data if isinstance(data, list) else []

        logger.info(f"Cargados {len(self.articles)} artículos desde {json_path}")

    # ============ MÉTRICAS BÁSICAS ============

    def calculate_basic_metrics(self) -> Dict:
        """Calcula métricas bibliométricas básicas."""
        total = len(self.articles)

        # Años
        years = []
        for a in self.articles:
            y = a.get('year') or a.get('publication_year') or a.get('pubYear')
            if y and str(y).isdigit():
                years.append(int(str(y)[:4]))

        # Autores únicos
        all_authors = []
        for a in self.articles:
            authors = a.get('authors', [])
            for auth in authors:
                if isinstance(auth, dict):
                    name = auth.get('fullName') or f"{auth.get('family', '')} {auth.get('given', '')}".strip()
                else:
                    name = str(auth)
                if name:
                    all_authors.append(name)

        # Journals
        journals = []
        for a in self.articles:
            j = (a.get('journal') or a.get('venue') or a.get('source') or a.get('journalTitle', ''))
            if j:
                journals.append(j)

        # DOIs
        dois = [a.get('doi', '') for a in self.articles if a.get('doi')]

        # Open Access
        oa_count = sum(1 for a in self.articles if a.get('is_open_access') or a.get('open_access_pdf'))

        self.metrics = {
            'total_articles': total,
            'unique_authors': len(set(all_authors)),
            'unique_journals': len(set(journals)),
            'with_doi': len(dois),
            'open_access': oa_count,
            'oa_percentage': round(oa_count / total * 100, 1) if total > 0 else 0,
            'year_range': (min(years), max(years)) if years else (None, None),
            'avg_citations': self._avg_citations()
        }

        return self.metrics

    def _avg_citations(self) -> float:
        """Calcula promedio de citaciones."""
        citations = []
        for a in self.articles:
            c = a.get('cited_by_count') or a.get('citationCount') or a.get('citations', 0)
            if isinstance(c, (int, float)):
                citations.append(c)
        return round(sum(citations) / len(citations), 1) if citations else 0.0

    # ============ GRÁFICOS ============

    def plot_publications_by_year(self, filename: str = "publications_by_year.png") -> Path:
        """Gráfico de barras: artículos por año."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.error("matplotlib no instalado")
            raise

        years = []
        for a in self.articles:
            y = a.get('year') or a.get('publication_year') or a.get('pubYear')
            if y and str(y).isdigit():
                years.append(int(str(y)[:4]))

        if not years:
            logger.warning("No hay datos de año")
            return None

        year_counts = Counter(years)
        min_year, max_year = min(years), max(years)
        all_years = range(min_year, max_year + 1)
        counts = [year_counts.get(y, 0) for y in all_years]

        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(all_years, counts, color='#1f77b4', edgecolor='white', alpha=0.8)

        # Añadir valores encima de barras
        for bar, count in zip(bars, counts):
            if count > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       str(count), ha='center', va='bottom', fontsize=9)

        ax.set_xlabel('Año', fontsize=12)
        ax.set_ylabel('Número de publicaciones', fontsize=12)
        ax.set_title('Producción de artículos por año', fontsize=14, fontweight='bold')
        ax.set_xticks(list(all_years))
        ax.set_xticklabels(list(all_years), rotation=45)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_file = self.output_path / filename
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Gráfico guardado: {output_file}")
        return output_file

    def plot_top_authors(self, top_n: int = 15, filename: str = "top_authors.png") -> Path:
        """Gráfico horizontal: autores más productivos."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise

        author_counts = Counter()
        for a in self.articles:
            authors = a.get('authors', [])
            for auth in authors:
                if isinstance(auth, dict):
                    name = auth.get('fullName') or f"{auth.get('family', '')} {auth.get('given', '')}".strip()
                else:
                    name = str(auth)
                if name:
                    # Normalizar: solo apellido + inicial
                    parts = name.split()
                    if len(parts) >= 2:
                        normalized = f"{parts[-1]} {parts[0][0]}."
                    else:
                        normalized = name
                    author_counts[normalized] += 1

        top = author_counts.most_common(top_n)
        if not top:
            return None

        names, counts = zip(*top)

        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.viridis(range(0, len(names) * 20, 20))
        bars = ax.barh(range(len(names)), counts, color=colors, edgecolor='white')
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names)
        ax.invert_yaxis()
        ax.set_xlabel('Número de artículos', fontsize=12)
        ax.set_title(f'Top {top_n} autores más productivos', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        # Valores
        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                   str(count), ha='left', va='center', fontsize=9)

        plt.tight_layout()
        output_file = self.output_path / filename
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file

    def plot_top_journals(self, top_n: int = 15, filename: str = "top_journals.png") -> Path:
        """Gráfico horizontal: journals más frecuentes."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise

        journal_counts = Counter()
        for a in self.articles:
            j = (a.get('journal') or a.get('venue') or a.get('source') or a.get('journalTitle', ''))
            if j:
                journal_counts[j] += 1

        top = journal_counts.most_common(top_n)
        if not top:
            return None

        names, counts = zip(*top)
        # Truncar nombres largos
        names = [n[:50] + '...' if len(n) > 50 else n for n in names]

        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.plasma(range(0, len(names) * 20, 20))
        bars = ax.barh(range(len(names)), counts, color=colors, edgecolor='white')
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names)
        ax.invert_yaxis()
        ax.set_xlabel('Número de artículos', fontsize=12)
        ax.set_title(f'Top {top_n} journals más frecuentes', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                   str(count), ha='left', va='center', fontsize=9)

        plt.tight_layout()
        output_file = self.output_path / filename
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file

    def plot_citation_distribution(self, filename: str = "citation_distribution.png") -> Path:
        """Histograma de distribución de citaciones."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            raise

        citations = []
        for a in self.articles:
            c = a.get('cited_by_count') or a.get('citationCount') or a.get('citations', 0)
            if isinstance(c, (int, float)) and c >= 0:
                citations.append(c)

        if not citations:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        # Usar bins logarítmicos si hay mucha variación
        if max(citations) > 100:
            bins = np.logspace(0, np.log10(max(citations) + 1), 30)
            ax.set_xscale('log')
        else:
            bins = 20

        ax.hist(citations, bins=bins, color='#2E7D32', edgecolor='white', alpha=0.8)
        ax.set_xlabel('Número de citaciones', fontsize=12)
        ax.set_ylabel('Frecuencia', fontsize=12)
        ax.set_title('Distribución de citaciones por artículo', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        # Estadísticas
        mean_c = sum(citations) / len(citations)
        median_c = sorted(citations)[len(citations) // 2]
        ax.axvline(mean_c, color='red', linestyle='--', label=f'Media: {mean_c:.1f}')
        ax.axvline(median_c, color='orange', linestyle='--', label=f'Mediana: {median_c:.1f}')
        ax.legend()

        plt.tight_layout()
        output_file = self.output_path / filename
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file

    def plot_coauthorship_network(self, min_collaborations: int = 2, 
                                   filename: str = "coauthorship_network.png") -> Path:
        """Red de co-autoría (requiere networkx)."""
        try:
            import matplotlib.pyplot as plt
            import networkx as nx
        except ImportError:
            logger.warning("networkx no instalado. Instálalo: pip install networkx")
            return None

        G = nx.Graph()

        for article in self.articles:
            authors = article.get('authors', [])
            names = []
            for auth in authors:
                if isinstance(auth, dict):
                    name = auth.get('fullName') or f"{auth.get('family', '')} {auth.get('given', '')}".strip()
                else:
                    name = str(auth)
                if name:
                    # Normalizar
                    parts = name.split()
                    if len(parts) >= 2:
                        normalized = f"{parts[-1]} {parts[0][0]}."
                    else:
                        normalized = name
                    names.append(normalized)

            # Añadir aristas entre todos los autores del artículo
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    if G.has_edge(names[i], names[j]):
                        G[names[i]][names[j]]['weight'] += 1
                    else:
                        G.add_edge(names[i], names[j], weight=1)

        # Filtrar por mínimo de colaboraciones
        edges_to_remove = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] < min_collaborations]
        G.remove_edges_from(edges_to_remove)
        nodes_to_remove = [n for n in G.nodes() if G.degree(n) == 0]
        G.remove_nodes_from(nodes_to_remove)

        if len(G.nodes()) == 0:
            logger.warning("No hay suficientes datos para red de co-autoría")
            return None

        fig, ax = plt.subplots(figsize=(14, 14))

        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

        # Tamaño de nodos por grado
        node_sizes = [G.degree(n) * 100 + 100 for n in G.nodes()]

        # Color por comunidad (componente conexa)
        components = list(nx.connected_components(G))
        colors = plt.cm.Set3(range(len(components)))
        node_colors = []
        for node in G.nodes():
            for i, comp in enumerate(components):
                if node in comp:
                    node_colors.append(colors[i])
                    break

        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8, ax=ax)
        nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.5, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=7, ax=ax)

        ax.set_title('Red de Co-autoría', fontsize=16, fontweight='bold')
        ax.axis('off')

        plt.tight_layout()
        output_file = self.output_path / filename
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Red de co-autoría guardada: {output_file}")
        return output_file

    def plot_keyword_cooccurrence(self, filename: str = "keyword_cooccurrence.png") -> Path:
        """Mapa de calor de co-ocurrencia de palabras clave en títulos."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            raise

        # Extraer palabras de títulos (stopwords básicas)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                     'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                     'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
                     'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
                     'study', 'effect', 'effects', 'using', 'use', 'used', 'analysis', 'based'}

        word_counts = Counter()
        article_words = []

        for a in self.articles:
            title = a.get('title', '').lower()
            abstract = a.get('abstract', '').lower()
            text = f"{title} {abstract}"
            words = re.findall(r'\b[a-z]{4,}\b', text)
            words = [w for w in words if w not in stopwords]
            article_words.append(set(words))
            word_counts.update(words)

        # Top palabras
        top_words = [w for w, c in word_counts.most_common(20)]
        if len(top_words) < 3:
            return None

        # Matriz de co-ocurrencia
        cooccur = np.zeros((len(top_words), len(top_words)))
        for words in article_words:
            for i, w1 in enumerate(top_words):
                if w1 in words:
                    for j, w2 in enumerate(top_words):
                        if w2 in words:
                            cooccur[i][j] += 1

        fig, ax = plt.subplots(figsize=(12, 10))
        im = ax.imshow(cooccur, cmap='YlOrRd', aspect='auto')

        ax.set_xticks(range(len(top_words)))
        ax.set_yticks(range(len(top_words)))
        ax.set_xticklabels(top_words, rotation=45, ha='right')
        ax.set_yticklabels(top_words)
        ax.set_title('Mapa de Co-ocurrencia de Términos', fontsize=14, fontweight='bold')

        # Añadir valores
        for i in range(len(top_words)):
            for j in range(len(top_words)):
                text = ax.text(j, i, int(cooccur[i, j]), ha='center', va='center',
                              color='white' if cooccur[i, j] > cooccur.max() / 2 else 'black',
                              fontsize=8)

        plt.colorbar(im, ax=ax, label='Co-ocurrencias')
        plt.tight_layout()

        output_file = self.output_path / filename
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file

    def generate_wordcloud(self, filename: str = "wordcloud.png") -> Path:
        """Nube de palabras de títulos y abstracts."""
        try:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
        except ImportError:
            logger.warning("wordcloud no instalado. Instálalo: pip install wordcloud")
            return None

        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                     'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                     'this', 'that', 'these', 'those', 'study', 'effect', 'effects', 'using', 'use', 'used',
                     'analysis', 'based', 'results', 'show', 'showed', 'found', 'between', 'among'}

        text = ""
        for a in self.articles:
            text += f" {a.get('title', '')} {a.get('abstract', '')}"

        text = text.lower()
        text = re.sub(r'[^a-z\s]', ' ', text)

        wordcloud = WordCloud(
            width=1200, height=600,
            background_color='white',
            stopwords=stopwords,
            max_words=100,
            colormap='viridis',
            relative_scaling=0.5
        ).generate(text)

        fig, ax = plt.subplots(figsize=(14, 7))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Nube de Palabras - Títulos y Abstracts', fontsize=14, fontweight='bold')

        plt.tight_layout()
        output_file = self.output_path / filename
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        return output_file

    def generate_full_report(self) -> Dict[str, Path]:
        """Genera todos los análisis y gráficos."""
        self.calculate_basic_metrics()

        results = {}

        try:
            results['publications_by_year'] = self.plot_publications_by_year()
        except Exception as e:
            logger.error(f"Error en publicaciones por año: {e}")

        try:
            results['top_authors'] = self.plot_top_authors()
        except Exception as e:
            logger.error(f"Error en top autores: {e}")

        try:
            results['top_journals'] = self.plot_top_journals()
        except Exception as e:
            logger.error(f"Error en top journals: {e}")

        try:
            results['citation_distribution'] = self.plot_citation_distribution()
        except Exception as e:
            logger.error(f"Error en distribución de citaciones: {e}")

        try:
            results['coauthorship_network'] = self.plot_coauthorship_network()
        except Exception as e:
            logger.error(f"Error en red de co-autoría: {e}")

        try:
            results['keyword_cooccurrence'] = self.plot_keyword_cooccurrence()
        except Exception as e:
            logger.error(f"Error en co-ocurrencia: {e}")

        try:
            results['wordcloud'] = self.generate_wordcloud()
        except Exception as e:
            logger.error(f"Error en wordcloud: {e}")

        # Guardar métricas
        metrics_file = self.output_path / 'bibliometric_metrics.json'
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        results['metrics'] = metrics_file

        logger.info(f"Reporte bibliométrico completo generado: {len(results)} gráficos")
        return results
