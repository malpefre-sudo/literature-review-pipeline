"""
PRISMAGenerator - Generación del diagrama de flujo PRISMA 2020

Crea diagramas de flujo estandarizados para revisiones sistemáticas
mostrando: identificación → screening → elegibilidad → inclusión.

Soporta salida como imagen PNG/SVG o HTML interactivo.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PRISMAGenerator:
    """Genera diagramas PRISMA 2020 a partir de conteos de artículos."""

    # Etiquetas estándar PRISMA 2020
    DEFAULT_LABELS = {
        'identification': {
            'records_databases': 'Registros identificados de bases de datos',
            'records_registers': 'Registros identificados de registros web',
            'records_other': 'Registros de otras fuentes',
            'records_total': 'Total de registros identificados',
            'duplicates': 'Registros duplicados eliminados'
        },
        'screening': {
            'records_screened': 'Registros screening (títulos/abstracts)',
            'records_excluded': 'Registros excluidos en screening',
            'fulltext_assessed': 'Artículos evaluados en texto completo',
            'fulltext_excluded': 'Artículos excluidos en texto completo'
        },
        'included': {
            'qualitative': 'Incluidos en síntesis cualitativa',
            'quantitative': 'Incluidos en meta-análisis (síntesis cuantitativa)'
        }
    }

    def __init__(self, output_path: Path, labels: Optional[Dict] = None):
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.labels = labels or self.DEFAULT_LABELS
        self.counts = {}

    def set_counts(self, counts: Dict[str, int]) -> None:
        """
        Establece conteos para cada etapa.

        Args:
            counts: Dict con claves como:
                - records_databases, records_registers, records_other
                - duplicates_removed
                - records_screened, records_excluded_titles
                - fulltext_assessed, fulltext_excluded
                - included_qualitative, included_quantitative
        """
        self.counts = counts

    def generate_matplotlib(self, filename: str = "prisma_diagram.png") -> Path:
        """Genera diagrama PRISMA como imagen usando matplotlib."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
        except ImportError:
            logger.error("matplotlib no está instalado. Instálalo: pip install matplotlib")
            raise

        fig, ax = plt.subplots(1, 1, figsize=(14, 18))
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 20)
        ax.axis('off')

        # Colores PRISMA
        color_id = '#E8F4FD'      # Azul claro - Identificación
        color_screen = '#FFF3E0'  # Naranja claro - Screening
        color_elig = '#F3E5F5'    # Morado claro - Elegibilidad
        color_incl = '#E8F5E9'    # Verde claro - Inclusión

        def draw_box(x, y, w, h, text, count, color, fontsize=10):
            box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                facecolor=color, edgecolor='#333', linewidth=1.5)
            ax.add_patch(box)
            label = f"{text}\n(n = {count})"
            ax.text(x + w/2, y + h/2, label, ha='center', va='center',
                   fontsize=fontsize, fontweight='bold', wrap=True)

        def draw_arrow(x1, y1, x2, y2, label=""):
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle="->", color='#555', lw=2))
            if label:
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                ax.text(mid_x + 0.3, mid_y, label, fontsize=9, color='#666')

        # ===== IDENTIFICACIÓN =====
        ax.text(7, 19.5, 'IDENTIFICACIÓN', fontsize=14, fontweight='bold', 
               ha='center', color='#1565C0')

        # Fuentes de registros
        y_start = 17.5
        sources = [
            ('records_databases', 2, 15.5),
            ('records_registers', 6, 15.5),
            ('records_other', 10, 15.5)
        ]

        for key, x, y in sources:
            count = self.counts.get(key, 0)
            if count > 0:
                label = self.labels['identification'].get(key, key)
                draw_box(x, y, 3, 1.5, label, count, color_id, 8)

        # Total identificados
        total_id = (self.counts.get('records_databases', 0) + 
                   self.counts.get('records_registers', 0) + 
                   self.counts.get('records_other', 0))
        draw_box(5.5, 13, 3, 1.5, 
                self.labels['identification']['records_total'], 
                total_id, color_id)

        # Duplicados
        dup = self.counts.get('duplicates_removed', 0)
        if dup > 0:
            draw_box(10, 13, 3, 1.5,
                    self.labels['identification']['duplicates'],
                    dup, '#FFEBEE')
            draw_arrow(8.5, 13.75, 10, 13.75, f"-{dup}")

        # ===== SCREENING =====
        ax.text(7, 11.5, 'SCREENING', fontsize=14, fontweight='bold',
               ha='center', color='#E65100')

        screened = self.counts.get('records_screened', total_id - dup)
        draw_box(5.5, 9.5, 3, 1.5,
                self.labels['screening']['records_screened'],
                screened, color_screen)

        # Excluidos en screening
        excl_screen = self.counts.get('records_excluded_titles', 0)
        if excl_screen > 0:
            draw_box(10, 9.5, 3, 1.5,
                    self.labels['screening']['records_excluded'],
                    excl_screen, '#FFEBEE')
            draw_arrow(8.5, 10.25, 10, 10.25, f"-{excl_screen}")

        # ===== ELEGIBILIDAD =====
        ax.text(7, 8, 'ELEGIBILIDAD', fontsize=14, fontweight='bold',
               ha='center', color='#6A1B9A')

        fulltext = self.counts.get('fulltext_assessed', screened - excl_screen)
        draw_box(5.5, 6, 3, 1.5,
                self.labels['screening']['fulltext_assessed'],
                fulltext, color_elig)

        # Excluidos en fulltext
        excl_full = self.counts.get('fulltext_excluded', 0)
        if excl_full > 0:
            draw_box(10, 6, 3, 1.5,
                    self.labels['screening']['fulltext_excluded'],
                    excl_full, '#FFEBEE')
            draw_arrow(8.5, 6.75, 10, 6.75, f"-{excl_full}")

        # ===== INCLUSIÓN =====
        ax.text(7, 4.5, 'INCLUSIÓN', fontsize=14, fontweight='bold',
               ha='center', color='#2E7D32')

        qual = self.counts.get('included_qualitative', fulltext - excl_full)
        draw_box(3, 2.5, 4, 1.5,
                self.labels['included']['qualitative'],
                qual, color_incl)

        quant = self.counts.get('included_quantitative', 0)
        if quant > 0:
            draw_box(8, 2.5, 4, 1.5,
                    self.labels['included']['quantitative'],
                    quant, color_incl)

        # Flechas principales
        draw_arrow(7, 13, 7, 11)
        draw_arrow(7, 9.5, 7, 7.5)
        draw_arrow(7, 6, 7, 4)

        plt.tight_layout()
        output_file = self.output_path / filename
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        logger.info(f"Diagrama PRISMA guardado: {output_file}")
        return output_file

    def generate_html(self, filename: str = "prisma_diagram.html") -> Path:
        """Genera diagrama PRISMA como HTML interactivo."""

        total_id = (self.counts.get('records_databases', 0) + 
                   self.counts.get('records_registers', 0) + 
                   self.counts.get('records_other', 0))
        dup = self.counts.get('duplicates_removed', 0)
        screened = self.counts.get('records_screened', total_id - dup)
        excl_screen = self.counts.get('records_excluded_titles', 0)
        fulltext = self.counts.get('fulltext_assessed', screened - excl_screen)
        excl_full = self.counts.get('fulltext_excluded', 0)
        qual = self.counts.get('included_qualitative', fulltext - excl_full)
        quant = self.counts.get('included_quantitative', 0)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Diagrama PRISMA 2020 - {self.counts.get('project_name', 'Review')}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ text-align: center; color: #333; }}
        .prisma-box {{ border: 2px solid #333; border-radius: 8px; padding: 15px; margin: 10px; text-align: center; min-width: 180px; }}
        .identification {{ background: #E3F2FD; border-color: #1565C0; }}
        .screening {{ background: #FFF3E0; border-color: #E65100; }}
        .eligibility {{ background: #F3E5F5; border-color: #6A1B9A; }}
        .included {{ background: #E8F5E9; border-color: #2E7D32; }}
        .excluded {{ background: #FFEBEE; border-color: #C62828; }}
        .row {{ display: flex; justify-content: center; align-items: center; margin: 15px 0; flex-wrap: wrap; }}
        .arrow {{ font-size: 24px; color: #555; margin: 0 15px; }}
        .arrow-down {{ writing-mode: vertical-rl; margin: 5px 0; }}
        .count {{ font-size: 1.4em; font-weight: bold; color: #333; }}
        .label {{ font-size: 0.9em; color: #555; margin-top: 5px; }}
        .section-title {{ font-size: 1.2em; font-weight: bold; text-align: center; margin: 20px 0 10px 0; }}
        .id-title {{ color: #1565C0; }}
        .scr-title {{ color: #E65100; }}
        .elig-title {{ color: #6A1B9A; }}
        .inc-title {{ color: #2E7D32; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f0f0f0; font-weight: bold; }}
        .timestamp {{ text-align: center; color: #999; margin-top: 20px; font-size: 0.85em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Diagrama de Flujo PRISMA 2020</h1>
        <p style="text-align:center; color:#666;">Revisión sistemática: {self.counts.get('project_name', 'Sin nombre')}</p>

        <div class="section-title id-title">🔍 IDENTIFICACIÓN</div>
        <div class="row">
            <div class="prisma-box identification">
                <div class="count">{self.counts.get('records_databases', 0)}</div>
                <div class="label">Bases de datos</div>
            </div>
            <div class="prisma-box identification">
                <div class="count">{self.counts.get('records_registers', 0)}</div>
                <div class="label">Registros web</div>
            </div>
            <div class="prisma-box identification">
                <div class="count">{self.counts.get('records_other', 0)}</div>
                <div class="label">Otras fuentes</div>
            </div>
        </div>

        <div class="row">
            <div class="arrow arrow-down">⬇</div>
        </div>

        <div class="row">
            <div class="prisma-box identification">
                <div class="count">{total_id}</div>
                <div class="label">Total registros identificados</div>
            </div>
            <div class="arrow">→</div>
            <div class="prisma-box excluded">
                <div class="count">-{dup}</div>
                <div class="label">Duplicados eliminados</div>
            </div>
        </div>

        <div class="section-title scr-title">🔎 SCREENING</div>
        <div class="row">
            <div class="arrow arrow-down">⬇</div>
        </div>

        <div class="row">
            <div class="prisma-box screening">
                <div class="count">{screened}</div>
                <div class="label">Registros screening (títulos/abstracts)</div>
            </div>
            <div class="arrow">→</div>
            <div class="prisma-box excluded">
                <div class="count">-{excl_screen}</div>
                <div class="label">Excluidos en screening</div>
            </div>
        </div>

        <div class="section-title elig-title">📋 ELEGIBILIDAD</div>
        <div class="row">
            <div class="arrow arrow-down">⬇</div>
        </div>

        <div class="row">
            <div class="prisma-box eligibility">
                <div class="count">{fulltext}</div>
                <div class="label">Artículos evaluados en texto completo</div>
            </div>
            <div class="arrow">→</div>
            <div class="prisma-box excluded">
                <div class="count">-{excl_full}</div>
                <div class="label">Excluidos en texto completo</div>
            </div>
        </div>

        <div class="section-title inc-title">✅ INCLUSIÓN</div>
        <div class="row">
            <div class="arrow arrow-down">⬇</div>
        </div>

        <div class="row">
            <div class="prisma-box included">
                <div class="count">{qual}</div>
                <div class="label">Incluidos en síntesis cualitativa</div>
            </div>
            {'<div class="prisma-box included"><div class="count">' + str(quant) + '</div><div class="label">Incluidos en meta-análisis</div></div>' if quant > 0 else ''}
        </div>

        <div class="timestamp">
            Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Literature Review Pipeline
        </div>
    </div>
</body>
</html>"""

        output_file = self.output_path / filename
        output_file.write_text(html, encoding='utf-8')
        logger.info(f"PRISMA HTML guardado: {output_file}")
        return output_file

    def generate_json_report(self, filename: str = "prisma_data.json") -> Path:
        """Guarda los datos PRISMA en JSON para otros usos."""
        data = {
            'prisma_version': '2020',
            'generated_at': datetime.now().isoformat(),
            'counts': self.counts,
            'labels': self.labels
        }

        output_file = self.output_path / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return output_file
