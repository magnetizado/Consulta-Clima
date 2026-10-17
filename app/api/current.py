"""Rota para consultar e apresentar as condições meteorológicas atuais."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ValidationError

from app.api.dependencies import get_client
from app.clients.openweather import OpenWeatherClient, ProviderError

logger = logging.getLogger("app.api")

router = APIRouter(prefix="/api")
Client = Annotated[OpenWeatherClient, Depends(get_client)]
Latitude = Annotated[float, Query(ge=-90, le=90)]
Longitude = Annotated[float, Query(ge=-180, le=180)]


class CurrentConditions(BaseModel):
    temperature: float
    feels_like: float
    humidity: int
    description: str
    icon: str


@router.get("/weather/current", response_model=CurrentConditions)
async def current_weather(lat: Latitude, lon: Longitude, client: Client) -> CurrentConditions:
    """Retorna os dados necessários para o primeiro cartão do dashboard."""
    bundle = await client.current(lat, lon)
    current = bundle.get("current")
    if not isinstance(current, dict):
        logger.warning("Resposta do provedor sem condições atuais")
        raise ProviderError("provider_unavailable")

    weather = current.get("weather")
    if not isinstance(weather, list) or not weather or not isinstance(weather[0], dict):
        logger.warning("Resposta do provedor sem descrição das condições atuais")
        raise ProviderError("provider_unavailable")

    try:
        return CurrentConditions.model_validate(
            {
                "temperature": current.get("temp"),
                "feels_like": current.get("feels_like"),
                "humidity": current.get("humidity"),
                "description": weather[0].get("description"),
                "icon": weather[0].get("icon"),
            }
        )
    except ValidationError as error:
        logger.warning("Resposta do provedor com campos atuais inválidos")
        raise ProviderError("provider_unavailable") from error
