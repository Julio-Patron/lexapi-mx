# Lex API MX en tu agente: inicio rápido MCP

Conecta la legislación federal mexicana vigente a Claude Desktop, Claude Code o
Cursor en cinco minutos, sin escribir código de integración.

El servidor `lex-api-mx-mcp` es código abierto (MIT) y vive en
[`packages/lex-mcp-server`](../packages/lex-mcp-server). Sólo traduce
herramientas MCP a la API y compacta la estructura de cada norma en un índice que
cabe en el contexto del agente; el corpus y su verificación permanecen en Lex API
MX.

## 1. Requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado
  (`uvx` viene incluido);
- una clave de Lex API MX con los scopes `resolve:run`, `articles:read` y
  `norms:read` (las trae el plan gratuito; créala en
  [lexapi.mx/cuenta](https://lexapi.mx/cuenta)).

El alta es de autoservicio: en [lexapi.mx/cuenta](https://lexapi.mx/cuenta)
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

Reinicia Claude Desktop. Verás las nueve herramientas de la versión 0.4.0 de Lex API MX en el menú de
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
leer el artículo 47 de la Ley Federal del Trabajo completo, con sus quince
fracciones, desde Lex API MX y responder con la cita canónica, la fuente oficial
y el checksum del texto.

## Herramientas

| Herramienta | Parámetros obligatorios | Devuelve |
|---|---|---|
| `resolve_legal_citation` | `query`, `fecha`, `jurisdiccion` | Paquete normativo v1: normas, nodos, citas, cobertura, fuente y checksum; en cada artículo o transitorio ("Artículo 2 transitorio LFT"), `full_text` con sus fracciones e incisos. |
| `search_mexican_law` | `query`, `fecha`, `jurisdiccion` | Artículos vigentes completos (con sus fracciones e incisos), con cita, vigencia, fuente y checksum. |
| `get_norm_structure` | `norma`, `fecha` | Índice de la norma: `resumen` con el primer y el último artículo y los nodos por tipo; `indice` con libros, títulos y capítulos en orden y los números de sus artículos (las fracciones e incisos se cuentan, no se listan), las secciones de transitorios y, al final, los decretos de reforma con su fecha del DOF y sus transitorios. `include_text=true` agrega en `textos` una página de 200 nodos en el orden del documento, cada uno con su texto, vigencia, fuente y checksum (`page`; revisa `text_page.has_more`), y se rige por los permisos y la cuota de la cuenta. |
| `map_legal_topic` | `query`, `fecha`, `jurisdiccion` | Citas del catálogo limitado de temas, fuentes y advertencias. |
| `get_legal_article` | `article_id`, `fecha` | Artículo completo por UUID con fuente, vigencia y SHA. |
| `list_legal_norms` | `jurisdiccion` | Catálogo paginado; filtros `materia`, `page` y `limit`. |
| `get_legal_norm` | `norma` | Metadatos actuales de la norma por slug. |
| `get_legal_article_history` | `article_id` | Versiones conservadas con sus periodos, fuente y SHA. |
| `get_corpus_status` | Ninguno | Estado público del corpus y monitor, con fecha UTC; sin consumo. |

- `fecha` acepta `"vigente"` (fecha actual en la Ciudad de México) o
  `YYYY-MM-DD`. Una fecha anterior al inicio de cobertura devuelve
  `outside_coverage` y una futura (más allá de mañana), `future_not_available`;
  nunca se presenta texto actual como histórico ni como futuro.
- `jurisdiccion` sólo acepta `"federal"` mientras no existan programas estatales.

## Errores

Cada error llega al agente con la acción para su siguiente llamada.

| Código | Lo que verá el agente |
|---|---|
| 401 | La clave es inválida, expiró o fue revocada. |
| 402 | Saldo agotado, con el enlace para recargar créditos y la indicación de no reintentar y avisar al responsable de la cuenta. |
| 403 | La clave no tiene el permiso requerido o conserva las restricciones de su contrato anterior. |
| 404 | La norma no existe (con la forma de obtener su slug u omitirlo) o, en `get_norm_structure`, la fecha es anterior al inicio de cobertura de la norma (`outside_coverage`, con la fecha desde la que hay texto y la fecha con la que conviene volver a llamar) o es futura (`future_not_available`, con la indicación de volver con `fecha="vigente"`). En `search_mexican_law` y `resolve_legal_citation` la falta de cobertura llega en la respuesta (`meta.coverage` y `coverage`), sin costo. |
| 429 | Límite de cuenta alcanzado. `Retry-After` indica la espera; `monthly_quota_exceeded` se renueva el siguiente mes UTC y no exige créditos. El SDK solo reintenta esperas cortas (hasta 30 s), hasta dos veces. |
| Red | No se pudo contactar a Lex API MX. |

## Lectura incluida y versión 0.4.0

API y MCP requieren la misma clave de una cuenta con correo confirmado. La política
activa de Cuenta determina cuota y permisos; la lectura incluida no exige créditos.
La cuota mensual se comparte entre claves por cuenta y mes UTC. `monthly_quota_exceeded`
indica cuándo se renueva; no se resuelve comprando créditos. Se mantienen límites de
texto, resultados, tamaño y concurrencia.

El MCP 0.4.0 incluye también mapa, artículo por UUID, catálogo paginado, metadatos
de norma, historial y estado del corpus. El mapa conserva un catálogo limitado de temas.
El SDK expone `article`, `list_norms`, `norm`, `article_history` y `corpus_status`.
Las ocho lecturas normativas aceptan
`idempotency_key`: conserva identificador y parámetros para el mismo reintento;
una petición distinta es otro evento. No se eliminan límites de ráfagas por reintentar.
`get_corpus_status` consulta el estado público y no consume cuota.

Los contratos previos, saldos e historial se conservan. El catálogo activo informa
la oferta gratuita y empresarial por volumen/garantías verificadas; sin precio ni
SLA por defecto, semántica, alertas en tiempo real ni CFDI automático operativo.
