import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from playwright.sync_api import Page, Route, expect


class QuietStaticHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def do_GET(self) -> None:
        if urlsplit(self.path).path == "/":
            self.path = "/static/index.html"
        super().do_GET()


@pytest.fixture
def frontend_url() -> str:
    root = Path(__file__).resolve().parents[2]
    handler = partial(QuietStaticHandler, directory=str(root))
    with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            thread.join()


@pytest.mark.e2e
def test_search_selects_city_and_refreshes_weather(page: Page, frontend_url: str) -> None:
    weather_queries: list[dict[str, list[str]]] = []

    def mock_api(route: Route) -> None:
        url = urlsplit(route.request.url)
        if url.path == "/api/geo/reverse":
            body = {
                "result": {
                    "name": "São Paulo",
                    "lat": -23.55,
                    "lon": -46.63,
                    "country": "BR",
                    "state": "São Paulo",
                }
            }
        elif url.path == "/api/geo/search":
            body = {
                "results": [
                    {
                        "name": "Curitiba",
                        "lat": -25.43,
                        "lon": -49.27,
                        "country": "BR",
                        "state": "Paraná",
                    }
                ]
            }
        elif url.path == "/api/weather/current":
            weather_queries.append(parse_qs(url.query))
            body = {
                "temperature": 20.5,
                "feels_like": 21.1,
                "humidity": 52,
                "description": "céu limpo",
                "icon": "01d",
            }
        else:
            route.fulfill(status=404, json={"error": {"code": "not_found"}})
            return

        route.fulfill(status=200, content_type="application/json", body=json.dumps(body))

    page.context.grant_permissions(["geolocation"])
    page.context.set_geolocation({"latitude": -23.55, "longitude": -46.63})
    page.route("**/api/**", mock_api)
    page.route("https://openweathermap.org/**", lambda route: route.abort())
    page.goto(frontend_url)

    expect(page.locator("#location")).to_have_text("São Paulo, BR")
    expect(page.locator("#temperature")).to_have_text("21°")

    page.get_by_label("Consultar outra cidade").fill("Curitiba")
    page.get_by_role("button", name="Buscar").click()
    page.get_by_role("button", name="Curitiba, Paraná, BR").click()

    expect(page.locator("#location")).to_have_text("Curitiba, Paraná, BR")
    expect(page.locator("#temperature")).to_have_text("21°")
    assert len(weather_queries) == 2
    assert weather_queries[0] == {"lat": ["-23.55"], "lon": ["-46.63"]}
    assert weather_queries[1] == {"lat": ["-25.43"], "lon": ["-49.27"]}
