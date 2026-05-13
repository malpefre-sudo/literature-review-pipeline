#!/usr/bin/env python3
"""
run.py - Ejecución directa vía línea de comandos (alternativa a Streamlit)

Uso:
    python run.py --config config.json
    python run.py --project-name "MiReview" --databases pubmed crossref --query "cancer immunotherapy"
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent))

from pipeline_setup import PipelineSetup
from config_manager import ConfigManager
from utils import generate_query_from_concepts

# Importar buscadores
from search_pubmed import SearchPubMed
from search_semantic_scholar import SearchSemanticScholar
from search_crossref import SearchCrossRef
from search_europe_pmc import SearchEuropePMC
from search_openalex import SearchOpenAlex
from search_scopus import SearchScopus


SEARCHERS = {
    'pubmed': SearchPubMed,
    'semantic_scholar': SearchSemanticScholar,
    'crossref': SearchCrossRef,
    'europe_pmc': SearchEuropePMC,
    'openalex': SearchOpenAlex,
    'scopus': SearchScopus
}


def main():
    parser = argparse.ArgumentParser(
        description="Literature Review Pipeline - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Setup + búsqueda completa
  python run.py --project-name "BaP_Review" --databases pubmed crossref openalex --query "benzo[a]pyrene respiratory toxicity"

  # Solo setup
  python run.py --project-name "NewReview" --setup-only

  # Desde config
  python run.py --config mi_config.json
        """
    )

    parser.add_argument('--project-name', '-p', type=str, help='Nombre del proyecto')
    parser.add_argument('--base-path', '-b', type=str, default='./literature_reviews')
    parser.add_argument('--databases', '-d', nargs='+', choices=list(SEARCHERS.keys()),
                        help='Bases de datos a usar')
    parser.add_argument('--query', '-q', type=str, help='Query de búsqueda')
    parser.add_argument('--max-results', '-m', type=int, default=100)
    parser.add_argument('--config', '-c', type=str, help='Archivo de configuración JSON')
    parser.add_argument('--setup-only', action='store_true', help='Solo crear estructura')
    parser.add_argument('--api-keys', '-k', type=str, help='Archivo .env con API keys')

    args = parser.parse_args()

    # Cargar config si se proporciona
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
        project_name = config.get('project_name', args.project_name)
        base_path = config.get('base_path', args.base_path)
        databases = config.get('selected_databases', args.databases)
        query = config.get('keywords', {}).get('query', args.query)
        api_keys = config.get('api_keys', {})
    else:
        if not args.project_name:
            parser.error("--project-name requerido (o usa --config)")
        project_name = args.project_name
        base_path = args.base_path
        databases = args.databases or []
        query = args.query
        api_keys = {}

    # Setup
    print(f"\n🏗️  Creando proyecto: {project_name}")
    setup = PipelineSetup(project_name=project_name, base_path=base_path)
    paths = setup.run()

    if args.setup_only:
        print("✅ Setup completado. Estructura creada.")
        return

    if not databases:
        parser.error("--databases requerido para búsqueda")
    if not query:
        parser.error("--query requerido para búsqueda")

    # Ejecutar búsquedas
    print(f"\n🔍 Query: {query}")
    print(f"🗄️  Bases de datos: {', '.join(databases)}\n")

    for db_name in databases:
        if db_name not in SEARCHERS:
            print(f"⚠️  Base de datos no soportada: {db_name}")
            continue

        searcher_class = SEARCHERS[db_name]
        output_path = paths.get(f'1_{db_name}', paths.get(f'2_{db_name}', paths.get(f'3_{db_name}', 
                              paths.get(f'4_{db_name}', paths.get(f'5_{db_name}', paths.get(f'6_{db_name}'))))))

        if not output_path:
            output_path = Path(base_path) / project_name / 'data_collection' / f'{db_name}_search'
            output_path.mkdir(parents=True, exist_ok=True)

        print(f"🔎 Buscando en {db_name}...")

        try:
            searcher = searcher_class(api_keys=api_keys, output_path=Path(output_path))
            results = searcher.search(query=query, max_results=args.max_results)
            print(f"   ✅ {len(results)} resultados guardados en {output_path}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n🎉 Pipeline completado!")


if __name__ == "__main__":
    main()
