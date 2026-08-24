# Agente — aula-sandbox

> Contrato de arranque. Todo lo que no está aquí se **enlaza**, no se copia.
> Mapa documental: [`docs/INDEX.md`](docs/INDEX.md) · Vínculo de planos: [`SOURCE.md`](SOURCE.md)

## Qué es este repo

Compose + imagen Docker (perfil Milpa `software-single`) con las herramientas del curso
Ecosistemas Inteligentes. **No** contiene lógica de negocio ni material didáctico: solo
empaqueta y arranca. El material vive en el repo del curso; la metodología, en `asilo-core`.

## Axiomas

| ID | Axioma |
|----|--------|
| AX-01 | Ningún secreto queda dentro de la imagen (`ENV`, `ARG` o capa copiada) |
| AX-02 | El único bind mount del host es `trabajo/`; estado efímero sólo en tmpfs `/tmp` |
| AX-03 | El proceso dentro del contenedor nunca corre como root |
| AX-04 | Ningún puerto se publica fuera de `127.0.0.1` |
| AX-05 | Telemetría de terceros apagada donde la herramienta lo permita |

## Reglas

1. **Esto no es asilo-sandbox.** No agregar aquí montajes de host, launchers de agentes
   autónomos ni promesas de aislamiento fuerte; eso vive (bloqueado) en `asilo-sandbox`.
2. **Ninguna credencial en ningún archivo versionado.** Las claves viven en el `.env` del
   estudiante, que `.gitignore` excluye.
3. **El pin es la imagen, no el Dockerfile.** Cambiar la lista de librerías exige
   reconstruir y redistribuir la imagen a todo el grupo, no editarla a mitad de curso.
4. **Los mensajes de los scripts van dirigidos a alguien que no programa.**
5. Los hallazgos que no son código van a `reports/` como `YYYY-MM-DD-tema.md`.

## Done

- [ ] `docker compose -f infrastructure/docker-compose.yml config` valida sin errores.
- [ ] La imagen construye desde cero y `versiones-instaladas.txt` queda dentro.
- [ ] Doble clic en `arrancar.command` llega a Jupyter y LangFlow en un equipo limpio.
- [ ] Lo creado en Jupyter aparece en `trabajo/` con permisos utilizables.
- [ ] Todo doc nuevo enlazado desde `docs/INDEX.md`.
