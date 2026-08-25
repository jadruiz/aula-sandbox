# Diagramas — Aula

## TL;DR

El servicio `lab` recibe un único workspace y secretos por entorno separado. Servicios
auxiliares usan volúmenes nombrados; no ven automáticamente el workspace.

## Montaje y servicios

```mermaid
flowchart LR
    user["Persona"] -->|"elige una carpeta"| validator["Validador de workspace"]
    validator -->|"AULA_WORKSPACE"| compose["Docker Compose"]

    subgraph host ["Host"]
        workspace["Workspace seleccionado"]
        envFile[".env de Aula"]
    end

    subgraph containers ["Contenedores"]
        lab["lab: Jupyter y CrewAI"]
        langflow["LangFlow"]
        redis["Redis"]
        optional["Letta / Flowise opcionales"]
    end

    workspace -->|"bind mount único"| lab
    envFile -.->|"variables"| lab
    envFile -.->|"variables"| langflow
    compose --> lab
    compose --> langflow
    compose --> redis
    compose --> optional
```

La flecha del `.env` representa inyección de variables, no un montaje del archivo.

## Flujo de Kasai Crew

```mermaid
sequenceDiagram
    participant H as Host
    participant K as Kasai Crew
    participant B as Bundle
    participant A as Aula
    participant P as Persona

    P->>K: Aprueba alcance de export
    K->>H: Lee inputs allowlisted
    K->>B: Escribe texto, hashes y snapshot relativo
    P->>A: Copia únicamente el bundle
    A->>B: Revalida tamaño y SHA-256
    A-->>P: Devuelve propuesta para revisión
```

El repo origen no participa en la segunda mitad: montar todo `Code/` rompería la frontera.

## Estado

- implementado: variable de workspace, validador, loopback, usuario no-root y tmpfs;
- verificado estáticamente: Compose y pruebas del validador;
- pendiente: E2E de selector/permiso en macOS, Linux y Windows;
- fuera de alcance: ejecución de código realmente no confiable.

## Siguientes lecturas

- [Quickstart](../QUICKSTART.md)
- [Frontera Kasai Crew](kasai-crew-runtime.md)
- [ADR del workspace](../../governance/decisions/ADR-003-workspace-explicito.md)
