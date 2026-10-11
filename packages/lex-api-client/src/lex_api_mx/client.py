from __future__ import annotations

from datetime import date
from typing import Any
from urllib.parse import quote

import httpx


class LexApiError(RuntimeError):
    def __init__(
        self,
        status_code: int,
        message: str,
        request_id: str | None = None,
        body: Any = None,
    ):
        self.status_code = status_code
        self.request_id = request_id
        self.detail = message
        self.body = body
        suffix = f" request_id={request_id}" if request_id else ""
        super().__init__(f"Lex API MX returned {status_code}: {message}{suffix}")


class LexApiClient:
    """Synchronous client for the stable Lex API MX integration surface."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
        user_agent: str | None = None,
    ) -> None:
        if not base_url.strip():
            raise ValueError("base_url is required")
        if not api_key.strip():
            raise ValueError("api_key is required")
        if user_agent is None:
            from . import __version__  # importación tardía: el paquete importa este módulo

            user_agent = f"lex-api-mx-python/{__version__}"
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            transport=transport,
            headers={
                "X-API-Key": api_key,
                "Accept": "application/json",
                "User-Agent": user_agent,
            },
        )

    def __enter__(self) -> "LexApiClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def resolve(
        self,
        *,
        query: str,
        norm: str | None = None,
        jurisdiction: str = "federal",
        as_of: date | str | None = None,
        limit: int = 10,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "query": query,
            "jurisdiction": jurisdiction,
            "limit": limit,
        }
        if norm is not None:
            payload["norm"] = norm
        if as_of is not None:
            payload["date"] = as_of.isoformat() if isinstance(as_of, date) else as_of
        return self._request(
            "POST",
            "/api/v1/resolve",
            json=payload,
            idempotency_key=idempotency_key,
        )

    def map(
        self,
        *,
        query: str,
        jurisdiction: str | None = None,
        as_of: date | str | None = None,
        mode: str = "api",
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"query": query, "mode": mode}
        if jurisdiction is not None:
            payload["jurisdiction"] = jurisdiction
        if as_of is not None:
            payload["date"] = as_of.isoformat() if isinstance(as_of, date) else as_of
        return self._request(
            "POST",
            "/api/v1/map",
            json=payload,
            idempotency_key=idempotency_key,
        )

    def search_articles(
        self,
        *,
        query: str,
        norm: str | None = None,
        matter: str | None = None,
        jurisdiction: str | None = None,
        as_of: date | str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"q": query, "limit": limit}
        if norm is not None:
            params["norma"] = norm
        if matter is not None:
            params["materia"] = matter
        if jurisdiction is not None:
            params["jurisdiccion"] = jurisdiction
        if as_of is not None:
            params["fecha"] = as_of.isoformat() if isinstance(as_of, date) else as_of
        return self._request("GET", "/api/v1/articulos/search", params=params)

    def norm_structure(
        self,
        norm: str,
        *,
        as_of: date | str | None = None,
        include_text: bool = False,
    ) -> dict[str, Any]:
        """Árbol de la norma; `include_text=True` agrega el texto de cada nodo y
        requiere un plan de la API (403 en el plan gratuito)."""
        if not norm.strip():
            raise ValueError("norm is required")
        params: dict[str, Any] = {"include_text": str(include_text).lower()}
        if as_of is not None:
            params["fecha"] = as_of.isoformat() if isinstance(as_of, date) else as_of
        return self._request(
            "GET",
            f"/api/v1/normas/{quote(norm.strip(), safe='')}/estructura",
            params=params,
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None
        response = self._client.request(method, path, json=json, params=params, headers=headers)
        if response.is_error:
            body: Any = None
            try:
                body = response.json()
                message = str(body.get("detail", body)) if isinstance(body, dict) else str(body)
            except ValueError:
                message = response.text or response.reason_phrase
            raise LexApiError(
                response.status_code,
                message,
                response.headers.get("X-Request-ID"),
                body,
            )
        try:
            value = response.json()
        except ValueError as exc:
            raise LexApiError(
                response.status_code,
                "response was not valid JSON",
                response.headers.get("X-Request-ID"),
            ) from exc
        if not isinstance(value, dict):
            raise LexApiError(
                response.status_code,
                "response JSON must be an object",
                response.headers.get("X-Request-ID"),
            )
        return value
