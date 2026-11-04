"""Adaptador MCP sobre la API pública de Lex API MX.

El servidor no contiene corpus ni lógica normativa: traduce llamadas de
herramientas MCP a la API HTTP y devuelve sus paquetes JSON sin reescribirlos.
La única excepción es la estructura de una norma, que se compacta en un índice
para que quepa en el contexto del agente (la de la LFT pesa más de 1 MB).
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import date, datetime
from typing import Annotated, Any, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
from lex_api_mx import LexApiClient, LexApiError
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from . import __version__

DEFAULT_BASE_URL = "https://api.lexapi.mx"
DASHBOARD_URL = "https://lexapi.mx/cuenta"

# Protección del contexto del agente: unos 100 mil tokens.
MAX_RESULT_CHARS = 400_000

INSTRUCTIONS = """\
Lex API MX entrega legislación federal mexicana estructurada y versionada, con la
fuente oficial, el checksum SHA-256 y la vigencia de cada texto. Reglas de uso:
1. Antes de afirmar qué dice una ley o un reglamento federal mexicano, consulta
   estas herramientas; no respondas de memoria.
2. Elige la herramienta: con una cita ("Artículo 47 LFT") o una situación descrita
   en una frase, resolve_legal_citation; para localizar artículos por tema sin
   conocer el número, search_mexican_law; para saber qué artículos tiene una norma
   o hasta qué número llega, get_norm_structure. Para descubrir slugs usa
   list_legal_norms; para metadatos actuales, get_legal_norm; para versiones
   conservadas, get_legal_article_history; para estado y alcance, get_corpus_status.
3. Cita exactamente la referencia canónica, el URL de la fuente oficial y el
   checksum que devuelva la herramienta; no inventes artículos ni fracciones.
4. Si la respuesta dice `not_found` o no trae resultados, dilo explícitamente. Si
   dice `outside_coverage`, explica que no hay texto anterior a
   `coverage_start_date`; si dice `future_not_available`, que no se pronostican
   reformas; nunca presentes el texto vigente como histórico ni como futuro.
5. Usa `fecha="vigente"` salvo que el usuario pregunte por un momento concreto. El
   texto devuelto es el que regía en esa fecha (`valid_from` a `valid_to`): si los
   hechos del caso ocurrieron en otra fecha, consulta también esa fecha y dilo.
6. Si una herramienta responde un error, sigue la acción que propone antes de
   rendirte.
7. API y MCP comparten cuenta, permisos y cuota. La lectura incluida permite
   artículos completos, estructura, FTS, resolve y mapa dentro de su cobertura.
   Respeta los límites de resultados, texto y concurrencia; no extraigas el corpus
   sin límite. Revisa la política activa de la cuenta.
8. Saldo anterior agotado (402): no reintentes; indica al responsable que revise
   Cuenta para activar el acceso gratuito. No sugieras comprar créditos.
9. Cuota mensual agotada (429 monthly_quota_exceeded): no reintentes en bucle;
   informa cuándo se renueva. No requiere comprar créditos. Para un reintento
   identificado conserva idempotency_key y todos los parámetros; la ráfaga sí cuenta.
"""

Fecha = Annotated[
    str,
    Field(
        pattern=r"^(vigente|\d{4}-\d{2}-\d{2})$",
        description=(
            "Fecha de vigencia a consultar: 'vigente' para la fecha actual en México, "
            "o una fecha ISO YYYY-MM-DD si el usuario pregunta por un momento concreto."
        ),
    ),
]
Jurisdiccion = Annotated[
    Literal["federal"],
    Field(description="Jurisdicción normativa. La cobertura actual es sólo federal."),
]
Norma = Annotated[
    str | None,
    Field(
        max_length=120,
        description="Slug de la norma para acotar la búsqueda (ej. 'lft', 'cff', 'lisr').",
    ),
]
IdempotencyKey = Annotated[
    str | None,
    Field(
        max_length=200,
        description="Identificador del mismo reintento; conserva también todos los parámetros. Una consulta distinta necesita otro identificador.",
    ),
]

READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True)

# Partes de un artículo: el índice no las lista, solo las cuenta.
ARTICLE_PARTS = frozenset({"fraccion", "inciso", "apartado"})
# Campos de cada nodo con texto (`include_text=True`), tal como los devuelve la API.
TEXT_FIELDS = (
    "node_type",
    "number",
    "label",
    "path",
    "node_version_id",
    "text",
    "checksum",
    "valid_from",
    "valid_to",
    "source",
    "source_url",
)


def today_in_mexico() -> date:
    try:
        return datetime.now(ZoneInfo("America/Mexico_City")).date()
    except ZoneInfoNotFoundError:
        return date.today()


def resolve_fecha(fecha: str) -> str:
    if fecha == "vigente":
        return today_in_mexico().isoformat()
    try:
        return date.fromisoformat(fecha).isoformat()
    except ValueError as exc:
        raise ToolError(f"Fecha inválida '{fecha}': usa 'vigente' o YYYY-MM-DD.") from exc


def _error_detail(error: LexApiError) -> dict[str, Any]:
    body = error.body if isinstance(error.body, dict) else {}
    detail = body.get("detail")
    return detail if isinstance(detail, dict) else {}


def _sentence(text: str) -> str:
    text = text.strip()
    return text if text.endswith((".", "!", "?")) else f"{text}."


def _wait_hint(seconds: float | None) -> str:
    if seconds is None:
        return "Espera un momento y reintenta."
    if seconds >= 3600:
        return f"Se libera en unas {round(seconds / 3600)} horas; no reintentes antes."
    return f"Reintenta en {max(1, round(seconds))} segundos."


NORM_HINT = (
    "Usa el slug que trae `norm.slug` en un resultado de resolve_legal_citation o "
    "search_mexican_law, u omite `norma` en esas herramientas: resolve_legal_citation "
    "infiere la norma de la cita (ej. 'Artículo 47 LFT')."
)


def describe_api_error(error: LexApiError) -> str:
    """Mensaje para el agente: qué pasó y qué hacer en la siguiente llamada."""
    detail = _error_detail(error)
    code = detail.get("code")
    message = _sentence(str(detail.get("message") or error.detail))
    if error.status_code == 402:
        return (
            "Saldo de las condiciones anteriores agotado. No reintentes: avisa al responsable "
            "de la cuenta para que revise sus condiciones y, si lo desea, active el acceso "
            f"gratuito en {DASHBOARD_URL}. Se conservan el saldo y el historial anteriores."
        )
    if error.status_code == 401:
        return "LEX_API_MX_KEY no es válida, expiró o fue revocada."
    if error.status_code == 403:
        if code == "paid_plan_required":
            return (
                "Esta operación no está habilitada en las condiciones anteriores de la cuenta. "
                f"Revisa los permisos en {DASHBOARD_URL}; su responsable puede activar allí "
                "voluntariamente el acceso gratuito, que incluye mapa y estructura con texto."
            )
        return f"La API key no tiene el permiso requerido para esta operación: {error.detail}"
    if error.status_code == 404:
        if code == "outside_coverage":
            start = detail.get("coverage_start_date")
            return (
                f"{message} Vuelve a llamar con una fecha igual o posterior a {start} o con "
                "fecha='vigente', y aclara al usuario que no hay texto anterior a esa fecha."
            )
        if code == "future_not_available":
            return (
                f"{message} Vuelve a llamar con fecha='vigente' y aclara al usuario que "
                "Lex API MX no pronostica reformas: el texto que recibirá es el vigente hoy."
            )
        if code in ("norm_not_found", "norm_blocked") or not code:
            return f"{message} {NORM_HINT}"
    if error.status_code == 409:
        return f"{message} {NORM_HINT}"
    if error.status_code == 429:
        if code == "monthly_quota_exceeded":
            return f"{message} No reintentes en bucle. La cuota se renueva en {detail.get('resets_at', 'el siguiente mes UTC')}; no se desbloquea comprando créditos."
        return f"Límite de peticiones alcanzado. {message} {_wait_hint(error.retry_after)}"
    suffix = f" (request_id={error.request_id})" if error.request_id else ""
    return f"Lex API MX respondió {error.status_code}: {message}{suffix}"


def _is_article(node: dict[str, Any]) -> bool:
    """Un artículo, o un transitorio que no agrupa otros transitorios."""
    if node.get("node_type") == "articulo":
        return True
    return node.get("node_type") == "transitorio" and not any(
        child.get("node_type") == "transitorio" for child in node.get("children") or []
    )


def _count(node: dict[str, Any], counts: Counter) -> None:
    counts[node.get("node_type")] += 1
    for child in node.get("children") or []:
        _count(child, counts)


def _index_entry(node: dict[str, Any], counts: Counter, articles: list[str]) -> Any:
    """Un artículo es su número; una división, su etiqueta con su contenido en orden."""
    if _is_article(node):
        _count(node, counts)
        number = str(node.get("number") or node.get("label") or "")
        if node.get("node_type") == "articulo":
            articles.append(number)
        return number
    counts[node.get("node_type")] += 1
    content = []
    for child in node.get("children") or []:
        if child.get("node_type") in ARTICLE_PARTS:
            _count(child, counts)
        else:
            content.append(_index_entry(child, counts, articles))
    label = node.get("label") or f"{node.get('node_type')} {node.get('number') or ''}".strip()
    return {"etiqueta": label, "contenido": content}


def _text_nodes(nodes: list[dict[str, Any]], out: list[dict[str, Any]]) -> None:
    for node in nodes:
        if "text" in node:
            out.append({field: node[field] for field in TEXT_FIELDS if field in node})
        _text_nodes(node.get("children") or [], out)


def compact_structure(payload: dict[str, Any]) -> dict[str, Any]:
    """Índice de la norma: divisiones con su contenido y artículos por número.

    Quita los ids, rutas y partes de artículo que inflan el árbol (3,312 nodos en la
    LFT) y agrega el primer y el último artículo. Los nodos con texto de la página
    pedida se devuelven aparte, en el orden del árbol y con sus campos sin cambios.
    """
    counts: Counter = Counter()
    articles: list[str] = []
    index = [_index_entry(node, counts, articles) for node in payload.get("estructura") or []]
    result: dict[str, Any] = {"norma": payload.get("norma"), "fecha": payload.get("fecha")}
    if payload.get("requested_slug"):
        result["requested_slug"] = payload["requested_slug"]
    if payload.get("applicability_notice"):
        result["applicability_notice"] = payload["applicability_notice"]
    result["resumen"] = {
        "articulos": len(articles),
        "primer_articulo": articles[0] if articles else None,
        "ultimo_articulo": articles[-1] if articles else None,
        "nodos_por_tipo": dict(sorted(counts.items(), key=lambda item: str(item[0]))),
    }
    result["indice"] = index
    if payload.get("text_page") is not None:
        texts: list[dict[str, Any]] = []
        _text_nodes(payload.get("estructura") or [], texts)
        result["text_page"] = payload["text_page"]
        result["textos"] = texts
    return result


def fit_context(result: dict[str, Any]) -> dict[str, Any]:
    size = len(json.dumps(result, ensure_ascii=False, default=str))
    if size > MAX_RESULT_CHARS:
        raise ToolError(
            "La respuesta es demasiado grande para el contexto del agente "
            f"({size // 1024} KB). Acota la consulta: reduce `limit`, filtra con `norma` "
            "o pide otra página."
        )
    return result


def build_server(client: LexApiClient) -> MCPServer:
    server = MCPServer(
        name="lex-api-mx",
        title="Lex API MX",
        description="Legislación mexicana vigente, estructurada y verificable.",
        instructions=INSTRUCTIONS,
        website_url="https://lexapi.mx",
        version=__version__,
    )

    def call(operation, **kwargs: Any) -> dict[str, Any]:
        try:
            return operation(**kwargs)
        except LexApiError as exc:
            raise ToolError(describe_api_error(exc)) from exc
        except httpx.HTTPError as exc:
            raise ToolError(
                "No se pudo contactar a Lex API MX. Revisa tu conexión o LEX_API_MX_BASE_URL."
            ) from exc

    @server.tool(annotations=READ_ONLY)
    def search_mexican_law(
        query: Annotated[
            str,
            Field(
                min_length=2,
                max_length=500,
                description=(
                    "De 2 a 5 términos jurídicos en español (ej. 'aguinaldo', 'rescisión "
                    "patrón'). Prioriza todos los términos en una disposición y después "
                    "añade coincidencias parciales mediante OR. Busca también en fracciones, "
                    "incisos y apartados, sin distinguir acentos. Las frases entre comillas, "
                    "OR explícito y exclusiones con - conservan sus operadores y no se amplían."
                ),
            ),
        ],
        fecha: Fecha,
        jurisdiccion: Jurisdiccion,
        norma: Norma = None,
        materia: Annotated[
            str | None,
            Field(max_length=80, description="Materia para acotar (ej. 'laboral', 'fiscal')."),
        ] = None,
        limit: Annotated[int, Field(ge=1, le=50)] = 10,
        idempotency_key: IdempotencyKey = None,
    ) -> dict[str, Any]:
        """Busca por términos artículos de leyes y reglamentos federales mexicanos con el texto que regía en `fecha`.

        Úsala cuando necesites el fundamento legal de un tema y no conozcas el artículo
        exacto; si ya tienes la cita (norma y número), usa resolve_legal_citation. La
        búsqueda es por términos, no semántica: escribe palabras clave, no una pregunta
        completa. Prioriza coincidencias de todos los términos en una disposición; después
        incluye coincidencias parciales mediante OR. Busca en el artículo y sus fracciones,
        incisos y apartados, sin distinguir acentos. Las frases entre comillas, OR explícito
        y exclusiones con - no se amplían. Cada resultado es el artículo completo con su
        cita canónica, su vigencia (`valid_from`, `valid_to`), el URL de la fuente
        oficial y el checksum SHA-256. Si `data` llega vacío, revisa
        `meta.coverage.status` y reformula con sinónimos jurídicos antes de concluir
        que no hay fundamento.
        """
        return fit_context(
            call(
                client.search_articles,
                query=query,
                norm=norma,
                matter=materia,
                jurisdiction=jurisdiccion,
                as_of=resolve_fecha(fecha),
                limit=limit,
                idempotency_key=idempotency_key,
            )
        )

    @server.tool(annotations=READ_ONLY)
    def get_norm_structure(
        norma: Annotated[
            str,
            Field(
                min_length=1,
                max_length=120,
                description="Slug de la norma (ej. 'lft', 'cff', 'cpeum').",
            ),
        ],
        fecha: Fecha,
        include_text: Annotated[
            bool,
            Field(
                description=(
                    "Incluir el texto de los nodos conforme a los permisos y cuota de la cuenta. "
                    "El texto llega por páginas de 200 nodos en el orden del árbol: "
                    "revisa text_page.has_more y pide la siguiente con page."
                )
            ),
        ] = False,
        page: Annotated[
            int, Field(ge=1, description="Página de texto cuando include_text=True.")
        ] = 1,
        idempotency_key: IdempotencyKey = None,
    ) -> dict[str, Any]:
        """Devuelve el índice de una norma federal mexicana en `fecha`: sus divisiones y los números de sus artículos.

        Úsala para conocer la numeración de una norma antes de citarla, para comprobar
        si un artículo existe cuando resolve_legal_citation no lo encuentra y para ubicar
        un artículo en su título o capítulo. `resumen` trae el primer y el último
        artículo y el número de nodos por tipo; en `indice`, cada división tiene su
        `etiqueta` y su `contenido` en orden, donde cada texto suelto es el número de un
        artículo. Las fracciones e incisos se cuentan pero no se listan. Con
        include_text=True, `textos` trae los nodos de la página pedida, en el orden del
        documento, con su texto, su vigencia, su fuente y su checksum.
        """
        return fit_context(
            compact_structure(
                call(
                    client.norm_structure,
                    norm=norma,
                    as_of=resolve_fecha(fecha),
                    include_text=include_text,
                    page=page,
                    idempotency_key=idempotency_key,
                )
            )
        )

    @server.tool(annotations=READ_ONLY)
    def resolve_legal_citation(
        query: Annotated[
            str,
            Field(
                min_length=2,
                max_length=2000,
                description=(
                    "Cita o situación a resolver, ej. 'Artículo 47 LFT', 'art. 27 CFF', "
                    "'Artículo 2 transitorio LFT' o 'causas de rescisión de la relación de "
                    "trabajo sin responsabilidad del patrón'."
                ),
            ),
        ],
        fecha: Fecha,
        jurisdiccion: Jurisdiccion,
        norma: Norma = None,
        limit: Annotated[int, Field(ge=1, le=20)] = 5,
        idempotency_key: IdempotencyKey = None,
    ) -> dict[str, Any]:
        """Resuelve una cita o una situación jurídica a un paquete normativo verificable. Es la herramienta preferida para fundamentar una respuesta.

        Úsala con una cita concreta ('Artículo 47 LFT') o con una situación descrita en
        una frase; la norma se infiere de la consulta, así que pasa `norma` solo si
        conoces su slug. Cada item trae la cita canónica, el artículo completo
        (`full_text`, con fracciones e incisos), la versión con su vigencia, la fuente
        oficial y el checksum. Revisa `coverage.status`: `not_found` significa que no hay
        fundamento para esa consulta (dilo; no lo suplas de memoria ni lo cambies por un
        artículo parecido) y `outside_coverage`, que la fecha es anterior al inicio de la
        cobertura. Lee también `warnings`. Si pediste un artículo por número y no aparece
        en `items`, consulta get_norm_structure para ver la numeración real de la norma.
        """
        return fit_context(
            call(
                client.resolve,
                query=query,
                norm=norma,
                jurisdiction=jurisdiccion,
                as_of=resolve_fecha(fecha),
                limit=limit,
                idempotency_key=idempotency_key,
            )
        )

    @server.tool(annotations=READ_ONLY)
    def map_legal_topic(
        query: Annotated[str, Field(min_length=2, max_length=2000)],
        fecha: Fecha,
        jurisdiccion: Jurisdiccion,
        idempotency_key: IdempotencyKey = None,
    ) -> dict[str, Any]:
        """Consulta el catálogo limitado de temas y sus citas normativas.

        No es un dictamen de aplicabilidad ni búsqueda semántica. Revisa coverage,
        articles_missing y warnings; conserva fuente, vigencia y SHA de cada artículo.
        """
        return fit_context(
            call(
                client.map,
                query=query,
                as_of=resolve_fecha(fecha),
                jurisdiction=jurisdiccion,
                idempotency_key=idempotency_key,
            )
        )

    @server.tool(annotations=READ_ONLY)
    def get_legal_article(
        article_id: Annotated[str, Field(min_length=36, max_length=36)],
        fecha: Fecha,
        idempotency_key: IdempotencyKey = None,
    ) -> dict[str, Any]:
        """Lee un artículo completo por el UUID devuelto por la API, con sus componentes y SHA exacto."""
        return fit_context(
            call(
                client.article,
                article_id=article_id,
                as_of=resolve_fecha(fecha),
                idempotency_key=idempotency_key,
            )
        )

    @server.tool(annotations=READ_ONLY)
    def list_legal_norms(
        jurisdiccion: Jurisdiccion,
        materia: Annotated[str | None, Field(max_length=120)] = None,
        page: Annotated[int, Field(ge=1)] = 1,
        limit: Annotated[int, Field(ge=1, le=100)] = 20,
        idempotency_key: IdempotencyKey = None,
    ) -> dict[str, Any]:
        """Lista el catálogo de normas disponibles y sus slugs, con paginación.

        Son metadatos actuales del catálogo; para texto a una fecha usa las herramientas de lectura.
        """
        return fit_context(
            call(
                client.list_norms,
                jurisdiction=jurisdiccion,
                matter=materia,
                page=page,
                limit=limit,
                idempotency_key=idempotency_key,
            )
        )

    @server.tool(annotations=READ_ONLY)
    def get_legal_norm(
        norma: Annotated[str, Field(min_length=1, max_length=120)],
        idempotency_key: IdempotencyKey = None,
    ) -> dict[str, Any]:
        """Obtiene metadatos actuales de una norma por slug; no representa su texto histórico."""
        return fit_context(call(client.norm, norm=norma, idempotency_key=idempotency_key))

    @server.tool(annotations=READ_ONLY)
    def get_legal_article_history(
        article_id: Annotated[str, Field(min_length=36, max_length=36)],
        idempotency_key: IdempotencyKey = None,
    ) -> dict[str, Any]:
        """Consulta las versiones conservadas de un artículo con fuente, SHA y vigencia.

        La historia es prospectiva desde el baseline; no completa periodos sin cobertura.
        """
        return fit_context(
            call(client.article_history, article_id=article_id, idempotency_key=idempotency_key)
        )

    @server.tool(annotations=READ_ONLY)
    def get_corpus_status() -> dict[str, Any]:
        """Estado vivo del corpus y monitor, con fecha UTC y alcance declarado por la API."""
        return fit_context(call(client.corpus_status))

    return server


def main() -> None:
    api_key = os.environ.get("LEX_API_MX_KEY", "").strip()
    if not api_key:
        print(
            "Falta LEX_API_MX_KEY. Obtén una clave gratuita en "
            f"{DASHBOARD_URL} y agrégala al bloque 'env' de tu cliente MCP.",
            file=sys.stderr,
        )
        sys.exit(1)
    base_url = os.environ.get("LEX_API_MX_BASE_URL", DEFAULT_BASE_URL)
    with LexApiClient(
        base_url=base_url,
        api_key=api_key,
        user_agent=f"lex-api-mx-mcp/{__version__}",
    ) as client:
        build_server(client).run("stdio")


if __name__ == "__main__":
    main()
