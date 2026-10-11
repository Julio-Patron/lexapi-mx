# Lex API MX — Política de IA

Vigente desde el 2026-10-10.

## Lo que hace la API

Lex API MX es un motor normativo estructurado: devuelve texto oficial vigente,
estructura (títulos, capítulos, artículos, fracciones), fuente, checksum SHA-256
y periodo de vigencia. No genera texto con modelos de lenguaje ni emite
explicaciones, resúmenes o recomendaciones.

## Lo que se espera de los agentes y aplicaciones que la usan

1. Citar únicamente nodos devueltos por la API (`resolve`, `map`, `articulos`,
   `normas`), con su `node_version_id`, vigencia y fuente.
2. No inventar artículos, reformas, jurisprudencia ni vigencias; cuando la API
   responde `outside_coverage` o no encuentra la disposición, decirlo.
3. Presentar el texto como auxiliar informativo: no sustituye asesoría legal ni
   el criterio de una autoridad.

El servidor MCP y el SDK exponen estas mismas operaciones de solo lectura; la
responsabilidad de la redacción final es del modelo que los consume.
