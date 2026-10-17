"""Contratos de resposta da API usados pelo frontend."""

from typing import Any

from pydantic import BaseModel


class CityView(BaseModel):
    name: str
    lat: float
    lon: float
    country: str
    state: str | None = None


class CitySearchResult(BaseModel):
    results: list[CityView]


class ReverseResult(BaseModel):
    result: CityView | None


class WeatherView(BaseModel):
    timezone_offset: int | None = None
    current: dict[str, Any] | None = None
    minutely: list[dict[str, Any]] | None = None
    hourly: list[dict[str, Any]] | None = None
    daily: list[dict[str, Any]] | None = None
    alerts: list[dict[str, Any]] | None = None
