"""
test_escenarios.py
------------------
Script de prueba automatizada que ejecuta los 3 escenarios de demostración
obligatorios según la rúbrica de evaluación.

Escenario 1: Consulta simple con respuesta directa en el corpus.
Escenario 2: Consulta compleja que requiere integrar información.
Escenario 3: Consulta sin respuesta en el corpus (manejo de ausencia).
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from rag_pipeline import RAGPipeline
from llm_integration import LLMIntegration


# ─────────────────────────────────────────────
# PREGUNTAS DE DEMOSTRACIÓN
# ─────────────────────────────────────────────

TEST_CASES = [
    {
        "escenario": 1,
        "tipo": "Consulta Simple",
        "descripcion": "Pregunta directa con respuesta explícita en el corpus.",
        "query": "¿Cómo crear una imagen Docker?",
        "esperado": "Debe responder con el comando 'docker build' y mencionar el Dockerfile."
    },
    {
        "escenario": 2,
        "tipo": "Consulta Compleja",
        "descripcion": "Pregunta que requiere integrar información de múltiples secciones.",
        "query": (
            "¿Qué debo hacer si encuentro un virus en mi computador "
            "y cómo abro un ticket de soporte urgente?"
        ),
        "esperado": "Debe combinar procedimiento de seguridad + apertura de ticket con prioridad crítica."
    },
    {
        "escenario": 3,
        "tipo": "Consulta Sin Respuesta Documental",
        "descripcion": "Pregunta cuya respuesta no existe en el corpus disponible.",
        "query": (
            "¿Cuál es la receta para preparar una torta de chocolate "
            "con tres capas de betún?"
        ),
        "esperado": "Debe indicar que no hay información en la documentación disponible."
    }
]

# Preguntas adicionales de ejemplo
EXTRA_TESTS = [
    "¿Cómo actualizar un repositorio Git con los últimos cambios remotos?",
    "¿Cómo visualizar los procesos en ejecución en Linux?",
    "¿Qué comandos uso para ver el espacio disponible en disco?",
    "¿Cómo mapear puertos en Docker?",
    "¿Cómo puedo restablecer mi contraseña corporativa?",
    "¿Cuánto tiempo se conservan los backups semanales?",
    "¿Cuáles son las políticas de seguridad de contraseñas?",
    "¿Qué es el precio de las acciones de Tesla hoy?"  # Sin contexto
]


# ─────────────────────────────────────────────
# FUNCIÓN DE PRUEBA
# ─────────────────────────────────────────────

def run_test(rag: RAGPipeline, llm: LLMIntegration, test_case: dict):
    """Ejecuta un caso de prueba y muestra resultados detallados."""
    print(f"\n{'═' * 65}")
    print(f"  ESCENARIO {test_case['escenario']}: {test_case['tipo'].upper()}")
    print(f"{'═' * 65}")
    print(f"  Descripción : {test_case['descripcion']}")
    print(f"  Resultado   : {test_case['esperado']}")
    print(f"{'─' * 65}")
    print(f"  PREGUNTA: {test_case['query']}")
    print(f"{'─' * 65}")

    start = time.time()

    # Recuperación semántica
    print("\n  [1/2] Recuperando fragmentos relevantes...")
    chunks = rag.retrieve(test_case["query"])

    print(f"  → {len(chunks)} fragmentos recuperados:")
    for i, chunk in enumerate(chunks, 1):
        print(f"     {i}. [{chunk['source']}] similitud={chunk['similarity']:.1%}")

    # Generación de respuesta
    print("\n  [2/2] Generando respuesta con LLM...")
    result = llm.generate_response(test_case["query"], chunks)

    elapsed = time.time() - start

    # Resultado
    print(f"\n{'─' * 65}")
    context_indicator = "✅ CON CONTEXTO" if result["has_context"] else "⚠️  SIN CONTEXTO"
    print(f"  RESPUESTA [{context_indicator}] (tiempo: {elapsed:.1f}s)")
    print(f"{'─' * 65}")
    print(f"\n{result['answer']}\n")

    if result["sources"]:
        print(f"{'─' * 65}")
        print("  FUENTES UTILIZADAS:")
        for src in result["sources"]:
            print(f"    • {src['file']} (relevancia: {src['similarity']:.1%})")

    return result


def run_all_tests():
    """Ejecuta todos los escenarios de demostración."""
    print("\n" + "═" * 65)
    print("   EJECUCIÓN DE ESCENARIOS DE DEMOSTRACIÓN - SISTEMA RAG")
    print("   Asignatura: IA Embebida en Sistemas Computacionales")
    print("=" * 65)

    # Inicializar sistema
    print("\n⏳ Inicializando sistema RAG...\n")
    rag = RAGPipeline()
    rag.index_documents()
    llm = LLMIntegration()

    print(f"\n✅ Sistema listo. Modelo LLM: {llm.model}")
    print(f"   Fragmentos en base vectorial: {rag.get_stats()['total_chunks']}\n")

    # Ejecutar escenarios obligatorios
    print("\n📋 EJECUTANDO ESCENARIOS OBLIGATORIOS (3/3)")
    results = []
    for test_case in TEST_CASES:
        result = run_test(rag, llm, test_case)
        results.append(result)
        time.sleep(1)  # Pausa entre pruebas

    # Resumen
    print(f"\n{'═' * 65}")
    print("   RESUMEN DE EJECUCIÓN")
    print(f"{'═' * 65}")
    for i, (test, result) in enumerate(zip(TEST_CASES, results), 1):
        status = "✅" if result["has_context"] else "⚠️ "
        print(f"  Escenario {i} ({test['tipo']:<30}) {status} "
              f"{'Contexto encontrado' if result['has_context'] else 'Sin contexto (correcto para E3)'}")

    print(f"\n{'─' * 65}")
    print("  PREGUNTAS EXTRA SUGERIDAS PARA LA DEMOSTRACIÓN:")
    print(f"{'─' * 65}")
    for q in EXTRA_TESTS:
        print(f"  • {q}")

    print(f"\n{'═' * 65}")
    print("  Todos los escenarios completados exitosamente.")
    print(f"{'═' * 65}\n")


# ─────────────────────────────────────────────
# MODO INTERACTIVO DE PRUEBA
# ─────────────────────────────────────────────

def interactive_test():
    """Modo interactivo para probar preguntas individualmente."""
    print("\n" + "═" * 65)
    print("   MODO DE PRUEBA INTERACTIVO")
    print("═" * 65)

    rag = RAGPipeline()
    rag.index_documents()
    llm = LLMIntegration()

    print(f"\n✅ Sistema listo. Escribe 'salir' para terminar.\n")

    while True:
        query = input("\n🔍 Pregunta de prueba: ").strip()
        if query.lower() in ("salir", "exit", "quit"):
            break
        if not query:
            continue

        chunks = rag.retrieve(query)
        result = llm.generate_response(query, chunks)

        print(f"\n{'─' * 65}")
        print(f"RESPUESTA ({'con contexto' if result['has_context'] else 'sin contexto'}):")
        print(f"{'─' * 65}")
        print(result["answer"])

        if result["sources"]:
            print("\nFUENTES:")
            for src in result["sources"]:
                print(f"  • {src['file']} ({src['similarity']:.1%})")


# ─────────────────────────────────────────────
# ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Script de prueba del Sistema RAG de Soporte Técnico"
    )
    parser.add_argument(
        "--modo",
        choices=["escenarios", "interactivo"],
        default="escenarios",
        help="Modo de ejecución: 'escenarios' (demo obligatoria) o 'interactivo'"
    )

    args = parser.parse_args()

    if args.modo == "interactivo":
        interactive_test()
    else:
        run_all_tests()
