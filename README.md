# aula-sandbox

> Las herramientas del curso **Ecosistemas Inteligentes** en contenedores. Instalar el aula
> son dos pasos: instalar [OrbStack](https://orbstack.dev) y hacer doble clic en
> `scripts/arrancar.command`.

**Perfil Milpa:** `software-single` (P2) · **Distribución prevista:** carpeta + imagen Docker · **Estado:** usable en aula

## Qué es (y qué no es)

Este repo empaqueta las **herramientas** de los labs para que nadie pierda una sesión
peleando con `pip`: JupyterLab con CrewAI/LangGraph ya instalados, LangFlow para construir
agentes sin programar, Redis para el lab de observabilidad y Letta para la demo de memoria.

**No es `asilo-sandbox`.** Aquel repo aísla a un agente autónomo con acceso a archivos y
sigue bloqueado hasta pasar revisión de seguridad. Aquí el modelo de amenazas es el de un
aula: el código lo escribe y ejecuta el estudiante, la única credencial es una clave
desechable con tope de gasto, y el único montaje es la carpeta `trabajo/`. Ver
`governance/decisions/ADR-001-alcance-y-frontera.md`.

## Arranque

1. **Instala OrbStack** — <https://orbstack.dev> → Download → arrastra a Aplicaciones →
   ábrelo una vez. (Docker Desktop también sirve; OrbStack es más ligero.)
2. **Descarga esta carpeta** — en <https://github.com/jadruiz/aula-sandbox>, botón verde
   **Code → Download ZIP**, y descomprime donde quieras (por ejemplo `Documentos`). Si usas
   git: `git clone https://github.com/jadruiz/aula-sandbox.git`.
3. **Doble clic en `scripts/arrancar.command`.** La primera vez te crea el `.env` y lo abre
   para que pegues tu clave; el segundo doble clic construye la imagen (10–15 min la
   primera vez) y levanta todo.
4. Abre las herramientas en el navegador:

| URL | Herramienta | Para qué |
|-----|-------------|----------|
| <http://localhost:8888> | JupyterLab | Labs M1–M6 (código y terminal) |
| <http://localhost:7860> | LangFlow | Construir agentes arrastrando cajas (Ruta B) |
| <http://localhost:8501> | Streamlit | Panel del Firewall Ético (M4, al correr `streamlit run`) |
| <http://localhost:8283> | Letta | Memoria persistente (M5) · `--profile memoria` |
| <http://localhost:3001> | Flowise | Alternativa a LangFlow · `--profile flowise` |

Para apagar: doble clic en `scripts/detener.command`. Los flujos de LangFlow y la memoria
de Letta sobreviven en volúmenes; la carpeta `trabajo/` es tuya y vive en el host.

## La carpeta `trabajo/`

```
aula-sandbox/trabajo/        ←→   /workspace/   (dentro del contenedor lab)
   ↑ lo que ves en Finder          ↑ lo que ve JupyterLab
```

Es la misma carpeta vista desde dos lados: copia ahí los archivos del lab del día y
aparecen en Jupyter; lo que guardes en Jupyter aparece en Finder. Es el **único** montaje.

## Contención honesta

Docker aporta contención **parcial**, no aislamiento absoluto: comparte el kernel y la red.
Lo que este diseño sí garantiza y por qué alcanza para un aula:

- Ningún puerto sale de `127.0.0.1`: nadie más en la red del salón puede entrar.
- Ninguna clave queda dentro de la imagen; viven en tu `.env`, que no se versiona.
- El contenedor no corre como root y solo ve `trabajo/`.
- La clave del curso debe ser **desechable y con tope de gasto** (5 USD bastan). Si se
  filtra, se revoca y se pierde el tope, no tu cuenta.
- LangFlow arranca con la telemetría apagada (`LANGFLOW_DO_NOT_TRACK=true`).

Lo que NO cubre: código malicioso que tú mismo pegues y ejecutes con tu clave. El firewall
para eso es M4 del curso, no este contenedor.

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
| [`milpa-sdk`](https://codeberg.org/kasailabs/milpa-sdk) · Codeberg | Implementación de la Metodología Milpa (roles Maíz/Frijol/Calabaza de M2) | Lo lee cuando M2 lo cite; no necesita instalarlo |
| [`asilo-core`](https://codeberg.org/kasailabs/asilo-core) · Codeberg | Implementación del marco ASILO (gobernanza de M4 y M7) | Lo lee en M7; no necesita instalarlo |
| [`asilo-sandbox`](https://github.com/jadruiz/asilo-sandbox) · GitHub | Prototipo de aislamiento para agentes autónomos | **Solo lectura**: su README explica por qué aún no se usa |

## Para docentes

- Construye la imagen **antes** de la sesión 1 (`scripts/arrancar.sh`) y con el wifi del
  salón en mente: repártela por `docker save kasailabs/aula-sandbox:dev -o aula.tar` +
  `docker load -i aula.tar`, en lugar de que 25 máquinas la construyan a la vez.
- No cambies la lista de librerías a mitad de curso: rompe la reproducibilidad del grupo
  (regla 3 de `AGENTS.md`).
- Letta y Flowise arrancan bajo perfil: `docker compose -f infrastructure/docker-compose.yml --profile memoria up -d` (ídem `--profile flowise`).
- Al cierre del curso recuerda al grupo revocar sus claves.

## Licencia

Apache-2.0 — texto completo en [`LICENSE`](LICENSE).

Este repo **no redistribuye** software de terceros: declara imágenes que Docker descarga,
cada una con su propia licencia. Ver [`NOTICE`](NOTICE) antes de repartir una imagen construida.
