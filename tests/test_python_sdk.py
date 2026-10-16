import json
from datetime import date

import httpx
import pytest

from lex_api_mx import LexApiClient, LexApiError, __version__


def test_sdk_resolve_sends_auth_idempotency_and_contract_payload():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/resolve"
        assert request.headers["X-API-Key"] == "test-key"
        assert request.headers["Idempotency-Key"] == "retry-1"
        assert request.headers["User-Agent"] == f"lex-api-mx-python/{__version__}"
        assert request.read()
        return httpx.Response(
            200,
            json={"contract_version": "1.0", "coverage": {"status": "covered"}},
        )

    with LexApiClient(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(handler),
    ) as client:
        response = client.resolve(
            query="Artículo 1 LCM",
            norm="lcm",
            as_of=date(2026, 6, 28),
            limit=5,
            idempotency_key="retry-1",
        )

    assert response["contract_version"] == "1.0"


def test_sdk_map_omits_optional_null_fields():
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload == {"query": "protección de datos", "mode": "api"}
        return httpx.Response(200, json={"coverage": {"coverage_status": "partial"}})

    with LexApiClient(
        base_url="https://api.example.test/",
        api_key="test-key",
        transport=httpx.MockTransport(handler),
    ) as client:
        response = client.map(query="protección de datos")

    assert response["coverage"]["coverage_status"] == "partial"


def test_sdk_exposes_request_id_on_api_error():
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            403,
            headers={"X-Request-ID": "req-123"},
            json={"detail": "Missing required scope(s)"},
        )
    )
    with LexApiClient(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=transport,
    ) as client:
        with pytest.raises(LexApiError) as captured:
            client.resolve(query="Artículo 1 LCM")

    assert captured.value.status_code == 403
    assert captured.value.request_id == "req-123"


def test_sdk_requires_base_url_and_api_key():
    with pytest.raises(ValueError, match="base_url"):
        LexApiClient(base_url="", api_key="key")
    with pytest.raises(ValueError, match="api_key"):
        LexApiClient(base_url="https://api.example.test", api_key="")


def test_norm_structure_sends_the_text_page_only_with_text():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(dict(request.url.params))
        return httpx.Response(200, json={"norma": "lft", "estructura": [], "text_page": None})

    with LexApiClient(
        api_key="k", base_url="https://api.test", transport=httpx.MockTransport(handler)
    ) as client:
        client.norm_structure("lft")
        client.norm_structure("lft", include_text=True, page=2, page_size=100)
    assert seen == [
        {"include_text": "false"},
        {"include_text": "true", "page": "2", "page_size": "100"},
    ]


def test_sdk_uses_the_message_of_a_structured_error_detail():
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            403,
            json={
                "detail": {
                    "code": "paid_plan_required",
                    "message": "El mapa normativo está incluido en los planes de la API.",
                    "upgrade_url": "https://lexapi.mx/dashboard",
                }
            },
        )
    )
    with LexApiClient(
        base_url="https://api.example.test", api_key="test-key", transport=transport
    ) as client:
        with pytest.raises(LexApiError) as captured:
            client.map(query="despido")

    assert captured.value.detail == "El mapa normativo está incluido en los planes de la API."
    assert captured.value.body["detail"]["code"] == "paid_plan_required"
    assert "planes de la API" in str(captured.value)


def _rate_limited_client(responses, monkeypatch, **options):
    """Cliente cuyas respuestas salen en orden de `responses`; registra las esperas."""
    sleeps = []
    monkeypatch.setattr("lex_api_mx.client.time.sleep", sleeps.append)
    queue = list(responses)
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return queue.pop(0)

    client = LexApiClient(
        base_url="https://api.example.test",
        api_key="test-key",
        transport=httpx.MockTransport(handler),
        **options,
    )
    return client, calls, sleeps


def _too_many(retry_after: str | None) -> httpx.Response:
    headers = {"Retry-After": retry_after} if retry_after is not None else {}
    return httpx.Response(429, headers=headers, json={"detail": "Too many requests."})


def test_sdk_waits_retry_after_and_retries_a_429(monkeypatch):
    client, calls, sleeps = _rate_limited_client(
        [_too_many("2"), httpx.Response(200, json={"data": []})], monkeypatch
    )
    with client:
        response = client.search_articles(query="aguinaldo")

    assert response == {"data": []}
    assert len(calls) == 2
    assert sleeps == [2.0]


def test_sdk_gives_up_after_max_retries_and_exposes_retry_after(monkeypatch):
    client, calls, sleeps = _rate_limited_client([_too_many("1")] * 3, monkeypatch)
    with client:
        with pytest.raises(LexApiError) as captured:
            client.resolve(query="Artículo 47 LFT", idempotency_key="k-1")

    assert len(calls) == 3
    assert sleeps == [1.0, 1.0]
    assert all(call.headers["Idempotency-Key"] == "k-1" for call in calls)
    assert captured.value.status_code == 429
    assert captured.value.retry_after == 1.0


@pytest.mark.parametrize(
    ("retry_after", "options", "expected"),
    [
        ("3600", {}, 3600.0),  # límite diario: no se espera una hora
        ("2", {"max_retries": 0}, 2.0),
        (None, {}, None),  # sin Retry-After no hay espera conocida
        ("Wed, 21 Oct 2026 07:28:00 GMT", {}, None),
    ],
)
def test_sdk_does_not_retry_long_or_unknown_waits(monkeypatch, retry_after, options, expected):
    client, calls, sleeps = _rate_limited_client([_too_many(retry_after)], monkeypatch, **options)
    with client:
        with pytest.raises(LexApiError) as captured:
            client.search_articles(query="aguinaldo")

    assert len(calls) == 1
    assert sleeps == []
    assert captured.value.retry_after == expected


def test_sdk_rejects_negative_max_retries():
    with pytest.raises(ValueError, match="max_retries"):
        LexApiClient(base_url="https://api.example.test", api_key="key", max_retries=-1)
