// pullShareValues.js

// pull price data from Holdings api endpoint and populate share values on dashboard

const HOLDINGS_PRICES_URL = "/trades/api/holdings/prices";
const POLLINTERVAL = 10000; // 10 seconds

async function fetchHoldingsPrices() {
  // Only run if there are cells expecting price data
  const priceCells = document.querySelectorAll('[data-field="price"]');
  if (!priceCells.length) {
    // No holdings table on this page; nothing to do
    return;
  }

  try {
    const response = await fetch(HOLDINGS_PRICES_URL, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    if (!response.ok) {
      console.error("Holdings prices request failed:", response.status);
      return;
    }

    const contentType = response.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
      console.warn("Expected JSON from holdings prices endpoint, got", contentType);
      return;
    }

    const data = await response.json();

    for (const [symbol, price] of Object.entries(data)) {
      // template format:
      // <td data-symbol="{{ h.ticker }}" data-field="price">loading…</td>
      const cell = document.querySelector(
        `[data-symbol="${symbol}"][data-field="price"]`
      );

      if (!cell) {
        continue;
      }

      if (price !== null && price !== undefined) {
        const numPrice = parseFloat(price).toFixed(2);
        cell.textContent = `$${numPrice}`;
      } else {
        cell.textContent = "—";
      }
    }
  } catch (error) {
    console.error("Error fetching holdings prices:", error);
  }
}

function startHoldingsPolling() {
  // Only start if there are any price cells on the page
  const priceCells = document.querySelectorAll('[data-field="price"]');
  if (!priceCells.length) {
    return;
  }

  fetchHoldingsPrices();
  setInterval(fetchHoldingsPrices, POLLINTERVAL);
}

document.addEventListener("DOMContentLoaded", startHoldingsPolling);
