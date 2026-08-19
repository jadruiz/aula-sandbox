# Vinculo entre planos

## Planeacion canonica

- **Ruta raiz**: el repo del curso — `Documents/Courses/Automatizacion_Colectiva_IA`
- **Documento rector**: `documentacion/guia_practica_paso_a_paso.md` (qué se practica y con qué)
- **Plano**: `planning` (el curso define QUÉ herramientas; este repo define CÓMO se levantan)

## Implementacion asociada

- **Ruta canonica**: `$CODE/ia-core/aula-sandbox`
- **Naturaleza**: empaquetado de herramientas de terceros; no implementa metodología
- **Estado**: `usable` — pendiente piloto en equipo limpio y congelado de imagen
- **Repo publicado**: <https://github.com/jadruiz/aula-sandbox>
- **Registro de imagen**: pendiente; mientras tanto se distribuye por `docker save`

## Dependencias entre repos

- **No consume** `asilo-core` ni `milpa-sdk`: los labs del curso usan frameworks públicos
  (CrewAI, LangGraph). Si el caso integrador M7 llegara a requerir los paquetes propios,
  eso abre un ADR aquí y pruebas de compatibilidad allá.
- `asilo-sandbox` queda como pieza hermana con otro modelo de amenazas; ver su ADR-002
  (perfil `course-restricted`) para la eventual convergencia.

## Regla de sincronizacion

- Un cambio en los labs del curso que agregue una librería abre un rebuild de imagen aquí.
- La imagen que usa el grupo se congela antes de la sesión 1 y no cambia a mitad de curso.
