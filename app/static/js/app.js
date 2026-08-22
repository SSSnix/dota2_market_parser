const searchButton = document.getElementById("search-button");
const itemNameInput = document.getElementById("item-name");
const descriptionInput = document.getElementById("description");
const resultsContainer = document.getElementById("results");


function showMessage(message) {
    resultsContainer.innerHTML = "";

    const messageElement = document.createElement("div");
    messageElement.className = "message";
    messageElement.textContent = message;

    resultsContainer.appendChild(messageElement);
}


function createResultCard(item) {
    const card = document.createElement("div");
    card.className = "result-card";

    const title = document.createElement("h3");
    title.textContent = item.name;

    const price = document.createElement("div");
    price.className = "result-price";
    price.textContent = item.price_rub !== null
        ? `${item.price_rub.toFixed(2)} ₽`
        : "Цена неизвестна";

    const count = document.createElement("div");
    count.className = "result-count";
    count.textContent =
        `Количество: ${item.count ?? "неизвестно"}`;

    const identifiers = document.createElement("div");
    identifiers.className = "result-identifiers";
    identifiers.textContent =
        `Class: ${item.class_id} | Instance: ${item.instance_id}`;

    const description = document.createElement("div");
    description.className = "result-description";
    description.textContent =
        item.description_text || "Описание отсутствует";

    const link = document.createElement("a");
    link.className = "market-link";
    link.href = item.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Открыть на Market";

    card.appendChild(title);
    card.appendChild(price);
    card.appendChild(count);
    card.appendChild(description);
    card.appendChild(identifiers);
    card.appendChild(link);

    return card;
}


function renderResults(data) {
    resultsContainer.innerHTML = "";

    if (!data.items || data.items.length === 0) {
        showMessage("Подходящих предметов не найдено.");
        return;
    }

    const header = document.createElement("div");
    header.className = "results-header";
    header.textContent =
        `Найдено вариантов: ${data.count}`;

    resultsContainer.appendChild(header);

    for (const item of data.items) {
        resultsContainer.appendChild(
            createResultCard(item)
        );
    }
}


async function searchItems() {
    const itemName = itemNameInput.value.trim();
    const description = descriptionInput.value.trim();

    if (!itemName) {
        showMessage("Введите название предмета.");
        return;
    }

    if (!description) {
        showMessage("Введите описание.");
        return;
    }

    searchButton.disabled = true;
    searchButton.textContent = "Поиск...";

    showMessage("Ищем предметы...");

    try {
        const params = new URLSearchParams();

        params.append("item_name", itemName);
        params.append("description", description);

        const response = await fetch(
            "/api/search",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/x-www-form-urlencoded",
                },
                body: params.toString(),
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Ошибка поиска"
            );
        }

        renderResults(data);
    } catch (error) {
        showMessage(
            `Ошибка: ${error.message}`
        );
    } finally {
        searchButton.disabled = false;
        searchButton.textContent = "Найти";
    }
}


searchButton.addEventListener(
    "click",
    searchItems
);


[itemNameInput, descriptionInput].forEach(
    (input) => {
        input.addEventListener(
            "keydown",
            (event) => {
                if (event.key === "Enter") {
                    searchItems();
                }
            }
        );
    }
);