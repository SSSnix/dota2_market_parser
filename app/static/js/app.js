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

const allGemsInput =
    document.getElementById("all-gems");

const descriptionLabel =
    document.getElementById(
        "description-label"
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
   GEM MODE
   ========================================================= */

function updateGemModeUI() {
    if (!allGemsInput) {
        return;
    }

    const gemMode =
        allGemsInput.checked;

    if (descriptionInput) {
        descriptionInput.disabled =
            gemMode;

        if (gemMode) {
            descriptionInput.value = "";
            descriptionInput.placeholder =
                "Описание не требуется";
        } else {
            descriptionInput.placeholder =
                "Например: Tnim S'nnam";
        }
    }

    if (descriptionLabel) {
        if (gemMode) {
            descriptionLabel.textContent =
                "Описание";
        } else {
            descriptionLabel.textContent =
                "Описание";
        }
    }
}


if (allGemsInput) {
    allGemsInput.addEventListener(
        "change",
        updateGemModeUI
    );
}


/* =========================================================
   PROGRESS
   ========================================================= */

function createProgressBlock() {
    resultsContainer.innerHTML = "";

    const block =
        document.createElement("div");

    block.className =
        "search-progress";

    block.innerHTML = `
        <div class="progress-header">
            <div
                id="progress-stage"
                class="progress-stage"
            >
                Подготовка
            </div>

            <div
                id="progress-percent"
                class="progress-percent"
            >
                0%
            </div>
        </div>

        <div class="progress-bar">
            <div
                id="progress-fill"
                class="progress-fill"
            ></div>
        </div>

        <div
            id="progress-message"
            class="progress-message"
        >
            Подготавливаем поиск...
        </div>

        <div
            id="progress-details"
            class="progress-details"
        ></div>
    `;

    resultsContainer.appendChild(
        block
    );
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

    if (
        !percentElement
        || !fillElement
    ) {
        return;
    }

    const rawPercent =
        Number(data.percent);

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
            data.stage || "Поиск";
    }

    if (messageElement) {
        messageElement.textContent =
            data.message || "";
    }

    if (!detailsElement) {
        return;
    }

    const details = [];

    if (
        data.gem_mode
    ) {
        details.push(
            "Режим: все призматические гемы"
        );
    }

    if (
        data.quality_number
        && data.quality_total
    ) {
        details.push(
            `Качество: `
            + `${data.quality_number}/`
            + `${data.quality_total}`
        );
    }

    if (
        data.found_for_quality !==
        undefined
    ) {
        details.push(
            `Найдено для качества: `
            + `${data.found_for_quality}`
        );
    }

    if (
        data.total_found !==
        undefined
    ) {
        details.push(
            `Всего найдено: `
            + `${data.total_found}`
        );
    }

    if (
        data.batch
        && data.total_batches
    ) {
        details.push(
            `MassInfo: `
            + `${data.batch}/`
            + `${data.total_batches}`
        );
    }

    if (
        data.processed !==
        undefined
        && data.total_items !==
        undefined
    ) {
        details.push(
            `Обработано: `
            + `${data.processed}/`
            + `${data.total_items}`
        );
    }

    if (
        data.descriptions !==
        undefined
    ) {
        details.push(
            `Получено описаний: `
            + `${data.descriptions}`
        );
    }

    if (
        data.checked !==
        undefined
        && data.total !==
        undefined
    ) {
        details.push(
            `Проверено: `
            + `${data.checked}/`
            + `${data.total}`
        );
    }

    if (
        data.matches !==
        undefined
    ) {
        details.push(
            `Предметов с гемами: `
            + `${data.matches}`
        );
    }

    if (
        data.gem_types !==
        undefined
    ) {
        details.push(
            `Видов гемов: `
            + `${data.gem_types}`
        );
    }

    detailsElement.textContent =
        details.join(" • ");
}


/* =========================================================
   GEM RESULTS
   ========================================================= */

function createGemCard(
    gemName,
    count
) {
    const card =
        document.createElement("button");

    card.type = "button";

    card.className =
        "gem-card";

    card.dataset.gem =
        gemName;

    const name =
        document.createElement("span");

    name.className =
        "gem-card-name";

    name.textContent =
        gemName;

    const countElement =
        document.createElement("span");

    countElement.className =
        "gem-card-count";

    countElement.textContent =
        `${count} предметов`;

    card.appendChild(name);
    card.appendChild(countElement);

    card.addEventListener(
        "click",
        () => {
            selectGem(
                gemName
            );
        }
    );

    return card;
}


function renderGemResults(
    data,
    elapsedSeconds
) {
    resultsContainer.innerHTML = "";

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "gem-results";

    const header =
        document.createElement("div");

    header.className =
        "results-header";

    const title =
        document.createElement("strong");

    title.textContent =
        "Призматические самоцветы";

    const count =
        document.createElement("span");

    count.textContent =
        `Предметов с гемами: ${data.count}`;

    const time =
        document.createElement("span");

    time.textContent =
        `Время: ${elapsedSeconds.toFixed(1)} сек.`;

    header.appendChild(title);
    header.appendChild(count);
    header.appendChild(time);

    wrapper.appendChild(header);

    const hint =
        document.createElement("div");

    hint.className =
        "gem-results-hint";

    hint.textContent =
        "Нажмите на гем, чтобы показать "
        + "все предметы с этим гемом.";

    wrapper.appendChild(hint);

    const grid =
        document.createElement("div");

    grid.className =
        "gem-grid";

    const gemCounts =
        data.gem_counts || {};

    const entries =
        Object.entries(
            gemCounts
        );

    if (!entries.length) {
        const empty =
            document.createElement("div");

        empty.className =
            "message";

        empty.textContent =
            "Призматических гемов "
            + "в найденных предметах не обнаружено.";

        wrapper.appendChild(empty);

        resultsContainer.appendChild(
            wrapper
        );

        return;
    }

    for (
        const [gemName, gemCount]
        of entries
    ) {
        grid.appendChild(
            createGemCard(
                gemName,
                gemCount
            )
        );
    }

    wrapper.appendChild(grid);

    resultsContainer.appendChild(
        wrapper
    );
}


function selectGem(gemName) {
    if (!descriptionInput) {
        return;
    }

    if (allGemsInput) {
        allGemsInput.checked =
            false;

        updateGemModeUI();
    }

    descriptionInput.value =
        gemName;

    searchItems();
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

    const gemMode =
        allGemsInput
            ? allGemsInput.checked
            : false;

    const description =
        descriptionInput.value.trim();

    if (!itemName) {
        showMessage(
            "Введите название предмета."
        );

        return;
    }

    if (
        !gemMode
        && !description
    ) {
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

    createProgressBlock();

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

        params.append(
            "gem_mode",
            gemMode
                ? "true"
                : "false"
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
                gemMode
                    ? "Анализ гемов завершён"
                    : "Поиск завершён",
            matches:
                resultData.count,
            gem_mode:
                resultData.gem_mode,
            gem_types:
                resultData.gem_counts
                    ? Object.keys(
                        resultData.gem_counts
                    ).length
                    : undefined,
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

        if (
            resultData.gem_mode
        ) {
            renderGemResults(
                resultData,
                elapsedSeconds
            );
        } else {
            renderResults(
                resultData,
                elapsedSeconds
            );
        }
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
updateGemModeUI();