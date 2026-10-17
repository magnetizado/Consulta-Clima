const fallbackLocation = {
  latitude: -18.9186,
  longitude: -48.2772,
  label: "Uberlândia, BR (localização padrão)",
};

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
  };
  return messages[code] ?? "Não foi possível carregar o clima. Verifique sua conexão e tente novamente.";
}

async function loadWeather() {
  retryButton.hidden = true;
  retryButton.disabled = true;
  messageElement.textContent = "";
  descriptionElement.textContent = "Carregando clima…";

  try {
    const location = await getLocation();
    locationElement.textContent = location.label;
    const query = new URLSearchParams({
      lat: String(location.latitude),
      lon: String(location.longitude),
    });
    const response = await fetch(`/api/weather/current?${query}`);

    if (!response.ok) {
      const body = await response.json();
      throw new Error(errorMessage(body.error?.code));
    }

    const weather = await response.json();
    iconElement.src = `https://openweathermap.org/img/wn/${encodeURIComponent(weather.icon)}@2x.png`;
    temperatureElement.textContent = `${Math.round(weather.temperature)}°`;
    descriptionElement.textContent = weather.description;
    feelsLikeElement.textContent = `${Math.round(weather.feels_like)}°`;
    humidityElement.textContent = `${weather.humidity}%`;
    messageElement.textContent = "";
  } catch (error) {
    descriptionElement.textContent = "Clima indisponível";
    messageElement.textContent =
      error instanceof Error ? error.message : "Ocorreu um erro inesperado ao carregar o clima.";
    retryButton.hidden = false;
  } finally {
    retryButton.disabled = false;
  }
}

retryButton.addEventListener("click", loadWeather);
loadWeather();
