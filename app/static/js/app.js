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

const qualityInputs =
    document.querySelectorAll(
        'input[name="quality"]'
    );

const allQualityInput =
    document.querySelector(
        'input[name="quality"][value="all"]'
    );


/* =========================================================
   MESSAGES
   ========================================================= */

function showMessage(message) {
    resultsContainer.innerHTML = "";

    const messageElement =
        document.createElement("div");

    messageElement.className =
        "message";

    messageElement.textContent =
        message;

    resultsContainer.appendChild(
        messageElement
    );
}


/* =========================================================
   QUALITY DROPDOWN
   ========================================================= */

function closeQualityDropdown() {
    if (!qualityDropdown) {
        return;
    }

    qualityDropdown.classList.remove(
        "is-open"
    );

    if (qualityButton) {
        qualityButton.classList.remove(
            "is-open"
        );
    }
}


function openQualityDropdown() {
    if (!qualityDropdown) {
        return;
    }

    qualityDropdown.classList.add(
        "is-open"
    );

    if (qualityButton) {
        qualityButton.classList.add(
            "is-open"
        );
    }
}


function toggleQualityDropdown() {
    if (!qualityDropdown) {
        return;
    }

    if (
        qualityDropdown.classList.contains(
            "is-open"
        )
    ) {
        closeQualityDropdown();
    } else {
        openQualityDropdown();
    }
}


function getSelectedQualities() {
    if (!qualityInputs.length) {
        return ["all"];
    }

    const selected = [];

    qualityInputs.forEach(
        (input) => {
            if (input.checked) {
                selected.push(
                    input.value
                );
            }
        }
    );

    if (
        selected.length === 0
    ) {
        return ["all"];
    }

    if (
        selected.includes("all")
    ) {
        return ["all"];
    }

    return selected;
}


function updateQualityButtonText() {
    if (!qualityButtonText) {
        return;
    }

    const selected =
        getSelectedQualities();

    if (
        selected.length === 1
        && selected[0] === "all"
    ) {
        qualityButtonText.textContent =
            "Все качества";

        return;
    }

    const labels = {
        normal: "Обычный",
        exalted: "Exalted",
        inscribed: "Inscribed",
        autographed: "Autographed",
        heroic: "Heroic",
        corrupted: "Corrupted",
    };

    const selectedLabels =
        selected
            .map(
                (value) =>
                    labels[value] || value
            );

    qualityButtonText.textContent =
        selectedLabels.join(", ");
}


function setupQualityDropdown() {
    if (
        !qualityButton
        || !qualityDropdown
        || !qualityInputs.length
    ) {
        return;
    }

    qualityButton.addEventListener(
        "click",
        (event) => {
            event.stopPropagation();
            toggleQualityDropdown();
        }
    );

    qualityDropdown.addEventListener(
        "click",
        (event) => {
            event.stopPropagation();
        }
    );

    qualityInputs.forEach(
        (input) => {
            input.addEventListener(
                "change",
                () => {
                    if (
                        input ===
                        allQualityInput
                    ) {
                        if (
                            input.checked
                        ) {
                            qualityInputs.forEach(
                                (other) => {
                                    if (
                                        other !==
                                        allQualityInput
                                    ) {
                                        other.checked =
                                            false;
                                    }
                                }
                            );
                        } else {
                            const anySelected =
                                Array.from(
                                    qualityInputs
                                ).some(
                                    (other) =>
                                        other !==
                                            allQualityInput
                                        && other.checked
                                );

                            if (
                                !anySelected
                                && allQualityInput
                            ) {
                                allQualityInput.checked =
                                    true;
                            }
                        }
                    } else if (
                        input.checked
                    ) {
                        if (
                            allQualityInput
                        ) {
                            allQualityInput.checked =
                                false;
                        }
                    } else {
                        const anySelected =
                            Array.from(
                                qualityInputs
                            ).some(
                                (other) =>
                                    other !==
                                        allQualityInput
                                    && other.checked
                            );

                        if (
                            !anySelected
                            && allQualityInput
                        ) {
                            allQualityInput.checked =
                                true;
                        }
                    }

                    updateQualityButtonText();
                }
            );
        }
    );

    updateQualityButtonText();
}


document.addEventListener(
    "click",
    () => {
        closeQualityDropdown();
    }
);


/* =========================================================
   PROGRESS
   ========================================================= */

function showProgressBlock() {
    const progressContainer =
        document.getElementById(
            "progress-container"
        );

    if (!progressContainer) {
        return;
    }

    progressContainer.style.display =
        "block";

    const percent =
        document.getElementById(
            "progress-percent"
        );

    const fill =
        document.getElementById(
            "progress-fill"
        );

    const stage =
        document.getElementById(
            "progress-stage"
        );

    const message =
        document.getElementById(
            "progress-message"
        );

    const details =
        document.getElementById(
            "progress-details"
        );

    if (percent) {
        percent.textContent = "0%";
    }

    if (fill) {
        fill.style.width = "0%";
    }

    if (stage) {
        stage.textContent =
            "Подготовка поиска";
    }

    if (message) {
        message.textContent =
            "Подготавливаем поиск...";
    }

    if (details) {
        details.textContent =
            "Ожидание начала поиска...";
    }
}


function updateProgress(data) {
    const percentElement =
        document.getElementById(
            "progress-percent"
        );

    const fillElement =
        document.getElementById(
            "progress-fill"
        );

    const stageElement =
        document.getElementById(
            "progress-stage"
        );

    const messageElement =
        document.getElementById(
            "progress-message"
        );

    const detailsElement =
        document.getElementById(
            "progress-details"
        );

    if (!percentElement || !fillElement) {
        return;
    }

    const rawPercent =
        Number(data?.percent);

    const percent =
        Number.isFinite(rawPercent)
            ? Math.max(
                0,
                Math.min(
                    100,
                    rawPercent
                )
            )
            : 0;

    percentElement.textContent =
        `${percent}%`;

    fillElement.style.width =
        `${percent}%`;

    if (stageElement) {
        stageElement.textContent =
            data?.stage || "Поиск";
    }

    if (messageElement) {
        messageElement.textContent =
            data?.message || "";
    }

    if (!detailsElement) {
        return;
    }

    const details = [];

    if (
        data?.quality_number !== undefined
        && data?.quality_total !== undefined
    ) {
        details.push(
            `Качество: `
            + `${data.quality_number}/`
            + `${data.quality_total}`
        );
    }

    if (
        data?.found_for_quality !== undefined
    ) {
        details.push(
            `Для качества: `
            + `${data.found_for_quality}`
        );
    }

    if (
        data?.total_found !== undefined
    ) {
        details.push(
            `Всего найдено: `
            + `${data.total_found}`
        );
    }

    if (
        data?.batch !== undefined
        && data?.total_batches !== undefined
    ) {
        details.push(
            `MassInfo: `
            + `${data.batch}/`
            + `${data.total_batches}`
        );
    }

    if (
        data?.processed !== undefined
        && data?.total_items !== undefined
    ) {
        details.push(
            `Обработано: `
            + `${data.processed}/`
            + `${data.total_items}`
        );
    }

    if (
        data?.descriptions !== undefined
    ) {
        details.push(
            `Получено описаний: `
            + `${data.descriptions}`
        );
    }

    if (
        data?.checked !== undefined
        && data?.total !== undefined
    ) {
        details.push(
            `Проверено: `
            + `${data.checked}/`
            + `${data.total}`
        );
    }

    if (
        data?.matches !== undefined
    ) {
        details.push(
            `Совпадений: `
            + `${data.matches}`
        );
    }

    detailsElement.textContent =
        details.length > 0
            ? details.join(" • ")
            : "Обработка...";
}

/* =========================================================
   RESULT CARD
   ========================================================= */

function createResultCard(item) {
    const card =
        document.createElement("div");

    card.className =
        "result-card";

    const title =
        document.createElement("h3");

    title.textContent =
        item.name;

    const price =
        document.createElement("div");

    price.className =
        "result-price";

    price.textContent =
        item.price_rub !== null
            ? `${item.price_rub.toFixed(2)} ₽`
            : "Цена неизвестна";

    const offers =
        document.createElement("div");

    offers.className =
        "result-count";

    offers.textContent =
        `Offers: ${
            item.offers ?? "неизвестно"
        }`;

    const identifiers =
        document.createElement("div");

    identifiers.className =
        "result-identifiers";

    identifiers.textContent =
        `Class: ${item.class_id}`
        + ` | Instance: ${item.instance_id}`;

    const description =
        document.createElement("div");

    description.className =
        "result-description";

    description.textContent =
        item.description_text
        || "Описание отсутствует";

    const link =
        document.createElement("a");

    link.className =
        "market-link";

    link.href =
        item.url;

    link.target =
        "_blank";

    link.rel =
        "noopener noreferrer";

    link.textContent =
        "Открыть на Market";

    card.appendChild(title);
    card.appendChild(price);
    card.appendChild(offers);
    card.appendChild(description);
    card.appendChild(identifiers);
    card.appendChild(link);

    return card;
}


function renderResults(
    data,
    elapsedSeconds
) {
    resultsContainer.innerHTML = "";

    if (
        !data.items
        || data.items.length === 0
    ) {
        showMessage(
            "Подходящих предметов не найдено."
            + ` Время поиска: `
            + `${elapsedSeconds.toFixed(1)} сек.`
        );

        return;
    }

    const header =
        document.createElement("div");

    header.className =
        "results-header";

    const title =
        document.createElement("strong");

    title.textContent =
        "Поиск завершён";

    const count =
        document.createElement("span");

    count.textContent =
        `Найдено вариантов: ${data.count}`;

    const time =
        document.createElement("span");

    time.textContent =
        `Время: ${elapsedSeconds.toFixed(1)} сек.`;

    header.appendChild(title);
    header.appendChild(count);
    header.appendChild(time);

    resultsContainer.appendChild(
        header
    );

    for (
        const item of data.items
    ) {
        resultsContainer.appendChild(
            createResultCard(item)
        );
    }
}


/* =========================================================
   ERRORS
   ========================================================= */

function formatError(data) {
    if (!data) {
        return "Неизвестная ошибка";
    }

    if (
        Array.isArray(data.detail)
    ) {
        return data.detail
            .map(
                (error) => {
                    const location =
                        error.loc
                            ? error.loc.join(".")
                            : "";

                    return (
                        `${location}: `
                        + `${error.msg}`
                    );
                }
            )
            .join("; ");
    }

    if (data.detail) {
        return String(
            data.detail
        );
    }

    if (data.message) {
        return String(
            data.message
        );
    }

    return "Ошибка поиска";
}


/* =========================================================
   SEARCH
   ========================================================= */

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

    const qualities =
        getSelectedQualities();

    searchButton.disabled =
        true;

    searchButton.textContent =
        "Поиск...";

    showProgressBlock();

    const startTime =
        performance.now();

    try {
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
                            "application/"
                            + "x-www-form-urlencoded",
                    },

                    body:
                        params.toString(),
                }
            );

        if (!response.ok) {
            let errorData = null;

            const responseText =
                await response.text();

            try {
                errorData =
                    JSON.parse(
                        responseText
                    );
            } catch {
                throw new Error(
                    responseText
                    || `HTTP ${response.status}`
                );
            }

            throw new Error(
                formatError(errorData)
            );
        }

        if (!response.body) {
            throw new Error(
                "Браузер не поддерживает "
                + "потоковый ответ."
            );
        }

        const reader =
            response.body.getReader();

        const decoder =
            new TextDecoder();

        let buffer = "";
        let resultData = null;

        while (true) {
            const {
                value,
                done,
            } = await reader.read();

            if (done) {
                break;
            }

            buffer += decoder.decode(
                value,
                {
                    stream: true,
                }
            );

            const lines =
                buffer.split("\n");

            buffer =
                lines.pop() || "";

            for (
                const line of lines
            ) {
                if (!line.trim()) {
                    continue;
                }

                let event;

                try {
                    event =
                        JSON.parse(line);
                } catch {
                    continue;
                }

                if (
                    event.event ===
                    "progress"
                ) {
                    updateProgress(
                        event.data
                    );
                }

                if (
                    event.event ===
                    "result"
                ) {
                    resultData =
                        event.data;
                }

                if (
                    event.event ===
                    "error"
                ) {
                    throw new Error(
                        event.data.message
                    );
                }
            }
        }

        if (!resultData) {
            throw new Error(
                "Сервер не вернул "
                + "результат поиска."
            );
        }

        updateProgress({
            percent: 100,
            stage: "Готово",
            message:
                "Поиск завершён",
            matches:
                resultData.count,
        });

        const elapsedSeconds =
            (
                performance.now()
                - startTime
            ) / 1000;

        await new Promise(
            (resolve) =>
                setTimeout(
                    resolve,
                    300
                )
        );

        renderResults(
            resultData,
            elapsedSeconds
        );
    } catch (error) {
        showMessage(
            `Ошибка: ${error.message}`
        );
    } finally {
        searchButton.disabled =
            false;

        searchButton.textContent =
            "Найти";
    }
}


/* =========================================================
   EVENTS
   ========================================================= */

searchButton.addEventListener(
    "click",
    searchItems
);


[
    itemNameInput,
    descriptionInput,
].forEach(
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


setupQualityDropdown();