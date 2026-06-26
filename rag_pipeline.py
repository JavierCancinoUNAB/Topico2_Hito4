"""
rag_pipeline.py
---------------
Módulo central del sistema RAG.
Maneja: carga de documentos, chunking, embeddings y base vectorial ChromaDB.
"""

import os
import glob
from typing import List, Tuple, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


# ─────────────────────────────────────────────
# CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────

# Tamaño de cada fragmento (chunk) en caracteres.
# Justificación: 800 caracteres capturan párrafos completos y mantienen contexto
# suficiente sin exceder el límite del modelo de embeddings (~512 tokens).
CHUNK_SIZE = 800

# Solapamiento entre chunks consecutivos en caracteres.
# Justificación: 150 caracteres (~10% del chunk) aseguran que las ideas
# que cruzan el borde entre dos chunks no se pierdan en la recuperación.
CHUNK_OVERLAP = 150

# Modelo de embeddings (all-MiniLM-L6-v2 es ligero, rápido y efectivo).
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Nombre de la colección en ChromaDB.
COLLECTION_NAME = "soporte_tecnico"

# Directorio donde ChromaDB persistirá los datos.
CHROMA_DIR = "./chroma_db"

# Directorio con los documentos del corpus.
DOCS_DIR = "./docs"

# Formatos de documentos aceptados.
SUPPORTED_EXTENSIONS = ["*.md", "*.txt", "*.pdf"]

# Número de fragmentos a recuperar por consulta.
TOP_K = 4


# ─────────────────────────────────────────────
# CLASE PRINCIPAL RAG
# ─────────────────────────────────────────────

class RAGPipeline:
    """
    Implementa el pipeline completo RAG:
    1. Ingesta de documentos
    2. Fragmentación (chunking)
    3. Generación de embeddings
    4. Almacenamiento en base vectorial
    5. Recuperación semántica
    """

    def __init__(self):
        print("Inicializando pipeline RAG...")

        # Cargar modelo de embeddings (SentenceTransformers)
        print(f"  → Cargando modelo de embeddings: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

        # Inicializar cliente ChromaDB con persistencia en disco
        print(f"  → Conectando a ChromaDB en: {CHROMA_DIR}")
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

        # Crear o recuperar la colección
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}  # Distancia coseno para embeddings de texto
        )

        print(f"  → Colección '{COLLECTION_NAME}' lista "
              f"({self.collection.count()} fragmentos almacenados)")
        print("Pipeline RAG inicializado correctamente.\n")

    # ─────────────────────────────────────────
    # 1. INGESTA DOCUMENTAL
    # ─────────────────────────────────────────

    def load_documents(self, docs_dir: str = DOCS_DIR) -> List[Tuple[str, str]]:
        """
        Carga todos los documentos del directorio indicado.

        Soporta: .md, .txt
        (PDF requiere PyMuPDF, ver load_pdf)

        Returns:
            Lista de tuplas (contenido_texto, ruta_archivo)
        """
        documents = []
        found_files = []

        for ext in ["*.md", "*.txt"]:
            pattern = os.path.join(docs_dir, "**", ext)
            found_files.extend(glob.glob(pattern, recursive=True))

        # Intentar cargar PDFs si PyMuPDF está disponible
        pdf_files = glob.glob(os.path.join(docs_dir, "**", "*.pdf"), recursive=True)
        if pdf_files:
            try:
                import fitz  # PyMuPDF
                for pdf_path in pdf_files:
                    text = self._extract_pdf_text(pdf_path)
                    if text.strip():
                        documents.append((text, pdf_path))
                        print(f"  [PDF] Cargado: {os.path.basename(pdf_path)}")
            except ImportError:
                print("  [AVISO] PyMuPDF no disponible; se omiten los PDFs.")

        if not found_files and not documents:
            raise FileNotFoundError(
                f"No se encontraron documentos en '{docs_dir}'. "
                "Asegúrese de tener archivos .md o .txt en la carpeta docs/"
            )

        for filepath in found_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if content.strip():
                    documents.append((content, filepath))
                    print(f"  [OK] Cargado: {os.path.basename(filepath)}")
            except Exception as e:
                print(f"  [ERROR] No se pudo leer {filepath}: {e}")

        print(f"\n  Total de documentos cargados: {len(documents)}\n")
        return documents

    def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extrae texto de un PDF usando PyMuPDF."""
        import fitz
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    # ─────────────────────────────────────────
    # 2. FRAGMENTACIÓN (CHUNKING)
    # ─────────────────────────────────────────

    def split_into_chunks(
        self,
        text: str,
        source: str,
        chunk_size: int = CHUNK_SIZE,
        overlap: int = CHUNK_OVERLAP
    ) -> List[dict]:
        """
        Divide el texto en fragmentos con solapamiento.

        Estrategia:
        - Divide primero por doble salto de línea (párrafos).
        - Si un párrafo supera chunk_size, lo divide por longitud.
        - Aplica solapamiento deslizante entre chunks consecutivos.

        Args:
            text: Contenido del documento.
            source: Nombre o ruta del documento origen.
            chunk_size: Tamaño máximo de cada chunk en caracteres.
            overlap: Solapamiento entre chunks consecutivos en caracteres.

        Returns:
            Lista de dicts con 'text', 'source' e 'index'.
        """
        # Dividir en párrafos naturales
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        chunks = []
        current_chunk = ""
        chunk_index = 0

        for paragraph in paragraphs:
            # Si el párrafo por sí solo excede el límite, cortarlo
            if len(paragraph) > chunk_size:
                # Guardar chunk actual si existe
                if current_chunk:
                    chunks.append({
                        "text": current_chunk.strip(),
                        "source": os.path.basename(source),
                        "source_path": source,
                        "index": chunk_index
                    })
                    chunk_index += 1
                    # Solapamiento: conservar últimos 'overlap' chars del chunk anterior
                    current_chunk = current_chunk[-overlap:] if overlap else ""

                # Dividir párrafo largo en sub-chunks
                for i in range(0, len(paragraph), chunk_size - overlap):
                    sub = paragraph[i: i + chunk_size]
                    chunks.append({
                        "text": sub.strip(),
                        "source": os.path.basename(source),
                        "source_path": source,
                        "index": chunk_index
                    })
                    chunk_index += 1
            else:
                # Agregar párrafo al chunk actual
                if len(current_chunk) + len(paragraph) + 2 > chunk_size:
                    # Guardar chunk y comenzar uno nuevo con solapamiento
                    if current_chunk:
                        chunks.append({
                            "text": current_chunk.strip(),
                            "source": os.path.basename(source),
                            "source_path": source,
                            "index": chunk_index
                        })
                        chunk_index += 1
                        current_chunk = current_chunk[-overlap:] + "\n\n" if overlap else ""
                current_chunk += paragraph + "\n\n"

        # Guardar último chunk pendiente
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "source": os.path.basename(source),
                "source_path": source,
                "index": chunk_index
            })

        return chunks

    # ─────────────────────────────────────────
    # 3. EMBEDDINGS
    # ─────────────────────────────────────────

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de textos.

        Usa SentenceTransformers (all-MiniLM-L6-v2):
        - 384 dimensiones
        - Entrenado para similitud semántica
        - Ligero y sin necesidad de GPU

        Returns:
            Lista de vectores de embeddings.
        """
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True  # Normalizar para similitud coseno
        )
        return embeddings.tolist()

    # ─────────────────────────────────────────
    # 4. BASE VECTORIAL (ChromaDB)
    # ─────────────────────────────────────────

    def index_documents(self, docs_dir: str = DOCS_DIR) -> int:
        """
        Pipeline completo de indexación:
        1. Carga documentos
        2. Los fragmenta
        3. Genera embeddings
        4. Los almacena en ChromaDB

        Returns:
            Número total de fragmentos indexados.
        """
        print("=" * 50)
        print("INICIANDO INDEXACIÓN DE DOCUMENTOS")
        print("=" * 50)

        # Verificar si ya hay documentos indexados
        existing_count = self.collection.count()
        if existing_count > 0:
            print(f"\n[INFO] La base vectorial ya contiene {existing_count} fragmentos.")
            respuesta = input("¿Desea reindexar los documentos? (s/N): ").strip().lower()
            if respuesta != "s":
                print("Indexación omitida. Usando base vectorial existente.\n")
                return existing_count
            else:
                # Limpiar colección
                print("Limpiando base vectorial existente...")
                self.chroma_client.delete_collection(COLLECTION_NAME)
                self.collection = self.chroma_client.get_or_create_collection(
                    name=COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )

        # Paso 1: Cargar documentos
        print("\n[Paso 1/3] Cargando documentos...")
        documents = self.load_documents(docs_dir)

        # Paso 2: Fragmentar
        print(f"[Paso 2/3] Fragmentando documentos "
              f"(chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
        all_chunks = []
        for content, filepath in documents:
            chunks = self.split_into_chunks(content, filepath)
            all_chunks.extend(chunks)
            print(f"  → {os.path.basename(filepath)}: {len(chunks)} fragmentos")

        print(f"\n  Total de fragmentos generados: {len(all_chunks)}")

        # Paso 3: Generar embeddings e indexar en ChromaDB
        print("\n[Paso 3/3] Generando embeddings e indexando en ChromaDB...")

        texts = [chunk["text"] for chunk in all_chunks]
        embeddings = self.generate_embeddings(texts)

        # Preparar datos para ChromaDB
        ids = [f"chunk_{i}" for i in range(len(all_chunks))]
        metadatas = [
            {
                "source": chunk["source"],
                "source_path": chunk["source_path"],
                "chunk_index": chunk["index"]
            }
            for chunk in all_chunks
        ]

        # Insertar en ChromaDB en lotes para eficiencia
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch_end = min(i + batch_size, len(all_chunks))
            self.collection.add(
                ids=ids[i:batch_end],
                embeddings=embeddings[i:batch_end],
                documents=texts[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )
            print(f"  Indexados {batch_end}/{len(all_chunks)} fragmentos...")

        total = self.collection.count()
        print(f"\n✓ Indexación completada. {total} fragmentos almacenados en ChromaDB.\n")
        return total

    # ─────────────────────────────────────────
    # 5. RECUPERACIÓN SEMÁNTICA
    # ─────────────────────────────────────────

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K
    ) -> List[dict]:
        """
        Recupera los fragmentos más relevantes para una consulta.

        Proceso:
        1. Convierte la consulta en embedding.
        2. Busca en ChromaDB por similitud coseno.
        3. Retorna los top_k fragmentos más similares.

        Args:
            query: Pregunta del usuario.
            top_k: Número de fragmentos a recuperar.

        Returns:
            Lista de dicts con 'text', 'source', 'distance' y 'chunk_index'.
        """
        if self.collection.count() == 0:
            raise ValueError(
                "La base vectorial está vacía. "
                "Ejecute primero la indexación de documentos."
            )

        # Generar embedding de la consulta
        query_embedding = self.generate_embeddings([query])[0]

        # Buscar en ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # Formatear resultados
        retrieved = []
        for i in range(len(results["documents"][0])):
            retrieved.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "source_path": results["metadatas"][0][i]["source_path"],
                "chunk_index": results["metadatas"][0][i]["chunk_index"],
                "distance": results["distances"][0][i],
                # Convertir distancia coseno a similitud (0 a 1)
                "similarity": 1 - results["distances"][0][i]
            })

        return retrieved

    def get_stats(self) -> dict:
        """Retorna estadísticas de la base vectorial."""
        return {
            "total_chunks": self.collection.count(),
            "collection_name": COLLECTION_NAME,
            "embedding_model": EMBEDDING_MODEL,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "chroma_dir": CHROMA_DIR
        }
