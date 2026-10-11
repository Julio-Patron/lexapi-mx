# Lex API MX — Especificación de API

**Base URL:** `https://api.lexapi.mx/api/v1` · Documentación interactiva:
[api.lexapi.mx/docs](https://api.lexapi.mx/docs) · Contrato OpenAPI:
[`openapi-v1.json`](openapi-v1.json)

---

## Autenticación y uso

- Todas las rutas `/api/v1/*` exigen la cabecera `X-API-Key` con una clave creada
  en [lexapi.mx/#cuenta](https://lexapi.mx/#cuenta). Cada operación valida su
  scope: `norms:read`, `articles:read`, `resolve:run`, `billing:read` y, en los
  planes de la API, `map:read`.
- Solo se cobran respuestas `2xx`, en créditos por operación
  ([`CATALOGO.md`](CATALOGO.md)). Un reintento con la misma `Idempotency-Key` y
  la misma petición no se cobra dos veces.
- Sin saldo la API responde `402` con `code: insufficient_credits` y el enlace
  para contratar; sin el scope, `403`; por encima del límite de peticiones por
  minuto, `429`. Cada respuesta lleva `X-Request-ID` para soporte.
- Cobertura: legislación federal vigente, prospectiva desde el baseline de cada
  norma. Una fecha anterior devuelve `outside_coverage`; nunca se presenta texto
  vigente como histórico.

## Operaciones

- `GET /normas`, `GET /normas/{slug}`, `GET /normas/{slug}/estructura`
- `GET /articulos/search`, `GET /articulos/{id}`, `GET /articulos/{id}/historial`
- `POST /resolve` — paquete normativo v1
  ([contrato](NORMATIVE_PACKAGE_CONTRACT.md))
- `POST /map` — mapa normativo (planes de la API)
- `GET /billing/plans`, `GET /billing/summary`, `GET /billing/ledger`

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

Fechas previas al baseline devuelven `outside_coverage`; fechas futuras,
`future_not_available`. No se reconstruye ni pronostica historia normativa.
El contrato completo está en [`NORMATIVE_PACKAGE_CONTRACT.md`](NORMATIVE_PACKAGE_CONTRACT.md).

---

## `POST /map`

Mapa Normativo. Dado un tema, devuelve las normas aplicables, artículos relevantes, vigencia y fuente.

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
      "confidence": 0.82
    }
  ],
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
    "requires_regulation": true,
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
      "checksum": "sha256 del texto, 64 caracteres hexadecimales"
    }
  ]
}
```

`articles` trae el texto vigente de cada artículo de referencia que sí está en la base, con su
fuente, su checksum y su vigencia. `source`, `source_url` y `checksum` llegan en `null` si la
versión no los tiene; nunca se rellenan con un valor supuesto.

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

Metadata de una norma.

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

Árbol jerárquico de una norma.

### Parámetros

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| fecha | date | Fecha de consulta (YYYY-MM-DD) |
| include_text | boolean | Incluir texto vigente (default false). Requiere un plan de la API (scope `map:read`); el plan gratuito recibe `403` con `code: paid_plan_required` |

### Respuesta

```json
{
  "norma": "lft",
  "fecha": "2025-01-01",
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

---

## `GET /articulos/search`

Búsqueda full-text de artículos. Devuelve como máximo una versión oficial por
nodo, aplicable a `fecha` o a la fecha actual del servidor cuando se omite.
Excluye normas deprecadas, fuentes no oficiales y datos de prueba.

### Parámetros

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| q | string | Término de búsqueda |
| materia | string | Filtro por materia |
| jurisdiccion | string | Filtro por jurisdicción |
| norma | string | Filtrar por slug de norma |
| fecha | date | Fecha de vigencia |
| limit | integer | Máximo de resultados |

### Respuesta

```json
{
  "data": [
    {
      "id": "uuid",
      "norma": "Ley Federal del Trabajo",
      "norma_slug": "lft",
      "label": "Artículo 47",
      "text": "…",
      "node_version_id": "uuid",
      "valid_from": "1970-04-01",
      "valid_to": null,
      "source": "Cámara de Diputados",
      "source_url": "https://...",
      "is_official": true,
      "checksum": "sha256",
      "canonical_citation": "Artículo 47 LFT"
    }
  ]
}
```

---

## `GET /articulos/{id}`

Artículo específico. Acepta `fecha` opcional (`YYYY-MM-DD`); cuando se omite,
selecciona la versión oficial aplicable a la fecha actual del servidor. Devuelve
`404` si no existe una versión oficial cubierta para esa fecha.

### Respuesta

```json
{
  "id": "uuid",
  "norma": "Ley Federal del Trabajo",
  "norma_slug": "lft",
  "label": "Artículo 47",
  "text": "…",
  "node_type": "articulo",
  "path": "/lft/titulo2/capitulo1/articulo47",
  "valid_from": "1970-04-01",
  "valid_to": null,
  "as_of": "2026-07-16",
  "source": "Cámara de Diputados",
  "source_url": "https://...",
  "is_official": true,
  "checksum": "sha256",
  "canonical_citation": "Artículo 47 LFT",
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
norma activa; no mezcla seeds manuales, mocks ni versiones de prueba.

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

