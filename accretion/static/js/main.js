//TODO: Fix failed to load bug

let totalValue = 0;
let startingValue = 0;

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

const changeRowTitleElement = document.getElementById("change-row-heading");

let currentView = "all";

let tradeData = {};
let dataOneYear = {};

//TODO: Update so only 1 api request is being made
function loadPortfolioPage() {
    const loadingElement = document.getElementById("loading");
    const contentElement = document.getElementById("content");
    const tableElement = document.getElementById("portfolio-table");

    $.ajax({
        dataType: "json",
        type: 'GET',
        url: '/api/portfolio/',
        success: response => {
            loadingElement.classList.add("hidden");
            contentElement.classList.remove("hidden");
            if (jQuery.isEmptyObject(response)) {
                createNoTradeDataElement();
            }
            else {
                tradeData = response;
                for (const [symbol, data] of Object.entries(response)) {
                    totalValue += data["value"];
                    const units = Number((data["units"]).toFixed(4));
                    if (units > 0) {
                        createPortfolioElement(symbol, data);
                    }
                }
                $("#total").append(`<h1 class="text-2xl font-normal">Portfolio</h2>`);
                $("#total").append(`<h3 class="my-2 text-2xl font-normal">${dollarFormatter.format(totalValue)}</h3>`);
                $("#total").append(`<p id="change-amount"><span class="${getColour(totalValue - startingValue)}">${dollarFormatterZero.format(totalValue - startingValue)} (${dollarFormatterZero.format((totalValue - startingValue) / startingValue * 100)}%)</span> Total</p>`);
            }
        },
        error: error => {
            console.log(error)
            loadingElement.classList.add("hidden");
            contentElement.classList.remove("hidden");
            tableElement.classList.add("hidden");
            $("#content").append(createErrorElement());
        }
    });
    setTimeout(() => {
        
    }, 10);
    //TODO: Make this the main api call
    $.ajax({
        dataType: "json",
        type: 'GET',
        url: '/api/portfolio-1y/',
        success: response => {
            dataOneYear = response
        }
    });
}

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

function createPortfolioElement(symbol, data) {

    const totalGains = data["value"] - data["purchase_price"];
    const totalGainsPercentage = ((data["value"] - data["purchase_price"]) / data["purchase_price"] * 100).toFixed(2)
    const value = dollarFormatter.format(data["value"]);
    const units = Number(data["units"]).toFixed(4);

    startingValue += data["purchase_price"];
    
    var newElement = $(`
    <tr class="">
        <td class="py-3">${symbol}</td>
        <td>${units}</td>
        <td>${value}</td>
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

//TODO: Add 6M, 1Y and YTD view
//TODO: Create checks to see how many shares they owned at each point in time
function portfolioView(peroid) {
    let peroidLong = "";
    let total = 0;
    let starting = 0;

    console.log(`peroid: {$peroid}`);

    const changeAmountElement = document.getElementById("change-amount");
    if (peroid == currentView) {
        return;
    }
    else if (peroid == "1d") {
        peroidLong = "Today"

        for (trade in tradeData) {
            if (tradeData[trade]["units"] > 0) {
                const tradeStarting = dataOneYear[trade][1]["close"]
                const tradeTotal = dataOneYear[trade][0]["close"]

                const tradeElement = document.getElementById(trade.toLowerCase() + "-change");
                const totalGainsPercentage = ((tradeTotal - tradeStarting) / tradeStarting * 100).toFixed(2)

                total += tradeTotal * tradeData[trade]["units"];
                starting += tradeStarting  * tradeData[trade]["units"];

                tradeElement.innerHTML = `<td class="${getColour(total-starting)}" id="${trade}-change">${dollarFormatterZero.format(total-starting)} (${dollarFormatterZero.format(totalGainsPercentage)}%)</td>`;
            }
        }
    }
    else if (peroid == "5d") {
        peroidLong = "Week"

        for (trade in tradeData) {
            if (tradeData[trade]["units"] > 0) {
            const tradeElement = document.getElementById(trade.toLowerCase() + "-change");
            const totalGainsPercentage = ((tradeData[trade]["close"] - dataOneYear[trade][4]["close"]) / 
            dataOneYear[trade][4]["close"] * 100).toFixed(2)

            total += tradeData[trade]["close"] * tradeData[trade]["units"];
            starting += dataOneYear[trade][4]["close"] * tradeData[trade]["units"];

            tradeElement.innerHTML = `<td class="${getColour(total-starting)}" id="${trade}-change">${dollarFormatterZero.format(total-starting)} (${dollarFormatterZero.format(totalGainsPercentage)}%)</td>`;
            }
        }
    }
    else if (peroid == "1m") {
        peroidLong = "1M"
        console.log("abc 123");

        let ny_time = new Date(new Date().toLocaleString("en-US", {timeZone: "America/New_York"}));
        ny_time.setMonth(ny_time.getMonth() - 1);
        ny_time = ny_time.toISOString().split('T')[0];
        
        for (trade in tradeData) {
            if (tradeData[trade]["units"] > 0) {
                let ny_time = new Date(new Date().toLocaleString("en-US", {timeZone: "America/New_York"}));
                ny_time.setMonth(ny_time.getMonth() - 1);
                ny_time = ny_time.toISOString().split('T')[0];

                let last_close;

                for (x in dataOneYear[trade]) {
                    if (new Date(Date.parse(ny_time)) >= new Date(Date.parse(dataOneYear[trade][x]["date"]))) {
                        console.log(dataOneYear[trade][x]["date"]);
                        console.log(last_close);
                        break;
                    }
                    last_close = dataOneYear[trade][x]["close"]
                }
                
                const tradeElement = document.getElementById(trade.toLowerCase() + "-change");
                const totalGainsPercentage = ((tradeData[trade]["close"] - last_close) / last_close * 100).toFixed(2);

                total += tradeData[trade]["close"] * tradeData[trade]["units"];
                starting += last_close * tradeData[trade]["units"];

                tradeElement.innerHTML = `<td class="${getColour(total-starting)}" id="${trade}-change">${dollarFormatterZero.format(total-starting)} (${dollarFormatterZero.format(totalGainsPercentage)}%)</td>`;
            }
        }
    }
    else if (peroid == "all") {
        peroidLong = "Total";
        total = totalValue;
        starting = startingValue;

        for (trade in tradeData) {
            if (tradeData[trade]["units"] > 0) {
            const totalGains = tradeData[trade]["value"] - tradeData[trade]["purchase_price"];
            const tradeElement = document.getElementById(trade.toLowerCase() + "-change");
            const totalGainsPercentage = (tradeData[trade]["value"] - tradeData[trade]["purchase_price"]) / tradeData[trade]["purchase_price"] * 100

            tradeElement.innerHTML = `<td class="${getColour(totalGains)}" id="${trade}-change">${dollarFormatterZero.format(totalGains)} (${dollarFormatterZero.format(totalGainsPercentage)}%)</td>`;
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