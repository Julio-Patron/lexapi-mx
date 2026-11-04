<!-- mcp-name: io.github.Julio-Patron/lex-api-mx -->
# Lex API MX — servidor MCP

Servidor [Model Context Protocol](https://modelcontextprotocol.io) que conecta
Claude Desktop, Claude Code, Cursor o cualquier agente MCP con la legislación
federal mexicana vigente de [Lex API MX](https://lexapi.mx).

El servidor es un adaptador ligero y de código abierto (MIT): no contiene el
corpus. Cada llamada consulta la API de Lex API MX con tu clave y devuelve el
paquete normativo tal cual, con cita canónica, vigencia, fuente oficial y
checksum SHA-256 del texto. La estructura de una norma llega como un índice
compacto (el árbol completo de la Ley Federal del Trabajo pesa más de 1 MB; su
índice, unos 15 KB).

## Herramientas

| Herramienta | Endpoint | Para qué |
|---|---|---|
| `resolve_legal_citation` | `POST /api/v1/resolve` | Resolver una cita o situación a un paquete normativo verificable. |
| `search_mexican_law` | `GET /api/v1/articulos/search` | Buscar artículos vigentes por texto, norma o materia. |
| `get_norm_structure` | `GET /api/v1/normas/{slug}/estructura` | Índice de una norma: primer y último artículo, divisiones en orden y números de artículo. El texto (`include_text`, por páginas de nodos con `page`) se rige por los permisos y la cuota de la cuenta. |
| `map_legal_topic` | `POST /api/v1/map` | Citas del catálogo limitado de temas, con cobertura y advertencias. |
| `get_legal_article` | `GET /api/v1/articulos/{id}` | Artículo completo por UUID, con fuente, vigencia y SHA. |
| `list_legal_norms` | `GET /api/v1/normas` | Catálogo paginado de normas y sus slugs. |
| `get_legal_norm` | `GET /api/v1/normas/{slug}` | Metadatos actuales de una norma. |
| `get_legal_article_history` | `GET /api/v1/articulos/{id}/historial` | Versiones conservadas con fuente, vigencia y SHA. |
| `get_corpus_status` | `GET /api/v1/corpus/status` | Estado público del corpus; no consume cuota. |

Las lecturas de texto exigen `fecha` (`"vigente"` o `YYYY-MM-DD`). Búsqueda,
resolución, mapa y catálogo reciben `jurisdiccion`, hoy solo `"federal"`.
Las lecturas de metadatos, historial y estado no reciben fecha.

## Instalación

Requiere [uv](https://docs.astral.sh/uv/) y una clave de Lex API MX. El plan
gratuito publica sus límites vigentes en Cuenta: crea tu cuenta con tu correo y genera la
clave en [lexapi.mx/cuenta](https://lexapi.mx/cuenta).

```json
{
  "mcpServers": {
    "lex-api-mx": {
      "command": "uvx",
      "args": ["lex-api-mx-mcp"],
      "env": { "LEX_API_MX_KEY": "tu_clave" }
    }
  }
}
```

- **Claude Desktop:** *Settings → Developer → Edit Config* y pega el bloque
  anterior en `claude_desktop_config.json`; reinicia la aplicación.
- **Claude Code:**
  `claude mcp add lex-api-mx --env LEX_API_MX_KEY=tu_clave -- uvx lex-api-mx-mcp`
- **Cursor:** el mismo bloque en `~/.cursor/mcp.json` (global) o
  `.cursor/mcp.json` (proyecto).

Pruébalo preguntando: *¿Cuáles son las causas de rescisión de la relación de
trabajo sin responsabilidad para el patrón? Cita el artículo exacto.*

## Variables de entorno

| Variable | Obligatoria | Valor por defecto |
|---|---|---|
| `LEX_API_MX_KEY` | Sí | — |
| `LEX_API_MX_BASE_URL` | No | `https://api.lexapi.mx` |

## Errores

Los errores de la API llegan al modelo como errores de herramienta legibles y
con la acción para la siguiente llamada: clave inválida (401), permiso faltante
o condiciones anteriores (403), saldo anterior agotado (402: no reintentar y avisar
al responsable para revisar y activar voluntariamente acceso gratuito en Cuenta), norma inexistente o fecha
anterior a la cobertura (404: qué slug o qué fecha usar) y límite de peticiones
(429). Ante un 429 con espera de 30 segundos o menos, el servidor reintenta solo
hasta dos veces.

## Código fuente

[github.com/Julio-Patron/lexapi-mx](https://github.com/Julio-Patron/lexapi-mx/tree/main/packages/lex-mcp-server)
(licencia MIT). También está en el [MCP Registry](https://registry.modelcontextprotocol.io)
como `io.github.Julio-Patron/lex-api-mx`.

## Lectura gratuita

API y MCP requieren la misma clave de una cuenta con correo confirmado. La política
activa de Cuenta determina cuota y permisos; la lectura incluida no exige créditos.
La cuota mensual se comparte entre claves por cuenta y mes UTC. `monthly_quota_exceeded`
indica cuándo se renueva; no se resuelve comprando créditos. Se mantienen límites de
texto, resultados, tamaño y concurrencia.

El MCP incluye búsqueda, estructura, resolve, `map_legal_topic`,
`get_legal_article`, `list_legal_norms`, `get_legal_norm`,
`get_legal_article_history` y `get_corpus_status`.
El mapa conserva un catálogo limitado de temas y citas; no determina todo el marco
aplicable a un caso. Revisa `coverage`, `articles_missing` y `warnings`.
Las ocho lecturas normativas aceptan
`idempotency_key`: conserva identificador y parámetros para el mismo reintento;
una petición distinta es otro evento. No se eliminan límites de ráfagas por reintentar.
`get_corpus_status` consulta el estado público y no consume cuota.

La API y el MCP son gratuitos; no se venden planes ni recargas. Confirma tu
correo y entra en Cuenta para recibir tu primera clave. Las cuentas anteriores
pueden aceptar allí los límites gratuitos, conservando saldos e historial.
