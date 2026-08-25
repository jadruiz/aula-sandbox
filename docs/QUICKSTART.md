# Quickstart — arrancar Aula y elegir carpeta

## TL;DR

Usa `arrancar.command` para la carpeta `trabajo/` o `montar_carpeta.command` para elegir
otra. El selector sólo expone una carpeta y rechaza raíz, home, symlinks y `.env`.

## Ruta A · Default para el curso

1. Abre OrbStack o Docker Desktop.
2. Haz doble clic en `scripts/arrancar.command`.
3. Si crea `.env`, pega una API key desechable con límite externo, guarda y repite.
4. Abre JupyterLab en <http://localhost:8888>.

```text
aula-sandbox/trabajo/ <-> /workspace
```

## Ruta B · Montar un proyecto existente

En macOS, doble clic:

```text
scripts/montar_carpeta.command
```

En Linux o terminal:

```bash
scripts/arrancar.sh /ruta/a/mi-proyecto
```

La carpeta elegida no se copia. Lo que Jupyter escribe aparece directamente en el host.
No selecciones un repo con información que los labs o modelos no deban leer.

## Qué bloquea el validador

| Caso | Motivo |
|---|---|
| `/`, home o un padre de home | exposición excesiva del host |
| enlace simbólico | la ruta visible no prueba el destino real |
| carpeta inexistente | Compose no debe crear una ruta accidental |
| carpeta con `.env` | evita entregar secretos como datos del workspace |

Invocar Compose directamente es una operación avanzada y omite ese gate.

## Comprobar antes de abrir

```bash
docker compose -f infrastructure/docker-compose.yml config --quiet
../.venv/bin/python -m pytest
```

Después de arrancar:

```bash
docker compose -f infrastructure/docker-compose.yml ps
docker compose -f infrastructure/docker-compose.yml exec lab id
docker compose -f infrastructure/docker-compose.yml exec lab pwd
```

La salida esperada muestra usuario no-root y `/workspace`. No prueba aislamiento fuerte.

## Kasai Crew

Para una corrida gobernada no montes el repo origen. Exporta un bundle en host y copia sólo ese
archivo a la carpeta visible por Aula. Ver [frontera de runtime](architecture/kasai-crew-runtime.md).

## Apagar

```bash
docker compose -f infrastructure/docker-compose.yml down
```

El workspace permanece en host; `/tmp` se pierde. Los servicios auxiliares pueden conservar
volúmenes nombrados.

## Siguiente lectura

- [Diagramas](architecture/DIAGRAMS.md)
- [Controles ASILO adoptados](asilo/README.md)
- [Mapa completo](INDEX.md)
