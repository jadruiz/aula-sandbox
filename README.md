# aula-sandbox

> Las herramientas del curso **Ecosistemas Inteligentes** en contenedores. Instalar el aula
> son dos pasos: instalar [OrbStack](https://orbstack.dev) y hacer doble clic en
> `scripts/arrancar.command`. El primer arranque es offline: no pide API key.

**Perfil Milpa:** `software-single` (P2) · **Distribución prevista:** carpeta + imagen Docker · **Estado:** usable en aula

## TL;DR

- Doble clic en `scripts/arrancar.command`: monta `trabajo/` y levanta el aula sin credenciales.
- Doble clic en `scripts/montar_carpeta.command`: elige otra carpeta sin copiarla.
- Siempre hay un solo bind mount para `lab`; raíz, home, symlinks y carpetas con `.env` se rechazan.
- Aula es contención educativa parcial, no `asilo-sandbox` ni una frontera para código hostil.
- Para Kasai Crew se copian bundles; nunca se monta todo el ecosistema.

Empieza por la [guía rápida](docs/QUICKSTART.md), mira los
[diagramas](docs/architecture/DIAGRAMS.md) y usa el [índice piramidal](docs/INDEX.md).

## Qué es (y qué no es)

Este repo empaqueta las **herramientas** de los labs para que nadie pierda una sesión
peleando con `pip`: JupyterLab con CrewAI/LangGraph ya instalados, LangFlow para construir
agentes sin programar, Redis para el lab de observabilidad y Letta para la demo de memoria.

**No es `asilo-sandbox`.** Aquel repo aísla a un agente autónomo con acceso a archivos y
sigue bloqueado hasta pasar revisión de seguridad. Aquí el modelo de amenazas es el de un
aula: el código lo escribe y ejecuta el estudiante. Si un laboratorio usa un proveedor,
la credencial debe ser desechable y tener un tope configurado en el proveedor; el único bind
mount del host para
el servicio `lab` es la carpeta `trabajo/`. Ver
`governance/decisions/ADR-001-alcance-y-frontera.md`.

## Arranque

1. **Instala OrbStack** — <https://orbstack.dev> → Download → arrastra a Aplicaciones →
   ábrelo una vez. (Docker Desktop también sirve; OrbStack es más ligero.)
2. **Descarga esta carpeta** — en <https://github.com/jadruiz/aula-sandbox>, botón verde
   **Code → Download ZIP**, y descomprime donde quieras (por ejemplo `Documentos`). Si usas
   git: `git clone https://github.com/jadruiz/aula-sandbox.git`.
3. **Doble clic en `scripts/arrancar.command`.** La primera vez crea un `.env` vacío y
   construye la imagen (10–15 min la primera vez); no necesitas una clave para abrir el aula.
   Si un laboratorio posterior requiere un proveedor, configura una clave desechable con hard cap
   en `.env` y vuelve a ejecutar. Nunca la guardes en `trabajo/`.
   Si quieres trabajar sobre otra carpeta sin copiarla, usa
   `scripts/montar_carpeta.command`; el selector valida la frontera antes de arrancar.
4. Abre las herramientas en el navegador:

| URL | Herramienta | Para qué |
|-----|-------------|----------|
| <http://localhost:8888> | JupyterLab | Labs M1–M6 (código y terminal) |
| <http://localhost:7860> | LangFlow | Construir agentes arrastrando cajas (Ruta B) |
| <http://localhost:8501> | Streamlit | Panel de compuerta de política (M4, al correr `streamlit run`) |
| <http://localhost:8283> | Letta | Memoria persistente (M5) · `--profile memoria` |
| <http://localhost:3001> | Flowise | Alternativa a LangFlow · `--profile flowise` |

Para apagar: doble clic en `scripts/detener.command`. Los flujos de LangFlow y la memoria
de Letta sobreviven en volúmenes; la carpeta `trabajo/` es tuya y vive en el host.

## La carpeta montada

```
aula-sandbox/trabajo/        ←→   /workspace/   (dentro del contenedor lab)
   ↑ lo que ves en Finder          ↑ lo que ve JupyterLab
```

Es la misma carpeta vista desde dos lados: copia ahí los archivos del lab del día y
aparecen en Jupyter; lo que guardes en Jupyter aparece en Finder. También puedes elegir
otra carpeta explícita. En ambos casos es el **único bind mount del host de `lab`**;
`/tmp` es tmpfs efímero y servicios auxiliares usan volúmenes nombrados separados.

En terminal:

```bash
scripts/arrancar.sh /ruta/a/mi-proyecto
```

El validador rechaza montajes demasiado amplios y carpetas con `.env`. Esto reduce exposición;
no convierte Docker en aislamiento absoluto.

## Contención honesta

Docker aporta contención **parcial**, no aislamiento absoluto: comparte el kernel/runtime y la red.
Lo que la configuración pretende y el baseline verificó sólo en parte:

- Ningún puerto sale de `127.0.0.1`: nadie más en la red del salón puede entrar.
- Ninguna clave queda dentro de la imagen; si existe una, vive en tu `.env`, que no se versiona.
- El proceso `lab` no corre como root y no recibe otros bind mounts del host; también ve su
  filesystem de imagen, tmpfs y recursos que Docker expone.
- Si un laboratorio usa una clave, debe ser **desechable, de mínimo alcance y con un hard cap pequeño
  definido por el docente/owner**. El compose no crea ni verifica ese tope.
- LangFlow arranca con la telemetría apagada (`LANGFLOW_DO_NOT_TRACK=true`).

Lo que NO cubre: código malicioso que tú mismo pegues y ejecutes con tu clave, procesos locales que
accedan a un puerto loopback sin token ni una dependencia que lea variables de entorno. M4 enseña
compuertas y red teaming; no debe presentarse como protección completa del contenedor.

## Reproducibilidad

Las librerías se instalan sin pin **en el build**, y el pin real es la **imagen**: el
instructor la construye una vez y la reparte (registro o `docker save`); todo el grupo corre
bits idénticos. La lista exacta quedó dentro: `cat /opt/aula/versiones-instaladas.txt`.

## Guía de uso en el curso

La guía paso a paso por sesión (qué plataforma abrir, en qué sección, cómo crear tu primer
agente) vive en el repo del curso: `documentacion/guia_practica_paso_a_paso.md`.

## Ecosistema de repositorios

| Repo | Qué es | El estudiante… |
|------|--------|----------------|
| **`aula-sandbox`** (este) · [GitHub](https://github.com/jadruiz/aula-sandbox) | Las herramientas del curso en contenedores | Lo descarga y lo usa toda sesión |
| [`milpa-sdk`](https://codeberg.org/kasailabs/milpa-sdk) · Codeberg | Proyección Python candidata; loader y validación de perfil ya son ejecutables, roles/dominios siguen diferidos | Lo usa para estructura, no como control de acceso |
| [`asilo-core`](https://codeberg.org/kasailabs/asilo-core) · Codeberg | Implementación candidata; schema/status ejecutan, política/HITL/audit siguen stubs | Usa sólo capacidades verificadas, nunca el nombre como enforcement |
| [`asilo-sandbox`](https://github.com/jadruiz/asilo-sandbox) · GitHub | Prototipo de aislamiento para agentes autónomos | **Solo lectura**: su README explica por qué aún no se usa |
| **`kasai-crew`** (local; publicación pendiente) | Un plano de control para todos los repos Kasai | Solo bundles revisados; no montar el ecosistema completo |

La frontera prevista para `kasai-crew` está documentada en
[`docs/architecture/kasai-crew-runtime.md`](docs/architecture/kasai-crew-runtime.md). No está
habilitada aún: la topología ya pasó un smoke offline desde source read-only, pero falta una wheel
revisada con hash y su fixture E2E en la imagen congelada.

## Para docentes

- Construye la imagen **antes** de la sesión 1 (`scripts/arrancar.sh`) y con el wifi del
  salón en mente: repártela por `docker save kasailabs/aula-sandbox:dev -o aula.tar` +
  `docker load -i aula.tar`, en lugar de que 25 máquinas la construyan a la vez.
- No cambies la lista de librerías a mitad de curso: rompe la reproducibilidad del grupo
  (regla 3 de `AGENTS.md`).
- Letta y Flowise arrancan bajo perfil: `docker compose -f infrastructure/docker-compose.yml --profile memoria up -d` (ídem `--profile flowise`).
- Al cierre del curso recuerda al grupo revocar sus claves.
- Para una carpeta distinta usa el selector o `scripts/arrancar.sh /ruta`; no edites Compose
  ni montes home/raíz para “hacerlo rápido”.

## Licencia

Apache-2.0 — texto completo en [`LICENSE`](LICENSE).

Este repo **no redistribuye** software de terceros: declara imágenes que Docker descarga,
cada una con su propia licencia. Ver [`NOTICE`](NOTICE) antes de repartir una imagen construida.
