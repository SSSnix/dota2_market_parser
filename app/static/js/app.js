const searchButton =
    document.getElementById("search-button");

const itemNameInput =
    document.getElementById("item-name");

const descriptionInput =
    document.getElementById("description");

const gemModeInput =
    document.getElementById("gem-mode");

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


let currentSearchData = null;
let currentGemFilter = null;
let currentSearchStartedAt = 0;


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

    qualityButton.classList.remove(
        "is-open"
    );
}


function toggleQualityDropdown() {
    if (!qualityDropdown) {
        return;
    }

    qualityDropdown.classList.toggle(
        "is-open"
    );

    qualityButton.classList.toggle(
        "is-open"
    );
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

    if (!selected.length) {
        return ["all"];
    }

    if (selected.includes("all")) {
        return ["all"];
    }

    return selected;
}


function updateQualityButtonText() {
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

    qualityButtonText.textContent =
        selected
            .map(
                (value) =>
                    labels[value] || value
            )
            .join(", ");
}


function setupQualityDropdown() {
    if (
        !qualityButton
        || !qualityDropdown
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
                            const otherSelected =
                                Array.from(
                                    qualityInputs
                                ).some(
                                    (other) =>
                                        other !==
                                            allQualityInput
                                        && other.checked
                                );

                            if (
                                !otherSelected
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
                        const otherSelected =
                            Array.from(
                                qualityInputs
                            ).some(
                                (other) =>
                                    other !==
                                        allQualityInput
                                    && other.checked
                            );

                        if (
                            !otherSelected
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

function updateGemMode() {
    if (!gemModeInput) {
        return;
    }

    const enabled =
        gemModeInput.checked;

    descriptionInput.disabled =
        enabled;

    if (enabled) {
        descriptionInput.value = "";
        descriptionInput.placeholder =
            "Описание не требуется";
    } else {
        descriptionInput.disabled =
            false;

        descriptionInput.placeholder =
            "Например: Tnim S'nnam";
    }
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
            `Совпадений: `
            + `${data.matches}`
        );
    }

    if (
        data.gems !==
        undefined
    ) {
        details.push(
            `Гемов: ${data.gems}`
        );
    }

    detailsElement.textContent =
        details.join(" • ");
}


function showFinalProgress() {
    updateProgress({
        percent: 100,
        stage: "Готово",
        message: "Поиск завершён",
    });
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

    const description =
        document.createElement("div");

    description.className =
        "result-description";

    description.textContent =
        item.description_text
        || "Описание отсутствует";

    const identifiers =
        document.createElement("div");

    identifiers.className =
        "result-identifiers";

    identifiers.textContent =
        `Class: ${item.class_id}`
        + ` | Instance: ${item.instance_id}`;

    card.appendChild(title);
    card.appendChild(price);
    card.appendChild(offers);

    if (
        item.gems
        && item.gems.length
    ) {
        const gems =
            document.createElement("div");

        gems.className =
            "result-gems";

        gems.textContent =
            `Гемы: ${item.gems.join(", ")}`;

        card.appendChild(gems);
    }

    card.appendChild(description);
    card.appendChild(identifiers);

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

    card.appendChild(link);

    return card;
}


/* =========================================================
   GEM TABS
   ========================================================= */

function createGemTabs(data) {
    const wrapper =
        document.createElement("div");

    wrapper.className =
        "gem-panel";

    const title =
        document.createElement("div");

    title.className =
        "gem-panel-title";

    title.textContent =
        "Гемы";

    wrapper.appendChild(title);

    const tabs =
        document.createElement("div");

    tabs.className =
        "gem-tabs";

    const allButton =
        document.createElement("button");

    allButton.type =
        "button";

    allButton.className =
        "gem-tab active";

    allButton.dataset.gem =
        "__all__";

    allButton.innerHTML =
        `<span>Все предметы</span>`
        + `<strong>${data.items.length}</strong>`;

    tabs.appendChild(allButton);

    /*
     * ВАЖНО:
     *
     * data.gems содержит не только гемы из
     * PRISMATIC_GEMS, но и автоматически найденные
     * неизвестные гемы.
     *
     * Поэтому здесь ничего дополнительно
     * фильтровать нельзя.
     */

    const gems =
        data.gems || [];

    for (
        const gem of gems
    ) {
        const button =
            document.createElement("button");

        button.type =
            "button";

        button.className =
            "gem-tab";

        button.dataset.gem =
            gem.name;

        const name =
            document.createElement("span");

        name.textContent =
            gem.name;

        const count =
            document.createElement("strong");

        count.textContent =
            gem.count;

        button.appendChild(name);
        button.appendChild(count);

        tabs.appendChild(button);
    }

    tabs.addEventListener(
        "click",
        (event) => {
            const button =
                event.target.closest(
                    ".gem-tab"
                );

            if (!button) {
                return;
            }

            const gem =
                button.dataset.gem;

            tabs
                .querySelectorAll(
                    ".gem-tab"
                )
                .forEach(
                    (tab) =>
                        tab.classList.remove(
                            "active"
                        )
                );

            button.classList.add(
                "active"
            );

            if (gem === "__all__") {
                currentGemFilter =
                    null;

                renderLocalItems(
                    data.items
                );

                return;
            }

            currentGemFilter =
                gem;

            const filtered =
                data.items.filter(
                    (item) =>
                        Array.isArray(
                            item.gems
                        )
                        && item.gems.includes(
                            gem
                        )
                );

            renderLocalItems(
                filtered,
                gem
            );
        }
    );

    wrapper.appendChild(tabs);

    return wrapper;
}


function renderLocalItems(
    items,
    selectedGem = null
) {
    const oldSection =
        document.querySelector(
            ".local-results"
        );

    if (oldSection) {
        oldSection.remove();
    }

    const section =
        document.createElement("div");

    section.className =
        "local-results";

    const title =
        document.createElement("div");

    title.className =
        "local-results-title";

    if (selectedGem) {
        title.textContent =
            `${selectedGem}: `
            + `${items.length} предметов`;
    } else {
        title.textContent =
            `Все предметы: `
            + `${items.length}`;
    }

    section.appendChild(title);

    if (!items.length) {
        const empty =
            document.createElement("div");

        empty.className =
            "message";

        empty.textContent =
            "Предметов не найдено.";

        section.appendChild(
            empty
        );
    } else {
        for (
            const item of items
        ) {
            section.appendChild(
                createResultCard(item)
            );
        }
    }

    resultsContainer.appendChild(
        section
    );
}


/* =========================================================
   GEM MODE RESULTS
   ========================================================= */

function renderGemResults(
    data,
    elapsedSeconds
) {
    resultsContainer.innerHTML = "";

    const header =
        document.createElement("div");

    header.className =
        "results-header";

    const title =
        document.createElement("strong");

    title.textContent =
        "Поиск завершён";

    const total =
        document.createElement("span");

    total.textContent =
        `Всего предметов: ${data.count}`;

    const time =
        document.createElement("span");

    time.textContent =
        `Время: ${elapsedSeconds.toFixed(1)} сек.`;

    header.appendChild(title);
    header.appendChild(total);
    header.appendChild(time);

    resultsContainer.appendChild(
        header
    );

    const gemPanel =
        createGemTabs(data);

    resultsContainer.appendChild(
        gemPanel
    );

    renderLocalItems(
        data.items
    );
}


/* =========================================================
   NORMAL RESULTS
   ========================================================= */

function renderNormalResults(
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

    const gemMode =
        gemModeInput
        && gemModeInput.checked;

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

    currentSearchData = null;
    currentGemFilter = null;

    createProgressBlock();

    currentSearchStartedAt =
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
            let errorData;

            try {
                errorData =
                    await response.json();
            } catch {
                throw new Error(
                    `HTTP ${response.status}`
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

        currentSearchData =
            resultData;

        showFinalProgress();

        const elapsedSeconds =
            (
                performance.now()
                - currentSearchStartedAt
            ) / 1000;

        await new Promise(
            (resolve) =>
                setTimeout(
                    resolve,
                    250
                )
        );

        if (gemMode) {
            renderGemResults(
                resultData,
                elapsedSeconds
            );
        } else {
            renderNormalResults(
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


if (gemModeInput) {
    gemModeInput.addEventListener(
        "change",
        updateGemMode
    );
}


setupQualityDropdown();
updateGemMode();