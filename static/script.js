
async function loadStocks() {
    const response = await fetch("/api/stocks");
    const stocks = await response.json();

    const priceResponse = await fetch("/api/stock-prices");
    const prices = await priceResponse.json();

    const stockList = document.getElementById("stock-list");

    stockList.innerHTML = "";

    for (const ticker in stocks) {
        const stock = stocks[ticker];
        const stockPrice = prices[ticker];
        const change = stockPrice && Number.isFinite(stockPrice.change)
            ? stockPrice.change
            : null;
        const changePercent = stockPrice && Number.isFinite(stockPrice.change_percent)
            ? stockPrice.change_percent
            : null;
        const changeClass = change === null
            ? "stock-change-unavailable"
            : change > 0
                ? "stock-change-positive"
                : change < 0
                    ? "stock-change-negative"
                    : "stock-change-neutral";
        const changeLabel = change === null
            ? "Unavailable"
            : `${change > 0 ? "+" : change < 0 ? "-" : ""}$${Math.abs(change).toFixed(2)}`;
        const changePercentLabel = changePercent === null
            ? "Percentage unavailable"
            : `${changePercent > 0 ? "+" : ""}${changePercent.toFixed(2)}%`;
        const priceLabel = stockPrice && Number.isFinite(stockPrice.price)
            ? `$${stockPrice.price.toFixed(2)}`
            : "Unavailable";

        const stockCard = document.createElement("div");
        stockCard.className = "stock-card";

        stockCard.dataset.search = `${stock.name} ${ticker}`.toLowerCase();

        stockCard.innerHTML = `
            <h3>${stock.name}</h3>
            <p class="stock-ticker">${ticker}</p>

            <p class="stock-price-label">LATEST AVAILABLE PRICE</p>

            <p class="stock-price">${priceLabel}</p>

            <p class="stock-daily-change ${changeClass}">
                ${changeLabel} (${changePercentLabel})
            </p>

            <p class="stock-category">${stock.category}</p>
            <p class="stock-exchange">${stock.exchange}</p>

            <p class="stock-exchange">
                Trading Day: ${stockPrice && stockPrice.latest_trading_day ? stockPrice.latest_trading_day : "Unavailable"}
            </p>
        `;

        stockList.appendChild(stockCard);
    }
}

// Stock search
const stockSearch = document.getElementById("stock-search");

stockSearch.addEventListener("input", function () {
    const searchTerm = stockSearch.value.toLowerCase();

    const stockCards = document.querySelectorAll(".stock-card");

    stockCards.forEach(function (card) {
        const matches = card.dataset.search.includes(searchTerm);

        card.style.display = matches ? "block" : "none";
    });
});

loadStocks();
