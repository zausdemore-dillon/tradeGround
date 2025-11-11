// pull price data from Holdings api endpoint and populate share values on dashboard

const HOLDINGS_PRICES_URL = "/trades/api/holdings/prices";

const POLLINTERVAL = 3000; // 3 seconds

async function fetchHoldingsPrices() {
    try {
        const response = await fetch(HOLDINGS_PRICES_URL);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();

        for (const [symbol, price] of Object.entries(data)) { 
        // use following format for displaying prices in template 
        // <td data-symbol="{{ h.ticker }}" data-field="price">loading…</td>
            const cell = document.querySelector(`[data-symbol="${symbol}"][data-field="price"]`);

            if (!cell) {
                continue;
            }

            if (price !== null && price !== undefined) {
                cell.textContent = `$${price}`;
            } else {
                cell.textContent = "—";
            }
        }

    } catch (error) {
        console.error("Error fetching holdings prices:", error);
        return null;
    }
}

function startHoldingsPolling() {
    fetchHoldingsPrices();
    setInterval(fetchHoldingsPrices, POLLINTERVAL);
}

document.addEventListener("DOMContentLoaded", startHoldingsPolling);
