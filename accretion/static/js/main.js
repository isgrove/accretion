
function loadPortfolioPage() {
    const spinnerBox = document.getElementById("spinner-box");
    const dataBox = document.getElementById("data-box");

    $.ajax({
        dataType: "json",
        type: 'GET',
        url: '/api/portfolio/',
        success: response => {
            spinnerBox.classList.add("hidden");
            dataBox.classList.remove("hidden");
            if (jQuery.isEmptyObject(response)) {
                createNoTradeDataElement();
            }
            else {
                var formatter = new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                });
                for (const [symbol, data] of Object.entries(response)) {
                    const value = formatter.format(data["value"]);
                    const units = Number((data["units"]).toFixed(4));
                    if (units > 0) {
                        createPortfolioElement(symbol, value, units);
                    }
                }
            }
        },
        error: error => {
            $("#data-box").append(createErrorElement());
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
    $("#data-box").append(newElement);
}

function createPortfolioElement(ticker, value, units) {
    var newElement = $(`
    <div class="py-4 border-0 border-b-2 border-gray-300 border-solid transition-all group grid grid-cols-2">
        <div>
            <p class="mr-2 mb-1 font-bold text-lg">${ticker}</p>
            <p class="mr-2">Holding value: ${value}</p>
            <p class="mr-2">Shares: ${units}</p>
        </div>
        <div class="text-right hidden group-hover:inline-block">
            <p>
                <span
                    class="text-gray-500 w-auto pt-3 pb-1 px-2 ml-2 rounded hover:bg-gray-100 w-auto transition-all">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                </span>
                <span
                    class="text-gray-500 w-auto pt-3 pb-1 px-2 ml-2 rounded hover:bg-gray-100 w-auto transition-all">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                </span>
            </p>
        </div>
    </div>`);
    $("#data-box").append(newElement);
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