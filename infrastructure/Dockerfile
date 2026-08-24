# syntax=docker/dockerfile:1
#
# Imagen "lab" del aula: JupyterLab con las librerías de los seis labs del curso
# ya instaladas (CrewAI, LangGraph, Streamlit, Langfuse, cliente Redis).
# No contiene ninguna credencial: las claves llegan por variables de entorno
# desde el .env del estudiante en tiempo de arranque.

FROM python:3.12-slim

LABEL org.opencontainers.image.title="aula-sandbox" \
      org.opencontainers.image.description="Herramientas del curso Ecosistemas Inteligentes preinstaladas" \
      org.opencontainers.image.licenses="Apache-2.0"

# git: los labs de M6 clonan repos. build-essential: dependencias nativas de crewai-tools.
RUN apt-get update \
 && apt-get install -y --no-install-recommends git curl ca-certificates build-essential \
 && rm -rf /var/lib/apt/lists/*

# Los archivos creados dentro deben quedar utilizables desde el host.
ARG UID=1000
ARG GID=1000
RUN groupadd -g "${GID}" aula \
 && useradd -m -u "${UID}" -g "${GID}" -s /bin/bash aula

# Sin pins en el build: el pin real es la imagen construida. Quien construye
# la imagen congela el entorno; los estudiantes reciben la MISMA imagen (por
# registro o docker save), no un build propio. Ver ADR-001. La lista exacta
# de versiones queda auditable dentro de la imagen:
RUN pip install --no-cache-dir \
      jupyterlab \
      "crewai[litellm]" crewai-tools \
      langgraph langchain langchain-core langchain-openai \
      openai anthropic \
      langfuse redis \
      streamlit pandas \
      fastapi "uvicorn[standard]" \
      python-dotenv \
 && python -c "from crewai import Agent, Crew, LLM, Task; print('CrewAI API base: OK')" \
 && mkdir -p /opt/aula \
 && pip freeze > /opt/aula/versiones-instaladas.txt

# CrewAI 1.15.x crea una clave local de su listener de tracing durante el
# import y usa ~/.local/share sin respetar XDG_DATA_HOME. La ruta queda como
# symlink inmutable a /tmp: la clave es efímera y nunca persiste en HOME.
RUN mkdir -p /home/aula/.local \
 && ln -s /tmp /home/aula/.local/share \
 && chown -R aula:aula /home/aula/.local

USER aula
WORKDIR /workspace

# El resto del estado/cache compatible con XDG también queda en /tmp.
ENV XDG_DATA_HOME=/tmp/aula/xdg-data \
    XDG_CACHE_HOME=/tmp/aula/xdg-cache

# /workspace espeja la carpeta trabajo/ del host. Es el ÚNICO montaje.
VOLUME ["/workspace"]

EXPOSE 8888 8501

# Sin token: el puerto solo se publica en 127.0.0.1 del host (ver compose),
# así que únicamente quien está sentado frente a la máquina puede entrar.
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", \
     "--IdentityProvider.token=", "--ServerApp.root_dir=/workspace"]
