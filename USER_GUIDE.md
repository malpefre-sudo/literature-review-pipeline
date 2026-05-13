# 📖 Guía de Usuario - Literature Review Pipeline App v2.0

**Aplicación modular para revisiones sistemáticas de literatura**

---

## 📋 Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Instalación](#2-instalación)
3. [Inicio Rápido](#3-inicio-rápido)
4. [Flujo de Trabajo Paso a Paso](#4-flujo-de-trabajo-paso-a-paso)
   - 4.1 [Configuración del Proyecto](#41-configuración-del-proyecto)
   - 4.2 [Selección de Bases de Datos](#42-selección-de-bases-de-datos)
   - 4.3 [Configuración de APIs](#43-configuración-de-apis)
   - 4.4 [Estrategia de Búsqueda](#44-estrategia-de-búsqueda)
   - 4.5 [Pipeline Setup](#45-pipeline-setup)
   - 4.6 [Ejecución de Búsquedas](#46-ejecución-de-búsquedas)
   - 4.7 [Deduplicación](#47-deduplicación)
   - 4.8 [Filtrado de Relevancia](#48-filtrado-de-relevancia)
   - 4.9 [Descarga de PDFs](#49-descarga-de-pdfs)
   - 4.10 [Diagrama PRISMA](#410-diagrama-prisma)
   - 4.11 [Análisis Bibliométrico](#411-análisis-bibliométrico)
   - 4.12 [Exportación de Referencias](#412-exportación-de-referencias)
5. [Uso por Línea de Comandos (CLI)](#5-uso-por-línea-de-comandos-cli)
6. [Solución de Problemas](#6-solución-de-problemas)
7. [Glosario](#7-glosario)

---

## 1. Introducción

### ¿Qué es esta aplicación?

**Literature Review Pipeline App** es una herramienta integral para realizar **revisiones sistemáticas de literatura** de forma estructurada, reproducible y automatizada. Te permite:

- 🔍 Buscar en **6 bases de datos** simultáneamente
- 🔄 **Deduplicar** resultados automáticamente
- 🧪 **Filtrar** por relevancia usando palabras clave
- 📄 **Descargar PDFs** desde DOI
- 📊 Generar **diagramas PRISMA 2020**
- 📈 Realizar **análisis bibliométrico**
- 📤 **Exportar** a Zotero, Mendeley, EndNote, LaTeX, Excel

### ¿Para quién es?

- 🎓 **Investigadores** que realizan revisiones sistemáticas
- 📚 **Estudiantes** de doctorado o máster
- 🔬 **Equipos de investigación** que necesitan colaborar
- 🏥 **Profesionales** de la salud que actualizan evidencia

### Flujo completo del pipeline

```
Configuración → Búsqueda → Deduplicación → Filtro → PDFs → PRISMA → Bibliometría → Exportación
```

---

## 2. Instalación

### Requisitos del sistema

- **Python 3.8** o superior
- **4 GB RAM** mínimo (8 GB recomendado)
- **Conexión a internet**
- **Navegador web** (Chrome, Firefox, Edge)

### Paso 1: Descargar la aplicación

Descarga la carpeta `literature_review_app/` con todos sus archivos.

### Paso 2: Crear entorno virtual (recomendado)

```bash
# Navegar a la carpeta
cd literature_review_app

# Crear entorno virtual
python -m venv venv

# Activar entorno
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

> 💡 **Tip**: El entorno virtual aísla las dependencias y evita conflictos con otros proyectos.

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- `streamlit` - Interfaz web
- `matplotlib` - Gráficos
- `pandas` - Procesamiento de datos
- `requests` - Llamadas HTTP
- `python-dotenv` - Variables de entorno

### Dependencias opcionales (recomendadas)

```bash
# Para redes de co-autoría
pip install networkx

# Para nube de palabras
pip install wordcloud

# Para soporte YAML
pip install pyyaml
```

### Paso 4: Verificar instalación

```bash
python -c "import streamlit; print('✅ Streamlit OK')"
python -c "import matplotlib; print('✅ Matplotlib OK')"
```

---

## 3. Inicio Rápido

### Lanzar la aplicación web

```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador en `http://localhost:8501`.

### Interfaz principal

La pantalla se divide en dos zonas:

```
┌─────────────────────────────────────────────────────────────┐
│  📚 LitReview App v2.0                                      │
│  ─────────────────────                                      │
│  🏠 Inicio                                                  │
│  ⚙️ Configuración                                           │
│  🗄️ Bases de Datos        ←  Menú lateral (navegación)     │
│  🔑 APIs & Credenciales                                     │
│  🔍 Palabras Clave                                          │
│  📂 Pipeline Setup                                          │
│  ▶️ Ejecutar Búsquedas                                      │
│  🔄 Deduplicar                                              │
│  🧪 Filtrar Relevancia                                      │
│  📄 Descargar PDFs                                          │
│  📊 Diagrama PRISMA                                         │
│  📈 Análisis Bibliométrico                                  │
│  📤 Exportar Referencias                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    Área de contenido                        │
│                    (cambia según sección)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Flujo de Trabajo Paso a Paso

### 4.1 Configuración del Proyecto

**Ubicación**: Menú lateral → `⚙️ Configuración`

#### Crear un nuevo proyecto

1. En la pestaña **"🆕 Nuevo Proyecto"**, introduce:
   - **Nombre del proyecto**: Usa solo letras, números, guiones y underscores
     - ✅ Ejemplo: `BaP_Respiratory_Toxicity`
     - ❌ Evita: espacios, acentos, caracteres especiales
   - **Ruta base**: Directorio donde se guardarán todos los proyectos
     - Por defecto: `./literature_reviews`
   - **Descripción**: Opcional, pero útil para recordar el objetivo

2. (Opcional) Desmarca "Usar estructura por defecto" si quieres personalizar las carpetas

3. Haz clic en **🚀 Crear Proyecto**

> ✅ Verás un mensaje de confirmación y el proyecto aparecerá en "Proyecto Actual" en la barra lateral.

#### Cargar un proyecto existente

1. Ve a la pestaña **"📂 Cargar Proyecto"**
2. Selecciona el proyecto de la lista desplegable
3. Haz clic en **📂 Cargar Proyecto**

#### Importar/Exportar configuración

- **📥 Importar**: Sube un archivo JSON con configuración guardada
- **📤 Exportar**: Descarga la configuración actual para compartir o respaldar

---

### 4.2 Selección de Bases de Datos

**Ubicación**: Menú lateral → `🗄️ Bases de Datos`

Aquí eliges de qué fuentes quieres obtener resultados.

#### Bases disponibles

| Base de datos | Icono | ¿Requiere API? | Tipo |
|---------------|-------|---------------|------|
| **PubMed** | 🏥 | Email (obligatorio) | Biomédica |
| **Europe PMC** | 🇪🇺 | Email (recomendado) | Europea OA |
| **Semantic Scholar** | 🧠 | Opcional (gratis) | Académica IA |
| **CrossRef** | 🔗 | No | Metadatos |
| **OpenAlex** | 📖 | Email (recomendado) | Grafo abierto |
| **Scopus** | 📚 | Key institucional | Comercial |

#### Cómo seleccionar

1. Marca las casillas de las bases que quieras usar
2. Si alguna base requiere credenciales que no has configurado, verás una advertencia ⚠️
3. Selecciona al menos **2-3 bases** para una búsqueda completa

> 💡 **Recomendación**: Para biomedicina, usa **PubMed + Europe PMC + Semantic Scholar**. Para ciencias sociales, añade **CrossRef + OpenAlex**.

---

### 4.3 Configuración de APIs

**Ubicación**: Menú lateral → `🔑 APIs & Credenciales`

#### Credenciales necesarias

Completa los campos según las bases que seleccionaste:

**📧 NCBI Entrez (PubMed / Europe PMC)**
- **Email Entrez**: Tu email personal (obligatorio para NCBI)
- **NCBI API Key**: Opcional. Aumenta el límite de requests de 3/seg a 10/seg
  - Obténla en: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/api-api-keys/

**🧠 Semantic Scholar**
- **API Key**: Opcional pero recomendada
  - Obténla en: https://www.semanticscholar.org/product/api
  - Sin key: 100 requests/5 minutos
  - Con key: 100 requests/segundo

**📖 OpenAlex**
- **Email**: Para "polite pool" (acceso prioritario)
  - No requiere registro, solo tu email

**📚 Scopus**
- **API Key**: Requiere suscripción institucional
  - Obténla en: https://dev.elsevier.com/

#### Guardar credenciales

1. Rellena los campos
2. Haz clic en **💾 Guardar Credenciales**
3. Se creará automáticamente un archivo `.env` en tu proyecto

> 🔒 **Seguridad**: Las credenciales se guardan localmente en tu computadora, nunca se envían a servidores externos.

---

### 4.4 Estrategia de Búsqueda

**Ubicación**: Menú lateral → `🔍 Palabras Clave`

Aquí defines **qué buscar**. La app genera automáticamente la query booleana.

#### Conceptos (PICO u otros frameworks)

Organiza tus términos en **grupos conceptuales**. Por ejemplo, para BaP y toxicidad respiratoria:

| Concepto | Términos |
|----------|----------|
| **Exposición** | benzo[a]pyrene, BaP, polycyclic aromatic hydrocarbons, PAHs |
| **Resultado** | respiratory, lung, pulmonary, bronchial |
| **Efecto** | toxicity, inflammation, oxidative stress, DNA damage |

**Para añadir/modificar conceptos:**
1. En la pestaña **"📝 Términos"**, edita los nombres y términos
2. Cada término va en una línea separada
3. Para añadir más conceptos, haz clic en **➕ Añadir Concepto**

#### Operadores booleanos

En la pestaña **"🔧 Estrategia Booleana"**:

| Opción | Descripción | Recomendación |
|--------|-------------|---------------|
| **Dentro de cada concepto** | OR / AND | Usa **OR** (sinónimos) |
| **Entre conceptos** | AND / OR | Usa **AND** (intersección) |
| **Usar paréntesis** | Sí / No | **Sí** (precedencia correcta) |

#### Query generada

En la pestaña **"📋 Preview"** verás la query final:

```
(benzo[a]pyrene OR BaP OR polycyclic aromatic hydrocarbons OR PAHs) 
AND (respiratory OR lung OR pulmonary OR bronchial) 
AND (toxicity OR inflammation OR oxidative stress OR DNA damage)
```

> ✅ Si la query te parece correcta, haz clic en **💾 Guardar Estrategia de Búsqueda**

---

### 4.5 Pipeline Setup

**Ubicación**: Menú lateral → `📂 Pipeline Setup`

Aquí se crea la **estructura de carpetas** donde se guardarán todos los resultados.

#### Antes de ejecutar

Verifica el resumen:
- ✅ Proyecto creado
- ✅ Bases de datos seleccionadas
- ✅ APIs configuradas
- ✅ Conceptos definidos

#### Ejecutar setup

1. Haz clic en **🏗️ Ejecutar Setup**
2. Se crearán automáticamente las carpetas:

```
literature_reviews/
└── BaP_Respiratory_Toxicity/
    ├── data_collection/
    │   ├── 1_pubmed_search/
    │   ├── 2_europe_pmc_search/
    │   ├── 3_crossref_search/
    │   ├── 4_semantic_scholar_search/
    │   ├── 5_openalex_search/
    │   └── 6_scopus_search/
    ├── data_processing/
    │   ├── 7_unification_deduplication/
    │   ├── 8_initial_filter/
    │   ├── 9_article_downloads/
    │   ├── 10_abstract_extraction/
    │   └── 11_fulltext_processing/
    └── analysis_visualization/
        ├── 12_research_goal_sorting/
        ├── 13_prisma_visualization/
        ├── 14_bibliometric_analysis/
        └── 15_final_reports/
```

> ✅ Verás la lista de rutas generadas en pantalla.

---

### 4.6 Ejecución de Búsquedas

**Ubicación**: Menú lateral → `▶️ Ejecutar Búsquedas`

#### Configurar límites

- **Máximo resultados por base**: Deslizador de 10 a 500
  - Recomendado: **100-200** para exploración inicial
  - Para revisión exhaustiva: **500**

#### Lanzar búsquedas

1. Haz clic en **🚀 Iniciar Búsquedas**
2. Verás una barra de progreso y el estado de cada base
3. Los resultados se guardan automáticamente en JSON dentro de cada carpeta

#### Estructura de resultados por base

Cada base genera un archivo JSON con:

```json
{
  "metadata": {
    "source": "SearchPubMed",
    "timestamp": "2026-05-12T10:30:00",
    "query": "benzo[a]pyrene respiratory toxicity",
    "total_results": 150,
    "status": "completed"
  },
  "results": [
    {
      "pmid": "12345678",
      "title": "Título del artículo",
      "authors": ["Autor A", "Autor B"],
      "year": "2024",
      "journal": "Nombre del Journal",
      "doi": "10.1234/example",
      "abstract": "Resumen del artículo...",
      "url": "https://..."
    }
  ]
}
```

---

### 4.7 Deduplicación

**Ubicación**: Menú lateral → `🔄 Deduplicar`

Elimina artículos repetidos entre diferentes bases de datos.

#### Criterios de deduplicación

La app detecta duplicados en este orden:

1. **DOI idéntico** (más confiable)
2. **PMID idéntico** (para artículos biomédicos)
3. **PMCID idéntico** (Europe PMC)
4. **Hash de título + año + primer autor**
5. **Similitud de título > 85%** (para variantes menores)

#### Configurar

- **Umbral de similitud de título**: 0.50 a 1.00
  - **0.85** (recomendado): Detecta "Benzo[a]pyrene toxicity" vs "Benzo[a]pyrene-induced toxicity"
  - **0.95**: Muy estricto, solo títulos casi idénticos
  - **0.70**: Más permisivo, puede eliminar artículos diferentes

#### Ejecutar

1. Haz clic en **🔄 Ejecutar Deduplicación**
2. Verás el resumen:
   - Total procesados
   - Únicos
   - Duplicados eliminados

> 💡 **Tip**: Revisa siempre los duplicados eliminados para confirmar que no se perdió nada importante.

---

### 4.8 Filtrado de Relevancia

**Ubicación**: Menú lateral → `🧪 Filtrar Relevancia`

Filtra artículos por relevancia usando palabras clave en títulos y abstracts.

#### Configurar filtros (pestaña "⚙️ Configurar Filtros")

**Palabras clave requeridas (Inclusión)**
- Artículos que **NO contengan TODOS** estos términos serán excluidos
- Ejemplo para BaP:
  ```
  benzo[a]pyrene
  respiratory
  toxicity
  ```

**Palabras clave excluyentes**
- Artículos que **contengan ALGUNO** de estos términos serán excluidos
- Ejemplo:
  ```
  review
  meta-analysis
  protocol
  ```
  (Si solo quieres artículos originales, no revisiones)

**Umbral de relevancia**
- Score mínimo: 0.0 a 1.0
- **0.3** (recomendado): Balanceado
- **0.5**: Más estricto, menos resultados pero más relevantes
- **0.1**: Más permisivo, más resultados

#### Ejecutar filtrado (pestaña "▶️ Ejecutar Filtrado")

1. Haz clic en **🧪 Ejecutar Filtrado**
2. Verás métricas:
   - 📄 Total
   - ✅ Relevantes
   - ❌ Excluidos
   - 📉 Bajo Score

#### Resultados del filtrado

Se generan tres archivos en `8_initial_filter/`:

| Archivo | Contenido |
|---------|-----------|
| `articles_relevant.json` | Artículos que pasaron el filtro |
| `articles_excluded.json` | Artículos excluidos (con razón) |
| `filtering_report.json` | Resumen y parámetros usados |

---

### 4.9 Descarga de PDFs

**Ubicación**: Menú lateral → `📄 Descargar PDFs`

Descarga automática de artículos en PDF desde múltiples fuentes.

#### Fuentes de descarga (en orden de prioridad)

1. **Unpaywall API** — Acceso abierto legal y gratuito
2. **OpenAlex** — Links a PDFs de acceso abierto
3. **Semantic Scholar** — PDFs open access
4. **DOI resolver directo** — Fallback final

#### Configurar

- **Máximo PDFs a descargar**: 1 a 500
  - Recomendado: descargar solo los artículos **relevantes** filtrados

#### Ejecutar

1. Haz clic en **📥 Iniciar Descarga**
2. Los PDFs se guardan en `9_article_downloads/`
3. Se genera `download_report.json` con:
   - Exitosos
   - Fallidos (con DOI para intentar manualmente)

> ⚠️ **Nota ética**: Esta herramienta respeta los rate limits y solo descarga artículos de acceso abierto o mediante APIs legales. No realiza scraping agresivo.

---

### 4.10 Diagrama PRISMA

**Ubicación**: Menú lateral → `📊 Diagrama PRISMA`

Genera el **diagrama de flujo PRISMA 2020**, estándar internacional para reportar revisiones sistemáticas.

#### Conteos por etapa

Completa los números para cada fase:

**🔍 Identificación**
- Registros de bases de datos
- Registros de registros web (ClinicalTrials, PROSPERO...)
- Otras fuentes (referencias manuales, contactos...)
- Duplicados eliminados

**🔎 Screening**
- Registros screening (títulos/abstracts revisados)
- Excluidos en screening

**📋 Elegibilidad**
- Evaluados en texto completo
- Excluidos en texto completo

**✅ Inclusión**
- Incluidos en síntesis cualitativa
- Incluidos en meta-análisis (si aplica)

> 💡 **Tip**: Los conteos se actualizan automáticamente si ejecutaste las etapas anteriores en la app.

#### Generar diagrama

Haz clic en:
- **🖼️ Generar Imagen PNG** — Para incluir en tu artículo/manuscrito
- **🌐 Generar HTML Interactivo** — Para presentaciones web

Los archivos se guardan en `13_prisma_visualization/`.

---

### 4.11 Análisis Bibliométrico

**Ubicación**: Menú lateral → `📈 Análisis Bibliométrico`

Genera métricas y visualizaciones del conjunto de referencias.

#### Métricas básicas (pestaña "📊 Métricas")

Muestra indicadores clave:
- 📄 Total de artículos
- 👥 Autores únicos
- 📚 Journals distintos
- 📎 Artículos con DOI
- 🔓 Porcentaje de Open Access
- ⭐ Citaciones promedio
- 📅 Rango de años

#### Gráficos (pestaña "📈 Gráficos")

Haz clic en **🎨 Generar Todos los Gráficos** para crear:

| Gráfico | Descripción |
|---------|-------------|
| **Producción por año** | Barras: artículos publicados cada año |
| **Top autores** | Autores más productivos (horizontal) |
| **Top journals** | Revistas más frecuentes |
| **Distribución de citaciones** | Histograma logarítmico |
| **Nube de palabras** | Términos más frecuentes en títulos+abstracts |
| **Mapa de co-ocurrencia** | Heatmap de términos que aparecen juntos |

#### Redes (pestaña "🕸️ Redes")

- **Red de co-autoría**: Quién publica con quién (requiere `networkx`)
- **Mapa de co-ocurrencia**: Qué términos aparecen juntos

> 📦 Los gráficos se guardan en `14_bibliometric_analysis/` en alta resolución (300 DPI).

---

### 4.12 Exportación de Referencias

**Ubicación**: Menú lateral → `📤 Exportar Referencias`

Exporta tus referencias finales a múltiples formatos.

#### Formatos disponibles

| Formato | Extensión | Para qué sirve |
|---------|-----------|---------------|
| **RIS** | `.ris` | Zotero, Mendeley, EndNote, RefWorks |
| **BibTeX** | `.bib` | LaTeX, JabRef, Overleaf |
| **CSV** | `.csv` | Excel, Google Sheets, R, Python |
| **JSON** | `.json` | APIs, bases de datos, interoperabilidad |

#### Cómo exportar

1. Haz clic en **📤 Exportar Todos los Formatos**
2. Se generan 4 archivos en `15_final_reports/`
3. Descarga cada uno con los botones de descarga

#### Importar en gestores bibliográficos

**Zotero:**
1. Archivo → Importar
2. Selecciona el archivo `.ris`
3. Zotero detectará automáticamente todos los campos

**Mendeley:**
1. Archivo → Añadir archivos → Importar
2. Selecciona `.ris` o `.bib`

**EndNote:**
1. File → Import → File
2. Select `.ris`, Import Option: Reference Manager (RIS)

**LaTeX (Overleaf):**
1. Sube el archivo `.bib` a tu proyecto
2. En tu `.tex`: `\bibliography{references}`

---

## 5. Uso por Línea de Comandos (CLI)

Para automatización o uso en servidores sin interfaz gráfica.

### Instalación rápida para CLI

```bash
pip install -r requirements.txt
```

### Comandos disponibles

```bash
# Ver ayuda
python run.py --help

# Crear proyecto + ejecutar búsqueda completa
python run.py \
  --project-name "BaP_Respiratory_Toxicity" \
  --databases pubmed europe_pmc crossref semantic_scholar openalex \
  --query "benzo[a]pyrene respiratory toxicity" \
  --max-results 200

# Solo crear estructura de carpetas
python run.py --project-name "Nueva_Revision" --setup-only

# Desde archivo de configuración
python run.py --config config_example.json

# Con API keys por variables de entorno
export ENTREZ_EMAIL="tu@email.com"
export SEMANTIC_SCHOLAR_API_KEY="tu_key"
python run.py --project-name "Review" --databases pubmed semantic_scholar --query "cancer"
```

### Opciones de línea de comandos

| Opción | Abreviatura | Descripción |
|--------|-------------|-------------|
| `--project-name` | `-p` | Nombre del proyecto (obligatorio) |
| `--base-path` | `-b` | Ruta base (default: ./literature_reviews) |
| `--databases` | `-d` | Lista de bases (pubmed, crossref, etc.) |
| `--query` | `-q` | Query de búsqueda |
| `--max-results` | `-m` | Máximo resultados por base (default: 100) |
| `--config` | `-c` | Archivo JSON de configuración |
| `--setup-only` | — | Solo crear carpetas |
| `--api-keys` | `-k` | Archivo .env con credenciales |

---

## 6. Solución de Problemas

### Error: "No module named 'streamlit'"

```bash
pip install streamlit
```

### Error: "Email de Entrez requerido"

1. Ve a `🔑 APIs & Credenciales`
2. Introduce tu email en "Email Entrez"
3. El email es obligatorio para usar PubMed

### Error: "networkx no instalado"

```bash
pip install networkx
```

### Error: "wordcloud no instalado"

```bash
pip install wordcloud
```

### La búsqueda en PubMed devuelve 0 resultados

- Verifica que tu query no tenga errores de sintaxis
- Prueba la query directamente en https://pubmed.ncbi.nlm.nih.gov/
- Asegúrate de que el email de Entrez está configurado

### Los PDFs no se descargan

- No todos los artículos tienen versión PDF de acceso abierto
- Verifica el reporte `download_report.json` para ver cuáles fallaron
- Intenta descargar manualmente los que fallaron desde el DOI

### El diagrama PRISMA no se genera

```bash
pip install matplotlib
```

### La app no se abre en el navegador

1. Verifica que no hay otro servicio usando el puerto 8501
2. Intenta: `streamlit run app.py --server.port 8502`

---

## 7. Glosario

| Término | Significado |
|---------|-------------|
| **DOI** | Digital Object Identifier — identificador único de artículos |
| **PMID** | PubMed ID — identificador en PubMed |
| **PMCID** | PubMed Central ID — identificador en Europe PMC |
| **PRISMA** | Preferred Reporting Items for Systematic Reviews and Meta-Analyses |
| **OA** | Open Access — acceso abierto (gratuito) |
| **API** | Application Programming Interface — interfaz para consultar datos |
| **Query booleana** | Búsqueda con operadores AND, OR, NOT |
| **Deduplicación** | Eliminación de resultados repetidos |
| **Rate limit** | Límite de peticiones por segundo impuesto por la API |
| **Bibliometría** | Análisis cuantitativo de la literatura científica |
| **RIS** | Research Information Systems — formato de intercambio de referencias |
| **BibTeX** | Formato de referencias para LaTeX |

---

## 📞 Soporte

Si encuentras algún problema:

1. Revisa la sección [Solución de Problemas](#6-solución-de-problemas)
2. Verifica que todas las dependencias están instaladas
3. Consulta los logs de error en la terminal

---

**Documento generado para Literature Review Pipeline App v2.0**
**Fecha**: 2026-05-12
