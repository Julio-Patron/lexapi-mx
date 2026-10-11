<!-- mcp-name: io.github.Julio-Patron/lex-api-mx -->
# Lex API MX — servidor MCP

Servidor [Model Context Protocol](https://modelcontextprotocol.io) que conecta
Claude Desktop, Claude Code, Cursor o cualquier agente MCP con la legislación
federal mexicana vigente de [Lex API MX](https://lexapi.mx).

El servidor es un adaptador ligero y de código abierto (MIT): no contiene el
corpus. Cada llamada consulta la API de Lex API MX con tu clave y devuelve el
paquete normativo tal cual, con cita canónica, vigencia, fuente oficial y
checksum SHA-256 del texto.

## Herramientas

| Herramienta | Endpoint | Para qué |
|---|---|---|
| `resolve_legal_citation` | `POST /api/v1/resolve` | Resolver una cita o situación a un paquete normativo verificable. |
| `search_mexican_law` | `GET /api/v1/articulos/search` | Buscar artículos vigentes por texto, norma o materia. |
| `get_norm_structure` | `GET /api/v1/normas/{slug}/estructura` | Recorrer el árbol de una norma; el texto completo (`include_text`) requiere un plan de la API. |

Todas exigen `fecha` (`"vigente"` o `YYYY-MM-DD`). Las de búsqueda y resolución
exigen además `jurisdiccion`; hoy la única cobertura es `"federal"`.

## Instalación

Requiere [uv](https://docs.astral.sh/uv/) y una clave de Lex API MX. El plan
gratuito incluye 500 créditos al mes: crea tu cuenta con tu correo y genera la
clave en [lexapi.mx/#cuenta](https://lexapi.mx/#cuenta).

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

Los errores de la API llegan al modelo como errores de herramienta legibles:
clave inválida (401), permiso faltante (403), saldo agotado (402) y límite de
peticiones (429).

## Código fuente

[github.com/Julio-Patron/lexapi-mx](https://github.com/Julio-Patron/lexapi-mx/tree/main/packages/lex-mcp-server)
(licencia MIT). También está en el [MCP Registry](https://registry.modelcontextprotocol.io)
como `io.github.Julio-Patron/lex-api-mx`.
