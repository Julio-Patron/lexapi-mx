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
| `norm_structure(norm, as_of=None, include_text=False, page=1, page_size=None)` | `GET /api/v1/normas/{slug}/estructura` (con `include_text=True` pagina nodos con `page`; revisa `text_page.has_more`) |
| `map(query, jurisdiction=None, as_of=None)` | `POST /api/v1/map` (requiere el permiso `map:read`) |
| `article(article_id, as_of=None)` | `GET /api/v1/articulos/{id}` |
| `article_history(article_id)` | `GET /api/v1/articulos/{id}/historial` |
| `list_norms(matter=None, jurisdiction=None, page=1, limit=20)` | `GET /api/v1/normas` |
| `norm(norm)` | `GET /api/v1/normas/{slug}` |
| `corpus_status()` | `GET /api/v1/corpus/status` (público, sin clave) |

Las ocho lecturas normativas aceptan `idempotency_key`: un reintento con la
misma clave e idéntica petición no contabiliza dos veces en el límite mensual,
aunque sigue contando para ráfagas por minuto y nodos diarios de texto. Los
errores HTTP se lanzan como `LexApiError` con `status_code`, `detail`,
`request_id`, `body` y `retry_after` (`401`, `403`, `404`, `422`, `429`; `402`
se conserva solo por compatibilidad retroactiva).

Un `429` (límite de uso alcanzado) no contabiliza en el tope mensual: el cliente
espera los segundos de `Retry-After` y reintenta solo, hasta `max_retries=2`
veces, cuando la espera no pasa de `max_retry_wait=30.0` segundos. Una espera
mayor (como la renovación mensual o diaria UTC) se lanza enseguida como
`LexApiError` con `retry_after`. `LexApiClient(..., max_retries=0)` desactiva
los reintentos automáticos.

Para obtener una clave, confirma tu correo en
[lexapi.mx/cuenta](https://lexapi.mx/cuenta). Guía y catálogo:
[lexapi.mx/docs](https://lexapi.mx/docs).

Para usar Lex API MX desde Claude, Cursor u otro agente, instala el servidor MCP
[`lex-api-mx-mcp`](https://pypi.org/project/lex-api-mx-mcp/).

Código fuente: [github.com/Julio-Patron/lexapi-mx](https://github.com/Julio-Patron/lexapi-mx/tree/main/packages/lex-api-client).
Licencia MIT.

## Acceso gratuito y límites de uso

API y MCP son de acceso gratuito con correo confirmado y comparten límites de
uso por cuenta (mes calendario UTC, peticiones por minuto, concurrencia, nodos
diarios de texto y tamaño de respuesta); no existen planes de pago ni recargas.
Solo las respuestas `2xx` con resultado contabilizan contra el límite mensual.
`corpus_status()` consulta el estado público del corpus y no consume límite.
