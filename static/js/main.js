import { renderForecasts, showForecastError, showForecastLoading } from "./forecasts.js";

const fallbackLocation = {
  latitude: -18.9186,
  longitude: -48.2772,
  label: "Uberlândia, BR (localização padrão)",
  reverseGeocode: false,
};

const searchForm = document.querySelector("#city-search");
const searchInput = document.querySelector("#city-query");
const searchSubmitButton = document.querySelector("#search-submit");
const searchMessageElement = document.querySelector("#search-message");
const searchResultsElement = document.querySelector("#search-results");
const locationElement = document.querySelector("#location");
const iconElement = document.querySelector("#weather-icon");
const temperatureElement = document.querySelector("#temperature");
const descriptionElement = document.querySelector("#description");
const feelsLikeElement = document.querySelector("#feels-like");
const humidityElement = document.querySelector("#humidity");
const messageElement = document.querySelector("#message");
const retryButton = document.querySelector("#retry");

function getLocation() {
  if (!navigator.geolocation) {
    return Promise.resolve(fallbackLocation);
  }

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      ({ coords }) =>
        resolve({
          latitude: coords.latitude,
          longitude: coords.longitude,
          label: "Sua localização",
          reverseGeocode: true,
        }),
      () => resolve(fallbackLocation),
      { timeout: 10000 },
    );
  });
}

function errorMessage(code) {
  const messages = {
    provider_unauthorized:
      "A chave do serviço de clima não foi aceita. Confira a configuração no arquivo .env.",
    provider_rate_limited:
      "O serviço de clima limitou as consultas. Aguarde um pouco e tente novamente.",
    provider_timeout: "O serviço de clima demorou para responder. Tente novamente.",
    network_unavailable: "Não foi possível conectar ao serviço de clima.",
    provider_unavailable: "O serviço de clima está indisponível no momento.",
    invalid_request: "Confira o nome da cidade e tente novamente.",
  };
  return (
    messages[code] ??
    "Não foi possível carregar o clima. Verifique sua conexão e tente novamente."
  );
}

function cityLabel(city) {
  const state = city.state === city.name ? undefined : city.state;
  return [city.name, state, city.country].filter(Boolean).join(", ");
}

async function identifyLocation(location) {
  if (!location.reverseGeocode) {
    return { location, notice: "" };
  }

  try {
    const query = new URLSearchParams({
      lat: String(location.latitude),
      lon: String(location.longitude),
    });
    const response = await fetch(`/api/geo/reverse?${query}`);
    if (!response.ok) {
      throw new Error("reverse_geocoding_failed");
    }
    const body = await response.json();
    if (body.result) {
      return {
        location: {
          ...location,
          label: cityLabel(body.result),
          reverseGeocode: false,
        },
        notice: "",
      };
    }
  } catch {
    return {
      location,
      notice: "Não foi possível identificar o nome da cidade; exibindo o clima da sua localização.",
    };
  }

  return {
    location: { ...location, label: "Sua localização", reverseGeocode: false },
    notice: "Não encontramos um nome de cidade para estas coordenadas.",
  };
}

let currentLocation;
let weatherLoadGeneration = 0;

async function loadWeather(location = currentLocation) {
  const generation = ++weatherLoadGeneration;
  retryButton.hidden = true;
  retryButton.disabled = true;
  messageElement.textContent = "";
  descriptionElement.textContent = "Carregando clima…";
  temperatureElement.textContent = "--°";
  feelsLikeElement.textContent = "--";
  humidityElement.textContent = "--";
  iconElement.removeAttribute("src");
  showForecastLoading();

  try {
    const requestedLocation = location ?? (await getLocation());
    if (generation !== weatherLoadGeneration) {
      return;
    }
    const identified = await identifyLocation(requestedLocation);
    if (generation !== weatherLoadGeneration) {
      return;
    }
    currentLocation = identified.location;
    locationElement.textContent = currentLocation.label;
    const query = new URLSearchParams({
      lat: String(currentLocation.latitude),
      lon: String(currentLocation.longitude),
    });
    const response = await fetch(`/api/weather?${query}`);
    if (generation !== weatherLoadGeneration) {
      return;
    }

    if (!response.ok) {
      const body = await response.json();
      throw new Error(errorMessage(body.error?.code));
    }

    const weather = await response.json();
    const current = weather.current;
    if (
      !current ||
      !Number.isFinite(current.temp) ||
      !Number.isFinite(current.feels_like) ||
      !Number.isFinite(current.humidity) ||
      !Array.isArray(current.weather) ||
      typeof current.weather[0]?.description !== "string" ||
      typeof current.weather[0]?.icon !== "string"
    ) {
      throw new Error("O serviço de clima não retornou as condições atuais.");
    }
    iconElement.src = `https://openweathermap.org/img/wn/${encodeURIComponent(current.weather[0].icon)}@2x.png`;
    temperatureElement.textContent = `${Math.round(current.temp)}°`;
    descriptionElement.textContent = current.weather[0].description;
    feelsLikeElement.textContent = `${Math.round(current.feels_like)}°`;
    humidityElement.textContent = `${current.humidity}%`;
    messageElement.textContent = identified.notice;
    renderForecasts(weather);
  } catch (error) {
    if (generation !== weatherLoadGeneration) {
      return;
    }
    descriptionElement.textContent = "Clima indisponível";
    messageElement.textContent =
      error instanceof Error ? error.message : "Ocorreu um erro inesperado ao carregar o clima.";
    showForecastError();
    retryButton.hidden = false;
  } finally {
    if (generation === weatherLoadGeneration) {
      retryButton.disabled = false;
    }
  }
}

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  searchSubmitButton.disabled = true;
  searchMessageElement.textContent = "Buscando cidades…";
  searchResultsElement.replaceChildren();

  try {
    const query = new URLSearchParams({ q: searchInput.value.trim() });
    const response = await fetch(`/api/geo/search?${query}`);
    if (!response.ok) {
      const body = await response.json();
      throw new Error(errorMessage(body.error?.code));
    }

    const body = await response.json();
    if (body.results.length === 0) {
      searchMessageElement.textContent = "Nenhuma cidade encontrada. Tente outro nome.";
      return;
    }

    searchMessageElement.textContent = "Escolha uma cidade:";
    for (const city of body.results) {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.className = "city-search__result";
      button.type = "button";
      button.textContent = cityLabel(city);
      button.addEventListener("click", () => {
        currentLocation = {
          latitude: city.lat,
          longitude: city.lon,
          label: cityLabel(city),
          reverseGeocode: false,
        };
        searchResultsElement.replaceChildren();
        searchMessageElement.textContent = "";
        loadWeather(currentLocation);
      });
      item.append(button);
      searchResultsElement.append(item);
    }
  } catch (error) {
    searchMessageElement.textContent =
      error instanceof Error ? error.message : "Não foi possível buscar a cidade.";
  } finally {
    searchSubmitButton.disabled = false;
  }
});

retryButton.addEventListener("click", () => loadWeather(currentLocation));
loadWeather();
