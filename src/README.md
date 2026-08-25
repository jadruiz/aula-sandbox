# Fuente local de Aula

## TL;DR

Aula no contiene lógica de negocio. Su “fuente” son Dockerfile, Compose y launchers; este
archivo hace explícita la excepción del perfil `software-single` sin fingir un paquete vacío.

## Propiedad

- `infrastructure/`: imagen y servicios;
- `scripts/`: UX y validación de montaje;
- `trabajo/`: workspace predeterminado, no fuente;
- `tests/`: controles estáticos del empaquetado.

Si aparece lógica de agentes en este directorio, debe moverse al repo dueño o justificarse con
ADR. Aula empaqueta herramientas; no crea una segunda implementación de Kasai Crew o ASILO.
