// static/js/charts.js

// API endpoints for Django views 
const PRICE_HISTORY_BASE_URL = "/trades/api/price-history/";
const PORTFOLIO_HISTORY_URL = "/trades/api/portfolio-history/";

// Global Chart.js instances so they can be updated instead of recreated
let priceChartInstance = null;
let portfolioChartInstance = null;

// Track currently selected ticker + range
let currentSymbol = "SPY";
let currentRange = "1D";  // default range for both charts

console.log("charts.js loaded");


// Tooltip time formatting helper (shared by both charts)
function formatTooltipTitle(raw) {
  if (!raw) return "";

  // Handle pure date strings "YYYY-MM-DD"
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
    const d = new Date(raw + "T00:00:00");
    return d.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  // Handle full datetime strings "YYYY-MM-DDTHH:MM:SS+00:00"
  const d = new Date(raw);
  if (Number.isNaN(d.getTime())) {
    return raw; // fallback for invalid date formats
  }

  const dateStr = d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  let hours = d.getHours();
  const minutes = d.getMinutes().toString().padStart(2, "0");
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12;

  const timeStr = `${hours}:${minutes} ${ampm}`;
  return `${dateStr} ${timeStr}`;
}


// PRICE HISTORY CHART (single ticker)
async function loadPriceHistory(symbol, range = currentRange, canvasId = "priceChart") {
  // Normalize ticker input
  symbol = (symbol || "").trim().toUpperCase();
  if (!symbol) return;

  // Save globally for range switching
  currentSymbol = symbol;
  currentRange = range;

  try {
    // Build API request URL
    const url = `${PRICE_HISTORY_BASE_URL}${encodeURIComponent(symbol)}/?range=${encodeURIComponent(range)}`;
    console.log("Fetching:", url);

    const resp = await fetch(url);
    console.log("price history response status:", resp.status, "symbol:", symbol, "range:", range);

    if (!resp.ok) {
      console.error("Failed to load price history", resp.status);
      return;
    }

    // Ensure JSON response
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

    // Extract timestamps + price points
    const labels = data.map(point => point.time);
    const prices = data.map(point => point.price);

    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.warn("No canvas with id", canvasId);
      return;
    }
    const ctx = canvas.getContext("2d");

    // Update existing chart or create new one
    if (priceChartInstance) {
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
            tension: 0.25,  // smooth curve line

            // hide points until hovered
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
            tooltip: {
              enabled: true,
              callbacks: {
                // Format tooltip timestamps using shared helper
                title: function (items) {
                  if (!items.length) return "";
                  return formatTooltipTitle(items[0].label);
                }
              }
            }
          },
          elements: {
            point: {
              radius: 0,
              hitRadius: 10,
              hoverRadius: 5
            }
          },
          scales: {
            x: { display: false }, // timestamps shown via tooltip only
            y: { beginAtZero: false }
          }
        }
      });
    }
  } catch (err) {
    console.error("Error loading price history:", err);
  }
}


// Initialize the ticker search bar + load default chart
function initTickerSearch() {
  const form = document.getElementById("tickerForm");
  const input = document.getElementById("tickerInput");
  const priceCanvas = document.getElementById("priceChart");

  console.log("initTickerSearch: form", !!form, "input", !!input, "canvas", !!priceCanvas);

  if (!form || !input || !priceCanvas) return;

  // Initial load
  loadPriceHistory(currentSymbol, currentRange);

  // Handle manual ticker search
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const symbol = input.value;
    if (!symbol) return;
    loadPriceHistory(symbol, currentRange);
  });
}


// PORTFOLIO HISTORY CHART (aggregated user portfolio value)
async function loadPortfolioHistory(range = currentRange, canvasId = "portfolioChart") {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return; // user may not be logged in

  try {
    const url = `${PORTFOLIO_HISTORY_URL}?range=${encodeURIComponent(range)}`;
    console.log("Fetching portfolio history:", url);

    const resp = await fetch(url);
    console.log("portfolio history response status:", resp.status, "range:", range);

    if (!resp.ok) {
      console.error("Failed to load portfolio history", resp.status);
      return;
    }

    // Validate JSON
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

    const ctx = canvas.getContext("2d");

    if (portfolioChartInstance) {
      // Update existing chart
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

            // hide points at rest
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
            tooltip: {
              enabled: true,
              callbacks: {
                title: function (items) {
                  if (!items.length) return "";
                  return formatTooltipTitle(items[0].label);
                }
              }
            }
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


// Load portfolio chart automatically on pages where it exists
function initPortfolioChartOnPageLoad() {
  if (document.getElementById("portfolioChart")) {
    loadPortfolioHistory(currentRange);
  }
}


// RANGE TABS (1D / 1W / 1M / 1Y / 5Y) – updates both charts
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

      // Update active visual state
      tabs.forEach(t => t.classList.toggle("active", t === tab));

      // Reload market chart if present
      if (document.getElementById("priceChart")) {
        loadPriceHistory(currentSymbol, newRange);
      }

      // Reload portfolio chart if present
      if (document.getElementById("portfolioChart")) {
        loadPortfolioHistory(newRange);
      }
    });
  });
}



// Boot everything once the DOM is fully ready
document.addEventListener("DOMContentLoaded", function () {
  console.log("DOMContentLoaded fired");
  initTickerSearch();
  initRangeTabs();
  initPortfolioChartOnPageLoad();
});
