import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from app.clients.openweather import OpenWeatherClient
from app.main import create_app


def test_current_weather_uses_provider_and_never_returns_api_key() -> None:
    requests: list[httpx.Request] = []

    def provider_response(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "temp": 27.4,
                        "feels_like": 29.1,
                        "humidity": 64,
                        "weather": [{"description": "céu limpo", "icon": "01d"}],
                    }
                ],
                "timezone_offset": -10800,
            },
        )

    http = httpx.AsyncClient(transport=httpx.MockTransport(provider_response))
    app = create_app(OpenWeatherClient(http, "test-api-key"))
    try:
        with TestClient(app) as browser:
            response = browser.get("/api/weather/current?lat=-18.9&lon=-48.2")
    finally:
        asyncio.run(http.aclose())

    assert response.status_code == 200
    assert response.json() == {
        "temperature": 27.4,
        "feels_like": 29.1,
        "humidity": 64,
        "description": "céu limpo",
        "icon": "01d",
    }
    assert len(requests) == 1
    assert requests[0].url.params["appid"] == "test-api-key"
    assert "test-api-key" not in response.text


def test_invalid_coordinates_are_rejected_before_provider_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-api-key")
    with TestClient(create_app()) as browser:
        response = browser.get("/api/weather/current?lat=91&lon=0")

    assert response.status_code == 422


def test_provider_error_is_returned_without_sensitive_details() -> None:
    def timeout(_: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("simulated timeout")

    http = httpx.AsyncClient(transport=httpx.MockTransport(timeout))
    app = create_app(OpenWeatherClient(http, "test-api-key"))
    try:
        with TestClient(app) as browser:
            response = browser.get("/api/weather/current?lat=0&lon=0")
    finally:
        asyncio.run(http.aclose())

    assert response.status_code == 504
    assert response.json() == {"error": {"code": "provider_timeout"}}


def test_page_and_frontend_script_are_served(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-api-key")
    with TestClient(create_app()) as browser:
        page = browser.get("/")
        script = browser.get("/static/js/main.js")
        forecasts = browser.get("/static/js/forecasts.js")

    assert page.status_code == 200
    assert "Condições atuais" in page.text
    assert "Consultar outra cidade" in page.text
    assert script.status_code == 200
    assert "api/weather?" in script.text
    assert "api/geo/search" in script.text
    assert "api/geo/reverse" in script.text
    assert forecasts.status_code == 200
    assert "renderForecasts" in forecasts.text


def test_server_requires_api_key_when_using_real_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    app = create_app()

    with pytest.raises(RuntimeError, match="OPENWEATHER_API_KEY"), TestClient(app):
        pass
