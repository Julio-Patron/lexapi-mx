# Lex API MX en tu agente: inicio rápido MCP

Conecta la legislación federal mexicana vigente a Claude Desktop, Claude Code o
Cursor en cinco minutos, sin escribir código de integración.

El servidor `lex-api-mx-mcp` es código abierto (MIT) y vive en
[`packages/lex-mcp-server`](../packages/lex-mcp-server). Sólo traduce
herramientas MCP a la API; el corpus y su verificación permanecen en Lex API MX.

## 1. Requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado
  (`uvx` viene incluido);
- una clave de Lex API MX con los scopes `resolve:run`, `articles:read` y
  `norms:read` (las trae el plan gratuito; créala en
  [lexapi.mx/#cuenta](https://lexapi.mx/#cuenta)).

El alta es de autoservicio: en [lexapi.mx/#cuenta](https://lexapi.mx/#cuenta)
escribe tu correo, abre el enlace que te enviamos y crea una clave (se muestra
una sola vez). El paquete [`lex-api-mx-mcp`](https://pypi.org/project/lex-api-mx-mcp/)
está en PyPI: `uvx` lo instala solo y apunta por defecto a `https://api.lexapi.mx`.

## 2. Claude Desktop

Abre *Settings → Developer → Edit Config* (`claude_desktop_config.json`) y
agrega:

```json
{
  "mcpServers": {
    "lex-api-mx": {
      "command": "uvx",
      "args": ["lex-api-mx-mcp"],
      "env": {
        "LEX_API_MX_KEY": "tu_clave"
      }
    }
  }
}
```

Reinicia Claude Desktop. Verás las tres herramientas de Lex API MX en el menú de
herramientas.

## 3. Claude Code

```bash
claude mcp add lex-api-mx --env LEX_API_MX_KEY=tu_clave -- uvx lex-api-mx-mcp
```

## 4. Cursor

En `~/.cursor/mcp.json` (global) o `.cursor/mcp.json` (proyecto) usa el mismo
bloque `mcpServers` del paso 2.

## 5. Pruébalo

Pregunta a tu agente:

> ¿Cuáles son las causas de rescisión de la relación de trabajo sin
> responsabilidad para el patrón? Cita el artículo exacto.

El agente debe llamar a `resolve_legal_citation` o `search_mexican_law`,
leer el artículo 47 de la Ley Federal del Trabajo desde Lex API MX y responder
con la cita canónica, la fuente oficial y el checksum de la versión.

## Herramientas

| Herramienta | Parámetros obligatorios | Devuelve |
|---|---|---|
| `resolve_legal_citation` | `query`, `fecha`, `jurisdiccion` | Paquete normativo v1: normas, nodos, citas, cobertura, fuente y checksum. |
| `search_mexican_law` | `query`, `fecha`, `jurisdiccion` | Artículos vigentes con texto, cita, vigencia, fuente y checksum. |
| `get_norm_structure` | `norma`, `fecha` | Árbol de la norma (libros, títulos, capítulos, artículos). `include_text=true` agrega el texto de cada nodo y requiere un plan de la API. |

- `fecha` acepta `"vigente"` (fecha actual en la Ciudad de México) o
  `YYYY-MM-DD`. Una fecha anterior al inicio de cobertura devuelve
  `outside_coverage`; nunca se presenta texto actual como histórico.
- `jurisdiccion` sólo acepta `"federal"` mientras no existan programas estatales.

## Errores

| Código | Lo que verá el agente |
|---|---|
| 401 | La clave es inválida, expiró o fue revocada. |
| 402 | Saldo agotado, con el enlace para recargar créditos. |
| 403 | La clave no tiene el scope requerido, o la operación es de los planes de la API (mapa normativo, texto completo de una norma). |
| 429 | Límite de peticiones por minuto alcanzado. |
| Red | No se pudo contactar a Lex API MX. |
