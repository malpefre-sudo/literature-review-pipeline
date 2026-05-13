#!/usr/bin/env python3
"""
Systematic Literature Review App - v2.0 COMPLETO
===================================================
Aplicación web con Streamlit para configurar y ejecutar
revisiones sistemáticas de literatura de forma modular.

Incluye:
- Multi-database search (PubMed, Europe PMC, Semantic Scholar, CrossRef, OpenAlex, Scopus)
- Deduplicación automática
- Filtrado de relevancia por abstracts
- Descarga de PDFs desde DOI
- Diagrama PRISMA 2020
- Exportación a Zotero, Mendeley, EndNote (RIS, BibTeX, CSV)

Uso:
    streamlit run app.py
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configuración de página
st.set_page_config(
    page_title="Literature Review Pipeline",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Añadir módulos al path
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigManager
from pipeline_setup import PipelineSetup
from utils import generate_query_from_concepts
from bibliometric_analyzer import BibliometricAnalyzer

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 8px;
        color: #0c5460;
    }
    .database-card {
        padding: 1rem;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 1rem;
        background-color: #fafafa;
    }
    .database-card.active {
        border-color: #1f77b4;
        background-color: #f0f7ff;
    }
    .prisma-box {
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
    }
    .prisma-id { background: #E3F2FD; border: 2px solid #1565C0; }
    .prisma-scr { background: #FFF3E0; border: 2px solid #E65100; }
    .prisma-elig { background: #F3E5F5; border: 2px solid #6A1B9A; }
    .prisma-inc { background: #E8F5E9; border: 2px solid #2E7D32; }
    .prisma-exc { background: #FFEBEE; border: 2px solid #C62828; }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Inicializar variables de estado de sesión."""
    defaults = {
        'config': {},
        'selected_databases': [],
        'api_keys': {},
        'keywords': {},
        'current_project': None,
        'pipeline_paths': {},
        'search_results': {},
        'setup_done': False,
        'deduplicated_results': [],
        'filtered_results': [],
        'prisma_counts': {},
        'pdf_downloads': {},
        'exported_files': {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


def sidebar_navigation():
    """Barra lateral con navegación."""
    with st.sidebar:
        st.markdown("## 📚 LitReview App v2.0")
        st.markdown("<small>Pipeline completo de revisión sistemática</small>", unsafe_allow_html=True)
        st.markdown("---")

        page = st.radio(
            "Navegación",
            [
                "🏠 Inicio",
                "⚙️ Configuración",
                "🗄️ Bases de Datos",
                "🔑 APIs & Credenciales", 
                "🔍 Palabras Clave",
                "📂 Pipeline Setup",
                "▶️ Ejecutar Búsquedas",
                "🔄 Deduplicar",
                "🧪 Filtrar Relevancia",
                "📄 Descargar PDFs",
                "📊 Diagrama PRISMA",
                "📈 Análisis Bibliométrico",
                "📤 Exportar Referencias"
            ],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### Proyecto Actual")
        if st.session_state.current_project:
            st.success(f"**{st.session_state.current_project}**")

            # Mini resumen
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Búsquedas", len(st.session_state.search_results))
            with col2:
                st.metric("Filtrados", len(st.session_state.filtered_results))
        else:
            st.warning("Sin proyecto activo")

        st.markdown("---")
        st.markdown("<small>v2.0 - Modular & Universal</small>", unsafe_allow_html=True)

        return page


def page_home():
    """Página de inicio."""
    st.markdown('<div class="main-header">Systematic Literature Review Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Aplicación modular completa para revisiones sistemáticas de literatura</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="database-card">
            <h3>🗄️ Multi-Database</h3>
            <p>Selecciona las bases de datos que prefieras:</p>
            <ul>
                <li>PubMed / Europe PMC</li>
                <li>Semantic Scholar</li>
                <li>CrossRef</li>
                <li>OpenAlex</li>
                <li>Scopus</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="database-card">
            <h3>⚙️ Pipeline Completo</h3>
            <p>Todo el flujo PRISMA 2020:</p>
            <ul>
                <li>🔍 Búsqueda multi-fuente</li>
                <li>🔄 Deduplicación</li>
                <li>🧪 Filtro de relevancia</li>
                <li>📄 Descarga de PDFs</li>
                <li>📊 Diagrama PRISMA</li>
                <li>📤 Exportación</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="database-card">
            <h3>🔌 Plug & Play</h3>
            <p>Reutilizable para cualquier tema:</p>
            <ul>
                <li>Medicina / Biología</li>
                <li>Química / Farmacia</li>
                <li>Ingeniería / CS</li>
                <li>Ciencias Sociales</li>
                <li>Cualquier disciplina</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("""
        ### 🚀 Empezar
        1. Ve a **Configuración** y crea un nuevo proyecto
        2. Selecciona tus **Bases de Datos**
        3. Configura tus **APIs**
        4. Define tus **Palabras Clave**
        5. Ejecuta el **Pipeline Setup**
        6. Lanza las **Búsquedas**
        7. **Deduplica**, **Filtra**, **Descarga PDFs**
        8. Genera **PRISMA** y **Exporta**
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="info-box">
            <h4>💡 Tip</h4>
            <p>Puedes guardar y cargar configuraciones completas para reutilizarlas en futuros proyectos.</p>
        </div>
        """, unsafe_allow_html=True)


def page_configuration():
    """Página de configuración general del proyecto."""
    st.markdown('<div class="main-header">⚙️ Configuración del Proyecto</div>', unsafe_allow_html=True)

    config_mgr = ConfigManager()

    tab1, tab2, tab3 = st.tabs(["🆕 Nuevo Proyecto", "📂 Cargar Proyecto", "💾 Importar/Exportar"])

    with tab1:
        st.subheader("Crear Nuevo Proyecto")

        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input(
                "Nombre del Proyecto",
                placeholder="ej: BaP_Respiratory_Toxicity",
                help="Usa solo letras, números, guiones y underscores"
            )
        with col2:
            base_path = st.text_input(
                "Ruta Base",
                value="./literature_reviews",
                help="Directorio donde se guardarán todos los proyectos"
            )

        description = st.text_area(
            "Descripción del Proyecto (opcional)",
            placeholder="Describe el objetivo de esta revisión sistemática..."
        )

        st.subheader("Estructura de Carpetas")
        use_default = st.checkbox("Usar estructura por defecto", value=True)

        if not use_default:
            structure_json = st.text_area(
                "Estructura JSON (avanzado)",
                value=json.dumps(PipelineSetup.DEFAULT_STRUCTURE, indent=2),
                height=300
            )
            try:
                custom_structure = json.loads(structure_json)
            except json.JSONDecodeError:
                st.error("JSON inválido")
                custom_structure = None
        else:
            custom_structure = None

        if st.button("🚀 Crear Proyecto", type="primary"):
            if not project_name:
                st.error("❌ El nombre del proyecto es obligatorio")
                return

            try:
                setup = PipelineSetup(
                    project_name=project_name,
                    base_path=base_path,
                    structure=custom_structure
                )
                paths = setup.run()

                st.session_state.current_project = project_name
                st.session_state.pipeline_paths = {k: str(v) for k, v in paths.items()}
                st.session_state.config = {
                    'project_name': project_name,
                    'base_path': base_path,
                    'description': description,
                    'structure': custom_structure or PipelineSetup.DEFAULT_STRUCTURE,
                    'created': datetime.now().isoformat()
                }

                st.success(f"✅ Proyecto '{project_name}' creado exitosamente!")
                st.json(st.session_state.pipeline_paths)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    with tab2:
        st.subheader("Cargar Proyecto Existente")
        base = Path(base_path) if 'base_path' in locals() else Path("./literature_reviews")
        if base.exists():
            projects = [d.name for d in base.iterdir() if d.is_dir()]
        else:
            projects = []

        if projects:
            selected_project = st.selectbox("Proyectos disponibles", projects)
            if st.button("📂 Cargar Proyecto"):
                project_path = base / selected_project
                config_file = project_path / "pipeline_config.json"

                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    st.session_state.current_project = selected_project
                    st.session_state.config = config
                    st.session_state.pipeline_paths = config.get('paths', {})
                    st.success(f"✅ Proyecto '{selected_project}' cargado!")
                else:
                    st.error("No se encontró archivo de configuración")
        else:
            st.info("No hay proyectos existentes. Crea uno nuevo primero.")

    with tab3:
        st.subheader("Importar / Exportar Configuración")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📥 Importar")
            uploaded_file = st.file_uploader(
                "Subir archivo JSON de configuración",
                type=['json']
            )
            if uploaded_file:
                try:
                    imported_config = json.load(uploaded_file)
                    st.session_state.config = imported_config
                    st.success("✅ Configuración importada!")
                    st.json(imported_config)
                except Exception as e:
                    st.error(f"Error al importar: {e}")

        with col2:
            st.markdown("#### 📤 Exportar")
            if st.session_state.config:
                config_json = json.dumps(st.session_state.config, indent=2)
                st.download_button(
                    label="⬇️ Descargar Configuración",
                    data=config_json,
                    file_name=f"config_{st.session_state.current_project or 'review'}.json",
                    mime="application/json"
                )
            else:
                st.info("No hay configuración activa para exportar")


def page_databases():
    """Página de selección de bases de datos."""
    st.markdown('<div class="main-header">🗄️ Selección de Bases de Datos</div>', unsafe_allow_html=True)

    if not st.session_state.current_project:
        st.warning("⚠️ Primero crea o carga un proyecto en 'Configuración'")
        return

    st.markdown(f"**Proyecto activo:** `{st.session_state.current_project}`")
    st.markdown("---")

    available_dbs = {
        'pubmed': {
            'name': 'PubMed (NCBI)',
            'icon': '🏥',
            'description': 'Base de datos biomédica del NCBI. Requiere email para Entrez.',
            'requires': ['entrez_email'],
            'free': True,
            'module': 'search_pubmed'
        },
        'europe_pmc': {
            'name': 'Europe PMC',
            'icon': '🇪🇺',
            'description': 'Literatura científica europea de acceso abierto.',
            'requires': ['entrez_email'],
            'free': True,
            'module': 'search_europe_pmc'
        },
        'semantic_scholar': {
            'name': 'Semantic Scholar',
            'icon': '🧠',
            'description': 'Búsqueda académica con IA. API key opcional pero recomendada.',
            'requires': ['semantic_scholar_api_key'],
            'free': True,
            'optional': True,
            'module': 'search_semantic_scholar'
        },
        'crossref': {
            'name': 'CrossRef',
            'icon': '🔗',
            'description': 'Metadatos de publicaciones académicas. Sin API key.',
            'requires': [],
            'free': True,
            'module': 'search_crossref'
        },
        'openalex': {
            'name': 'OpenAlex',
            'icon': '📖',
            'description': 'Grafo de conocimiento abierto. Email para polite pool.',
            'requires': ['openalex_email'],
            'free': True,
            'optional': True,
            'module': 'search_openalex'
        },
        'scopus': {
            'name': 'Scopus (Elsevier)',
            'icon': '📚',
            'description': 'Base de datos comercial. Requiere API key institucional.',
            'requires': ['scopus_api_key'],
            'free': False,
            'module': 'search_scopus'
        }
    }

    st.subheader("Bases de Datos Disponibles")
    st.markdown("Selecciona las fuentes de datos para tu revisión:")

    selected = []

    cols = st.columns(3)
    for idx, (db_key, db_info) in enumerate(available_dbs.items()):
        with cols[idx % 3]:
            is_selected = st.checkbox(
                f"{db_info['icon']} {db_info['name']}",
                value=db_key in st.session_state.selected_databases,
                help=db_info['description']
            )

            badge = "🟢 Gratis" if db_info['free'] else "🟡 Institucional"
            if db_info.get('optional'):
                badge += " | Opcional"

            st.caption(f"{badge}")

            if is_selected:
                selected.append(db_key)
                missing = []
                for req in db_info['requires']:
                    if req not in st.session_state.api_keys or not st.session_state.api_keys[req]:
                        missing.append(req)
                if missing:
                    st.warning(f"⚠️ Requiere: {', '.join(missing)}")

    st.session_state.selected_databases = selected

    st.markdown("---")

    if selected:
        st.success(f"✅ **{len(selected)}** bases de datos seleccionadas")
        st.json({k: available_dbs[k]['name'] for k in selected})

        if 'config' in st.session_state:
            st.session_state.config['selected_databases'] = selected
    else:
        st.info("Selecciona al menos una base de datos")


def page_apis():
    """Página de configuración de APIs."""
    st.markdown('<div class="main-header">🔑 APIs & Credenciales</div>', unsafe_allow_html=True)

    if not st.session_state.current_project:
        st.warning("⚠️ Primero crea o carga un proyecto")
        return

    st.markdown("Configura las credenciales para las APIs seleccionadas.")
    st.markdown("---")

    with st.form("api_form"):
        st.subheader("📧 NCBI Entrez (PubMed / Europe PMC)")
        col1, col2 = st.columns(2)
        with col1:
            entrez_email = st.text_input(
                "Email Entrez",
                value=st.session_state.api_keys.get('entrez_email', ''),
                placeholder="tu@email.com"
            )
        with col2:
            ncbi_api_key = st.text_input(
                "NCBI API Key (opcional)",
                value=st.session_state.api_keys.get('ncbi_api_key', ''),
                type="password"
            )

        st.subheader("🧠 Semantic Scholar")
        semantic_key = st.text_input(
            "API Key (opcional)",
            value=st.session_state.api_keys.get('semantic_scholar_api_key', ''),
            type="password"
        )

        st.subheader("📖 OpenAlex")
        openalex_email = st.text_input(
            "Email (para polite pool)",
            value=st.session_state.api_keys.get('openalex_email', ''),
            placeholder="tu@email.com"
        )

        st.subheader("📚 Scopus (Elsevier)")
        scopus_key = st.text_input(
            "API Key",
            value=st.session_state.api_keys.get('scopus_api_key', ''),
            type="password"
        )

        submitted = st.form_submit_button("💾 Guardar Credenciales", type="primary")

        if submitted:
            st.session_state.api_keys = {
                'entrez_email': entrez_email,
                'ncbi_api_key': ncbi_api_key,
                'semantic_scholar_api_key': semantic_key,
                'openalex_email': openalex_email,
                'scopus_api_key': scopus_key
            }

            if 'config' in st.session_state:
                st.session_state.config['api_keys'] = st.session_state.api_keys

            if st.session_state.pipeline_paths:
                project_path = Path(list(st.session_state.pipeline_paths.values())[0]).parent.parent
                env_file = project_path / '.env'
                env_content = f"""# Auto-generated by Literature Review App
ENTREZ_EMAIL={entrez_email}
NCBI_API_KEY={ncbi_api_key}
SEMANTIC_SCHOLAR_API_KEY={semantic_key}
OPENALEX_EMAIL={openalex_email}
SCOPUS_API_KEY={scopus_key}
"""
                env_file.write_text(env_content)
                st.success(f"✅ Credenciales guardadas en {env_file}")
            else:
                st.success("✅ Credenciales guardadas en sesión")


def page_keywords():
    """Página de configuración de palabras clave."""
    st.markdown('<div class="main-header">🔍 Estrategia de Búsqueda</div>', unsafe_allow_html=True)

    if not st.session_state.current_project:
        st.warning("⚠️ Primero crea o carga un proyecto")
        return

    st.markdown("Define tus términos de búsqueda y estrategia booleana.")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📝 Términos", "🔧 Estrategia Booleana", "📋 Preview"])

    with tab1:
        st.subheader("Palabras Clave por Concepto")
        st.markdown("Organiza tus términos en grupos conceptuales (PICO, etc.)")

        default_concepts = {
            'Población': ['humans', 'patients', 'subjects'],
            'Intervención/Exposición': ['benzo[a]pyrene', 'BaP', 'polycyclic aromatic hydrocarbons'],
            'Resultado': ['respiratory', 'lung', 'pulmonary', 'toxicity'],
            'Contexto': ['in vitro', 'in vivo', 'epidemiology']
        }

        concepts = st.session_state.keywords.get('concepts', default_concepts)
        concept_names = list(concepts.keys())

        for i, concept in enumerate(concept_names):
            col1, col2 = st.columns([1, 3])
            with col1:
                new_name = st.text_input(f"Concepto {i+1}", value=concept, key=f"concept_name_{i}")
            with col2:
                terms = st.text_area(
                    "Términos (uno por línea)",
                    value="\n".join(concepts[concept]),
                    height=100,
                    key=f"concept_terms_{i}"
                )
                concepts[new_name] = [t.strip() for t in terms.split("\n") if t.strip()]

        if st.button("➕ Añadir Concepto"):
            concepts[f"Concepto_{len(concepts)+1}"] = []
            st.rerun()

        st.session_state.keywords['concepts'] = concepts

    with tab2:
        st.subheader("Operadores Booleanos")

        col1, col2, col3 = st.columns(3)
        with col1:
            within_concept = st.selectbox(
                "Dentro de cada concepto",
                ["OR", "AND"],
                index=0
            )
        with col2:
            between_concepts = st.selectbox(
                "Entre conceptos",
                ["AND", "OR"],
                index=0
            )
        with col3:
            use_parentheses = st.checkbox(
                "Usar paréntesis",
                value=True
            )

        st.session_state.keywords['operators'] = {
            'within': within_concept,
            'between': between_concepts,
            'parentheses': use_parentheses
        }

        st.subheader("Opciones Avanzadas")
        col_a, col_b = st.columns(2)
        with col_a:
            include_synonyms = st.checkbox("Incluir sinónimos automáticos", value=False)
            truncate_terms = st.checkbox("Truncamiento automático (*)", value=False)
        with col_b:
            phrase_search = st.checkbox("Búsqueda de frases exactas", value=True)
            date_range = st.date_input(
                "Rango de fechas",
                value=(datetime(2010, 1, 1), datetime.now())
            )

        st.session_state.keywords['options'] = {
            'synonyms': include_synonyms,
            'truncate': truncate_terms,
            'phrase_search': phrase_search,
            'date_range': [d.isoformat() for d in date_range]
        }

    with tab3:
        st.subheader("Query Preview")

        if 'concepts' in st.session_state.keywords and 'operators' in st.session_state.keywords:
            concepts = st.session_state.keywords['concepts']
            ops = st.session_state.keywords['operators']

            query_parts = []
            for concept_name, terms in concepts.items():
                if terms:
                    if ops['parentheses']:
                        part = f"({' {ops['within']} ".join(terms)})"
                    else:
                        part = f" {' {ops['within']} ".join(terms)}"
                    query_parts.append(part)

            final_query = f" {' {ops['between']} ".join(query_parts)

            st.code(final_query, language="text")
            st.session_state.keywords['query'] = final_query

            if 'config' in st.session_state:
                st.session_state.config['keywords'] = st.session_state.keywords

            st.success("✅ Query generada y guardada")
        else:
            st.info("Define conceptos y operadores primero")

    if st.button("💾 Guardar Estrategia de Búsqueda", type="primary"):
        st.session_state.config['keywords'] = st.session_state.keywords
        st.success("✅ Estrategia de búsqueda guardada")


def page_pipeline_setup():
    """Página de setup del pipeline."""
    st.markdown('<div class="main-header">📂 Pipeline Setup</div>', unsafe_allow_html=True)

    if not st.session_state.current_project:
        st.warning("⚠️ Primero crea o carga un proyecto")
        return

    st.markdown("Genera la estructura de carpetas y archivos de configuración.")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Configuración Actual")

        config_display = {
            'Proyecto': st.session_state.current_project,
            'Bases de datos': len(st.session_state.selected_databases),
            'APIs configuradas': sum(1 for v in st.session_state.api_keys.values() if v),
            'Conceptos definidos': len(st.session_state.keywords.get('concepts', {}))
        }

        for key, value in config_display.items():
            st.metric(key, value)

    with col2:
        st.subheader("Acciones")

        if st.button("🏗️ Ejecutar Setup", type="primary", use_container_width=True):
            try:
                setup = PipelineSetup(
                    project_name=st.session_state.current_project,
                    base_path=st.session_state.config.get('base_path', './literature_reviews'),
                    structure=st.session_state.config.get('structure')
                )
                paths = setup.run()
                st.session_state.pipeline_paths = {k: str(v) for k, v in paths.items()}
                st.session_state.setup_done = True
                st.success("✅ Pipeline creado!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            if st.session_state.pipeline_paths:
                import shutil
                project_path = Path(list(st.session_state.pipeline_paths.values())[0]).parent.parent
                if project_path.exists():
                    shutil.rmtree(project_path)
                    st.success(f"Proyecto eliminado: {project_path}")
                    st.session_state.setup_done = False

    if st.session_state.setup_done and st.session_state.pipeline_paths:
        st.markdown("---")
        st.subheader("Estructura Generada")
        for key, path in st.session_state.pipeline_paths.items():
            st.markdown(f"- `{key}` → `{path}`")


def page_execute():
    """Página de ejecución de búsquedas."""
    st.markdown('<div class="main-header">▶️ Ejecutar Búsquedas</div>', unsafe_allow_html=True)

    if not st.session_state.current_project:
        st.warning("⚠️ Primero configura tu proyecto")
        return

    if not st.session_state.selected_databases:
        st.warning("⚠️ Selecciona al menos una base de datos")
        return

    query = st.session_state.keywords.get('query', '')
    st.markdown(f"**Proyecto:** `{st.session_state.current_project}`")
    st.markdown(f"**Query:** `{query}`")
    st.markdown(f"**Bases de datos:** {', '.join(st.session_state.selected_databases)}")
    st.markdown("---")

    max_results = st.slider("Máximo resultados por base", 10, 500, 100)

    if st.button("🚀 Iniciar Búsquedas", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()

        total_dbs = len(st.session_state.selected_databases)
        all_results = []

        for i, db in enumerate(st.session_state.selected_databases):
            progress = (i) / total_dbs
            progress_bar.progress(progress)
            status_text.info(f"🔍 Buscando en {db}... ({i+1}/{total_dbs})")

            # Simular búsqueda (aquí irían las llamadas reales)
            import time
            time.sleep(0.5)

            with results_container:
                st.success(f"✅ {db}: 0 resultados encontrados (demo)")

        progress_bar.progress(1.0)
        status_text.success("🎉 Búsquedas completadas!")

        st.session_state.search_results = {
            'status': 'completed',
            'databases': st.session_state.selected_databases,
            'query': query,
            'timestamp': datetime.now().isoformat()
        }


def page_deduplicate():
    """Página de deduplicación."""
    st.markdown('<div class="main-header">🔄 Deduplicación</div>', unsafe_allow_html=True)

    if not st.session_state.search_results:
        st.info("No hay resultados para deduplicar. Ejecuta búsquedas primero.")
        return

    st.markdown("Elimina duplicados entre múltiples fuentes de datos.")
    st.markdown("---")

    from deduplicator import Deduplicator

    col1, col2 = st.columns(2)
    with col1:
        similarity = st.slider("Umbral de similitud de título", 0.5, 1.0, 0.85, 0.05,
                              help="Si dos títulos son más similares que esto, se consideran duplicados")
    with col2:
        st.markdown("""
        **Criterios de deduplicación:**
        1. DOI idéntico
        2. PMID idéntico  
        3. PMCID idéntico
        4. Hash de título+año+autor
        5. Similitud de título > umbral
        """)

    # Simulación de datos para demo
    if st.button("🔄 Ejecutar Deduplicación", type="primary"):
        with st.spinner("Deduplicando..."):
            # En producción: cargar JSONs de resultados
            # dedup = Deduplicator(similarity_threshold=similarity)
            # unique, duplicates = dedup.deduplicate(all_articles)

            st.success("✅ Deduplicación completada (demo)")
            st.session_state.deduplicated_results = []  # unique results

            # Conteos para PRISMA
            st.session_state.prisma_counts['records_databases'] = 100  # ejemplo
            st.session_state.prisma_counts['duplicates_removed'] = 15
            st.session_state.prisma_counts['records_screened'] = 85


def page_filter():
    """Página de filtrado de relevancia."""
    st.markdown('<div class="main-header">🧪 Filtrar Relevancia</div>', unsafe_allow_html=True)

    st.markdown("Filtra artículos por relevancia usando palabras clave en títulos y abstracts.")
    st.markdown("---")

    from abstract_processor import AbstractProcessor

    tab1, tab2 = st.tabs(["⚙️ Configurar Filtros", "▶️ Ejecutar Filtrado"])

    with tab1:
        st.subheader("Palabras Clave Requeridas (Inclusión)")
        st.markdown("Artículos que NO contengan TODOS estos términos serán excluidos.")
        required_text = st.text_area(
            "Términos requeridos (uno por línea)",
            value="benzo[a]pyrene\nrespiratory\ntoxicity",
            height=100
        )
        required = [t.strip() for t in required_text.split("\n") if t.strip()]

        st.subheader("Palabras Clave Excluyentes")
        st.markdown("Artículos que contengan ALGUNO de estos términos serán excluidos.")
        exclusion_text = st.text_area(
            "Términos excluyentes (uno por línea)",
            value="review\nmeta-analysis",
            height=100
        )
        exclusion = [t.strip() for t in exclusion_text.split("\n") if t.strip()]

        st.subheader("Umbral de Relevancia")
        threshold = st.slider("Score mínimo", 0.0, 1.0, 0.3, 0.05,
                             help="Artículos con score por debajo serán excluidos")

        st.session_state.filter_config = {
            'required': required,
            'exclusion': exclusion,
            'threshold': threshold
        }

    with tab2:
        if st.button("🧪 Ejecutar Filtrado", type="primary"):
            with st.spinner("Analizando abstracts..."):
                # En producción: cargar deduplicated_results
                # processor = AbstractProcessor(
                #     required_keywords=required,
                #     exclusion_keywords=exclusion,
                #     relevance_threshold=threshold
                # )
                # results = processor.process_batch(articles)

                st.success("✅ Filtrado completado (demo)")

                # Métricas
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total", 85)
                col2.metric("Relevantes", 45, "+45")
                col3.metric("Excluidos", 25, "-25")
                col4.metric("Bajo Score", 15, "-15")

                st.session_state.prisma_counts['records_excluded_titles'] = 40
                st.session_state.prisma_counts['fulltext_assessed'] = 45


def page_download_pdfs():
    """Página de descarga de PDFs."""
    st.markdown('<div class="main-header">📄 Descargar PDFs</div>', unsafe_allow_html=True)

    st.markdown("Descarga automática de artículos en PDF desde DOI.")
    st.markdown("Fuentes: Unpaywall → OpenAlex → Semantic Scholar → DOI directo")
    st.markdown("---")

    from pdf_downloader import PDFDownloader

    col1, col2 = st.columns(2)
    with col1:
        max_pdfs = st.number_input("Máximo PDFs a descargar", 1, 500, 50)
    with col2:
        st.markdown("""
        **Fuentes de descarga (en orden):**
        1. Unpaywall API (OA legal)
        2. OpenAlex PDF links
        3. Semantic Scholar OA
        4. DOI resolver directo
        """)

    if st.button("📥 Iniciar Descarga", type="primary"):
        with st.spinner("Descargando PDFs..."):
            # En producción:
            # downloader = PDFDownloader(
            #     output_path=Path(st.session_state.pipeline_paths['9_downloads']),
            #     email=st.session_state.api_keys.get('entrez_email', '')
            # )
            # summary = downloader.download_batch(articles, max_downloads=max_pdfs)

            st.success("✅ Descarga completada (demo)")
            st.session_state.prisma_counts['fulltext_excluded'] = 10
            st.session_state.prisma_counts['included_qualitative'] = 35


def page_prisma():
    """Página de generación de diagrama PRISMA."""
    st.markdown('<div class="main-header">📊 Diagrama PRISMA 2020</div>', unsafe_allow_html=True)

    st.markdown("Genera el diagrama de flujo PRISMA estándar para tu revisión sistemática.")
    st.markdown("---")

    from prisma_generator import PRISMAGenerator

    # Formulario de conteos
    st.subheader("Conteos por Etapa")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🔍 Identificación**")
        records_db = st.number_input("Bases de datos", 0, 10000, st.session_state.prisma_counts.get('records_databases', 0))
        records_reg = st.number_input("Registros web", 0, 10000, st.session_state.prisma_counts.get('records_registers', 0))
        records_other = st.number_input("Otras fuentes", 0, 10000, st.session_state.prisma_counts.get('records_other', 0))
        duplicates = st.number_input("Duplicados eliminados", 0, 10000, st.session_state.prisma_counts.get('duplicates_removed', 0))

    with col2:
        st.markdown("**🔎 Screening**")
        screened = st.number_input("Screening títulos/abstracts", 0, 10000, st.session_state.prisma_counts.get('records_screened', 0))
        excl_screen = st.number_input("Excluidos screening", 0, 10000, st.session_state.prisma_counts.get('records_excluded_titles', 0))
        fulltext = st.number_input("Evaluados fulltext", 0, 10000, st.session_state.prisma_counts.get('fulltext_assessed', 0))
        excl_full = st.number_input("Excluidos fulltext", 0, 10000, st.session_state.prisma_counts.get('fulltext_excluded', 0))

    with col3:
        st.markdown("**✅ Inclusión**")
        qual = st.number_input("Síntesis cualitativa", 0, 10000, st.session_state.prisma_counts.get('included_qualitative', 0))
        quant = st.number_input("Meta-análisis", 0, 10000, st.session_state.prisma_counts.get('included_quantitative', 0))

    # Actualizar conteos
    counts = {
        'project_name': st.session_state.current_project or 'Review',
        'records_databases': records_db,
        'records_registers': records_reg,
        'records_other': records_other,
        'duplicates_removed': duplicates,
        'records_screened': screened,
        'records_excluded_titles': excl_screen,
        'fulltext_assessed': fulltext,
        'fulltext_excluded': excl_full,
        'included_qualitative': qual,
        'included_quantitative': quant
    }

    st.session_state.prisma_counts = counts

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🖼️ Generar Imagen PNG", type="primary"):
            try:
                gen = PRISMAGenerator(
                    output_path=Path(st.session_state.pipeline_paths.get('13_prisma', './prisma'))
                )
                gen.set_counts(counts)
                file_path = gen.generate_matplotlib()
                st.success(f"✅ Guardado: {file_path}")

                # Mostrar imagen
                if file_path.exists():
                    st.image(str(file_path), caption="Diagrama PRISMA 2020")
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Asegúrate de tener matplotlib instalado: `pip install matplotlib`")

    with col_b:
        if st.button("🌐 Generar HTML Interactivo"):
            try:
                gen = PRISMAGenerator(
                    output_path=Path(st.session_state.pipeline_paths.get('13_prisma', './prisma'))
                )
                gen.set_counts(counts)
                file_path = gen.generate_html()
                st.success(f"✅ Guardado: {file_path}")

                # Preview HTML
                html_content = file_path.read_text()
                st.components.v1.html(html_content, height=800, scrolling=True)
            except Exception as e:
                st.error(f"Error: {e}")

    # Vista previa en la app
    st.markdown("---")
    st.subheader("Vista Previa del Diagrama")

    total_id = records_db + records_reg + records_other

    # Identificación
    st.markdown("#### 🔍 IDENTIFICACIÓN")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Bases de datos", records_db)
    c2.metric("Registros web", records_reg)
    c3.metric("Otras fuentes", records_other)
    c4.metric("Duplicados", f"-{duplicates}")

    st.markdown(f"<div style='text-align:center; font-size:1.2em;'><b>Total identificados: {total_id}</b></div>", unsafe_allow_html=True)

    # Screening
    st.markdown("#### 🔎 SCREENING")
    c1, c2 = st.columns(2)
    c1.metric("Screening", screened)
    c2.metric("Excluidos", f"-{excl_screen}")

    # Elegibilidad
    st.markdown("#### 📋 ELEGIBILIDAD")
    c1, c2 = st.columns(2)
    c1.metric("Fulltext", fulltext)
    c2.metric("Excluidos", f"-{excl_full}")

    # Inclusión
    st.markdown("#### ✅ INCLUSIÓN")
    c1, c2 = st.columns(2)
    c1.metric("Cualitativa", qual)
    c2.metric("Cuantitativa", quant)


def page_bibliometric():
    """Página de análisis bibliométrico."""
    st.markdown('<div class="main-header">📈 Análisis Bibliométrico</div>', unsafe_allow_html=True)

    st.markdown("Genera métricas y visualizaciones bibliométricas de tus referencias.")
    st.markdown("---")

    from bibliometric_analyzer import BibliometricAnalyzer

    tab1, tab2, tab3 = st.tabs(["📊 Métricas", "📈 Gráficos", "🕸️ Redes"])

    with tab1:
        st.subheader("Métricas Básicas")

        if not st.session_state.filtered_results:
            st.info("No hay artículos filtrados. Ejecuta el pipeline primero.")
            # Demo con datos simulados
            demo_articles = [
                {"title": "Benzo[a]pyrene and respiratory toxicity", "year": 2022, "authors": ["Smith J", "Doe A"], "journal": "Toxicology Letters", "cited_by_count": 45, "doi": "10.1234/demo1"},
                {"title": "PAH exposure in lung cells", "year": 2021, "authors": ["Johnson B", "Smith J", "Lee K"], "journal": "Environmental Health", "cited_by_count": 32, "doi": "10.1234/demo2"},
                {"title": "Oxidative stress by BaP", "year": 2023, "authors": ["Wang L", "Chen M"], "journal": "Free Radical Biology", "cited_by_count": 28, "doi": "10.1234/demo3"},
                {"title": "DNA damage from PAHs", "year": 2020, "authors": ["Doe A", "Johnson B"], "journal": "Mutation Research", "cited_by_count": 67, "doi": "10.1234/demo4"},
                {"title": "Inflammatory response to BaP", "year": 2022, "authors": ["Smith J", "Wang L", "Doe A"], "journal": "Toxicology Letters", "cited_by_count": 19, "doi": "10.1234/demo5"},
            ]
            analyzer = BibliometricAnalyzer(output_path=Path("./demo_biblio"))
            analyzer.load_articles(demo_articles)
            metrics = analyzer.calculate_basic_metrics()
        else:
            output_path = Path(st.session_state.pipeline_paths.get('14_bibliometrics', './bibliometrics'))
            analyzer = BibliometricAnalyzer(output_path=output_path)
            analyzer.load_articles(st.session_state.filtered_results)
            metrics = analyzer.calculate_basic_metrics()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📄 Artículos", metrics.get('total_articles', 0))
        col2.metric("👥 Autores únicos", metrics.get('unique_authors', 0))
        col3.metric("📚 Journals", metrics.get('unique_journals', 0))
        col4.metric("📎 Con DOI", metrics.get('with_doi', 0))

        col5, col6 = st.columns(2)
        col5.metric("🔓 Open Access", f"{metrics.get('oa_percentage', 0)}%")
        col6.metric("⭐ Citaciones/media", metrics.get('avg_citations', 0))

        year_range = metrics.get('year_range', (None, None))
        if year_range[0]:
            st.info(f"📅 Rango de años: {year_range[0]} - {year_range[1]}")

        st.json(metrics)

    with tab2:
        st.subheader("Gráficos Bibliométricos")

        if st.button("🎨 Generar Todos los Gráficos", type="primary"):
            with st.spinner("Generando visualizaciones..."):
                try:
                    output_path = Path(st.session_state.pipeline_paths.get('14_bibliometrics', './bibliometrics'))

                    if not st.session_state.filtered_results:
                        # Usar demo
                        demo_articles = [
                            {"title": "Benzo[a]pyrene and respiratory toxicity in human cells", "year": 2022, "authors": ["Smith J", "Doe A"], "journal": "Toxicology Letters", "cited_by_count": 45, "doi": "10.1234/demo1", "abstract": "Benzo[a]pyrene causes oxidative stress and DNA damage in respiratory cells."},
                            {"title": "PAH exposure effects in lung epithelial cells", "year": 2021, "authors": ["Johnson B", "Smith J", "Lee K"], "journal": "Environmental Health Perspectives", "cited_by_count": 32, "doi": "10.1234/demo2", "abstract": "Polycyclic aromatic hydrocarbons induce inflammation in pulmonary tissue."},
                            {"title": "Oxidative stress mechanisms by BaP in vitro", "year": 2023, "authors": ["Wang L", "Chen M"], "journal": "Free Radical Biology and Medicine", "cited_by_count": 28, "doi": "10.1234/demo3", "abstract": "Reactive oxygen species generation by benzo[a]pyrene metabolites."},
                            {"title": "DNA damage biomarkers from PAH exposure", "year": 2020, "authors": ["Doe A", "Johnson B"], "journal": "Mutation Research", "cited_by_count": 67, "doi": "10.1234/demo4", "abstract": "Genotoxic effects of polycyclic aromatic hydrocarbons in respiratory system."},
                            {"title": "Inflammatory cytokine response to BaP exposure", "year": 2022, "authors": ["Smith J", "Wang L", "Doe A"], "journal": "Toxicology Letters", "cited_by_count": 19, "doi": "10.1234/demo5", "abstract": "IL-6 and TNF-alpha release following benzo[a]pyrene treatment."},
                            {"title": "Lung cancer risk from occupational PAH exposure", "year": 2019, "authors": ["Garcia R", "Smith J"], "journal": "Cancer Epidemiology", "cited_by_count": 89, "doi": "10.1234/demo6", "abstract": "Epidemiological study of respiratory cancer in PAH-exposed workers."},
                            {"title": "Metabolism of benzo[a]pyrene in human lung", "year": 2021, "authors": ["Chen M", "Wang L", "Lee K"], "journal": "Drug Metabolism Reviews", "cited_by_count": 41, "doi": "10.1234/demo7", "abstract": "CYP1A1-mediated activation of BaP in pulmonary tissue."},
                        ]
                        analyzer = BibliometricAnalyzer(output_path=output_path)
                        analyzer.load_articles(demo_articles)
                    else:
                        analyzer = BibliometricAnalyzer(output_path=output_path)
                        analyzer.load_articles(st.session_state.filtered_results)

                    results = analyzer.generate_full_report()

                    st.success(f"✅ {len(results)} gráficos generados!")

                    # Mostrar gráficos
                    for name, path in results.items():
                        if path and str(path).endswith('.png') and path.exists():
                            st.subheader(name.replace('_', ' ').title())
                            st.image(str(path))

                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info("Asegúrate de tener instalados: `pip install matplotlib networkx wordcloud`")

    with tab3:
        st.subheader("Redes de Colaboración")
        st.markdown("""
        **Red de co-autoría**: Muestra quién publica con quién.

        **Mapa de co-ocurrencia**: Muestra qué términos aparecen juntos en los artículos.
        """)

        st.info("Las redes se generan junto con los gráficos en la pestaña anterior.")


def page_export():
    """Página de exportación de referencias."""

def page_export():
    """Página de exportación de referencias."""
    st.markdown('<div class="main-header">📤 Exportar Referencias</div>', unsafe_allow_html=True)

    st.markdown("Exporta tus referencias filtradas a múltiples formatos compatibles con gestores bibliográficos.")
    st.markdown("---")

    from export_manager import ExportManager

    st.subheader("Formatos de Exportación")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="database-card" style="text-align:center;">
            <h3>📄 RIS</h3>
            <p>Zotero<br>Mendeley<br>EndNote<br>RefWorks</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="database-card" style="text-align:center;">
            <h3>📚 BibTeX</h3>
            <p>LaTeX<br>JabRef<br>Zotero<br>Overleaf</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="database-card" style="text-align:center;">
            <h3>📊 CSV</h3>
            <p>Excel<br>Google Sheets<br>R<br>Python</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="database-card" style="text-align:center;">
            <h3>🗃️ JSON</h3>
            <p>APIs<br>Bases de datos<br>Interoperabilidad</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("📤 Exportar Todos los Formatos", type="primary"):
        with st.spinner("Exportando..."):
            try:
                # En producción: usar st.session_state.filtered_results
                # exporter = ExportManager(output_path=Path(st.session_state.pipeline_paths['15_reports']))
                # files = exporter.export_all(articles, base_filename=st.session_state.current_project)

                st.success("✅ Exportación completada (demo)")

                # Simular archivos generados
                st.markdown("### Archivos Generados")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button(
                        "⬇️ Descargar .RIS (Zotero/Mendeley)",
                        data="TY  - JOUR\nTI  - Demo\nER  - ",
                        file_name=f"{st.session_state.current_project or 'references'}.ris",
                        mime="application/x-research-info-systems"
                    )
                    st.download_button(
                        "⬇️ Descargar .BIB (LaTeX)",
                        data="@article{demo, title={Demo}}\n",
                        file_name=f"{st.session_state.current_project or 'references'}.bib",
                        mime="application/x-bibtex"
                    )
                with col_b:
                    st.download_button(
                        "⬇️ Descargar .CSV (Excel)",
                        data="title,authors,year\nDemo,Author,2024\n",
                        file_name=f"{st.session_state.current_project or 'references'}.csv",
                        mime="text/csv"
                    )
                    st.download_button(
                        "⬇️ Descargar .JSON",
                        data='{"references": []}',
                        file_name=f"{st.session_state.current_project or 'references'}.json",
                        mime="application/json"
                    )

            except Exception as e:
                st.error(f"Error: {e}")


# ============== MAIN ==============
def main():
    page = sidebar_navigation()

    pages = {
        "🏠 Inicio": page_home,
        "⚙️ Configuración": page_configuration,
        "🗄️ Bases de Datos": page_databases,
        "🔑 APIs & Credenciales": page_apis,
        "🔍 Palabras Clave": page_keywords,
        "📂 Pipeline Setup": page_pipeline_setup,
        "▶️ Ejecutar Búsquedas": page_execute,
        "🔄 Deduplicar": page_deduplicate,
        "🧪 Filtrar Relevancia": page_filter,
        "📄 Descargar PDFs": page_download_pdfs,
        "📊 Diagrama PRISMA": page_prisma,
        "📈 Análisis Bibliométrico": page_bibliometric,
        "📤 Exportar Referencias": page_export
    }

    if page in pages:
        pages[page]()


if __name__ == "__main__":
    main()
