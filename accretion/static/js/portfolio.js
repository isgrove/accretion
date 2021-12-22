let totalValue = 0;
let startingValue = 0;
let allData = {};
let currentView = "all";

var percentageFormatter = new Intl.NumberFormat('en-US', {
    style: "percent",
    signDisplay: "exceptZero",
});

var dollarFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
});

var dollarFormatterZero = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    signDisplay: "exceptZero",
});

function createNoTradeDataElement() {
    var newElement = $(`
    <div class="mt-16 text-center mx-auto py-8 px-8 max-w-lg bg-gray-100 rounded-lg">
        <h3 class="mb-4">Keep track of your portfolio</h3>
        <p class="mb-4 text-gray-700">You haven't added any trade data but once you do you will be able to get insights on your stock portfolio.</p>
        <a class="font-medium text-white px-4 py-2 no-underline bg-blue-800 rounded inline-block transition-all hover:bg-blue-700" href="/account/portfolio/">Add trade data</a>
    </div>
    `);
    $("#content").append(newElement);
}

function createPortfolioElement(symbol, value, purchasePrice ,units) {

    const totalGains = value - purchasePrice;
    const totalGainsPercentage = ((value - purchasePrice) / purchasePrice * 100).toFixed(2)

    startingValue += purchasePrice;
    
    var newElement = $(`
    <tr class="">
        <td class="py-3">${symbol}</td>
        <td>${Number(units).toFixed(4)}</td>
        <td>${dollarFormatter.format(value)}</td>
        <td class="${getColour(totalGains)}" id="${symbol.toLowerCase()}-change">${dollarFormatterZero.format(totalGains)} (${dollarFormatterZero.format(totalGainsPercentage)}%)</td>
    </tr>
    `)
    $("#portfolio-table-body").append(newElement);
}

function createErrorElement() {
    var newElement = $(`
    <div class="mt-4 text-center mx-auto py-8 px-8 max-w-lg bg-gray-100 rounded-lg">
        <h3 class="mb-4">Oops! Something went wrong...</h3>
        <p class="mb-4 text-gray-700">We encountered an error. If this error persists please contact support.</p>
        <a class="font-medium text-white px-4 py-2 no-underline bg-blue-800 rounded inline-block transition-all hover:bg-blue-700" onClick="window.location.reload();" href="#">Try again</a>
    </div>
    `);
    return newElement;
}

function getColour(num) {
    if (num > 0) {
        return "text-green-700";
    }
    else {
        return "text-red-700"
    }
    
}

function loadPortfolioPage() {
    const loadingElement = document.getElementById("loading");
    const contentElement = document.getElementById("content");
    const tableElement = document.getElementById("portfolio-table");
    
    $.ajax({
        dataType: "json",
        type: 'GET',
        url: '/api/portfolio-1y/',
        success: response => {
            loadingElement.classList.add("hidden");
            contentElement.classList.remove("hidden");
            if (jQuery.isEmptyObject(response)) {
                createNoTradeDataElement();
            }
            else {
                for (x in response["tradeData"]) {
                    let totalPurchasePrice = 0;
                    let totalUnits = 0;
                    for (y in response["tradeData"][x]) {
                        purchasePrice = response["tradeData"][x][y]["purchasePrice"];
                        units = response["tradeData"][x][y]["units"];
                        tradeType = response["tradeData"][x][y]["tradeType"]
                        if (tradeType == "B") {
                            totalPurchasePrice += purchasePrice * units;
                            totalUnits += units;
                        }
                        else if (tradeType == "S") {
                            totalPurchasePrice -= purchasePrice * units;
                            totalUnits -= units;
                        }
                    }
                    value = response["chartData"][x][0]["close"] * totalUnits;
                    totalValue += value;
                    if (value > 0) {
                        createPortfolioElement(x, value, totalPurchasePrice, units);
                    }
                }
            }
            $("#total").append(`<h1 class="text-2xl font-normal">Portfolio</h2>`);
            $("#total").append(`<h3 class="my-2 text-2xl font-normal">${dollarFormatter.format(totalValue)}</h3>`);
            $("#total").append(`<p id="change-amount"><span class="${getColour(totalValue - startingValue)}">${dollarFormatterZero.format(totalValue - startingValue)} (${dollarFormatterZero.format((totalValue - startingValue) / startingValue * 100)}%)</span> Total</p>`);

            allData = response;
        },
        error: error => {
                console.log(error)
                loadingElement.classList.add("hidden");
                contentElement.classList.remove("hidden");
                tableElement.classList.add("hidden");
                $("#content").append(createErrorElement());
        }
    });
}

//TODO: Add 6M, 1Y and YTD view
//TODO: Create checks to see how many shares they owned at each point in time
function portfolioView(peroid) {
    let peroidLong;
    let total = 0;
    let starting = 0;

    const tradeData = allData["tradeData"];
    const chartData = allData["chartData"];

    let currentTotalUnits;
    let previousClosePrice;
    let todaysClosePrice;
    let totalGainsPercentage;
    let tradeElement;

    let currentStarting;
    let currentTotal;

    let units;
    let tradeType;

    let currentPruchasePrice;
    let purchasePrice

    const changeAmountElement = document.getElementById("change-amount");
    if (peroid == currentView) {
        return;
    }
    // TODO: refactor
    else if (peroid == "1d") {
        peroidLong = "Today";

        for (trade in tradeData) {
            tradeElement = document.getElementById(trade.toLowerCase() + "-change");

            previousClosePrice = chartData[trade][1]["close"];
            todaysClosePrice = chartData[trade][0]["close"];
            
            currentTotalUnits = 0;
            for (order in tradeData[trade]) {
                units = tradeData[trade][order]["units"];
                tradeType = tradeData[trade][order]["tradeType"];

                if (tradeType == "B") {
                    currentTotalUnits += units;
                }
                else if (tradeType == "S") {
                    currentTotalUnits -= units;
                }
            }

            currentTotal = todaysClosePrice * currentTotalUnits;
            currentStarting = previousClosePrice * currentTotalUnits;

            totalGainsPercentage = ((currentTotal - currentStarting) / currentStarting * 100).toFixed(2);
            
            if (currentTotalUnits > 0) {
                total += currentTotal;
                starting += currentStarting;
                tradeElement.innerHTML = `<td class="${getColour(currentTotal-currentStarting)}" id="${trade}-change">${dollarFormatterZero.format(currentTotal-currentStarting)} (${dollarFormatterZero.format(totalGainsPercentage)}%)</td>`;
            }
        }
    }
    else if (peroid == "1m") {
        peroidLong = "1M"

        let ny_time = new Date(new Date().toLocaleString("en-US", {timeZone: "America/New_York"}));
        let last_month = ny_time.setMonth(ny_time.getMonth() - 1);
        last_month = ny_time.toISOString().split('T')[0];

        for (trade in tradeData) {
            // get the price last month (get the price at last_month date or the most recent price after that date)
            todaysClosePrice = chartData[trade][0]["close"];

            for (data in chartData[trade]) {
                if (chartData[trade][data]["date"] == last_month) {
                    console.log(trade + ": " + chartData[trade][data]["close"]);
                }
            }
 
            for (order in tradeData[trade]) {
                if (last_month < tradeData["date"]) {
                    // price of purchase
                }
                else {
                    // price last month
                }
            }
        }
    }
    else if (peroid == "all") {
        peroidLong = "Today";

        for (trade in tradeData) {
            tradeElement = document.getElementById(trade.toLowerCase() + "-change");

            todaysClosePrice = chartData[trade][0]["close"];
            
            currentTotalUnits = 0;
            currentPruchasePrice = 0;

            for (order in tradeData[trade]) {
                purchasePrice = tradeData[trade][order]["purchasePrice"];
                units = tradeData[trade][order]["units"];
                tradeType = tradeData[trade][order]["tradeType"]
                if (tradeType == "B") {
                    currentPruchasePrice += purchasePrice * units;
                    currentTotalUnits += units;
                }
                else if (tradeType == "S") {
                    currentPruchasePrice -= purchasePrice * units;
                    currentTotalUnits -= units;
                }
            }

            currentTotal = todaysClosePrice * currentTotalUnits;
            currentStarting = currentPruchasePrice;

            total += currentTotal;
            starting += currentStarting;

            totalGainsPercentage = ((currentTotal - currentStarting) / currentStarting * 100).toFixed(2);
            
            if (currentTotalUnits > 0) {
                tradeElement.innerHTML = `<td class="${getColour(currentTotal-currentStarting)}" id="${trade}-change">${dollarFormatterZero.format(currentTotal-currentStarting)} (${dollarFormatterZero.format(totalGainsPercentage)}%)</td>`;
            }
        }
    }
    currentView = peroid;
    setActiveButton(currentView);

    // console.log("starting:" + starting);
    // console.log("ending: " + total);
    // console.log("diff: " + (starting - total));
    // console.log(tradeData);
    // console.log(peroid);

    changeAmountElement.innerHTML = `<span class="${getColour(total - starting)}">${dollarFormatterZero.format(total - starting)} (${dollarFormatterZero.format((total - starting) / starting * 100)}%)</span> ${peroidLong}</p>`
}

function setActiveButton(activeButton) {
    const buttons = ["1d", "5d", "1m", "3m", "6m", "1y", "ytd", "all"];
    const activeButtonElement = document.getElementById(activeButton + "-button");

    activeButtonElement.classList = "";
    activeButtonElement.classList.add("font-medium", "text-white", "px-2", "py-2", "no-underline", "bg-blue-800", "rounded", "inline-block", "transition-all", "hover:bg-blue-700");

    for (button in buttons) {
        if (buttons[button] != activeButton) {
            const buttonElement = document.getElementById(buttons[button] + "-button");
            buttonElement.classList = "";
            buttonElement.classList.add("font-medium", "text-black", "px-2", "py-2", "no-underline", "rounded", "inline-block", "transition-all", "hover:bg-gray-100");
        }
    }
}