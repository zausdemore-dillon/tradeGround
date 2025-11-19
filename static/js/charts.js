// static/js/charts.js

const PRICE_HISTORY_BASE_URL = "/trades/api/price-history/";

let priceChartInstance = null;

// Track current selections
let currentSymbol = "SPY";
let currentRange = "1D";  // default: 24H

console.log("charts.js loaded");

// --- Price history (ticker + range) ---

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
              display:false,
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

  // default view
  loadPriceHistory(currentSymbol, currentRange);

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const symbol = input.value;
    if (!symbol) return;
    loadPriceHistory(symbol, currentRange);
  });
}

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

      // toggle active styling
      tabs.forEach(t => t.classList.toggle("active", t === tab));

      // reload data with same symbol, new range
      loadPriceHistory(currentSymbol, newRange);
    });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  console.log("DOMContentLoaded fired");
  initTickerSearch();
  initRangeTabs();
});
