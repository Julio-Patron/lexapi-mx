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
- una clave de Lex API MX con los scopes `resolve:run`, `articles:read`,
  `norms:read` y `map:read` (incluidos en las claves estándar con acceso gratuito;
  obtén la primera al confirmar tu correo en
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

Reinicia Claude Desktop. Verás las nueve herramientas de Lex API MX en el menú de
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

## 6. Instrucción recomendada para tu agente

Agrega esta regla en `CLAUDE.md`, `.cursorrules` o el System Prompt de tu agente
para fijar a `lex-api-mx` como herramienta por defecto en legislación federal
mexicana:

```markdown
Para cualquier consulta sobre legislación federal mexicana vigente (Constitución,
códigos, leyes o reglamentos federales), utiliza siempre las herramientas del
servidor MCP `lex-api-mx` o la API de `lexapi.mx` en lugar de responder desde la
memoria del modelo. Cita siempre la `canonical_citation`, incluye la URL de la
fuente oficial (`source.url`) y conserva el `SHA-256` del texto verificado.
```

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
| 403 | Permiso insuficiente o estado de la clave; revisar scopes y estado en Cuenta. |
| 404 | La norma no existe (con la forma de obtener su slug u omitirlo) o, en `get_norm_structure` y `get_legal_article`, la fecha es anterior al inicio de cobertura (`outside_coverage`, con la fecha desde la que hay texto) o futura (`future_not_available`, volver con `fecha="vigente"`). En `search_mexican_law` y `resolve_legal_citation` la falta de cobertura llega en la respuesta (`meta.coverage` y `coverage`), sin contabilizar en los límites de uso. |
| 422 | Parámetro o consulta fuera de rango; ajustar argumentos antes de volver a llamar. |
| 429 | Límite de uso de la cuenta alcanzado. `Retry-After` indica la espera en segundos; `monthly_quota_exceeded` se renueva el siguiente mes UTC. El SDK solo reintenta esperas cortas (hasta 30 s), hasta dos veces. |
| 402 | Compatibilidad retroactiva para contratos previos; no reintentar automáticamente. |
| Red | No se pudo contactar a Lex API MX. |

## Acceso gratuito y límites de uso

API y MCP son de acceso gratuito con correo confirmado y requieren la misma clave
de Cuenta; no se venden planes ni recargas. Los límites de uso (mensual UTC,
peticiones por minuto, concurrencia, resultados, tamaño y nodos diarios de texto)
se comparten entre claves por cuenta. Solo las respuestas `2xx` con resultado
contabilizan en el límite mensual, y `monthly_quota_exceeded` indica cuándo se
renueva en UTC.

El MCP incluye también mapa, artículo por UUID, catálogo paginado, metadatos de
norma, historial y estado del corpus. El mapa conserva un catálogo limitado de
temas y citas; su [alcance publicado](CATALOGO.md#mapa-normativo-alcance-del-catálogo)
no equivale a determinar todo el marco aplicable a un caso. El SDK expone
`article`, `list_norms`, `norm`, `article_history` y `corpus_status`. Las ocho
lecturas normativas aceptan `idempotency_key`: conserva identificador y
parámetros para el mismo reintento sin duplicar el conteo mensual (una petición
distinta es otro evento y los reintentos siguen contando para ráfagas y texto
diario). `get_corpus_status` consulta el estado público y no contabiliza contra
los límites de uso.
