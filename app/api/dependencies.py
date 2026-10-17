"""Dependências compartilhadas pelas rotas da API."""

from fastapi import Request

from app.clients.openweather import OpenWeatherClient


def get_client(request: Request) -> OpenWeatherClient:
    """Cliente do provedor criado no ciclo de vida da aplicação."""
    return request.app.state.client
