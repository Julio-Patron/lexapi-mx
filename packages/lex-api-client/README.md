# Lex API MX — cliente Python

Cliente mínimo de [Lex API MX](https://lexapi.mx) para consultar la legislación
federal mexicana vigente. Cada respuesta trae la fuente oficial, el checksum
SHA-256 del texto y su periodo de vigencia.

```bash
pip install lex-api-mx-client
```

```python
from lex_api_mx import LexApiClient, LexApiError

with LexApiClient(base_url="https://api.lexapi.mx", api_key="tu_clave") as lex:
    paquete = lex.resolve(query="Artículo 47 LFT", as_of="2026-10-08")
    articulos = lex.search_articles(query="aguinaldo", norm="lft", jurisdiction="federal")
    arbol = lex.norm_structure("lft")
```

| Método | Endpoint |
|---|---|
| `resolve(query, norm=None, jurisdiction="federal", as_of=None, limit=10)` | `POST /api/v1/resolve` |
| `search_articles(query, norm=None, matter=None, jurisdiction=None, as_of=None, limit=20)` | `GET /api/v1/articulos/search` |
| `norm_structure(norm, as_of=None, include_text=False)` | `GET /api/v1/normas/{slug}/estructura` (texto completo solo en planes de la API) |
| `map(query, jurisdiction=None, as_of=None)` | `POST /api/v1/map` (requiere el permiso `map:read`) |

`resolve` y `map` aceptan `idempotency_key`: un reintento con la misma clave no
se cobra dos veces. Los errores HTTP se lanzan como `LexApiError` con
`status_code`, `detail`, `request_id` y `body`; `402` significa saldo agotado.

Para obtener una clave, crea tu cuenta en
[lexapi.mx/#cuenta](https://lexapi.mx/#cuenta). Referencia de la API:
[lexapi.mx/docs](https://lexapi.mx/docs).

Para usar Lex API MX desde Claude, Cursor u otro agente, instala el servidor MCP
[`lex-api-mx-mcp`](https://pypi.org/project/lex-api-mx-mcp/).

Código fuente: [github.com/Julio-Patron/lexapi-mx](https://github.com/Julio-Patron/lexapi-mx/tree/main/packages/lex-api-client).
Licencia MIT.
