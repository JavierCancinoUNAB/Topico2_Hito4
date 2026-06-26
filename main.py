"""
main.py
-------
Punto de entrada principal del Asistente RAG de Soporte Técnico.
Implementa la interfaz de línea de comandos interactiva.
"""

import os
import sys
import time

# Agregar directorio src al path de Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from rag_pipeline import RAGPipeline
from llm_integration import LLMIntegration


# ─────────────────────────────────────────────
# BANNER Y UTILIDADES DE INTERFAZ
# ─────────────────────────────────────────────

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║          ASISTENTE RAG - SOPORTE TÉCNICO INTERNO            ║
║          Ingeniería Informática · IA Embebida               ║
╚══════════════════════════════════════════════════════════════╝

Corpus documental disponible:
  • Manual de Docker
  • Manual de Linux
  • Manual de Git
  • Procedimientos de Soporte y FAQ

Comandos disponibles:
  /ayuda     → Muestra esta información
  /fuentes   → Lista los documentos indexados
  /estadisticas → Muestra estadísticas del sistema
  /modelo    → Cambia el modelo LLM
  /reindexar → Vuelve a indexar los documentos
  /salir     → Termina el programa

Escriba su pregunta y presione Enter.
"""

SEPARATOR = "─" * 65


def print_separator():
    print(f"\n{SEPARATOR}")


def print_banner():
    print(BANNER)


def print_response(result: dict, show_chunks: bool = True):
    """
    Muestra la respuesta del sistema de forma estructurada.

    Args:
        result: Diccionario con la respuesta del LLM y metadatos.
        show_chunks: Si True, muestra también los fragmentos recuperados.
    """
    print_separator()

    # Encabezado con indicador de contexto
    if result["has_context"]:
        print(f"✅ RESPUESTA (basada en {len(result['used_chunks'])} fragmentos recuperados)")
    else:
        print("⚠️  RESPUESTA (sin contexto documental suficiente)")

    print_separator()
    print(f"\n{result['answer']}\n")

    # Fuentes utilizadas
    if result["sources"]:
        print_separator()
        print("📚 FUENTES DOCUMENTALES UTILIZADAS:")
        print_separator()
        for i, source in enumerate(result["sources"], 1):
            print(f"  {i}. {source['file']}")
            print(f"     Relevancia: {source['similarity']:.1%} | "
                  f"Fragmento #{source['chunk_index']}")

    # Fragmentos recuperados (detalle opcional)
    if show_chunks and result["used_chunks"]:
        print_separator()
        print("🔍 FRAGMENTOS RECUPERADOS (contexto utilizado):")
        print_separator()
        for i, chunk in enumerate(result["used_chunks"], 1):
            print(f"\n[Fragmento {i}] Fuente: {chunk['source']} | "
                  f"Similitud: {chunk['similarity']:.1%}")
            # Mostrar solo los primeros 300 caracteres del fragmento
            preview = chunk["text"][:300]
            if len(chunk["text"]) > 300:
                preview += "..."
            print(f"  {preview}")

    print_separator()


# ─────────────────────────────────────────────
# COMANDOS ESPECIALES
# ─────────────────────────────────────────────

def handle_command(
    command: str,
    rag: RAGPipeline,
    llm: LLMIntegration
) -> bool:
    """
    Procesa comandos especiales del usuario.

    Returns:
        True si se debe continuar el loop, False si hay que salir.
    """
    cmd = command.strip().lower()

    if cmd == "/salir" or cmd == "/exit" or cmd == "/quit":
        print("\n👋 ¡Hasta luego! Sistema RAG cerrado.\n")
        return False

    elif cmd == "/ayuda" or cmd == "/help":
        print_banner()

    elif cmd == "/estadisticas":
        stats = rag.get_stats()
        print_separator()
        print("📊 ESTADÍSTICAS DEL SISTEMA RAG")
        print_separator()
        print(f"  Colección ChromaDB : {stats['collection_name']}")
        print(f"  Fragmentos totales : {stats['total_chunks']}")
        print(f"  Modelo embeddings  : {stats['embedding_model']}")
        print(f"  Tamaño de chunk    : {stats['chunk_size']} caracteres")
        print(f"  Solapamiento       : {stats['chunk_overlap']} caracteres")
        print(f"  Modelo LLM         : {llm.model}")
        print(f"  Directorio DB      : {stats['chroma_dir']}")
        print_separator()

    elif cmd == "/fuentes":
        print_separator()
        print("📄 DOCUMENTOS EN EL CORPUS")
        print_separator()
        docs_dir = "./docs"
        if os.path.exists(docs_dir):
            files = [f for f in os.listdir(docs_dir)
                     if f.endswith((".md", ".txt", ".pdf"))]
            for f in sorted(files):
                size = os.path.getsize(os.path.join(docs_dir, f))
                print(f"  • {f}  ({size:,} bytes)")
        print_separator()

    elif cmd == "/reindexar":
        print("\n🔄 Iniciando reindexación de documentos...\n")
        # Forzar reindexación eliminando la colección
        rag.chroma_client.delete_collection("soporte_tecnico")
        rag.collection = rag.chroma_client.get_or_create_collection(
            name="soporte_tecnico",
            metadata={"hnsw:space": "cosine"}
        )
        rag.index_documents()

    elif cmd.startswith("/modelo"):
        parts = command.strip().split(maxsplit=1)
        if len(parts) > 1:
            new_model = parts[1].strip()
            llm.change_model(new_model)
            print(f"\n✅ Modelo cambiado a: {new_model}\n")
        else:
            models = llm.list_available_models()
            print_separator()
            print("🤖 MODELOS DISPONIBLES EN OLLAMA")
            print_separator()
            for m in models:
                marker = "→" if llm.model in m else " "
                print(f"  {marker} {m}")
            print(f"\n  Uso: /modelo nombre_modelo")
            print_separator()

    else:
        print(f"\n  [?] Comando no reconocido: '{command}'")
        print("  Escriba /ayuda para ver los comandos disponibles.\n")

    return True


# ─────────────────────────────────────────────
# LOOP PRINCIPAL
# ─────────────────────────────────────────────

def main():
    """Función principal: inicializa el sistema y ejecuta el loop de conversación."""

    print_banner()

    # ── Inicialización ──────────────────────────────────────────
    try:
        print("🚀 Iniciando sistema RAG...\n")

        # Inicializar pipeline RAG
        rag = RAGPipeline()

        # Indexar documentos (si no están ya indexados)
        rag.index_documents()

        # Inicializar integración LLM
        print("Conectando con Ollama (LLM)...")
        llm = LLMIntegration()
        print(f"  → Modelo LLM activo: {llm.model}\n")

    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    except ConnectionError as e:
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR inesperado durante la inicialización]: {e}")
        sys.exit(1)

    print("\n✅ Sistema listo. Puede comenzar a hacer preguntas.\n")
    print(SEPARATOR)

    # ── Loop de conversación ────────────────────────────────────
    show_chunks = True  # Mostrar fragmentos recuperados por defecto

    while True:
        try:
            # Leer pregunta del usuario
            user_input = input("\n🔍 Pregunta: ").strip()

            if not user_input:
                continue

            # Verificar si es un comando especial
            if user_input.startswith("/"):
                should_continue = handle_command(user_input, rag, llm)
                if not should_continue:
                    break
                continue

            # ── Pipeline RAG ────────────────────────────────────
            print("\n⏳ Procesando consulta...", end="", flush=True)
            start_time = time.time()

            # Paso 1: Recuperación semántica
            retrieved_chunks = rag.retrieve(user_input)

            # Paso 2: Generación de respuesta con LLM
            result = llm.generate_response(user_input, retrieved_chunks)

            elapsed = time.time() - start_time
            print(f" ({elapsed:.1f}s)")

            # Paso 3: Mostrar respuesta
            print_response(result, show_chunks=show_chunks)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupción del usuario. Cerrando sistema.\n")
            break
        except ValueError as e:
            print(f"\n[ERROR] {e}")
            print("Ejecute '/reindexar' para cargar los documentos.\n")
        except Exception as e:
            print(f"\n[ERROR inesperado]: {e}")
            print("Por favor, reportelo al equipo de soporte.\n")


# ─────────────────────────────────────────────
# ENTRADA DEL PROGRAMA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    main()
