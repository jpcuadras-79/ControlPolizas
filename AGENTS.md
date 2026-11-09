# AGENTS.md

Este repositorio no es un proyecto de código. Es un repositorio de documentos de pólizas de seguros.

## Contenido

- `polizas/` — 24 PDF de pólizas, nombrados `Poliza_<TIPO>-2026-<NNNN>.pdf`
  - Tipos: `AIS` (5 archivos), `PCS` (9 archivos), `SPC` (6 archivos)
  - Número secuencial de 4 dígitos (ej. `0001`, `0002`)
- `Maestro_Clientes.xlsx` — archivo Excel maestro de clientes

## Git

- Usuario configurado globalmente: `jpcuadras-79` / `jp.cuadras@gmail.com`
- No hay repositorio `.git` local inicializado en esta carpeta (por ahora).

## Comandos

No hay comandos de build, test, lint ni typecheck. No hay código que ejecutar.

## Notas para agentes

- No asumas que hay un proyecto de software aquí. No busques `package.json`, `requirements.txt`, `Makefile`, ni CI workflows — no existen.
- Si necesitas agregar una nueva póliza, sigue el patrón de nombre: `Poliza_<TIPO>-2026-<NNNN>.pdf` dentro de `polizas/`.
