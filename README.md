# Asistente RAG de Soporte Técnico

**Asignatura:** IA Embebida en Sistemas Computacionales  
**Carrera:** Ingeniería Informática  
**Caso de Uso:** Caso 2 — Asistente de Soporte Técnico

---

## Descripción del Proyecto

Sistema de pregunta-respuesta basado en la arquitectura **RAG (Retrieval Augmented Generation)**. El asistente responde preguntas técnicas utilizando documentación interna (Docker, Linux, Git, Procedimientos de Soporte), recuperando información relevante antes de generar una respuesta fundamentada.

```
Usuario → Pregunta → [Embedding] → [ChromaDB] → Contexto → [LLM Ollama] → Respuesta + Fuentes
```

---

## Estructura del Proyecto

```
rag-soporte-tecnico/
│
├── main.py                    # Interfaz interactiva principal (CLI)
├── test_escenarios.py         # Pruebas de los 3 escenarios de demostración
├── requirements.txt           # Dependencias Python
│
├── src/
│   ├── rag_pipeline.py        # Pipeline RAG: ingesta, chunking, embeddings, ChromaDB
│   └── llm_integration.py     # Integración con Ollama (LLM)
│
├── docs/                      # Corpus documental
│   ├── manual_docker.md
│   ├── manual_linux.md
│   ├── manual_git.md
│   └── procedimientos_soporte.md
│
└── chroma_db/                 # Base vectorial (generada automáticamente)
```

---

## Requisitos del Sistema

- Python 3.10 o superior
- 8 GB RAM mínimo (16 GB recomendado)
- 10 GB espacio en disco (para el modelo LLM)
- Conexión a internet (solo para descargar modelos la primera vez)

---

## Instalación Paso a Paso

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/rag-soporte-tecnico.git
cd rag-soporte-tecnico
```

### Paso 2: Crear entorno virtual Python

```bash
python -m venv venv

# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Paso 3: Instalar dependencias Python

```bash
pip install -r requirements.txt
```

> **Nota:** La primera instalación descargará el modelo de embeddings (~90MB).

### Paso 4: Instalar Ollama

Descargar desde: **https://ollama.ai/download**

Disponible para Linux, macOS y Windows.

```bash
# Verificar instalación:
ollama --version
```

### Paso 5: Descargar modelo LLM

```bash
# Recomendado (Mistral 7B, ~4.1GB):
ollama pull mistral

# Alternativas:
ollama pull llama3    # Meta Llama 3 8B
ollama pull gemma     # Google Gemma 7B
```

### Paso 6: Iniciar Ollama

```bash
# En una terminal separada:
ollama serve
```

---

## Ejecución

### Asistente interactivo (uso normal):

```bash
python main.py
```

El sistema automáticamente:
1. Carga e indexa los documentos del corpus
2. Se conecta con Ollama
3. Inicia la interfaz de conversación

### Demostración de escenarios (para presentación):

```bash
python test_escenarios.py
```

Ejecuta automáticamente los 3 escenarios requeridos en la rúbrica.

### Modo de prueba interactivo:

```bash
python test_escenarios.py --modo interactivo
```

---

## Comandos del Asistente

| Comando | Descripción |
|---|---|
| `/ayuda` | Muestra la ayuda del sistema |
| `/estadisticas` | Fragmentos indexados, modelo, configuración |
| `/fuentes` | Lista los documentos del corpus |
| `/modelo mistral` | Cambia el modelo LLM en uso |
| `/reindexar` | Vuelve a indexar los documentos |
| `/salir` | Termina el programa |

---

## Preguntas de Ejemplo

**Consultas simples:**
- `¿Cómo crear una imagen Docker?`
- `¿Cómo actualizar un repositorio Git?`
- `¿Cómo visualizar procesos en Linux?`
- `¿Cómo abrir un ticket de soporte?`

**Consultas complejas:**
- `¿Qué debo hacer si encuentro un virus en mi equipo y cómo reportarlo?`
- `¿Cómo configuro Docker Compose con una base de datos y qué volumenes necesito?`

**Consultas sin respuesta (manejo de ausencia):**
- `¿Cuál es el precio del dólar hoy?`
- `¿Qué es el protocolo médico para emergencias cardíacas?`

---

## Decisiones Técnicas

### Chunking
- **Tamaño de chunk:** 800 caracteres  
  *Justificación:* Captura párrafos completos y mantiene contexto semántico sin exceder el límite del modelo de embeddings (~512 tokens ≈ ~2000 caracteres, pero se prefiere menos para mayor precisión en la recuperación).*
  
- **Solapamiento:** 150 caracteres  
  *Justificación:* El 18% de solapamiento asegura que las ideas que cruzan el borde entre dos chunks no se pierdan durante la recuperación semántica.*

### Embeddings
- **Modelo:** `all-MiniLM-L6-v2` (Sentence Transformers)  
  *Justificación:* Modelo ligero (80MB), 384 dimensiones, entrenado específicamente para similitud semántica de oraciones. No requiere GPU y es muy eficiente.*

### Base Vectorial
- **Motor:** ChromaDB con persistencia en disco  
  *Justificación:* Fácil instalación, no requiere servidor externo, soporta búsqueda por similitud coseno y persiste los embeddings entre ejecuciones.*

### LLM
- **Motor:** Ollama (servidor local)  
  *Justificación:* Permite ejecutar modelos de lenguaje en hardware local sin dependencias de APIs externas ni costos.*
  
- **Modelo:** Mistral 7B  
  *Justificación:* Cumple el requisito ≤7B parámetros, excelente balance rendimiento/recursos, buena comprensión del español.*

### Umbral de similitud
- **Mínimo:** 0.45 (similitud coseno)  
  *Justificación:* Por debajo de este umbral, los fragmentos recuperados tienen muy baja relevancia semántica. Si ningún fragmento supera el umbral, el sistema indica que no tiene información, cumpliendo el requisito de manejo de preguntas fuera del corpus. Se usa 0.45 en lugar de 0.30 para evitar falsos positivos donde fragmentos poco relacionados superaban el umbral anterior y el resumen marcaba incorrectamente "Contexto encontrado".*

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    FASE DE INDEXACIÓN                   │
│                 (se ejecuta una sola vez)                │
├──────────────┬──────────────┬──────────────┬────────────┤
│   Ingesta    │  Chunking    │  Embeddings  │  ChromaDB  │
│              │              │              │            │
│  .md/.txt/   │  chunk=800   │ MiniLM-L6-v2 │ Colección  │
│  .pdf files  │  overlap=150 │  384 dims    │ cosine sim │
└──────────────┴──────────────┴──────────────┴────────────┘

┌─────────────────────────────────────────────────────────┐
│                 FASE DE CONSULTA (RAG)                  │
│                  (por cada pregunta)                     │
├────────────┬───────────────┬──────────────┬─────────────┤
│  Pregunta  │  Embedding    │  Búsqueda    │     LLM     │
│  usuario   │  consulta →   │  semántica → │  Ollama     │
│            │  384 dims     │  top-4 docs  │  Mistral 7B │
└────────────┴───────────────┴──────────────┴─────────────┘
                                                    │
                                          ┌─────────▼────────┐
                                          │ Respuesta + Fuentes│
                                          └──────────────────┘
```

---

## Solución de Problemas

**Ollama no conecta:**
```bash
# Verificar que está corriendo:
ollama serve

# Verificar modelos instalados:
ollama list
```

**Error de memoria al cargar modelo:**
```bash
# Usar modelo más pequeño:
ollama pull gemma:2b
python main.py
# Luego: /modelo gemma:2b
```

**Base vectorial corrupta:**
```bash
rm -rf chroma_db/
python main.py  # Se reindexará automáticamente
```

---

## Video de Demostración

El video de demostración se encuentra disponible en Canvas según los requisitos de entrega.

---

## Referencias

- [LangChain Documentation](https://python.langchain.com)
- [ChromaDB Documentation](https://docs.trychroma.com)
- [Sentence Transformers](https://www.sbert.net)
- [Ollama](https://ollama.ai)
- Lewis, P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020.
