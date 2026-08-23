const searchButton =
    document.getElementById("search-button");

const itemNameInput =
    document.getElementById("item-name");

const descriptionInput =
    document.getElementById("description");

const resultsContainer =
    document.getElementById("results");

const qualityButton =
    document.getElementById("quality-button");

const qualityButtonText =
    document.getElementById("quality-button-text");

const qualityDropdown =
    document.getElementById("quality-dropdown");

const qualityCheckboxes =
    document.querySelectorAll(
        ".quality-option input"
    );


function showMessage(message) {
    resultsContainer.innerHTML = "";

    const messageElement =
        document.createElement("div");

    messageElement.className = "message";
    messageElement.textContent = message;

    resultsContainer.appendChild(
        messageElement
    );
}


function getSelectedQualities() {
    const selected = [];

    qualityCheckboxes.forEach(
        (checkbox) => {
            if (
                checkbox.checked
                && checkbox.value !== "all"
            ) {
                selected.push(checkbox.value);
            }
        }
    );

    return selected;
}


function updateQualityButtonText() {
    const allCheckbox =
        document.querySelector(
            '.quality-option input[value="all"]'
        );

    if (allCheckbox.checked) {
        qualityButtonText.textContent =
            "Все качества";
        return;
    }

    const selected = getSelectedQualities();

    if (selected.length === 0) {
        qualityButtonText.textContent =
            "Выберите качество";
        return;
    }

    const names = {
        normal: "Обычный",
        exalted: "Exalted",
        inscribed: "Inscribed",
        autographed: "Autographed",
        heroic: "Heroic",
        corrupted: "Corrupted",
    };

    if (selected.length === 1) {
        qualityButtonText.textContent =
            names[selected[0]];
        return;
    }

    qualityButtonText.textContent =
        `Выбрано: ${selected.length}`;
}


function handleQualityChange(event) {
    const changedCheckbox =
        event.target;

    const allCheckbox =
        document.querySelector(
            '.quality-option input[value="all"]'
        );

    if (changedCheckbox.value === "all") {
        if (changedCheckbox.checked) {
            qualityCheckboxes.forEach(
                (checkbox) => {
                    if (
                        checkbox.value !== "all"
                    ) {
                        checkbox.checked = false;
                    }
                }
            );
        }
    } else {
        allCheckbox.checked = false;

        const selected =
            getSelectedQualities();

        if (selected.length === 0) {
            allCheckbox.checked = true;
        }
    }

    updateQualityButtonText();
}


qualityCheckboxes.forEach(
    (checkbox) => {
        checkbox.addEventListener(
            "change",
            handleQualityChange
        );
    }
);


qualityButton.addEventListener(
    "click",
    () => {
        qualityDropdown.classList.toggle(
            "open"
        );
    }
);


document.addEventListener(
    "click",
    (event) => {
        if (
            !qualityDropdown.contains(
                event.target
            )
            && !qualityButton.contains(
                event.target
            )
        ) {
            qualityDropdown.classList.remove(
                "open"
            );
        }
    }
);


function createResultCard(item) {
    const card =
        document.createElement("div");

    card.className = "result-card";

    const title =
        document.createElement("h3");

    title.textContent = item.name;

    const price =
        document.createElement("div");

    price.className = "result-price";

    price.textContent =
        item.price_rub !== null
            ? `${item.price_rub.toFixed(2)} ₽`
            : "Цена неизвестна";

    const offers =
        document.createElement("div");

    offers.className = "result-count";

    offers.textContent =
        `Предложений: ${item.offers ?? "неизвестно"}`;

    const identifiers =
        document.createElement("div");

    identifiers.className =
        "result-identifiers";

    identifiers.textContent =
        `Class: ${item.class_id} | `
        + `Instance: ${item.instance_id}`;

    const description =
        document.createElement("div");

    description.className =
        "result-description";

    description.textContent =
        item.description_text
            || "Описание отсутствует";

    const link =
        document.createElement("a");

    link.className = "market-link";
    link.href = item.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Открыть на Market";

    card.appendChild(title);
    card.appendChild(price);
    card.appendChild(offers);
    card.appendChild(description);
    card.appendChild(identifiers);
    card.appendChild(link);

    return card;
}


function renderResults(data) {
    resultsContainer.innerHTML = "";

    if (
        !data.items
        || data.items.length === 0
    ) {
        showMessage(
            "Подходящих предметов не найдено."
        );
        return;
    }

    const header =
        document.createElement("div");

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
    const itemName =
        itemNameInput.value.trim();

    const description =
        descriptionInput.value.trim();

    if (!itemName) {
        showMessage(
            "Введите название предмета."
        );
        return;
    }

    if (!description) {
        showMessage(
            "Введите описание."
        );
        return;
    }

    searchButton.disabled = true;
    searchButton.textContent = "Поиск...";

    showMessage(
        "Ищем предметы..."
    );

    try {
        const selected =
            getSelectedQualities();

        const allCheckbox =
            document.querySelector(
                '.quality-option input[value="all"]'
            );

        let qualities;

        if (
            allCheckbox.checked
            || selected.length === 0
        ) {
            qualities = ["all"];
        } else {
            qualities = selected;
        }

        const params =
            new URLSearchParams();

        params.append(
            "item_name",
            itemName
        );

        params.append(
            "description",
            description
        );

        params.append(
            "qualities",
            qualities.join(",")
        );

        const response =
            await fetch(
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

        const responseText =
            await response.text();

        let data;

        try {
            data = JSON.parse(
                responseText
            );
        } catch {
            throw new Error(
                `Сервер вернул некорректный ответ: `
                + `${responseText.slice(0, 200)}`
            );
        }

        if (!response.ok) {
            let errorMessage = "Ошибка поиска";

            if (Array.isArray(data.detail)) {
                errorMessage = data.detail
                    .map((error) => {
                        const location =
                            error.loc
                                ? error.loc.join(".")
                                : "";

                        return (
                            `${location}: `
                            + `${error.msg}`
                        );
                    })
                    .join("; ");
            } else if (data.detail) {
                errorMessage = String(
                    data.detail
                );
            }

            throw new Error(errorMessage);
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
                if (
                    event.key === "Enter"
                ) {
                    searchItems();
                }
            }
        );
    }
);