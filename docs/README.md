# 📚 Literature Review Pipeline App v2.0

Aplicación modular y universal para realizar **revisiones sistemáticas de literatura** completas, desde la búsqueda hasta la exportación final.

## ✨ Novedades v2.0

- **🔄 Deduplicación automática** entre múltiples fuentes
- **🧪 Filtro de relevancia** por palabras clave en abstracts
- **📄 Descarga de PDFs** desde DOI (Unpaywall, OpenAlex, etc.)
- **📊 Diagrama PRISMA 2020** generado automáticamente (PNG + HTML)
- **📤 Exportación** a RIS, BibTeX, CSV, JSON (Zotero, Mendeley, EndNote)

---

## 🎯 Características Principales

| Función | Descripción |
|---------|-------------|
| 🗄️ **Multi-Database** | PubMed, Europe PMC, Semantic Scholar, CrossRef, OpenAlex, Scopus |
| ⚙️ **Pipeline Completo** | Búsqueda → Deduplicación → Filtro → PDFs → PRISMA → Exportación |
| 🔌 **Plug & Play** | Aplicable a medicina, biología, química, ingeniería, ciencias sociales... |
| 🖥️ **Interfaz Web** | Streamlit para uso visual + CLI para automatización |
| 🔑 **APIs Configurables** | Credenciales vía `.env`, sin hardcodear |

---

## 🚀 Instalación Rápida

```bash
# 1. Clonar o descargar esta carpeta
cd literature_review_app

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## 🖥️ Uso con Interfaz Web (Streamlit)

```bash
streamlit run app.py
```

Se abre en tu navegador (`http://localhost:8501`). Flujo completo:

| Paso | Sección | Qué haces |
|------|---------|-----------|
| 1 | **⚙️ Configuración** | Crear proyecto, definir estructura |
| 2 | **🗄️ Bases de Datos** | Tildar las fuentes que usarás |
| 3 | **🔑 APIs** | Configurar credenciales |
| 4 | **🔍 Palabras Clave** | Definir conceptos y query booleana |
| 5 | **📂 Pipeline Setup** | Generar carpetas |
| 6 | **▶️ Ejecutar Búsquedas** | Lanzar búsquedas en paralelo |
| 7 | **🔄 Deduplicar** | Eliminar duplicados entre fuentes |
| 8 | **🧪 Filtrar Relevancia** | Filtrar por keywords en abstracts |
| 9 | **📄 Descargar PDFs** | Descargar artículos desde DOI |
| 10 | **📊 Diagrama PRISMA** | Generar diagrama de flujo |
| 11 | **📤 Exportar** | Exportar a Zotero, Mendeley, etc. |

---

## 💻 Uso por Línea de Comandos (CLI)

```bash
# Todo en una línea
python run.py \
  --project-name "BaP_Respiratory_Toxicity" \
  --databases pubmed crossref openalex \
  --query "benzo[a]pyrene respiratory toxicity" \
  --max-results 200
```

---

## 📁 Estructura del Proyecto Generado

```
literature_reviews/
└── {TU_PROYECTO}/
    ├── data_collection/
    │   ├── 1_pubmed_search/
    │   ├── 2_europe_pmc_search/
    │   ├── 3_crossref_search/
    │   ├── 4_semantic_scholar_search/
    │   ├── 5_openalex_search/
    │   └── 6_scopus_search/
    ├── data_processing/
    │   ├── 7_unification_deduplication/
    │   │   ├── deduplication_report.json
    │   │   └── merged_results.json
    │   ├── 8_initial_filter/
    │   │   ├── articles_relevant.json
    │   │   ├── articles_excluded.json
    │   │   └── filtering_report.json
    │   ├── 9_article_downloads/
    │   │   ├── download_report.json
    │   │   └── *.pdf
    │   ├── 10_abstract_extraction/
    │   └── 11_fulltext_processing/
    └── analysis_visualization/
        ├── 12_research_goal_sorting/
        ├── 13_prisma_visualization/
        │   ├── prisma_diagram.png
        │   └── prisma_diagram.html
        ├── 14_bibliometric_analysis/
        └── 15_final_reports/
            ├── references.ris      ← Zotero, Mendeley, EndNote
            ├── references.bib      ← LaTeX, JabRef
            ├── references.csv      ← Excel, Google Sheets
            └── references.json     ← APIs, Bases de datos
```

---

## 🔑 APIs y Credenciales

| Base de Datos | Requiere Key | Obtener en |
|---------------|-------------|------------|
| **PubMed** | Email obligatorio | https://www.ncbi.nlm.nih.gov/ |
| **Europe PMC** | Email recomendado | https://europepmc.org/ |
| **Semantic Scholar** | Opcional (gratis) | https://www.semanticscholar.org/product/api |
| **CrossRef** | No requiere | https://www.crossref.org/ |
| **OpenAlex** | Email recomendado | https://openalex.org/ |
| **Scopus** | Key institucional | https://dev.elsevier.com/ |

Las credenciales se guardan en un archivo `.env` dentro de cada proyecto.

---

## 📤 Formatos de Exportación

| Formato | Extensión | Compatible con |
|---------|-----------|---------------|
| **RIS** | `.ris` | Zotero, Mendeley, EndNote, RefWorks |
| **BibTeX** | `.bib` | LaTeX, JabRef, Zotero, Overleaf |
| **CSV** | `.csv` | Excel, Google Sheets, R, Python |
| **JSON** | `.json` | APIs, Bases de datos, Interoperabilidad |

---

## 🔧 Personalización Avanzada

### Cambiar estructura de carpetas

Edita `pipeline_setup.py` o pasa una estructura JSON personalizada:

```json
{
  "data_collection": {
    "1_pubmed": "1_pubmed_search",
    "2_scopus": "2_scopus_search"
  },
  "mi_categoria": {
    "3_mis_datos": "3_datos_personalizados"
  }
}
```

### Añadir una nueva base de datos

1. Crea `search_nuevadb.py` heredando de `BaseSearch`
2. Implementa `search()` y `validate_credentials()`
3. Regístrala en `run.py` y `app.py`

```python
from base_search import BaseSearch

class SearchNuevaDB(BaseSearch):
    def search(self, query, max_results=100, **kwargs):
        # Tu lógica de búsqueda aquí
        pass

    def validate_credentials(self):
        return True
```

---

## 📦 Módulos Incluidos

| Archivo | Función |
|---------|---------|
| `app.py` | **Interfaz web Streamlit** (completa) |
| `run.py` | **CLI** para ejecución directa |
| `pipeline_setup.py` | Creación de carpetas |
| `config_manager.py` | Gestión de configuraciones |
| `base_search.py` | Clase base para buscadores |
| `search_*.py` | Implementaciones por base de datos (6 módulos) |
| `deduplicator.py` | Motor de deduplicación |
| `abstract_processor.py` | Filtro de relevancia por keywords |
| `pdf_downloader.py` | Descarga de PDFs desde DOI |
| `prisma_generator.py` | Diagrama PRISMA 2020 (PNG + HTML) |
| `export_manager.py` | Exportación a RIS, BibTeX, CSV, JSON |
| `utils.py` | Funciones compartidas |

---

## 🧪 Ejemplo: Revisión sobre BaP

```bash
# 1. Crear proyecto
python run.py --project-name "BaP_Respiratory" --setup-only

# 2. Configurar APIs (editar .env)
echo "ENTREZ_EMAIL=tu@email.com" >> literature_reviews/BaP_Respiratory/.env

# 3. Ejecutar pipeline completo
python run.py --config config_bap.json
```

---

## 📄 Licencia

MIT / Uso académico libre.
