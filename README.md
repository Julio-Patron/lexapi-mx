<p align="center">
  <img src="brand/lex-api-mx-logo-original.jpg" alt="Lex API MX — Sistema de inteligencia jurídica" width="100%">
</p>

# Lex API MX

**La legislación federal mexicana vigente, como servidor MCP y API.** Cada artículo con su
fuente oficial, su checksum SHA-256 y su periodo de vigencia, listo para que tu
aplicación o tu agente de IA cite la ley sin construir ni mantener un corpus.

Sistema de inteligencia jurídica · [lexapi.mx](https://lexapi.mx) ·
[Documentación](https://lexapi.mx/docs) ·
[Probar sin clave](https://lexapi.mx/probar) ·
[Crear cuenta gratis](https://lexapi.mx/cuenta)

## Para quién

Equipos que necesitan citar la ley con precisión dentro de software: agentes y
asistentes de IA, legaltech, nómina, facturación, contabilidad y fintech. Lex API
MX no es un chatbot ni emite opiniones: devuelve texto vigente, estructura,
fuente, checksum y vigencia, y tu sistema decide qué hacer con ellos.

## Cobertura

| | |
|---|---|
| Ordenamientos federales | Constitución, códigos, leyes y reglamentos; [lista y cifras por fecha de corte](docs/CATALOGO.md) |
| Artículos y disposiciones vigentes hoy | [Estado del corpus](https://api.lexapi.mx/api/v1/corpus/status) (sin clave) |
| Fuente oficial y checksum por disposición | 100 % |
| Fuentes | Cámara de Diputados, Diario Oficial de la Federación, STPS y TJA CDMX |

La lista completa de normas está en [`docs/CATALOGO.md`](docs/CATALOGO.md). La
cobertura es federal y prospectiva: cada norma se conserva desde su fecha de
incorporación; una fecha anterior responde `outside_coverage` y nunca se
presenta texto vigente como histórico.

## Empieza en cinco minutos

**1. Crea tu cuenta** en [lexapi.mx/cuenta](https://lexapi.mx/cuenta): te
enviamos un enlace al correo, sin contraseña ni tarjeta. La clave se muestra una sola vez. Consulta en Cuenta los permisos y límites activos; API y MCP comparten consumo por cuenta.

**2. Conecta tu agente (MCP).** Claude Code:

```bash
claude mcp add lex-api-mx --env LEX_API_MX_KEY=tu_clave -- uvx lex-api-mx-mcp
```

Claude Desktop o Cursor (`claude_desktop_config.json`, `.cursor/mcp.json`):

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

El adaptador incorpora nueve herramientas: `resolve_legal_citation`,
`search_mexican_law`, `get_norm_structure`, `map_legal_topic`, `get_legal_article`,
`list_legal_norms`, `get_legal_norm`, `get_legal_article_history` y `get_corpus_status`. Guía completa:
[`docs/MCP_QUICKSTART.md`](docs/MCP_QUICKSTART.md).

**3. O llama a la API directamente.**

```bash
curl "https://api.lexapi.mx/api/v1/articulos/search?q=rescisi%C3%B3n%20sin%20responsabilidad&norma=lft" \
  -H "X-API-Key: tu_clave"
```

```python
# pip install lex-api-mx-client
from lex_api_mx import LexApiClient

with LexApiClient(base_url="https://api.lexapi.mx", api_key="tu_clave") as client:
    package = client.resolve(query="Artículo 47 LFT", norm="lft")
```

Guía: [`docs/QUICKSTART.md`](docs/QUICKSTART.md) · Referencia:
[`docs/API_SPEC.md`](docs/API_SPEC.md) · Contrato del paquete normativo:
[`docs/NORMATIVE_PACKAGE_CONTRACT.md`](docs/NORMATIVE_PACKAGE_CONTRACT.md).

El mapa está incluido en API y MCP y consulta un catálogo limitado de temas y
citas. No determina de forma exhaustiva el marco aplicable a un caso ni cubre
todas las normas publicadas. Consulta el
[alcance del catálogo](docs/CATALOGO.md#mapa-normativo-alcance-del-catálogo) y revisa
`coverage`, `articles_missing` y `warnings` en cada respuesta.

## Acceso gratuito

Las cuentas con lectura incluida pueden consultar artículos completos, estructura,
búsqueda por términos, resolve y mapa, dentro de su cobertura actual. Se exige
registro por correo confirmado y API key. La cuota mensual se comparte entre
API, SDK y MCP, por cuenta y mes calendario UTC; no exige comprar créditos.
Los valores activos se consultan en [Cuenta](https://lexapi.mx/cuenta) y
`GET /api/v1/checkout/catalog`; se mantienen límites de resultados, tamaño,
concurrencia y texto entregado. El acceso no implica extracción ilimitada.

Solo consumen éxitos con resultado. Errores, vacíos y fuera de cobertura no
consumen; un reintento con idéntica Idempotency-Key y petición no duplica cuota
mensual, pero sí cuenta para ráfagas y texto. Al agotarse la cuota, 429
`monthly_quota_exceeded` indica cuándo se renueva; no exige una recarga.

La API y el MCP son gratuitos; no se venden planes ni recargas. Confirma tu
correo y entra en [Cuenta](https://lexapi.mx/cuenta) para recibir tu primera
clave, que se muestra una sola vez. Las cuentas anteriores pueden aceptar
los límites gratuitos desde Cuenta; sus saldos e historial se conservan.

## Qué hay en este repositorio

- [`packages/lex-api-client`](packages/lex-api-client): SDK de Python
  ([`lex-api-mx-client`](https://pypi.org/project/lex-api-mx-client/) en PyPI).
- [`packages/lex-mcp-server`](packages/lex-mcp-server): servidor MCP
  ([`lex-api-mx-mcp`](https://pypi.org/project/lex-api-mx-mcp/) en PyPI y en el
  [MCP Registry](https://registry.modelcontextprotocol.io) como
  `io.github.Julio-Patron/lex-api-mx`).
- [`docs/`](docs): guías, catálogo de normas, referencia de la API, contrato
  OpenAPI y política de uso de IA.
- [`examples/`](examples): ejemplos de integración.

El SDK y el servidor MCP son adaptadores delgados bajo licencia MIT (ver cada
paquete). El servicio, el corpus normativo, la plataforma y la marca Lex API MX
son propiedad de Lex API MX y no forman parte de este repositorio.

## Soporte

- Dudas e incidencias del SDK o del MCP:
  [Issues](https://github.com/Julio-Patron/lexapi-mx/issues).
- Cuenta, facturación o cobertura: [admin@lexapi.mx](mailto:admin@lexapi.mx).
- [Aviso de Privacidad](https://lexapi.mx/privacidad) ·
  [Términos y Condiciones](https://lexapi.mx/terminos)
