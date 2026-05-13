"""
PipelineSetup - Creación de estructura de carpetas para revisiones sistemáticas
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PipelineSetup:
    """Crea y gestiona la estructura de carpetas del pipeline."""

    DEFAULT_STRUCTURE = {
        'data_collection': {
            '1_pubmed': '1_pubmed_search',
            '2_europe_pmc': '2_europe_pmc_search',
            '3_crossref': '3_crossref_search',
            '4_semantic_scholar': '4_semantic_scholar_search',
            '5_openalex': '5_openalex_search',
            '6_scopus': '6_scopus_search'
        },
        'data_processing': {
            '7_unified': '7_unification_deduplication',
            '8_initial_filter': '8_initial_filter',
            '9_downloads': '9_article_downloads',
            '10_abstracts': '10_abstract_extraction',
            '11_fulltext': '11_fulltext_processing'
        },
        'analysis_visualization': {
            '12_sorted': '12_research_goal_sorting',
            '13_prisma': '13_prisma_visualization',
            '14_bibliometrics': '14_bibliometric_analysis',
            '15_reports': '15_final_reports'
        }
    }

    def __init__(
        self,
        project_name: str,
        base_path: str = "./literature_reviews",
        structure: Optional[Dict] = None,
        api_keys: Optional[Dict] = None
    ):
        self.project_name = self._sanitize_name(project_name)
        self.base_path = Path(base_path).resolve()
        self.master_folder = self.base_path / self.project_name
        self.structure = structure or self.DEFAULT_STRUCTURE
        self.api_keys = api_keys or {}
        self.paths = {}

    @staticmethod
    def _sanitize_name(name: str) -> str:
        """Limpia el nombre para uso en filesystem."""
        return "".join(c if c.isalnum() or c in ('_', '-', ' ') else '_' for c in name).strip()

    def create_folders(self) -> Dict[str, Path]:
        """Crea toda la estructura de carpetas."""
        logger.info(f"Creando proyecto: {self.project_name}")

        for category, steps in self.structure.items():
            category_path = self.master_folder / category
            category_path.mkdir(parents=True, exist_ok=True)

            for step_key, step_name in steps.items():
                step_path = category_path / step_name
                step_path.mkdir(parents=True, exist_ok=True)
                self.paths[step_key] = step_path

        return self.paths

    def generate_readme(self) -> None:
        """Genera README.md dinámico."""
        lines = [f"# {self.project_name}", ""]

        for category, steps in self.structure.items():
            lines.append(f"## {category.replace('_', ' ').title()}")
            for step_name in steps.values():
                lines.append(f"- `{step_name}/`")
            lines.append("")

        lines.extend([
            "## Pipeline",
            "```",
            "data_collection → data_processing → analysis_visualization",
            "```",
            "",
            f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])

        readme_path = self.master_folder / "README.md"
        readme_path.write_text("\n".join(lines), encoding='utf-8')

    def generate_config(self) -> None:
        """Guarda configuración como JSON."""
        config = {
            'project_name': self.project_name,
            'master_folder': str(self.master_folder),
            'structure': self.structure,
            'paths': {k: str(v) for k, v in self.paths.items()},
            'created': datetime.now().isoformat(),
            'version': '2.0.0'
        }

        config_path = self.master_folder / 'pipeline_config.json'
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def create_env_template(self) -> None:
        """Crea plantilla .env.template."""
        env_content = """# API Keys - Copy to .env and fill values
SEMANTIC_SCHOLAR_API_KEY=
ENTREZ_EMAIL=
NCBI_API_KEY=
SCOPUS_API_KEY=
OPENALEX_EMAIL=
"""
        env_path = self.master_folder / '.env.template'
        env_path.write_text(env_content, encoding='utf-8')

    def run(self) -> Dict[str, Path]:
        """Ejecuta el setup completo."""
        self.create_folders()
        self.generate_readme()
        self.generate_config()
        self.create_env_template()
        return self.paths
