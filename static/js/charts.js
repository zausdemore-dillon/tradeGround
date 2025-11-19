// static/js/charts.js

// --- API endpoints for Django views ---
const PRICE_HISTORY_BASE_URL = "/trades/api/price-history/";
const PORTFOLIO_HISTORY_URL = "/trades/api/portfolio-history/";

// Chart.js instances (so we can update instead of recreate)
let priceChartInstance = null;
let portfolioChartInstance = null;

// Track the currently-selected ticker + range
let currentSymbol = "SPY";
let currentRange = "1D";  // default range

console.log("charts.js loaded");


// PRICE HISTORY CHART (single ticker)
async function loadPriceHistory(symbol, range = currentRange, canvasId = "priceChart") {
  // Normalize ticker input
  symbol = (symbol || "").trim().toUpperCase();
  if (!symbol) return;

  // Update global selections
  currentSymbol = symbol;
  currentRange = range;

  try {
    // Build request URL with query parameter for date range
    const url = `${PRICE_HISTORY_BASE_URL}${encodeURIComponent(symbol)}/?range=${encodeURIComponent(range)}`;
    console.log("Fetching:", url);

    const resp = await fetch(url);
    console.log("price history response status:", resp.status, "symbol:", symbol, "range:", range);

    // Ensure the API responded successfully
    if (!resp.ok) {
      console.error("Failed to load price history", resp.status);
      return;
    }

    // Validate response format
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

    // Extract chart labels + values
    const labels = data.map(point => point.time);
    const prices = data.map(point => point.price);

    // Find chart canvas
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.warn("No canvas with id", canvasId);
      return;
    }
    const ctx = canvas.getContext("2d");

    // Update existing chart or create a new one
    if (priceChartInstance) {
      // Update in-place for smoother UX
      priceChartInstance.data.labels = labels;
      priceChartInstance.data.datasets[0].label = `${symbol} (${range})`;
      priceChartInstance.data.datasets[0].data = prices;
      priceChartInstance.update();
    } else {
      // Create chart.js line chart
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

            // hide point dots until hover
            pointRadius: 3,
            pointBackgroundColor: "rgba(0,0,0,0)",
            pointBorderColor: "rgba(0,0,0,0)",

            // hover styling
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
              display: false, // hide x-axis, tooltip provides timestamps
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


// Initialize ticker search form + default view
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

  // Load default chart on page load
  loadPriceHistory(currentSymbol, currentRange);

  // When user submits a new ticker
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const symbol = input.value;
    if (!symbol) return;
    loadPriceHistory(symbol, currentRange);
  });
}


// PORTFOLIO HISTORY CHART (aggregated portfolio value)
async function loadPortfolioHistory(range = currentRange, canvasId = "portfolioChart") {
  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    // No portfolio chart on this page (e.g., user logged out)
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

    // Convert to chart-readable arrays
    const labels = data.map(point => point.time);
    const values = data.map(point => point.value);

    const ctx = canvas.getContext("2d");

    // Update existing chart or create new one
    if (portfolioChartInstance) {
      portfolioChartInstance.data.labels = labels;
      portfolioChartInstance.data.datasets[0].label = `Portfolio (${range})`;
      portfolioChartInstance.data.datasets[0].data = values;
      portfolioChartInstance.update();
    } else {
      // eslint-disable-next-line no-undef
      portfolioChartInstance = new Chart(ctx, {
        type: "line",
        data: {
          labels: labels,
          datasets: [{
            label: `Portfolio (${range})`,
            data: values,
            borderWidth: 2,
            fill: false,
            tension: 0.25,

            // hide points until hover
            pointRadius: 3,
            pointBackgroundColor: "rgba(0,0,0,0)",
            pointBorderColor: "rgba(0,0,0,0)",

            // hover style
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
            x: { display: false },
            y: { beginAtZero: false }
          }
        }
      });
    }
  } catch (err) {
    console.error("Error loading portfolio history:", err);
  }
}


// Load portfolio chart automatically if its canvas exists
function initPortfolioChartOnPageLoad() {
  if (document.getElementById("portfolioChart")) {
    loadPortfolioHistory(currentRange);
  }
}


// RANGE TABS – controls (1D / 1W / 1M / 1Y / 5Y)
function initRangeTabs() {
  const tabs = document.querySelectorAll(".chart-tab[data-range]");
  if (!tabs.length) {
    console.log("No range tabs found");
    return;
  }

  // Attach click handler to each tab
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const newRange = tab.dataset.range;
      if (!newRange) return;

      console.log("Range tab clicked:", newRange);

      // Update visual active tab
      tabs.forEach(t => t.classList.toggle("active", t === tab));

      // Reload price chart with same ticker but new range
      loadPriceHistory(currentSymbol, newRange);

      // If user is logged in, update portfolio chart too
      if (document.getElementById("portfolioChart")) {
        loadPortfolioHistory(newRange);
      }
    });
  });
}


// MAIN INITIALIZER – run after HTML finishes loading
document.addEventListener("DOMContentLoaded", function () {
  console.log("DOMContentLoaded fired");
  initTickerSearch();
  initRangeTabs();
  initPortfolioChartOnPageLoad();
});
