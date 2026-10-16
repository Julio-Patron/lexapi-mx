import asyncio
import json
from datetime import date

import httpx
import pytest
from mcp.server.mcpserver.exceptions import ToolError

from lex_api_mx import LexApiClient
from lex_api_mx_mcp import server as mcp_server


def _build(handler):
    client = LexApiClient(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(handler),
        user_agent="lex-api-mx-mcp/test",
    )
    return mcp_server.build_server(client)


def _call(server, name, arguments):
    return asyncio.run(server.call_tool(name, arguments))


def test_tools_require_date_and_jurisdiction():
    server = _build(lambda request: httpx.Response(500))
    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(tools) == {
        "search_mexican_law",
        "get_norm_structure",
        "resolve_legal_citation",
    }
    assert set(tools["search_mexican_law"].input_schema["required"]) == {
        "query",
        "fecha",
        "jurisdiccion",
    }
    assert set(tools["resolve_legal_citation"].input_schema["required"]) == {
        "query",
        "fecha",
        "jurisdiccion",
    }
    assert set(tools["get_norm_structure"].input_schema["required"]) == {"norma", "fecha"}
    assert all(tool.annotations.read_only_hint for tool in tools.values())


def test_resolve_forwards_contract_payload_and_returns_package_unchanged():
    package = {"contract_version": "1.0", "coverage": {"status": "covered"}, "items": []}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/v1/resolve"
        assert request.headers["X-API-Key"] == "test-key"
        assert request.headers["User-Agent"] == "lex-api-mx-mcp/test"
        assert json.loads(request.content) == {
            "query": "Artículo 47 LFT",
            "norm": "lft",
            "jurisdiction": "federal",
            "limit": 5,
            "date": "2026-08-01",
        }
        return httpx.Response(200, json=package)

    result = _call(
        _build(handler),
        "resolve_legal_citation",
        {
            "query": "Artículo 47 LFT",
            "fecha": "2026-08-01",
            "jurisdiccion": "federal",
            "norma": "lft",
        },
    )

    assert not result.is_error
    assert result.structured_content == package


def test_search_maps_vigente_to_today_in_mexico(monkeypatch):
    monkeypatch.setattr(mcp_server, "today_in_mexico", lambda: date(2026, 10, 8))

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/articulos/search"
        assert dict(request.url.params) == {
            "q": "despido justificado",
            "limit": "10",
            "jurisdiccion": "federal",
            "fecha": "2026-10-08",
            "materia": "laboral",
        }
        return httpx.Response(200, json={"data": []})

    result = _call(
        _build(handler),
        "search_mexican_law",
        {
            "query": "despido justificado",
            "fecha": "vigente",
            "jurisdiccion": "federal",
            "materia": "laboral",
        },
    )

    assert result.structured_content == {"data": []}


def test_structure_escapes_slug_and_sends_flags():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.raw_path.startswith(b"/api/v1/normas/lft%2F..%2Fx/estructura")
        assert dict(request.url.params) == {"include_text": "false", "fecha": "2026-08-01"}
        return httpx.Response(200, json={"norma": "lft", "estructura": []})

    result = _call(
        _build(handler),
        "get_norm_structure",
        {"norma": "lft/../x", "fecha": "2026-08-01"},
    )

    assert result.structured_content["norma"] == "lft"


@pytest.mark.parametrize(
    "arguments",
    [
        {"query": "Artículo 1", "fecha": "ayer", "jurisdiccion": "federal"},
        {"query": "Artículo 1", "fecha": "2026-02-30", "jurisdiccion": "federal"},
        {"query": "Artículo 1", "fecha": "vigente", "jurisdiccion": "jalisco"},
        {"query": "Artículo 1", "jurisdiccion": "federal"},
    ],
)
def test_invalid_date_or_jurisdiction_never_reaches_api(arguments):
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("the API must not be called")

    with pytest.raises(ToolError):
        _call(_build(handler), "resolve_legal_citation", arguments)


@pytest.mark.parametrize(
    ("status", "body", "expected"),
    [
        (402, {"detail": "Insufficient credits"}, "lexapi.mx/dashboard"),
        (
            402,
            {"detail": {"code": "insufficient_credits", "message": "Saldo agotado: recarga."}},
            "Saldo agotado: recarga.",
        ),
        (401, {"detail": "Invalid API Key"}, "LEX_API_MX_KEY"),
        (403, {"detail": "Missing required scope(s)"}, "no tiene el permiso requerido"),
        (
            403,
            {
                "detail": {
                    "code": "paid_plan_required",
                    "message": "El texto completo está en los planes de la API. Contrata uno.",
                    "upgrade_url": "https://lexapi.mx/dashboard",
                }
            },
            "Contrata uno",
        ),
        (429, {"detail": "Too many requests"}, "Límite de peticiones"),
    ],
)
def test_api_errors_become_readable_tool_errors(status, body, expected):
    server = _build(lambda request: httpx.Response(status, json=body))

    with pytest.raises(ToolError, match=expected):
        _call(
            server,
            "search_mexican_law",
            {"query": "aguinaldo", "fecha": "vigente", "jurisdiccion": "federal"},
        )


def test_network_failure_becomes_readable_tool_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    with pytest.raises(ToolError, match="No se pudo contactar"):
        _call(
            _build(handler),
            "get_norm_structure",
            {"norma": "lft", "fecha": "vigente"},
        )


def test_main_requires_api_key(monkeypatch, capsys):
    monkeypatch.delenv("LEX_API_MX_KEY", raising=False)

    with pytest.raises(SystemExit) as exit_info:
        mcp_server.main()

    assert exit_info.value.code == 1
    assert "LEX_API_MX_KEY" in capsys.readouterr().err


def test_norm_structure_text_pages_are_forwarded():
    def handler(request: httpx.Request) -> httpx.Response:
        assert dict(request.url.params) == {
            "include_text": "true",
            "page": "3",
            "fecha": "2026-08-01",
        }
        return httpx.Response(200, json={"norma": "lft", "estructura": [], "text_page": None})

    result = _call(
        _build(handler),
        "get_norm_structure",
        {"norma": "lft", "fecha": "2026-08-01", "include_text": True, "page": 3},
    )
    assert result.structured_content["norma"] == "lft"


def _node(node_type, number, label, children=(), **extra):
    return {
        "id": f"id-{label}",
        "parent_id": None,
        "node_type": node_type,
        "number": number,
        "label": label,
        "path": f"/x/{node_type}/{number}",
        "sort_order": 1,
        "stable_identifier": f"x:{node_type}:{number}",
        "children": list(children),
        **extra,
    }


def _articulo(number, *fracciones, **extra):
    parts = [_node("fraccion", f, f"Artículo {number} Fracción {f}") for f in fracciones]
    return _node("articulo", number, f"Artículo {number}", parts, **extra)


SAMPLE_TREE = [
    _node("titulo", "PRIMERO", "Título PRIMERO", [_articulo("1"), _articulo("2", "I", "II")]),
    _node(
        "titulo",
        "SEGUNDO",
        "Título SEGUNDO",
        [
            _articulo("3"),
            _node("capitulo", "I", "Capítulo I", [_articulo("4 Bis"), _articulo("5")]),
        ],
    ),
    _node(
        "transitorio",
        "transitorios",
        "Transitorios",
        [_node("transitorio", "Primero", "Artículo Primero Transitorio")],
    ),
]


def test_structure_becomes_a_compact_index_with_article_range():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "norma": "x",
                "requested_slug": None,
                "fecha": "2026-08-01",
                "text_page": None,
                "estructura": SAMPLE_TREE,
            },
        )

    result = _call(_build(handler), "get_norm_structure", {"norma": "x", "fecha": "2026-08-01"})

    assert result.structured_content == {
        "norma": "x",
        "fecha": "2026-08-01",
        "resumen": {
            "articulos": 5,
            "primer_articulo": "1",
            "ultimo_articulo": "5",
            "nodos_por_tipo": {
                "articulo": 5,
                "capitulo": 1,
                "fraccion": 2,
                "titulo": 2,
                "transitorio": 2,
            },
        },
        "indice": [
            {"etiqueta": "Título PRIMERO", "contenido": ["1", "2"]},
            {
                "etiqueta": "Título SEGUNDO",
                "contenido": ["3", {"etiqueta": "Capítulo I", "contenido": ["4 Bis", "5"]}],
            },
            {"etiqueta": "Transitorios", "contenido": ["Primero"]},
        ],
    }


def test_structure_text_page_keeps_node_text_fields_in_tree_order():
    version = {
        "node_version_id": "v-2",
        "checksum": "c" * 64,
        "valid_from": "2026-07-18",
        "valid_to": None,
        "source": "Cámara de Diputados",
        "source_url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/x.pdf",
    }
    tree = [
        _node(
            "titulo",
            "PRIMERO",
            "Título PRIMERO",
            [
                _articulo("1"),
                _articulo("2", text="Artículo 2.- Texto.", **version),
            ],
        )
    ]
    tree[0]["children"][1]["children"] = [
        _node("fraccion", "I", "Artículo 2 Fracción I", text="Primera;", **version)
    ]
    page = {"page": 1, "page_size": 200, "total_nodes": 4, "has_more": False}

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"norma": "x", "fecha": "2026-08-01", "text_page": page, "estructura": tree},
        )

    result = _call(
        _build(handler),
        "get_norm_structure",
        {"norma": "x", "fecha": "2026-08-01", "include_text": True},
    )

    content = result.structured_content
    assert content["text_page"] == page
    assert [node["label"] for node in content["textos"]] == [
        "Artículo 2",
        "Artículo 2 Fracción I",
    ]
    assert content["textos"][0] == {
        "node_type": "articulo",
        "number": "2",
        "label": "Artículo 2",
        "path": "/x/articulo/2",
        "node_version_id": "v-2",
        "text": "Artículo 2.- Texto.",
        "checksum": "c" * 64,
        "valid_from": "2026-07-18",
        "valid_to": None,
        "source": "Cámara de Diputados",
        "source_url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/x.pdf",
    }


def test_large_structure_fits_the_agent_context():
    # La LFT sin texto pesa más de 1 MB: 1,266 artículos y 1,700 fracciones con ids y rutas.
    articles = [_articulo(str(n), "I", "II", "III") for n in range(1, 1501)]
    tree = [_node("titulo", "UNICO", "Título ÚNICO", articles)]
    raw = {"norma": "x", "fecha": "2026-08-01", "text_page": None, "estructura": tree}
    assert len(json.dumps(raw)) > mcp_server.MAX_RESULT_CHARS

    result = _call(
        _build(lambda request: httpx.Response(200, json=raw)),
        "get_norm_structure",
        {"norma": "x", "fecha": "2026-08-01"},
    )

    assert not result.is_error
    assert result.structured_content["resumen"]["ultimo_articulo"] == "1500"


def test_oversized_search_result_asks_to_narrow_the_query():
    big = {"data": [{"text": "x" * (mcp_server.MAX_RESULT_CHARS + 1)}]}

    with pytest.raises(ToolError, match="Acota la consulta"):
        _call(
            _build(lambda request: httpx.Response(200, json=big)),
            "search_mexican_law",
            {"query": "aguinaldo", "fecha": "vigente", "jurisdiccion": "federal"},
        )


@pytest.mark.parametrize(
    ("status", "body", "headers", "expected"),
    [
        (
            404,
            {
                "detail": {
                    "code": "outside_coverage",
                    "message": "La fecha 2001-01-01 es anterior al inicio de la cobertura.",
                    "coverage_start_date": "2026-06-17",
                }
            },
            {},
            "posterior a 2026-06-17 o con fecha='vigente'",
        ),
        (
            404,
            {"detail": {"code": "norm_not_found", "message": "Norma 'lfx' no encontrada"}},
            {},
            r"Norma 'lfx' no encontrada\. Usa el slug .* infiere la norma",
        ),
        (404, {"detail": "Norma no encontrada"}, {}, r"Norma no encontrada\. .*omite `norma`"),
        (
            402,
            {
                "detail": {
                    "code": "insufficient_credits",
                    "message": "Saldo agotado.",
                    "top_up_url": "https://lexapi.mx/dashboard",
                }
            },
            {},
            "No reintentes: avisa al responsable .* en https://lexapi.mx/dashboard",
        ),
        (429, {"detail": "Too many requests."}, {"Retry-After": "7200"}, "unas 2 horas"),
        (429, {"detail": "Too many requests."}, {"Retry-After": "45"}, "Reintenta en 45 segundos"),
    ],
)
def test_api_errors_tell_the_agent_what_to_do_next(status, body, headers, expected):
    server = _build(lambda request: httpx.Response(status, headers=headers, json=body))

    with pytest.raises(ToolError, match=expected):
        _call(
            server,
            "resolve_legal_citation",
            {"query": "Artículo 47 LFT", "fecha": "vigente", "jurisdiccion": "federal"},
        )


def test_tool_descriptions_route_the_agent_between_tools():
    server = _build(lambda request: httpx.Response(500))
    tools = {tool.name: tool.description for tool in asyncio.run(server.list_tools())}

    assert "resolve_legal_citation" in tools["search_mexican_law"]
    assert "get_norm_structure" in tools["resolve_legal_citation"]
    assert "`resumen`" in tools["get_norm_structure"]
