# Lex API MX — Especificación de API

**Base URL:** `https://api.lexapi.mx/api/v1` · Guía: [lexapi.mx/docs](https://lexapi.mx/docs)
· Referencia interactiva: [lexapi.mx/docs/api](https://lexapi.mx/docs/api) · Contrato OpenAPI:
[`openapi-v1.json`](openapi-v1.json)

---

## Autenticación y uso

- Todas las rutas `/api/v1/*` exigen la cabecera `X-API-Key` con una clave creada
  en [lexapi.mx/cuenta](https://lexapi.mx/cuenta). Cada operación valida su
  scope: `norms:read`, `articles:read`, `resolve:run`, `billing:read` y, en los
  planes de la API, `map:read`.
- Solo se cobran respuestas `2xx` con resultado, en créditos por operación
  ([`CATALOGO.md`](CATALOGO.md)): una búsqueda sin artículos responde `200` con
  `data: []` y la cabecera `X-Normative-Metering: skipped`, sin cargo, igual que
  un paquete de `POST /resolve` sin items. Un reintento con la misma
  `Idempotency-Key` y la misma petición no se cobra dos veces.
- Sin saldo la API responde `402` con `code: insufficient_credits` y el enlace
  para contratar; una operación de los planes de la API (mapa normativo, texto
  completo de una norma) con una clave del plan gratuito responde `403` con
  `code: paid_plan_required`, `message` y `upgrade_url`; sin otro scope, `403`
  con un texto plano; por encima del límite de peticiones, `429` con
  `Retry-After`. Límites: plan gratuito, 10 peticiones por minuto y 200 por día
  (UTC) por cuenta, sumando todas sus claves, y hasta 2 claves activas; planes de
  la API, 120 por minuto por clave en normas y artículos, 60 en `resolve` y `map`,
  y hasta 10 claves. Los límites vigentes de cada plan los publica la API:
  `GET /api/v1/checkout/catalog` (campo `limits` de cada plan, sin clave) y
  `GET /api/v1/account` (`plan.limits`, con la sesión de la cuenta), con
  `max_active_keys`, `requests_per_minute`, `requests_per_minute_map_resolve`,
  `requests_per_day` (`null` en los planes de la API), `requests_scope`
  (`account` o `key`) y `search_results`. Cada respuesta lleva `X-Request-ID`
  para soporte.
- Entradas inválidas: en la búsqueda, una `q` vacía o fuera de 2 a 500
  caracteres responde `422` con `code: invalid_query`; un slug de norma
  desconocido responde `404` con `code: norm_not_found` y un alias bloqueado,
  `404` con `code: norm_blocked` y el motivo; un artículo inexistente, o un id
  que no es UUID, responde `404` con `code: article_not_found`. Todos llevan
  `message` en `detail` y ninguno se cobra.
- Cobertura: legislación federal vigente, prospectiva desde el baseline de cada
  norma (la primera fecha de vigencia de sus versiones). Una fecha anterior
  devuelve `outside_coverage` y nunca se presenta texto vigente como histórico:
  `GET /articulos/{id}` y `GET /normas/{slug}/estructura` responden `404` con
  `code: outside_coverage`, `message`, `as_of`, `coverage_start_date` y
  `norm_slug`; la búsqueda responde `200` con `data: []` y
  `meta.coverage.status: outside_coverage`, y `POST /resolve`, con
  `coverage.status: outside_coverage`. Ninguna de esas respuestas se cobra. Una
  fecha futura responde `future_not_available` por las mismas vías (`404` en el
  artículo y la estructura, `meta.coverage.status` en la búsqueda,
  `coverage.status` en `resolve`), tampoco se cobra, y "futura" es más allá de
  mañana: el servidor cuenta en UTC y un cliente adelantado (o el MCP, con la
  fecha de la Ciudad de México) manda su "hoy".

## Operaciones

- `GET /normas`, `GET /normas/{slug}`, `GET /normas/{slug}/estructura`
- `GET /articulos/search`, `GET /articulos/{id}`, `GET /articulos/{id}/historial`
- `POST /resolve` — paquete normativo v1
  ([contrato](NORMATIVE_PACKAGE_CONTRACT.md))
- `POST /map` — mapa normativo (planes de la API)
- `GET /billing/plans`, `GET /billing/summary`, `GET /billing/ledger`
- `GET /corpus/status` — cifras del corpus y última revisión de las fuentes (sin clave ni cobro)

## Consumo

Endpoints de solo lectura protegidos por el scope `billing:read`:

### `GET /api/v1/billing/plans`

Devuelve ofertas activas. `include_drafts=true` permite inspeccionar borradores a clientes autorizados durante configuración.

### `GET /api/v1/billing/summary`

Devuelve exclusivamente para el cliente autenticado:

- plan y términos vigentes;
- saldo y sobregiro;
- eventos del mes;
- eventos aún no valorizados;
- cargos del mes;
- alerta de saldo bajo.

### `GET /api/v1/billing/ledger`

Devuelve los movimientos recientes de la cuenta del cliente autenticado. Acepta `days` y `limit`.

Los endpoints no permiten modificar términos, recargar saldo ni activar precios.

---

## `POST /resolve`

Convierte contexto, cita o identificador en un paquete normativo trazable. Usa
el scope `resolve:run` y genera el evento `resolution.run`.

### Payload

```json
{
  "query": "Artículo 1 LCM",
  "norm": "lcm",
  "jurisdiction": "federal",
  "date": "2026-06-28",
  "limit": 5
}
```

### Respuesta abreviada

```json
{
  "contract_version": "1.0",
  "package_id": "urn:lexapi-mx:package:v1:{sha256}",
  "retrieval": {
    "strategy": "structured_full_text",
    "semantic_available": false,
    "semantic_used": false
  },
  "coverage": {
    "policy": "current_baseline_and_prospective",
    "status": "covered",
    "historical_audit": false,
    "retrospective_exception": null
  },
  "items": [
    {
      "norm": {"urn": "urn:lexapi-mx:norm:v1:lcm", "slug": "lcm"},
      "node": {
        "urn": "urn:lexapi-mx:node:v1:lcm:titulo:primero:capitulo:i:articulo:1",
        "stable_identifier": "lcm:titulo:primero:capitulo:i:articulo:1"
      },
      "version": {"id": "uuid", "checksum": "sha256"},
      "citation": {
        "canonical": "Artículo 1 LCM",
        "status": "derived",
        "origin": "node_metadata",
        "ambiguity_count": 1
      },
      "text": "...",
      "full_text": "...",
      "full_text_checksum": "sha256",
      "components": [{"node_type": "articulo", "node_version_id": "uuid", "checksum": "sha256"}],
      "source": {"url": "https://...", "is_official": true}
    }
  ],
  "relationships": [
    {
      "source_norm_urn": "urn:lexapi-mx:norm:v1:reg_lie_rnie",
      "target_norm_urn": "urn:lexapi-mx:norm:v1:lie",
      "relationship_type": "reglamenta"
    }
  ]
}
```

Fechas previas al baseline devuelven `outside_coverage` con `coverage_start_date`;
fechas futuras, `future_not_available`. No se reconstruye ni pronostica historia
normativa. Un paquete sin items (esos dos casos y `not_found`) no se cobra y
lleva la cabecera `X-Normative-Metering: skipped`.

Una cita de artículo con norma reconocible (`"Artículo 1500 LFT"`, o `norm` en la
petición) cuyo artículo no rige en esa fecha responde `not_found` sin items, en
vez de otros artículos que solo comparten palabras o cifras. `warnings` dice la
numeración vigente de la norma ("va del artículo 1 al 1010") o, si el artículo
rige en otra fecha, ese periodo, y remite a `GET /api/v1/normas/{slug}/estructura`.
La cita reconoce los ordinales (`3o`, `3º` = artículo 3), la letra en mayúscula
separada por espacio (`69 B` = 69-B) y "constitucional", "Constitución" o "Carta
Magna" como la CPEUM, salvo que la consulta nombre una ley reglamentaria.

Un artículo transitorio se cita con su norma: `"Artículo 2 transitorio LFT"`,
`"artículo segundo transitorio de la Ley de Amparo"`, `"Disposición Primera
Transitoria LISF"` o `"transitorio único"` con `norm`. El item es el nodo
`transitorio`, no el artículo con ese número; sin norma reconocible responde
`not_found` y pide indicarla. Cada sección de transitorios numera los suyos (la
de la ley y la del decreto que la expide), así que un número puede salir más de
una vez: van todos, en el orden del documento, con `citation.status`
`ambiguous_legacy`, `ambiguity_count` y un aviso en `warnings`. Una cita en
femenino ("Primera") se queda con la sección que numera así. Si el transitorio
no existe, `warnings` dice cuáles tiene la norma ("sus transitorios son 1 a 13").
Los transitorios de los decretos que reformaron la norma no se citan por número:
están en `estructura`, bajo el nodo `decreto` "Artículos transitorios de decretos
de reforma" y, dentro, un nodo `decreto` por decreto con su fecha de publicación
(`/lft/decreto/decretos-de-reforma/decreto/dof-2019-05-01`, "Decreto DOF
2019-05-01": título del decreto y línea del DOF en su texto) y sus artículos
transitorios debajo (`…/transitorio/transitorios/transitorio/primero`).

En cada item que es un artículo o un transitorio, `full_text` trae el texto
completo, con sus fracciones e incisos; `full_text_checksum` es su SHA-256 y `components`, las
versiones que lo forman, como en la búsqueda. `text` y `version` siguen siendo los
del nodo del artículo.
El contrato completo está en [`NORMATIVE_PACKAGE_CONTRACT.md`](NORMATIVE_PACKAGE_CONTRACT.md).

---

## `POST /map`

Mapa Normativo. Dado un tema, devuelve las normas aplicables, artículos relevantes, vigencia y fuente.
Cuesta 2 créditos cuando detecta un tema; si no lo detecta responde `200` con
`coverage_status: "not_found"`, la cabecera `X-Normative-Metering: skipped` y **no se
cobra**. `query` admite de 2 a 2,000 caracteres. Requiere un plan de la API: con una clave
del plan gratuito responde `403` con `code: paid_plan_required` y `upgrade_url`.

La detección compara la consulta con las palabras clave de cada tema del catálogo por
lexemas en español, sin distinguir acentos, mayúsculas, singular o plural ("liquidaciones"
encuentra "liquidación"; "marco jurídico" no encuentra "ARCO"). Un tema se detecta cuando
al menos una de sus palabras clave aparece completa en la consulta; `confidence` crece con
el número de palabras clave presentes (de 0.62 a 0.98). Si ningún tema se detecta, la
respuesta `not_found` trae en `suggested_topics` hasta tres temas que comparten alguna
palabra con la consulta (`confidence` menor que 0.5) y un `warning` que recomienda repetir
la consulta con las palabras del tema o usar `/articulos/search`.

### Payload

```json
{
  "query": "protección de datos personales en México",
  "jurisdiction": "federal",
  "date": "2025-01-01",
  "mode": "api"
}
```

### Respuesta

```json
{
  "query": "protección de datos personales en México",
  "detected_topics": [
    {
      "slug": "proteccion_datos",
      "name": "Protección de datos personales",
      "confidence": 0.75
    }
  ],
  "suggested_topics": [],
  "applicable_norms": [
    {
      "norm": "Constitución Política de los Estados Unidos Mexicanos",
      "slug": "cpeum",
      "articles": ["6", "16"],
      "relevance": "primary",
      "reason": "Base constitucional de privacidad y protección de datos personales.",
      "matter": "constitucional",
      "norm_type": "constitucion",
      "status": "vigente",
      "jurisdiction": "federal",
      "authority": null,
      "relationships": [],
      "ingestion_status": "fully_ingested",
      "expected_citations_total": 2,
      "expected_citations_found": ["Artículo 6", "Artículo 16"],
      "expected_citations_missing": []
    },
    {
      "norm": "Ley Federal de Protección de Datos Personales en Posesión de los Particulares",
      "slug": "lfpdppp",
      "articles": ["1", "2", "3", "6", "7", "8"],
      "relevance": "primary",
      "reason": "Ley especial aplicable a particulares.",
      "matter": "proteccion_datos",
      "norm_type": "ley",
      "status": "vigente",
      "jurisdiction": "federal",
      "authority": null,
      "relationships": [],
      "ingestion_status": "partially_ingested",
      "expected_citations_total": 6,
      "expected_citations_found": ["Artículo 1", "Artículo 2"],
      "expected_citations_missing": ["Artículo 3", "Artículo 6", "Artículo 7", "Artículo 8"]
    }
  ],
  "coverage": {
    "federal": true,
    "state_specific": false,
    "requires_regulation": false,
    "requires_jurisprudence": false,
    "coverage_status": "partial"
  },
  "traceability": [
    {
      "topic_slug": "proteccion_datos",
      "norm_slug": "cpeum",
      "node_id": null,
      "node_version_id": null,
      "confidence": "high"
    }
  ],
  "warnings": [],
  "articles": [
    {
      "id": "uuid",
      "norm": "LFPDPPP",
      "stable_identifier": "lfpdppp:articulo:1",
      "label": "Artículo 1",
      "text": "La presente Ley es de orden público...",
      "node_version_id": "uuid",
      "valid_from": "2025-03-21",
      "valid_to": null,
      "source": "Cámara de Diputados",
      "source_url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf",
      "checksum": "sha256 del texto completo, 64 caracteres hexadecimales",
      "components": [{"node_type": "articulo", "node_version_id": "uuid", "checksum": "sha256"}]
    }
  ]
}
```

`articles` trae el texto vigente de cada artículo de referencia que sí está en la base, con su
fuente, su checksum y su vigencia. Cada artículo llega completo, como en la búsqueda: `text`
incluye sus fracciones e incisos, `checksum` es el SHA-256 de ese texto y `components` lista
cada parte con su versión (`node_version_id` sigue siendo la del artículo). `source`,
`source_url` y `checksum` llegan en `null` si la versión no los tiene; nunca se rellenan con
un valor supuesto.

---

## `GET /corpus/status`

Estado del corpus. No pide clave ni descuenta créditos; la respuesta se calcula como
mucho cada diez minutos y lleva `Cache-Control: public, max-age=300`.

### Respuesta

```json
{
  "as_of": "2026-10-16",
  "norms": 123,
  "articles": 29511,
  "provisions": 78479,
  "latest_version_from": "2026-10-15",
  "monitor": {
    "cadence": "daily",
    "last_checked_at": "2026-10-16T13:02:11+00:00",
    "targets": 123,
    "pending_changes": 0
  },
  "computed_at": "2026-10-16T14:00:00+00:00"
}
```

`norms`, `articles` y `provisions` son los ordenamientos, artículos y disposiciones con
texto oficial vigente en `as_of` (las cifras que publica la web). `latest_version_from`
es la vigencia más reciente entre las versiones oficiales (una reforma o una corrección
de extracción). `monitor` dice cuándo se revisaron por última vez los documentos
oficiales, cuántos se vigilan y cuántos cambios esperan revisión jurídica.

---

## `GET /normas`

Lista de normas disponibles.

### Parámetros

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| materia | string | Filtro por materia |
| jurisdiccion | string | Filtro por jurisdicción |
| page | integer | Página (default 1) |
| limit | integer | Por página (default 20) |

### Respuesta

```json
{
  "data": [
    {
      "id": "uuid",
      "slug": "lft",
      "official_name": "Ley Federal del Trabajo",
      "short_name": "LFT",
      "jurisdiction": "federal",
      "matter": "laboral",
      "status": "vigente",
      "latest_reform_date": "2024-01-01"
    }
  ],
  "total": 1,
  "page": 1
}
```

---

## `GET /normas/{slug}`

Metadata de una norma. Acepta el slug canónico o un alias histórico (`ccomercio`
→ `ccom`; la respuesta añade `requested_slug` y `canonical_slug`). Un slug
desconocido responde `404` con `code: norm_not_found`; un alias bloqueado, `404`
con `code: norm_blocked` y el motivo en `message`.

### Respuesta

```json
{
  "id": "uuid",
  "slug": "lft",
  "official_name": "Ley Federal del Trabajo",
  "short_name": "LFT",
  "jurisdiction": "federal",
  "matter": "laboral",
  "norm_type": "ley",
  "authority": "Congreso de la Unión",
  "status": "vigente",
  "publication_date": "1970-04-01",
  "latest_reform_date": "2024-01-01",
  "source": {
    "name": "Cámara de Diputados",
    "url": "https://..."
  }
}
```

---

## `GET /normas/{slug}/estructura`

Árbol jerárquico de una norma en la fecha de consulta: los nodos con una versión
oficial que rige en ella. Un nodo que una corrección retira sale del árbol desde
ese día y sigue apareciendo en las fechas anteriores. Un slug desconocido o
bloqueado responde `404` como `GET /normas/{slug}`.

### Parámetros

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| fecha | date | Fecha de consulta (YYYY-MM-DD); hoy si se omite |
| include_text | boolean | Incluir texto vigente (default false). Requiere un plan de la API (scope `map:read`); el plan gratuito recibe `403` con `code: paid_plan_required` |
| page | integer | Página de texto cuando `include_text=true` (default 1) |
| page_size | integer | Nodos con texto por página (default 200, máximo 500) |

Con `include_text=true` el árbol llega completo, pero el texto solo acompaña a los
nodos de la página pedida, en el orden del documento (cada nodo antes que sus
hijos). Cada nodo con texto trae `text`, `node_version_id`, su vigencia
(`valid_from`, `valid_to`), su fuente (`source`, `source_url`, `is_official`) y
`checksum`, el SHA-256 de ese `text`. `text_page` indica la página, el total de
nodos y si hay más (`has_more`); cada página es una consulta (1 crédito). Sin
`include_text`, `text_page` es `null`.

Los nodos con texto tienen un tope diario por cuenta (día UTC), publicado como
`text_nodes_per_day` en `GET /api/v1/account` y en `GET /api/v1/checkout/catalog`.
Al rebasarlo la página responde `429` con `code: text_quota_exceeded`, `limit` y
`Retry-After` (segundos hasta el siguiente día UTC); no se cobra ni se entrega
texto. Para leer artículos concretos, la búsqueda y `GET /articulos/{id}` no
cuentan contra ese tope.

Una `fecha` anterior al baseline de la norma responde `404` con
`code: outside_coverage`, con o sin `include_text`: el árbol y el texto vigentes
no se presentan como los de esa fecha. No se cobra. Una fecha futura (más allá de
mañana) responde `404` con `code: future_not_available`.

```json
{
  "detail": {
    "code": "outside_coverage",
    "message": "La fecha 2020-01-01 es anterior al inicio de la cobertura de la norma 'lft' (2026-07-18): Lex API MX no reconstruye versiones anteriores a la incorporación de cada norma.",
    "as_of": "2020-01-01",
    "coverage_start_date": "2026-07-18",
    "norm_slug": "lft"
  }
}
```

### Respuesta

```json
{
  "norma": "lft",
  "fecha": "2025-01-01",
  "text_page": {"page": 1, "page_size": 200, "total_nodes": 1842, "has_more": true},
  "estructura": [
    {
      "id": "uuid",
      "parent_id": null,
      "node_type": "titulo",
      "label": "Título Primero",
      "children": [
        {
          "id": "uuid",
          "parent_id": "uuid",
          "node_type": "capitulo",
          "label": "Capítulo I",
          "children": [
            {
              "id": "uuid",
              "parent_id": "uuid",
              "node_type": "articulo",
              "label": "Artículo 47",
              "node_version_id": "uuid",
              "text": "…",
              "checksum": "sha256",
              "valid_from": "2026-07-18",
              "valid_to": null,
              "source": "Cámara de Diputados",
              "source_url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf",
              "is_official": true,
              "children": [
                {
                  "node_type": "fraccion",
                  "label": "Fracción I",
                  "text": "…"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Los nodos de título, capítulo y sección llevan en `text` la línea del
encabezado, su nombre y sus anotaciones ("CAPÍTULO I", "Disposiciones
generales", "Capítulo adicionado DOF 09-12-2019", una por línea), con su
`checksum` y su fuente como cualquier otro nodo; `label` conserva la forma de
cita ("Capítulo I").

---

## `GET /articulos/search`

Búsqueda full-text de artículos. Devuelve como máximo una versión oficial por
nodo, aplicable a `fecha` o a la fecha actual del servidor cuando se omite.
Excluye normas deprecadas, fuentes no oficiales y datos de prueba.

Busca tanto en el texto del artículo como en sus fracciones, incisos y apartados,
sin distinguir acentos. Si varias partes coinciden, el artículo aparece una sola
vez. Para texto libre, primero devuelve los artículos que tienen todos los
términos en una misma disposición y después los que tienen alguno (respaldo OR),
hasta el `limit` solicitado.

Las frases entre comillas, el operador `OR` y las exclusiones con `-` conservan
su significado y no activan esa ampliación. Los operadores se evalúan por
disposición: `hostigamiento -sexual` puede encontrar una fracción sin «sexual»
y devolver el artículo completo, aunque otra fracción sí contenga esa palabra.
El orden prioriza coincidencias estrictas y relevancia; los empates se resuelven
por nombre corto de norma, orden del documento e identificador del artículo.

### Parámetros

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| q | string | Término de búsqueda. Obligatorio, de 2 a 500 caracteres; si no, `422` con `code: invalid_query` |
| materia | string | Filtro por materia |
| jurisdiccion | string | Filtro por jurisdicción |
| norma | string | Filtrar por slug de norma (o alias histórico). Desconocido o bloqueado: `404` con `code: norm_not_found` o `norm_blocked` |
| fecha | date | Fecha de vigencia |
| limit | integer | Resultados por búsqueda (default 10). Máximo 50 en los planes de la API y 10 en el plan gratuito: un valor mayor se recorta, no se rechaza. `meta.limit` dice cuántos se aplicaron |

### Respuesta

`meta` informa el tope aplicado y el costo: hoy una búsqueda cuesta 1 crédito con
cualquier `limit`. Sin resultados, `data` llega vacío y la petición no se cobra
(cabecera `X-Normative-Metering: skipped`).

`meta.coverage` declara la cobertura en `as_of` (la `fecha` pedida o la de hoy) de
las normas que abarca la búsqueda: la de `norma` o las que dejan `materia` y
`jurisdiccion`.

- `covered`: todas tienen texto a esa fecha.
- `partial`: algunas empiezan después; sus slugs van en `norms_outside_coverage`
  y la búsqueda no las incluye.
- `outside_coverage`: ninguna tiene texto a esa fecha; `data` llega vacío,
  `coverage_start_date` dice desde cuándo hay texto y la petición no se cobra.
- `future_not_available`: la fecha está más allá de mañana; `data` llega vacío y
  la petición no se cobra (no se pronostican reformas).

Cada artículo llega completo: `text` incluye sus fracciones e incisos en el orden
del documento, con su marcador («I.», «a)»), y `checksum` es el SHA-256 de ese
texto. `components` lista cada parte (el artículo y sus fracciones, incisos y
apartados) con su `node_version_id`, el checksum de su versión almacenada y su
vigencia; `valid_from` y `valid_to` del artículo son la intersección de esas
vigencias. Un artículo sin fracciones conserva el texto y el checksum de su
versión.

Cada artículo trae también `canonical_citation` y `citation_status`: `canonical`
si la cita viene del catálogo de citas, `derived` si se arma con la sigla de la
norma y el número del artículo, y `ambiguous_legacy` si ese número se repite en
otro artículo de la misma norma vigente en esa fecha (la cita no identifica uno
solo).

```json
{
  "meta": {
    "limit": 10,
    "max_limit": 50,
    "credits": 1,
    "coverage": {"as_of": "2026-10-12", "status": "covered"}
  },
  "data": [
    {
      "id": "uuid",
      "norm_id": "uuid",
      "norm": "LFT",
      "norm_slug": "lft",
      "node_type": "articulo",
      "number": "47",
      "label": "Artículo 47",
      "text": "Son causas de rescisión de la relación de trabajo, sin responsabilidad para el patrón:\nI. Engañarlo el trabajador …\nII. …",
      "node_version_id": "uuid",
      "valid_from": "2026-07-18",
      "valid_to": null,
      "source": "Cámara de Diputados",
      "source_url": "https://...",
      "is_official": true,
      "checksum": "sha256 del texto completo",
      "components": [
        {
          "node_id": "uuid",
          "node_type": "articulo",
          "number": "47",
          "node_version_id": "uuid",
          "checksum": "sha256",
          "valid_from": "2026-07-18",
          "valid_to": null
        },
        {
          "node_id": "uuid",
          "node_type": "fraccion",
          "number": "I",
          "node_version_id": "uuid",
          "checksum": "sha256",
          "valid_from": "2026-07-18",
          "valid_to": null
        }
      ],
      "canonical_citation": "Artículo 47 LFT",
      "citation_status": "derived"
    }
  ]
}
```

Con una fecha anterior al baseline de las normas buscadas:

```json
{
  "meta": {
    "limit": 10,
    "max_limit": 50,
    "credits": 1,
    "coverage": {
      "as_of": "2020-01-01",
      "status": "outside_coverage",
      "coverage_start_date": "2026-07-18"
    }
  },
  "data": []
}
```

---

## `GET /articulos/{id}`

Artículo específico. Acepta `fecha` opcional (`YYYY-MM-DD`); cuando se omite,
selecciona la versión oficial aplicable a la fecha actual del servidor. Devuelve
`404` con `code: article_not_found` si el id no es un UUID, no existe o no regía
en esa fecha, y `404` con `code: outside_coverage`, `coverage_start_date` y
`norm_slug` si la fecha es anterior al baseline de su norma, y `404` con
`code: future_not_available` si está más allá de mañana. El texto completo
(`text`, `checksum`, `components`) y la cita (`canonical_citation`,
`citation_status`) siguen las reglas de la búsqueda.

### Respuesta

```json
{
  "id": "uuid",
  "norm": "LFT",
  "norm_slug": "lft",
  "number": "47",
  "label": "Artículo 47",
  "text": "Son causas de rescisión de la relación de trabajo, sin responsabilidad para el patrón:\nI. Engañarlo el trabajador …",
  "node_type": "articulo",
  "path": "/lft/titulo/segundo/capitulo/iv/articulo/47",
  "valid_from": "2026-07-18",
  "valid_to": null,
  "as_of": "2026-10-12",
  "source": "Cámara de Diputados",
  "source_url": "https://...",
  "is_official": true,
  "checksum": "sha256 del texto completo",
  "components": [{"node_type": "articulo", "node_version_id": "uuid", "checksum": "sha256"}],
  "canonical_citation": "Artículo 47 LFT",
  "citation_status": "derived",
  "historial_url": "/api/v1/articulos/{id}/historial"
}
```

---

## `GET /articulos/{id}/historial`

Versiones realmente almacenadas de un artículo dentro de su periodo de
cobertura. Este endpoint no garantiza historia anterior a la incorporación de
la norma. Si la fecha solicitada queda fuera de cobertura, la API debe declarar
la limitación y no presentar el texto vigente como histórico.

Sólo devuelve versiones con procedencia de ingesta oficial, fuente oficial y
norma activa; no mezcla seeds manuales, mocks ni versiones de prueba. Un id que
no es UUID o un artículo sin versiones oficiales responde `404` con
`code: article_not_found`.

### Respuesta

```json
{
  "data": [
    {
      "node_version_id": "uuid",
      "text": "…",
      "valid_from": "2023-01-01",
      "valid_to": null,
      "reform": {
        "date": "2023-01-01",
        "decree_title": "Decreto por el que se reforma…",
        "dof_url": "https://…"
      }
    }
  ]
}
```

