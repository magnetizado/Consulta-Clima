const unavailable = "Previsão indisponível para esta cidade.";
const numberFormat = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 });
const svgNamespace = "http://www.w3.org/2000/svg";

function message(text) {
  const element = document.createElement("p");
  element.className = "forecast-message";
  element.textContent = text;
  return element;
}

function temperature(value) {
  return Number.isFinite(value) ? `${Math.round(value)}°` : "—";
}

function precipitation(value) {
  return Number.isFinite(value) ? `${numberFormat.format(value)} mm` : "—";
}

function chance(value) {
  return Number.isFinite(value) && value >= 0 && value <= 1
    ? `${Math.round(value * 100)}%`
    : "—";
}

function condition(record) {
  const description = record.weather?.[0]?.description;
  return typeof description === "string" ? description : "Descrição indisponível";
}

function localDate(timestamp, offset, options) {
  if (!Number.isFinite(timestamp) || !Number.isFinite(offset)) {
    return "Horário indisponível";
  }
  return new Intl.DateTimeFormat("pt-BR", { ...options, timeZone: "UTC" }).format(
    new Date((timestamp + offset) * 1000),
  );
}

function renderDaily(records, offset) {
  const tabs = document.querySelector("#daily-forecast");
  const summary = document.querySelector("#daily-summary");
  tabs.replaceChildren();
  if (!Array.isArray(records) || records.length === 0) {
    summary.textContent = unavailable;
    tabs.append(message(unavailable));
    return;
  }

  function selectDay(index) {
    const selected = records[index];
    const date = index === 0 ? "Hoje" : localDate(selected.dt, offset, { weekday: "long" });
    const temperatureRange = `Máx. ${temperature(selected.temp?.max)} · Mín. ${temperature(selected.temp?.min)}`;
    const chanceOfRain = `Chuva ${chance(selected.pop)}`;
    summary.textContent = `${date}: ${condition(selected)}. ${temperatureRange}. ${chanceOfRain}.`;
    for (const [tabIndex, button] of [...tabs.children].entries()) {
      button.setAttribute("aria-pressed", String(tabIndex === index));
    }
  }

  records.slice(0, 8).forEach((record, index) => {
    const button = document.createElement("button");
    button.className = "daily-forecast__day";
    button.type = "button";
    button.setAttribute("aria-pressed", String(index === 0));
    button.setAttribute(
      "aria-label",
      `${index === 0 ? "Hoje" : localDate(record.dt, offset, { weekday: "long" })}: ${temperature(record.temp?.max)} máxima`,
    );
    const day = document.createElement("span");
    day.textContent =
      index === 0
        ? "Hoje"
        : localDate(record.dt, offset, { weekday: "short", day: "numeric" }).replace(".", "");
    const high = document.createElement("strong");
    high.textContent = temperature(record.temp?.max);
    const low = document.createElement("span");
    low.textContent = temperature(record.temp?.min);
    button.append(day, high, low);
    button.addEventListener("click", () => selectDay(index));
    tabs.append(button);
  });
  selectDay(0);
}

function rainVolume(record) {
  if (Number.isFinite(record.rain)) {
    return record.rain;
  }
  if (record.rain && typeof record.rain === "object") {
    const amount = record.rain["1h"] ?? record.rain["3h"];
    return Number.isFinite(amount) ? amount : undefined;
  }
  return undefined;
}

function drawTemperatureChart(records) {
  const chart = document.querySelector("#hourly-chart");
  chart.replaceChildren();
  const values = records.map((record) => record.temp).filter(Number.isFinite);
  if (values.length < 2) {
    chart.append(message(unavailable));
    return;
  }

  const width = 720;
  const height = 180;
  const padding = 18;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max === min ? 1 : max - min;
  const points = values
    .map((value, index) => {
      const x = padding + (index * (width - padding * 2)) / (values.length - 1);
      const y = height - padding - ((value - min) * (height - padding * 2)) / range;
      return { x, y };
    });
  const svg = document.createElementNS(svgNamespace, "svg");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", "Curva de temperatura nas próximas horas");
  const polyline = document.createElementNS(svgNamespace, "polyline");
  polyline.setAttribute("points", points.map(({ x, y }) => `${x},${y}`).join(" "));
  polyline.setAttribute("fill", "none");
  polyline.setAttribute("stroke", "#2475bd");
  polyline.setAttribute("stroke-width", "4");
  polyline.setAttribute("stroke-linecap", "round");
  polyline.setAttribute("stroke-linejoin", "round");
  svg.append(polyline);
  chart.append(svg);
}

function renderHourly(records, offset) {
  const list = document.querySelector("#hourly-forecast");
  list.replaceChildren();
  if (!Array.isArray(records) || records.length === 0) {
    drawTemperatureChart([]);
    list.append(message(unavailable));
    return;
  }

  const visible = records.slice(0, 24);
  drawTemperatureChart(visible);
  for (const record of visible) {
    const item = document.createElement("article");
    item.className = "hourly-forecast__hour";
    const time = document.createElement("strong");
    time.textContent = localDate(record.dt, offset, { hour: "2-digit", minute: "2-digit" });
    const degrees = document.createElement("span");
    degrees.textContent = temperature(record.temp);
    const rain = document.createElement("span");
    rain.textContent = `Chuva ${chance(record.pop)}`;
    const volume = document.createElement("span");
    volume.textContent = `Volume ${precipitation(rainVolume(record))}`;
    item.append(time, degrees, rain, volume);
    list.append(item);
  }
}

function renderMinutely(records, offset) {
  const chart = document.querySelector("#minutely-chart");
  const summary = document.querySelector("#minutely-summary");
  chart.replaceChildren();
  if (!Array.isArray(records) || records.length === 0) {
    summary.textContent = unavailable;
    chart.append(message(unavailable));
    return;
  }

  const visible = records.slice(0, 60);
  const amounts = visible.map((record) => record.precipitation);
  const known = amounts.filter(Number.isFinite);
  if (known.length === 0) {
    summary.textContent = unavailable;
    chart.append(message(unavailable));
    return;
  }

  const total = known.reduce((sum, value) => sum + value, 0);
  summary.textContent = `Precipitação prevista na próxima hora: ${precipitation(total)}.`;
  const bars = document.createElement("div");
  bars.className = "minutely-chart__bars";
  bars.setAttribute("role", "img");
  bars.setAttribute("aria-label", summary.textContent);
  const max = Math.max(...known);
  visible.forEach((record, index) => {
    const amount = record.precipitation;
    const item = document.createElement("div");
    item.className = "minutely-chart__item";
    const bar = document.createElement("span");
    bar.className = "minutely-chart__bar";
    bar.setAttribute("aria-hidden", "true");
    bar.style.height = `${Number.isFinite(amount) && max > 0 ? Math.max(3, (amount / max) * 72) : 3}px`;
    bar.title = `${localDate(record.dt, offset, { hour: "2-digit", minute: "2-digit" })}: ${precipitation(amount)}`;
    item.append(bar);
    if (index % 10 === 0) {
      const label = document.createElement("span");
      label.className = "minutely-chart__time";
      label.textContent = localDate(record.dt, offset, { hour: "2-digit", minute: "2-digit" });
      item.append(label);
    }
    bars.append(item);
  });
  chart.append(bars);
}

export function showForecastLoading() {
  document.querySelector("#daily-summary").textContent = "Carregando previsão…";
  document.querySelector("#daily-forecast").replaceChildren(message("Carregando previsão…"));
  document.querySelector("#hourly-chart").replaceChildren(message("Carregando previsão…"));
  document.querySelector("#hourly-forecast").replaceChildren();
  document.querySelector("#minutely-summary").textContent = "Carregando previsão…";
  document.querySelector("#minutely-chart").replaceChildren();
}

export function showForecastError() {
  for (const selector of [
    "#daily-summary",
    "#minutely-summary",
  ]) {
    document.querySelector(selector).textContent = unavailable;
  }
  for (const selector of [
    "#daily-forecast",
    "#hourly-chart",
    "#hourly-forecast",
    "#minutely-chart",
  ]) {
    document.querySelector(selector).replaceChildren(message(unavailable));
  }
}

export function renderForecasts(weather) {
  const offset = weather.timezone_offset;
  renderDaily(weather.daily, offset);
  renderHourly(weather.hourly, offset);
  renderMinutely(weather.minutely, offset);
}
