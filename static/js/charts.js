// static/js/charts.js

const PRICE_HISTORY_BASE_URL = "/trades/api/price-history/";
const PORTFOLIO_HISTORY_URL = "/trades/api/portfolio-history/";

let priceChartInstance = null;
let portfolioChartInstance = null;

// Track current selections
let currentSymbol = "SPY";
let currentRange = "1D";  // default: 24H

console.log("charts.js loaded");

// Price history (ticker + range) 
async function loadPriceHistory(symbol, range = currentRange, canvasId = "priceChart") {
  symbol = (symbol || "").trim().toUpperCase();
  if (!symbol) return;

  currentSymbol = symbol;
  currentRange = range;

  try {
    const url = `${PRICE_HISTORY_BASE_URL}${encodeURIComponent(symbol)}/?range=${encodeURIComponent(range)}`;
    console.log("Fetching:", url);
    const resp = await fetch(url);
    console.log("price history response status:", resp.status, "symbol:", symbol, "range:", range);

    if (!resp.ok) {
      console.error("Failed to load price history", resp.status);
      return;
    }

    const contentType = resp.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
      console.error("Expected JSON, got", contentType);
      return;
    }

    const data = await resp.json();
    console.log("price history data length:", Array.isArray(data) ? data.length : "not array");

    if (!Array.isArray(data) || data.length === 0) {
      console.warn("No price data received for", symbol, "range", range);
      return;
    }

    const labels = data.map(point => point.time);
    const prices = data.map(point => point.price);

    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.warn("No canvas with id", canvasId);
      return;
    }
    const ctx = canvas.getContext("2d");

    if (priceChartInstance) {
      // update existing chart
      priceChartInstance.data.labels = labels;
      priceChartInstance.data.datasets[0].label = `${symbol} (${range})`;
      priceChartInstance.data.datasets[0].data = prices;
      priceChartInstance.update();
    } else {
      // eslint-disable-next-line no-undef
      priceChartInstance = new Chart(ctx, {
        type: "line",
        data: {
          labels: labels,
          datasets: [{
            label: `${symbol} (${range})`,
            data: prices,
            borderWidth: 2,
            fill: false,
            tension: 0.25,  // smooth curve

            // invisible points at rest
            pointRadius: 3,
            pointBackgroundColor: "rgba(0,0,0,0)",
            pointBorderColor: "rgba(0,0,0,0)",

            // hover behavior
            pointHitRadius: 10,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: "rgba(17,17,17,1)",
            pointHoverBorderColor: "rgba(17,17,17,1)",
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: "index",
            intersect: false
          },
          plugins: {
            legend: { display: true },
            tooltip: { enabled: true }
          },
          elements: {
            point: {
              radius: 0,
              hitRadius: 10,
              hoverRadius: 5
            }
          },
          scales: {
            x: {
              display: false,  // hide x labels; tooltip shows time
              ticks: {
                autoSkip: true,
                maxTicksLimit: 8
              }
            },
            y: {
              beginAtZero: false
            }
          }
        }
      });
    }
  } catch (err) {
    console.error("Error loading price history:", err);
  }
}

function initTickerSearch() {
  const form = document.getElementById("tickerForm");
  const input = document.getElementById("tickerInput");
  const priceCanvas = document.getElementById("priceChart");

  console.log(
    "initTickerSearch: form",
    !!form,
    "input",
    !!input,
    "canvas",
    !!priceCanvas
  );

  if (!form || !input || !priceCanvas) return;

  // default view (for Market Overview)
  loadPriceHistory(currentSymbol, currentRange);

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const symbol = input.value;
    if (!symbol) return;
    loadPriceHistory(symbol, currentRange);
  });
}

// Portfolio history (per user, same ranges)
async function loadPortfolioHistory(range = currentRange, canvasId = "portfolioChart") {
  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    // no portfolio chart on this page (logged out)
    return;
  }

  try {
    const url = `${PORTFOLIO_HISTORY_URL}?range=${encodeURIComponent(range)}`;
    console.log("Fetching portfolio history:", url);
    const resp = await fetch(url);
    console.log("portfolio history response status:", resp.status, "range:", range);

    if (!resp.ok) {
      console.error("Failed to load portfolio history", resp.status);
      return;
    }

    const contentType = resp.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
      console.error("Expected JSON, got", contentType);
      return;
    }

    const data = await resp.json();
    console.log("portfolio history data length:", Array.isArray(data) ? data.length : "not array");

    if (!Array.isArray(data) || data.length === 0) {
      console.warn("No portfolio data received for range", range);
      return;
    }

    const labels = data.map(point => point.time);
    const values = data.map(point => point.value);
    // Normalize so the chart shows change from first point (P&L style)
    const base = values[0];
    const deltaValues = values.map(v => v - base);

    const ctx = canvas.getContext("2d");

    if (portfolioChartInstance) {
      portfolioChartInstance.data.labels = labels;
      portfolioChartInstance.data.datasets[0].label = `Portfolio (${range})`;
      portfolioChartInstance.data.datasets[0].data = deltaValues;
      portfolioChartInstance.update();
    } else {
      // eslint-disable-next-line no-undef
      portfolioChartInstance = new Chart(ctx, {
        type: "line",
        data: {
          deltaValues,
          labels: labels,
          datasets: [{
            label: `Portfolio ($) (${range})`,
            data: values,
            borderWidth: 2,
            fill: false,
            tension: 0.25,

            // invisible points at rest
            pointRadius: 3,
            pointBackgroundColor: "rgba(0,0,0,0)",
            pointBorderColor: "rgba(0,0,0,0)",

            // hover behavior
            pointHitRadius: 10,
            pointHoverRadius: 5,
            pointHoverBackgroundColor: "rgba(17,17,17,1)",
            pointHoverBorderColor: "rgba(17,17,17,1)",
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: "index",
            intersect: false
          },
          plugins: {
            legend: { display: true },
            tooltip: { enabled: true }
          },
          elements: {
            point: {
              radius: 0,
              hitRadius: 10,
              hoverRadius: 5
            }
          },
          scales: {
            x: {
              display: false
            },
            y: {
              beginAtZero: false
            }
          }
        }
      });
    }
  } catch (err) {
    console.error("Error loading portfolio history:", err);
  }
}

function initPortfolioChartOnPageLoad() {
  if (document.getElementById("portfolioChart")) {
    loadPortfolioHistory(currentRange);
  }
}

// Range tabs: drive price chart, and portfolio if present
function initRangeTabs() {
  const tabs = document.querySelectorAll(".chart-tab[data-range]");
  if (!tabs.length) {
    console.log("No range tabs found");
    return;
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const newRange = tab.dataset.range;
      if (!newRange) return;

      console.log("Range tab clicked:", newRange);

      // toggle active styling (across all tabs)
      tabs.forEach(t => t.classList.toggle("active", t === tab));

      // reload Market Overview chart if it's present
      if (document.getElementById("priceChart")) {
        loadPriceHistory(currentSymbol, newRange);
      }

      // reload portfolio chart if it's present
      if (document.getElementById("portfolioChart")) {
        loadPortfolioHistory(newRange);
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  console.log("DOMContentLoaded fired");
  initTickerSearch();             // only does anything on logged-out homepage
  initRangeTabs();                // works for Market Overview tabs or Portfolio tabs
  initPortfolioChartOnPageLoad(); // only does anything when logged in
});

