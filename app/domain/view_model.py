"""Transformações dos modelos internos para as respostas públicas da API."""

from app.schemas.provider import GeoResult, OneCallBundle
from app.schemas.view import CitySearchResult, CityView, ReverseResult, WeatherView


def build_weather_view(bundle: OneCallBundle) -> WeatherView:
    """Entrega os blocos meteorológicos presentes no pacote do provedor."""
    return WeatherView.model_validate(bundle.model_dump(exclude_none=True))


def build_search_result(cities: list[GeoResult]) -> CitySearchResult:
    """Converte os resultados de geocodificação para o contrato público da busca."""
    return CitySearchResult(
        results=[
            CityView(
                name=city.name,
                lat=city.lat,
                lon=city.lon,
                country=city.country,
                state=city.state,
            )
            for city in cities
        ]
    )


def build_reverse_result(cities: list[GeoResult]) -> ReverseResult:
    """Retorna a primeira cidade encontrada ou `null` quando não há resultado."""
    results = build_search_result(cities).results
    return ReverseResult(result=results[0] if results else None)
