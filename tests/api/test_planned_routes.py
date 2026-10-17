import asyncio
from collections.abc import Callable

import httpx
import pytest
from fastapi.testclient import TestClient

from app.clients.openweather import OpenWeatherClient
from app.main import create_app

ProviderHandler = Callable[[httpx.Request], httpx.Response]


def _browser(handler: ProviderHandler) -> tuple[TestClient, httpx.AsyncClient]:
    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    app = create_app(OpenWeatherClient(http, "test-api-key"))
    return TestClient(app), http


def test_weather_route_returns_available_forecast_blocks() -> None:
    def provider_response(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/current"):
            record = {"temp": 22, "weather": [{"description": "nublado", "icon": "04d"}]}
        elif request.url.path.endswith("/1min"):
            record = {"dt": 1, "precipitation": 0}
        elif request.url.path.endswith("/1h"):
            record = {"dt": int(request.url.params["start"]), "temp": 23}
        elif request.url.path.endswith("/1day"):
            record = {"dt": 2, "temp": {"min": 18, "max": 25}}
        else:
            pytest.fail(f"unexpected provider path: {request.url.path}")
        return httpx.Response(200, json={"data": [record], "timezone_offset": -10800})

    browser, http = _browser(provider_response)
    try:
        with browser:
            response = browser.get("/api/weather?lat=-18.9&lon=-48.2")
    finally:
        asyncio.run(http.aclose())

    assert response.status_code == 200
    body = response.json()
    assert body["timezone_offset"] == -10800
    assert body["current"]["temp"] == 22
    assert body["minutely"] == [{"dt": 1, "precipitation": 0}]
    assert len(body["hourly"]) == 2
    assert body["daily"] == [{"dt": 2, "temp": {"min": 18, "max": 25}}]
    assert "test-api-key" not in response.text


def test_city_search_returns_validated_city_fields() -> None:
    def provider_response(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "name": "Curitiba",
                    "lat": -25.4284,
                    "lon": -49.2733,
                    "country": "BR",
                    "state": "Paraná",
                }
            ],
        )

    browser, http = _browser(provider_response)
    try:
        with browser:
            response = browser.get("/api/geo/search?q=Curitiba")
    finally:
        asyncio.run(http.aclose())

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {
                "name": "Curitiba",
                "lat": -25.4284,
                "lon": -49.2733,
                "country": "BR",
                "state": "Paraná",
            }
        ]
    }


def test_reverse_geocoding_returns_null_when_city_is_not_found() -> None:
    def provider_response(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    browser, http = _browser(provider_response)
    try:
        with browser:
            response = browser.get("/api/geo/reverse?lat=0&lon=0")
    finally:
        asyncio.run(http.aclose())

    assert response.status_code == 200
    assert response.json() == {"result": None}


def test_short_city_search_term_returns_documented_client_error() -> None:
    def unexpected_provider_call(_: httpx.Request) -> httpx.Response:
        pytest.fail("the provider should not be called for an invalid search term")

    browser, http = _browser(unexpected_provider_call)
    try:
        with browser:
            response = browser.get("/api/geo/search?q=a")
    finally:
        asyncio.run(http.aclose())

    assert response.status_code == 400
    assert response.json() == {"error": {"code": "invalid_request"}}


def test_invalid_provider_city_data_is_reported_as_provider_failure() -> None:
    def provider_response(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[{"name": "cidade sem coordenadas"}])

    browser, http = _browser(provider_response)
    try:
        with browser:
            response = browser.get("/api/geo/search?q=teste")
    finally:
        asyncio.run(http.aclose())

    assert response.status_code == 502
    assert response.json() == {"error": {"code": "provider_unavailable"}}


def test_weather_route_does_not_report_an_empty_bundle_as_success() -> None:
    def provider_response(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": []})

    browser, http = _browser(provider_response)
    try:
        with browser:
            response = browser.get("/api/weather?lat=0&lon=0")
    finally:
        asyncio.run(http.aclose())

    assert response.status_code == 502
    assert response.json() == {"error": {"code": "provider_unavailable"}}


def test_precipitation_tile_returns_png_bytes() -> None:
    image = b"\x89PNG\r\n\x1a\nmock"

    def provider_response(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=image)

    browser, http = _browser(provider_response)
    try:
        with browser:
            response = browser.get("/api/tiles/precipitation/1/0/0.png")
    finally:
        asyncio.run(http.aclose())

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == image
