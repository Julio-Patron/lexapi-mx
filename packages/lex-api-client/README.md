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
| `norm_structure(norm, as_of=None, include_text=False, page=1, page_size=None)` | `GET /api/v1/normas/{slug}/estructura` (texto según permisos de la cuenta, por páginas de nodos: revisa `text_page.has_more`) |
| `map(query, jurisdiction=None, as_of=None)` | `POST /api/v1/map` (requiere el permiso `map:read`) |

`resolve` y `map` aceptan `idempotency_key`: un reintento con la misma clave no
se cobra dos veces. Los errores HTTP se lanzan como `LexApiError` con
`status_code`, `detail`, `request_id`, `body` y `retry_after`; `402` significa
saldo agotado.

Un `429` (límite de peticiones) no se cobra: el cliente espera los segundos de
`Retry-After` y reintenta solo, hasta `max_retries=2` veces, cuando la espera no
pasa de `max_retry_wait=30.0` segundos. Una espera mayor, como el límite diario
del plan gratuito, se lanza enseguida como `LexApiError` con `retry_after`.
`LexApiClient(..., max_retries=0)` desactiva los reintentos.

Para obtener una clave, crea tu cuenta en
[lexapi.mx/cuenta](https://lexapi.mx/cuenta). Referencia de la API:
[lexapi.mx/docs](https://lexapi.mx/docs).

Para usar Lex API MX desde Claude, Cursor u otro agente, instala el servidor MCP
[`lex-api-mx-mcp`](https://pypi.org/project/lex-api-mx-mcp/).

Código fuente: [github.com/Julio-Patron/lexapi-mx](https://github.com/Julio-Patron/lexapi-mx/tree/main/packages/lex-api-client).
Licencia MIT.

## Lectura incluida y versión 0.4.0

API y MCP requieren la misma clave de una cuenta con correo confirmado. La política
activa de Cuenta determina cuota y permisos; la lectura incluida no exige créditos.
La cuota mensual se comparte entre claves por cuenta y mes UTC. `monthly_quota_exceeded`
indica cuándo se renueva; no se resuelve comprando créditos. Se mantienen límites de
texto, resultados, tamaño y concurrencia.

El MCP 0.4.0 añade `map_legal_topic(query, fecha, jurisdiccion)` y
`get_legal_article(article_id, fecha)`; el mapa conserva un catálogo limitado de temas.
El SDK añade `article(article_id, as_of=...)`. Las cinco lecturas aceptan
`idempotency_key`: conserva identificador y parámetros para el mismo reintento;
una petición distinta es otro evento. No se eliminan límites de ráfagas por reintentar.

Los contratos previos, saldos e historial se conservan. El catálogo activo informa
la oferta gratuita y empresarial por volumen/garantías verificadas; sin precio ni
SLA por defecto, semántica, alertas en tiempo real ni CFDI automático operativo.
