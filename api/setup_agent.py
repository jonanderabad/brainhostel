"""
One-time setup script: creates the Claude Managed Agent and Environment.
Run this once locally. It prints AGENT_ID and ENV_ID — add them to your .env.

Usage:
    python setup_agent.py
"""

import os
import anthropic
from dotenv import load_dotenv
from wiki_loader import load_wiki

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env")

client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
    default_headers={"anthropic-beta": "managed-agents-2026-04-01"},
)

SYSTEM_PROMPT_TEMPLATE = """\
Eres BRAINHOSTEL, un asistente especializado en el Convenio Colectivo de Hostelería de Bizkaia 2025.

Tu misión es responder preguntas de trabajadores y responsables de hostelería sobre sus derechos y \
condiciones laborales según este convenio.

Instrucciones:
- Responde siempre en español.
- Sé preciso y cita el artículo o sección del convenio cuando sea relevante.
- Si la pregunta no está cubierta por el convenio, dilo explícitamente y con claridad.
- No inventes cifras ni plazos: si no lo sabes con certeza, dilo.
- Mantén un tono profesional pero cercano.

=== BASE DE CONOCIMIENTO: WIKI DEL CONVENIO ===

{wiki_content}
"""


def main():
    print("Cargando wiki...")
    wiki_content = load_wiki()
    print(f"Wiki cargada: {len(wiki_content):,} caracteres ({len(wiki_content) // 4:,} tokens aprox.)")

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(wiki_content=wiki_content)

    print("\nCreando environment...")
    environment = client.beta.environments.create(
        name="brainhostel-env",
        config={
            "type": "cloud",
            "networking": {"type": "unrestricted"},
        },
    )
    print(f"Environment creado: {environment.id}")

    print("\nCreando agente...")
    agent = client.beta.agents.create(
        name="brainhostel",
        model="claude-haiku-4-5-20251001",
        system=system_prompt,
        tools=[],
    )
    print(f"Agente creado: {agent.id}")

    print("\n" + "=" * 50)
    print("Añade estas variables a tu .env y a Railway:")
    print(f"AGENT_ID={agent.id}")
    print(f"ENV_ID={environment.id}")
    print("=" * 50)


if __name__ == "__main__":
    main()
