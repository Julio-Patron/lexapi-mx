# Contrato de paquete normativo v1

## Propósito

Un paquete normativo es la unidad estable que Lex API MX entrega a otro
sistema. No es una respuesta libre ni una conclusión jurídica: es un conjunto
de normas y nodos con versión, cita, texto, fuente, checksum, cobertura y
trazabilidad verificables.

La versión inicial del contrato es `1.0` y se expone mediante
`POST /api/v1/resolve`.

## Identificadores

Los UUID de base de datos se conservan para trazabilidad interna. Los
identificadores públicos estables usan URN versionadas:

| Entidad | Formato |
| --- | --- |
| Norma | `urn:lexapi-mx:norm:v1:{slug}` |
| Nodo | `urn:lexapi-mx:node:v1:{stable_identifier}` |
| Versión de nodo | `urn:lexapi-mx:node-version:v1:{uuid}` |
| Cita | `urn:lexapi-mx:citation:v1:{stable_identifier}` |
| Paquete | `urn:lexapi-mx:package:v1:{sha256}` |

El `package_id` se calcula sobre versión de contrato, consulta normalizada,
fecha solicitada y versiones devueltas: las de cada item y, cuando un artículo
trae `full_text`, las de sus fracciones e incisos. La misma consulta sobre las
mismas versiones produce el mismo identificador.

## Citas

Cada resultado declara:

- `canonical`: texto humano, por ejemplo `Artículo 47 LFT`;
- `urn`: identificador de cita ligado al nodo;
- `origin`: `citation_catalog` o `node_metadata`;
- `status`: `canonical`, `derived` o `ambiguous_legacy`;
- `ambiguity_count`: nodos que competían por la misma cita humana.

Una cita `derived` es reproducible pero todavía no está acreditada en
`legal_citations`. Una cita `ambiguous_legacy` nunca debe tratarse como una
selección jurídica exhaustiva. El resolvedor conserva el primer nodo por orden
oficial, omite duplicados humanos y emite advertencia.

Un artículo transitorio (`"Artículo 2 transitorio LFT"`) resuelve al nodo
`transitorio` de su norma. Cada sección de transitorios numera los suyos (la de la
ley y la del decreto que la expide): si el número se repite, van todos los nodos
en el orden del documento, cada uno `ambiguous_legacy` con su `ambiguity_count`,
y `warnings` lo explica.

Los números compuestos (`1390 Bis 1`, `195-Z-40`, `58-14`) se conservan tal
cual en las citas.

## Artículo completo

En el corpus cada artículo es un árbol: el nodo del artículo lleva el
encabezado y cada fracción, inciso o apartado es un nodo con su propia versión.
Cuando el nodo de un item es un artículo, el item agrega tres campos opcionales:

- `full_text`: el artículo con sus fracciones, incisos y apartados en el orden
  del documento; fracciones e incisos llevan su marcador («I.», «a)»);
- `full_text_checksum`: SHA-256 de `full_text`;
- `components`: cada nodo que forma `full_text`, el artículo primero, con su
  `node_version_id`, el checksum de su versión almacenada y su vigencia.

`text` y `version` siguen siendo los del nodo del artículo.

## Cobertura temporal

La política general es `current_baseline_and_prospective`:

- `coverage_start_date` es la fecha operativa desde la que Lex API MX conserva
  cobertura verificable de esa norma;
- `valid_from` y `valid_to` describen el intervalo de la versión almacenada;
- una fecha anterior al baseline devuelve `outside_coverage`;
- una fecha futura devuelve `future_not_available`: la API no pronostica
  reformas;
- `historical_audit` es siempre `false` en el contrato general;
- `retrospective_exception` sólo podrá contener un código aprobado para una
  norma y un caso de uso concretos. No habilita auditoría histórica general.

Las primeras excepciones candidatas siguen limitadas a pensiones y seguridad
social cuando la fecha determine el régimen aplicable. Requieren un registro y
evidencia propios antes de exponerse.

## Recuperación

La estrategia activa es `structured_full_text`:

1. resuelve slug, alias o sigla de norma;
2. reconoce citas explícitas y números compuestos;
3. infiere norma por términos jurídicos significativos;
4. consulta `search_vector` sobre versiones oficiales;
5. ordena resultados y elimina citas humanas duplicadas;
6. devuelve fuente y versión exactas usadas.

`semantic_available` y `semantic_used` permanecen en `false` mientras no exista
un modelo aprobado, embeddings completos y un benchmark jurídico que demuestre
mejora de recall. La base estructurada continúa siendo la fuente de verdad.

## Compatibilidad

- Campos existentes de `1.0` no cambian de significado.
- Nuevos campos opcionales pueden añadirse sin romper consumidores.
- Cambios incompatibles requieren `contract_version` y URN de versión nuevas.
- Un modelo de recuperación distinto debe declararse en `retrieval.strategy`.
