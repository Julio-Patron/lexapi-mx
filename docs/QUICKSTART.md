# Inicio rápido de Lex API MX

La API pública está en `https://api.lexapi.mx` y la web, con el alta de
cuentas, en `https://lexapi.mx`. Usa esa URL en `LEX_API_BASE_URL`.

## Requisitos

- Python 3.11 o posterior;
- una clave con el scope de la operación: `resolve:run`, `map:read`,
  `norms:read`, `articles:read` o `billing:read`. Créala en
  [lexapi.mx/#cuenta](https://lexapi.mx/#cuenta): el plan gratuito trae 500
  créditos al mes y todos los scopes salvo `map:read`, que llega con los planes
  de pago;
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
checksum. Una fecha anterior al baseline devuelve `outside_coverage`; no se
reconstruye historia general.

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

El SDK cubre `resolve`, `map`, `search_articles` y `norm_structure`. Los
errores HTTP levantan `LexApiError` con código de estado y `X-Request-ID`
cuando está disponible; `402` significa saldo agotado.

## La web

En [lexapi.mx](https://lexapi.mx) puedes probar el mapa normativo y el
playground con tu clave: se guarda solo en `sessionStorage` durante la pestaña y
se envía como `X-API-Key`. Un `403` indica que la clave es válida pero su plan no
incluye la operación (mapa normativo o texto completo de una norma).

## OpenAPI

El contrato está en [`openapi-v1.json`](openapi-v1.json) y la documentación
interactiva en [api.lexapi.mx/docs](https://api.lexapi.mx/docs).
