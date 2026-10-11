"""Adaptador MCP sobre la API pública de Lex API MX.

El servidor no contiene corpus ni lógica normativa: traduce llamadas de
herramientas MCP a la API HTTP y devuelve sus paquetes JSON sin reescribirlos.
"""

from __future__ import annotations

import os
import sys
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
DASHBOARD_URL = "https://lexapi.mx/dashboard"

INSTRUCTIONS = """\
Lex API MX entrega legislación federal mexicana estructurada, versionada y con
fuente oficial. Reglas de uso:
1. Antes de afirmar qué dice una ley mexicana, consulta estas herramientas.
2. Cita exactamente la referencia canónica, el URL de la fuente oficial y el
   checksum que devuelva la herramienta; no inventes artículos ni fracciones.
3. Si la cobertura indica `outside_coverage` o no hay resultados, dilo
   explícitamente; nunca presentes texto vigente como histórico.
4. Usa `fecha="vigente"` salvo que el usuario pregunte por una fecha concreta.
5. `include_text=True` en get_norm_structure requiere un plan de la API; con el
   plan gratuito responde 403. Para leer artículos usa search_mexican_law o
   resolve_legal_citation.
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

READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True)


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


def describe_api_error(error: LexApiError) -> str:
    if error.status_code == 402:
        body = error.body if isinstance(error.body, dict) else {}
        detail = body.get("detail")
        if isinstance(detail, dict) and detail.get("message"):
            return str(detail["message"])
        return (
            "Saldo agotado. El plan gratuito incluye 500 créditos al mes. Para más volumen "
            f"o para integrar Lex API MX en tu producto, contrata un plan en {DASHBOARD_URL}"
        )
    if error.status_code == 401:
        return "LEX_API_MX_KEY no es válida, expiró o fue revocada."
    if error.status_code == 403:
        return f"La API key no tiene el permiso requerido para esta operación: {error.detail}"
    if error.status_code == 429:
        return "Límite de peticiones por minuto alcanzado. Espera un momento y reintenta."
    suffix = f" (request_id={error.request_id})" if error.request_id else ""
    return f"Lex API MX respondió {error.status_code}: {error.detail}{suffix}"


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
            result = operation(**kwargs)

            # Protección de Context Window (aprox. 100k tokens max = ~400k caracteres)
            import json

            size = len(json.dumps(result))
            if size > 400000:
                raise ToolError(
                    "La respuesta es demasiado grande para el contexto del agente "
                    f"({size // 1024} KB). Por favor, acota tu búsqueda (reduce el límite "
                    "o establece include_text=False en get_norm_structure)."
                )

            return result
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
                description="Términos a buscar en artículos vigentes (búsqueda full-text en español).",
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
    ) -> dict[str, Any]:
        """Busca artículos de leyes y reglamentos federales mexicanos vigentes a una fecha.

        Cada resultado trae texto oficial, cita canónica, vigencia, fuente oficial y checksum.
        """
        return call(
            client.search_articles,
            query=query,
            norm=norma,
            matter=materia,
            jurisdiction=jurisdiccion,
            as_of=resolve_fecha(fecha),
            limit=limit,
        )

    @server.tool(annotations=READ_ONLY)
    def get_norm_structure(
        norma: Annotated[
            str,
            Field(min_length=1, max_length=120, description="Slug de la norma (ej. 'lft')."),
        ],
        fecha: Fecha,
        include_text: Annotated[
            bool,
            Field(
                description=(
                    "Incluir el texto de cada nodo (planes de la API; el plan gratuito recibe "
                    "403). Respuestas grandes; úsalo con cuidado."
                )
            ),
        ] = False,
    ) -> dict[str, Any]:
        """Devuelve el árbol de una norma federal: libros, títulos, capítulos, artículos y fracciones."""
        return call(
            client.norm_structure,
            norm=norma,
            as_of=resolve_fecha(fecha),
            include_text=include_text,
        )

    @server.tool(annotations=READ_ONLY)
    def resolve_legal_citation(
        query: Annotated[
            str,
            Field(
                min_length=2,
                max_length=2000,
                description=(
                    "Cita o situación a resolver, ej. 'Artículo 47 LFT' o "
                    "'causas de rescisión de la relación de trabajo sin responsabilidad del patrón'."
                ),
            ),
        ],
        fecha: Fecha,
        jurisdiccion: Jurisdiccion,
        norma: Norma = None,
        limit: Annotated[int, Field(ge=1, le=20)] = 5,
    ) -> dict[str, Any]:
        """Resuelve una consulta o cita a un paquete normativo verificable.

        Devuelve normas, nodos, citas canónicas, versiones vigentes, cobertura temporal,
        fuente oficial y checksum. Es la herramienta preferida para fundamentar respuestas.
        """
        return call(
            client.resolve,
            query=query,
            norm=norma,
            jurisdiction=jurisdiccion,
            as_of=resolve_fecha(fecha),
            limit=limit,
        )

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
