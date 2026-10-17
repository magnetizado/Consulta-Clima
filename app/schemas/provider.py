"""Modelos para os dados normalizados recebidos do cliente OpenWeatherMap."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class GeoResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    lat: float
    lon: float
    country: str
    state: str | None = None


class OneCallBundle(BaseModel):
    model_config = ConfigDict(extra="ignore")

    timezone_offset: int | None = None
    current: dict[str, Any] | None = None
    minutely: list[dict[str, Any]] | None = None
    hourly: list[dict[str, Any]] | None = None
    daily: list[dict[str, Any]] | None = None
    alerts: list[dict[str, Any]] | None = None
