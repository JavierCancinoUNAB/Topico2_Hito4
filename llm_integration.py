"""
llm_integration.py
-------------------
Módulo de integración con el modelo de lenguaje (LLM) vía Ollama.
Responsable de generar respuestas fundamentadas en el contexto recuperado.
"""

import requests
import json
from typing import List, Optional


# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────

# URL de la API de Ollama (servidor local)
OLLAMA_BASE_URL = "http://localhost:11434"

# Modelo LLM a utilizar (máximo 7B según requisitos del laboratorio)
DEFAULT_MODEL = "mistral"        # Alternativas: llama3, gemma

# Umbral mínimo de similitud para considerar un fragmento relevante.
# Si ningún fragmento supera este umbral, el sistema indica falta de información.
MIN_SIMILARITY_THRESHOLD = 0.45

# Número máximo de tokens en la respuesta
MAX_TOKENS = 1024

# Temperatura del modelo (0 = determinístico, 1 = creativo)
TEMPERATURE = 0.1


# ─────────────────────────────────────────────
# CLASE LLM
# ─────────────────────────────────────────────

class LLMIntegration:
    """
    Gestiona la generación de respuestas mediante un LLM local (Ollama).

    El flujo es:
    1. Filtrar fragmentos según umbral de similitud.
    2. Construir el prompt con la pregunta + contexto recuperado.
    3. Enviar a Ollama y retornar la respuesta.
    """

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.base_url = OLLAMA_BASE_URL
        self._verify_ollama_connection()

    def _verify_ollama_connection(self):
        """Verifica que Ollama esté disponible."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                print(f"  → Ollama disponible. Modelos instalados: {models}")

                # Verificar si el modelo seleccionado está disponible
                model_available = any(
                    self.model in m for m in models
                )
                if not model_available:
                    print(f"\n  [AVISO] El modelo '{self.model}' no está instalado.")
                    print(f"  Ejecute: ollama pull {self.model}")
                    if models:
                        self.model = models[0].split(":")[0]
                        print(f"  Usando modelo disponible: {self.model}\n")
            else:
                self._raise_ollama_error()
        except requests.exceptions.ConnectionError:
            self._raise_ollama_error()

    def _raise_ollama_error(self):
        raise ConnectionError(
            "\n[ERROR] No se puede conectar con Ollama.\n"
            "Asegúrese de que Ollama esté ejecutándose:\n"
            "  1. Instalar: https://ollama.ai/download\n"
            "  2. Iniciar: ollama serve\n"
            f"  3. Descargar modelo: ollama pull {self.model}\n"
        )

    # ─────────────────────────────────────────
    # CONSTRUCCIÓN DEL PROMPT
    # ─────────────────────────────────────────

    def _build_prompt(
        self,
        query: str,
        context_chunks: List[dict]
    ) -> str:
        """
        Construye el prompt para el LLM con pregunta + contexto recuperado.

        Arquitectura del prompt:
        - Rol del sistema: Define el comportamiento del asistente.
        - Contexto: Fragmentos recuperados numerados con su fuente.
        - Instrucción: Reglas para generar la respuesta.
        - Pregunta: La consulta del usuario.

        Args:
            query: Pregunta del usuario.
            context_chunks: Fragmentos recuperados de la base vectorial.

        Returns:
            Prompt completo listo para enviar al LLM.
        """
        # Construir sección de contexto
        context_section = ""
        for i, chunk in enumerate(context_chunks, 1):
            context_section += (
                f"\n[Fuente {i}: {chunk['source']} "
                f"(similitud: {chunk['similarity']:.2%})]\n"
                f"{chunk['text']}\n"
                f"{'─' * 40}\n"
            )

        prompt = f"""Eres un asistente técnico experto de soporte informático. \
Tu rol es responder preguntas utilizando ÚNICAMENTE la información proporcionada \
en el contexto a continuación. Sé preciso, claro y cita las fuentes.

REGLAS IMPORTANTES:
1. Responde SOLO con información presente en el contexto proporcionado.
2. Si la respuesta no está en el contexto, di explícitamente: \
"No encontré información sobre esto en la documentación disponible."
3. Cita siempre qué fuente documental utilizaste (ejemplo: "Según manual_docker.md...").
4. Si hay código o comandos, inclúyelos con formato claro.
5. Responde en español.
6. Sé conciso pero completo.

CONTEXTO RECUPERADO:
{context_section}

PREGUNTA DEL USUARIO:
{query}

RESPUESTA:"""

        return prompt

    def _build_no_context_prompt(self, query: str) -> str:
        """
        Prompt para cuando no se encontraron fragmentos con similitud suficiente.
        El LLM debe indicar que no tiene información en el corpus.
        """
        return f"""Eres un asistente técnico de soporte informático. \
El sistema de búsqueda documental no encontró información relevante \
en la documentación disponible para responder la siguiente pregunta.

INSTRUCCIÓN:
Informa al usuario de forma amable que la pregunta no se puede responder \
con la documentación actual disponible. Sugiere que podría:
1. Reformular la pregunta con otros términos.
2. Consultar directamente con el equipo de soporte técnico.
3. Abrir un ticket de soporte si es un problema urgente.

No inventes información ni respondas desde tu conocimiento general \
sobre el tema, ya que el sistema está diseñado para responder \
solo desde la documentación oficial.

PREGUNTA: {query}

RESPUESTA:"""

    # ─────────────────────────────────────────
    # GENERACIÓN DE RESPUESTA
    # ─────────────────────────────────────────

    def generate_response(
        self,
        query: str,
        retrieved_chunks: List[dict],
        min_similarity: float = MIN_SIMILARITY_THRESHOLD
    ) -> dict:
        """
        Genera una respuesta usando el LLM con el contexto recuperado.

        Args:
            query: Pregunta del usuario.
            retrieved_chunks: Fragmentos recuperados de RAG.
            min_similarity: Umbral mínimo de similitud para usar un fragmento.

        Returns:
            Dict con 'answer', 'sources', 'used_chunks' y 'has_context'.
        """
        # Filtrar fragmentos por umbral de similitud
        relevant_chunks = [
            chunk for chunk in retrieved_chunks
            if chunk["similarity"] >= min_similarity
        ]

        has_context = len(relevant_chunks) > 0

        # Elegir prompt según disponibilidad de contexto
        if has_context:
            prompt = self._build_prompt(query, relevant_chunks)
        else:
            prompt = self._build_no_context_prompt(query)

        # Llamar a Ollama API
        response_text = self._call_ollama(prompt)

        # Extraer fuentes únicas de los fragmentos usados
        sources = []
        if has_context:
            seen = set()
            for chunk in relevant_chunks:
                source = chunk["source"]
                if source not in seen:
                    sources.append({
                        "file": source,
                        "similarity": chunk["similarity"],
                        "chunk_index": chunk["chunk_index"]
                    })
                    seen.add(source)

        return {
            "answer": response_text,
            "sources": sources,
            "used_chunks": relevant_chunks,
            "has_context": has_context,
            "model_used": self.model
        }

    def _call_ollama(self, prompt: str) -> str:
        """
        Llama a la API de Ollama para generar texto.

        Args:
            prompt: Prompt completo para el modelo.

        Returns:
            Texto generado por el modelo.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": TEMPERATURE,
                "num_predict": MAX_TOKENS,
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120  # 2 minutos máximo para modelos lentos
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()

        except requests.exceptions.Timeout:
            return (
                "[ERROR] El modelo tardó demasiado en responder. "
                "Intente con un modelo más pequeño o espere un momento."
            )
        except requests.exceptions.RequestException as e:
            return f"[ERROR] No se pudo obtener respuesta del modelo: {str(e)}"
        except json.JSONDecodeError:
            return "[ERROR] La respuesta del modelo no pudo ser procesada."

    def list_available_models(self) -> List[str]:
        """Lista los modelos disponibles en Ollama."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            models = [m["name"] for m in resp.json().get("models", [])]
            return models
        except Exception:
            return []

    def change_model(self, model_name: str):
        """Cambia el modelo LLM en uso."""
        self.model = model_name
        print(f"  → Modelo cambiado a: {self.model}")
