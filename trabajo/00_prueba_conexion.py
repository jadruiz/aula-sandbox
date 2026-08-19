"""Prueba de conexión: confirma que tu clave funciona antes de empezar el lab.

Dentro del contenedor la clave ya llegó como variable de entorno desde tu .env;
fuera de él, lee el .env de la carpeta del sandbox si existe.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

clave = os.getenv("OPENAI_API_KEY", "")
modelo = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

if not clave or "PEGA-AQUI" in clave:
    raise SystemExit(
        "❌ No hay clave. Edita el archivo .env de la carpeta aula-sandbox,\n"
        "   pega tu OPENAI_API_KEY y reinicia con scripts/arrancar.command."
    )

try:
    from openai import OpenAI
    respuesta = OpenAI(api_key=clave).chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": "Responde solo: listo"}],
        max_tokens=5,
    )
    print(f"✅ Conexión buena · modelo {modelo} respondió: {respuesta.choices[0].message.content!r}")
except Exception as exc:  # el mensaje llano importa más que el tipo exacto
    nombre = type(exc).__name__
    if "Authentication" in nombre:
        print("❌ La clave no es válida (¿la copiaste completa, sin espacios?).")
    elif "RateLimit" in nombre or "insufficient_quota" in str(exc):
        print("❌ La clave funciona pero no tiene crédito. Revisa Billing en platform.openai.com.")
    else:
        print(f"❌ Falló la conexión: {nombre}. Haz captura y mándala al instructor.")
    raise SystemExit(1)
