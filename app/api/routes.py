"""Rotas `/api`: validam os parâmetros, chamam o cliente e devolvem o view model (seção 6.1).

Nenhuma regra de negócio mora aqui: as regras ficam em `app/domain/`. Parâmetro inválido
levanta `InvalidRequestError` antes de qualquer chamada ao provedor.
"""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, Response
from pydantic import ValidationError

from app.api.dependencies import get_client
from app.clients.openweather import OpenWeatherClient, ProviderError
from app.domain.view_model import build_reverse_result, build_search_result, build_weather_view
from app.schemas.provider import GeoResult, OneCallBundle
from app.schemas.view import CitySearchResult, ReverseResult, WeatherView

MIN_TERM = 2  # RN-004
MAX_TERM = 100
MAX_ZOOM = 18
logger = logging.getLogger("app.api")

router = APIRouter(prefix="/api")


class InvalidRequestError(Exception):
    """Parâmetro fora do contrato da seção 6.1. Vira `400 invalid_request`."""


Client = Annotated[OpenWeatherClient, Depends(get_client)]
Latitude = Annotated[float, Query(ge=-90, le=90)]
Longitude = Annotated[float, Query(ge=-180, le=180)]
TileIndex = Annotated[int, Path(ge=0)]


def _cities(raw: list[Any]) -> list[GeoResult]:
    """Itens da geocodificação; o que não for um objeto é ignorado (seção 6.2)."""
    cities = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            cities.append(GeoResult.model_validate(item))
        except ValidationError as error:
            logger.warning("Resposta de geocodificação com campos inválidos")
            raise ProviderError("provider_unavailable") from error
    return cities


@router.get("/weather")
async def weather(lat: Latitude, lon: Longitude, client: Client) -> WeatherView:
    """Condições atuais e previsões da coordenada (RN-059, ADR-013)."""
    bundle = await client.weather(lat, lon)
    try:
        provider_bundle = OneCallBundle.model_validate(bundle)
    except ValidationError as error:
        logger.warning("Resposta meteorológica com campos inválidos")
        raise ProviderError("provider_unavailable") from error
    if provider_bundle.current is None:
        logger.warning("Resposta meteorológica sem condições atuais")
        raise ProviderError("provider_unavailable")
    return build_weather_view(provider_bundle)


@router.get("/geo/search")
async def search(q: str, client: Client) -> CitySearchResult:
    """Até 5 cidades para o termo, que precisa ter de 2 a 100 caracteres (RN-004)."""
    term = q.strip()
    if not MIN_TERM <= len(term) <= MAX_TERM:
        raise InvalidRequestError
    return build_search_result(_cities(await client.geocode(term)))


@router.get("/geo/reverse")
async def reverse(lat: Latitude, lon: Longitude, client: Client) -> ReverseResult:
    """Cidade da localização, ou `null` para "Sua localização" (RN-009)."""
    return build_reverse_result(_cities(await client.reverse(lat, lon)))


@router.get("/tiles/precipitation/{z}/{x}/{y}.png", response_class=Response)
async def precipitation_tile(
    z: Annotated[int, Path(ge=0, le=MAX_ZOOM)], x: TileIndex, y: TileIndex, client: Client
) -> Response:
    """Tile da camada de chuva, com `x` e `y` em [0, 2^z − 1] (ADR-006)."""
    if x >= 2**z or y >= 2**z:
        raise InvalidRequestError
    return Response(await client.tile(z, x, y), media_type="image/png")
