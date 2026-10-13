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
| `get_norm_structure` | `GET /api/v1/normas/{slug}/estructura` | Índice de una norma: primer y último artículo, divisiones en orden y números de artículo. El texto (`include_text`, por páginas de nodos con `page`) requiere un plan de la API. |

Todas exigen `fecha` (`"vigente"` o `YYYY-MM-DD`). Las de búsqueda y resolución
exigen además `jurisdiccion`; hoy la única cobertura es `"federal"`.

## Instalación

Requiere [uv](https://docs.astral.sh/uv/) y una clave de Lex API MX. El plan
gratuito incluye 500 créditos al mes: crea tu cuenta con tu correo y genera la
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
o plan requerido (403), saldo agotado (402: no reintentar y avisar al
responsable de la cuenta con el enlace de recarga), norma inexistente o fecha
anterior a la cobertura (404: qué slug o qué fecha usar) y límite de peticiones
(429). Ante un 429 con espera de 30 segundos o menos, el servidor reintenta solo
hasta dos veces.

## Código fuente

[github.com/Julio-Patron/lexapi-mx](https://github.com/Julio-Patron/lexapi-mx/tree/main/packages/lex-mcp-server)
(licencia MIT). También está en el [MCP Registry](https://registry.modelcontextprotocol.io)
como `io.github.Julio-Patron/lex-api-mx`.
