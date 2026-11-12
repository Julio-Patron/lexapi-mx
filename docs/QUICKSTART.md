# Inicio rápido de Lex API MX

La API pública está en `https://api.lexapi.mx` y la web, con el alta de
cuentas, en `https://lexapi.mx`. Usa esa URL en `LEX_API_BASE_URL`.

## Requisitos

- Python 3.11 o posterior;
- una clave con el scope de la operación: `resolve:run`, `map:read`,
  `norms:read` o `articles:read`. Créala en
  [lexapi.mx/cuenta](https://lexapi.mx/cuenta) después de confirmar tu correo
  (las claves estándar incluyen todos los permisos de lectura);
- `Idempotency-Key` estable por operación reintentable.

## cURL

```bash
export LEX_API_BASE_URL="https://api.lexapi.mx"
export LEX_API_KEY="tu_clave"

curl -X POST "$LEX_API_BASE_URL/api/v1/resolve" \
  -H "X-API-Key: $LEX_API_KEY" \
  -H "Idempotency-Key: quickstart-resolve-001" \
  -H "Content-Type: application/json" \
  -d '{"query":"Artículo 1 LCM","norm":"lcm","limit":5}'
```

La respuesta incluye `contract_version`, cobertura temporal, citas, fuente y
checksum. Una fecha anterior al baseline devuelve `outside_coverage` y una futura,
`future_not_available`; no se reconstruye ni se pronostica historia.

## SDK Python

```bash
pip install lex-api-mx-client
python examples/python/resolve.py
```

```python
from lex_api_mx import LexApiClient

with LexApiClient(base_url=base_url, api_key=api_key) as client:
    package = client.resolve(query="Artículo 1 LCM", norm="lcm")
```

El SDK cubre `resolve`, `map`, `search_articles`, `norm_structure`, `article`,
`article_history`, `list_norms`, `norm` y `corpus_status`. Los errores HTTP
levantan `LexApiError` con código de estado y `X-Request-ID` cuando está
disponible (`401`, `403`, `404`, `422`, `429`; `402` se conserva solo por
compatibilidad retroactiva).

## Límites de uso

[Cuenta](https://lexapi.mx/cuenta) muestra el consumo y los límites activos de tu
cuenta. Los límites se comparten entre claves, API, SDK y MCP por mes calendario
UTC: solo contabilizan respuestas `2xx` con resultado. La misma `Idempotency-Key`
e idéntica petición no duplican el consumo mensual, aunque los reintentos siguen
contando para ráfagas por minuto y nodos diarios de texto. Un `limit` de
búsqueda mayor al permitido se recorta y `meta.limit` indica el valor aplicado.
Al alcanzar un límite, `429` incluye `Retry-After` (segundos) y, en
`monthly_quota_exceeded`, la fecha de renovación mensual UTC.

## La web

En [lexapi.mx/probar](https://lexapi.mx/probar) consultas respuestas reales sin
clave y pruebas la API con tu clave (resolver una cita, buscar artículos,
estructura de una norma y mapa normativo): la clave se guarda solo en
`sessionStorage` durante la pestaña y se envía como `X-API-Key`. La guía y el
catálogo están en [lexapi.mx/docs](https://lexapi.mx/docs). Un `403` indica
permisos insuficientes o estado de la clave. [Cuenta](https://lexapi.mx/cuenta)
muestra tus claves activas y el avance mensual de consultas.

## OpenAPI

El contrato está en [`openapi-v1.json`](openapi-v1.json) y la referencia
interactiva en [lexapi.mx/docs/api](https://lexapi.mx/docs/api).

La primera clave se entrega al entrar en Cuenta tras confirmar tu correo.
Cópiala en ese momento: no se vuelve a mostrar. La API y el MCP son de acceso
gratuito; no requieren tarjeta ni existen recargas.
