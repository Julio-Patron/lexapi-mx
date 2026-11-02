# Inicio rápido de Lex API MX

La API pública está en `https://api.lexapi.mx` y la web, con el alta de
cuentas, en `https://lexapi.mx`. Usa esa URL en `LEX_API_BASE_URL`.

## Requisitos

- Python 3.11 o posterior;
- una clave con el scope de la operación: `resolve:run`, `map:read`,
  `norms:read`, `articles:read` o `billing:read`. Créala en
  [lexapi.mx/cuenta](https://lexapi.mx/cuenta) después de confirmar tu correo.
  Las cuentas con lectura incluida tienen acceso a las cinco funciones de
  lectura; consulta los permisos y límites activos de tu cuenta;
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

El SDK 0.4.0 cubre `resolve`, `map`, `search_articles`, `norm_structure` y `article`. Los
errores HTTP levantan `LexApiError` con código de estado y `X-Request-ID`
cuando está disponible; `402` significa saldo insuficiente en un contrato de
prepago que exige saldo. La cuota incluida no depende de comprar créditos.

## Límites de uso

Cuenta y `GET /api/v1/checkout/catalog` publican los límites vigentes. La cuota
incluida se comparte por cuenta, sumando claves, API y MCP, por mes calendario
UTC. Solo consumen respuestas exitosas con resultado. La misma Idempotency-Key
y petición no duplica consumo mensual; los reintentos cuentan para ráfagas y
texto. Se mantienen límites de concurrencia, resultados y tamaño de respuesta.
Un `limit` de búsqueda mayor se recorta y `meta.limit` indica el valor aplicado.
Al superar un límite, `429` incluye `Retry-After` (segundos).
`monthly_quota_exceeded` indica la renovación mensual sin exigir recargas.
Los contratos anteriores conservan sus condiciones, saldos e historial.

## La web

En [lexapi.mx/probar](https://lexapi.mx/probar) ves respuestas reales sin clave
y pruebas la API con tu clave (resolver una cita, buscar artículos, estructura de
una norma y mapa normativo): la clave se guarda solo en `sessionStorage` durante
la pestaña y se envía como `X-API-Key`. La guía en español está en
[lexapi.mx/docs](https://lexapi.mx/docs). Un `403` indica permisos insuficientes;
se conserva `paid_plan_required` para contratos anteriores sin acceso a mapa o
texto completo. [Cuenta](https://lexapi.mx/cuenta) muestra los permisos,
la cuota incluida cuando corresponde, el saldo anterior y los límites activos.

## OpenAPI

El contrato está en [`openapi-v1.json`](openapi-v1.json) y la referencia
interactiva en [lexapi.mx/docs/api](https://lexapi.mx/docs/api).
