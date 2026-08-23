from typing import Any, AsyncGenerator
from urllib.parse import quote
import re

from app.services.description_parser import (
    description_contains,
    extract_description_text,
)
from app.services.market_api import MarketAPI


QUALITY_NAMES = {
    "normal": "",
    "exalted": "Exalted ",
    "inscribed": "Inscribed ",
    "autographed": "Autographed ",
    "heroic": "Heroic ",
    "corrupted": "Corrupted ",
}


QUALITY_LABELS = {
    "normal": "Обычный",
    "exalted": "Exalted",
    "inscribed": "Inscribed",
    "autographed": "Autographed",
    "heroic": "Heroic",
    "corrupted": "Corrupted",
}


# =========================================================
# ПРИЗМАТИЧЕСКИЕ САМОЦВЕТЫ
# =========================================================

PRISMATIC_GEMS = [
    "Red",
    "Gold",
    "Blue",
    "Purple",
    "Orange",
    "Lime",
    "Deep Blue",
    "Sea Green",
    "Green",
    "Deep Green",
    "Bright Green",
    "Bright Purple",
    "Calm Blue",
    "Summer Warmth",
    "Muted Red",
    "Maker's Light",
    "Scarlet Blossom",
    "Blue Crystal",
    "Rubiline",
    "Absorbing Black",
    "Miasmatic Grey",
    "Champion's Blue",
    "Champion's Green",
    "Champion's Purple",
    "Midas Gold",
    "Green Planet",
    "Ember Flame",
    "Diretide Orange",
    "Dredge Earth",
    "Dungeon Doom",
    "Tnim S'nnam",
    "Brusque Britches Beige",
    "Unhallowed Ground",
    "Ships in the Night",
    "Pristine Platinum",
    "Vermillion Renewal",
    "Reflection's Shade",
    "Pyroclastic Flow",
    "Glacial Flow",
    "Plushy Shag",
    "Explosive Burst",
]


PRISMATIC_GEM_ALIASES = {
    "Red": [
        "Red",
        "Красный",
    ],
    "Gold": [
        "Gold",
        "Золотой",
    ],
    "Blue": [
        "Blue",
        "Синий",
    ],
    "Purple": [
        "Purple",
        "Фиолетовый",
    ],
    "Orange": [
        "Orange",
        "Оранжевый",
    ],
    "Lime": [
        "Lime",
        "Светло-зеленый",
        "Светло-зелёный",
    ],
    "Deep Blue": [
        "Deep Blue",
        "Глубокий синий",
    ],
    "Sea Green": [
        "Sea Green",
        "Сине-зеленый",
        "Сине-зелёный",
    ],
    "Green": [
        "Green",
        "Зеленая сосна",
        "Зелёная сосна",
    ],
    "Deep Green": [
        "Deep Green",
        "Глубокий зеленый",
        "Глубокий зелёный",
    ],
    "Bright Green": [
        "Bright Green",
        "Ярко-зеленый",
        "Ярко-зелёный",
    ],
    "Bright Purple": [
        "Bright Purple",
        "Ярко-фиолетовый",
    ],
    "Calm Blue": [
        "Calm Blue",
        "Спокойный синий",
    ],
    "Summer Warmth": [
        "Summer Warmth",
        "Летнее тепло",
    ],
    "Muted Red": [
        "Muted Red",
        "Сдержанно-красный",
        "Сдержанно-красный",
    ],
    "Maker's Light": [
        "Maker's Light",
        "Свет создателя",
    ],
    "Scarlet Blossom": [
        "Scarlet Blossom",
        "Аленький цветочек",
    ],
    "Blue Crystal": [
        "Blue Crystal",
        "Синий кристалл",
    ],
    "Rubiline": [
        "Rubiline",
    ],
    "Absorbing Black": [
        "Absorbing Black",
        "Отталкивающий черный",
        "Отталкивающий чёрный",
    ],
    "Miasmatic Grey": [
        "Miasmatic Grey",
        "Чумной серый",
    ],
    "Champion's Blue": [
        "Champion's Blue",
        "Чемпионский синий",
    ],
    "Champion's Green": [
        "Champion's Green",
        "Чемпионский зеленый",
        "Чемпионский зелёный",
    ],
    "Champion's Purple": [
        "Champion's Purple",
        "Чемпионский фиолетовый",
    ],
    "Midas Gold": [
        "Midas Gold",
        "Золото Мидаса",
    ],
    "Green Planet": [
        "Green Planet",
        "Зеленая планета",
        "Зелёная планета",
    ],
    "Ember Flame": [
        "Ember Flame",
        "Тлеющее пламя",
    ],
    "Diretide Orange": [
        "Diretide Orange",
    ],
    "Dredge Earth": [
        "Dredge Earth",
    ],
    "Dungeon Doom": [
        "Dungeon Doom",
    ],
    "Tnim S'nnam": [
        "Tnim S'nnam",
    ],
    "Brusque Britches Beige": [
        "Brusque Britches Beige",
    ],
    "Unhallowed Ground": [
        "Unhallowed Ground",
    ],
    "Ships in the Night": [
        "Ships in the Night",
    ],
    "Pristine Platinum": [
        "Pristine Platinum",
    ],
    "Vermillion Renewal": [
        "Vermillion Renewal",
    ],
    "Reflection's Shade": [
        "Reflection's Shade",
    ],
    "Pyroclastic Flow": [
        "Pyroclastic Flow",
    ],
    "Glacial Flow": [
        "Glacial Flow",
    ],
    "Plushy Shag": [
        "Plushy Shag",
    ],
    "Explosive Burst": [
        "Explosive Burst",
    ],
}


MASS_INFO_BATCH_SIZE = 100


class SearchService:
    def __init__(self) -> None:
        self.market_api = MarketAPI()

    @staticmethod
    def chunks(
        items: list[str],
        size: int,
    ) -> list[list[str]]:
        """Split list into batches."""
        return [
            items[index:index + size]
            for index in range(
                0,
                len(items),
                size,
            )
        ]

    @staticmethod
    def normalize_qualities(
        qualities: list[str],
    ) -> list[str]:
        """Normalize selected quality values."""
        if not qualities:
            return list(QUALITY_NAMES)

        if "all" in qualities:
            return list(QUALITY_NAMES)

        result = []

        for quality in qualities:
            if quality in QUALITY_NAMES:
                if quality not in result:
                    result.append(quality)

        return result or list(QUALITY_NAMES)

    @staticmethod
    def extract_gems(
            description: Any,
    ) -> list[str]:
        """
        Extract exactly one prismatic gem from description.
        """

        if not description:
            return []

        text = extract_description_text(description)

        if not text:
            return []

        gem_names = sorted(
            PRISMATIC_GEMS,
            key=len,
            reverse=True,
        )

        for gem_name in gem_names:
            aliases = PRISMATIC_GEM_ALIASES.get(
                gem_name,
                [gem_name],
            )

            for alias in aliases:
                pattern = (
                        r"(?<!\w)"
                        + re.escape(alias)
                        + r"(?!\w)"
                )

                if re.search(
                        pattern,
                        text,
                        flags=re.IGNORECASE,
                ):
                    return [gem_name]

        return []

    @staticmethod
    def build_gem_statistics(
            items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Build statistics only for prismatic gems.

        Every item contributes to at most one gem because
        extract_gems() returns at most one prismatic gem.
        """

        counters = {
            gem: 0
            for gem in PRISMATIC_GEMS
        }

        for item in items:
            gems = item.get("gems", [])

            if not gems:
                continue

            # One item = one prismatic gem.
            gem = gems[0]

            if gem in counters:
                counters[gem] += 1

        return [
            {
                "name": gem,
                "count": counters[gem],
            }
            for gem in PRISMATIC_GEMS
        ]

    async def search(
        self,
        item_name: str,
        description_query: str,
        qualities: list[str],
        gem_mode: bool = False,
    ) -> AsyncGenerator[
        dict[str, Any],
        None,
    ]:
        selected_qualities = self.normalize_qualities(
            qualities
        )

        quality_total = len(selected_qualities)

        # ==================================================
        # ЭТАП 1. SEARCH ITEM
        # ==================================================

        all_items: list[dict[str, Any]] = []

        for quality_number, quality in enumerate(
            selected_qualities,
            start=1,
        ):
            prefix = QUALITY_NAMES[quality]
            quality_label = QUALITY_LABELS[quality]

            search_name = (
                f"{prefix}{item_name}"
            )

            yield {
                "type": "progress",
                "data": {
                    "percent": self._search_percent(
                        quality_number,
                        quality_total,
                    ),
                    "stage": (
                        f"Поиск: {quality_label}"
                    ),
                    "message": (
                        f"Ищем «{search_name}» "
                        f"на Market..."
                    ),
                    "quality_number": quality_number,
                    "quality_total": quality_total,
                    "quality": quality_label,
                },
            }

            search_result = (
                await self.market_api.search_item(
                    search_name,
                )
            )

            items = search_result.get(
                "list",
                [],
            )

            all_items.extend(items)

            yield {
                "type": "progress",
                "data": {
                    "percent": self._search_percent(
                        quality_number,
                        quality_total,
                        completed=True,
                    ),
                    "stage": (
                        f"Поиск: {quality_label}"
                    ),
                    "message": (
                        f"Найдено вариантов: "
                        f"{len(items)}"
                    ),
                    "quality_number": quality_number,
                    "quality_total": quality_total,
                    "found_for_quality": len(items),
                    "total_found": len(all_items),
                },
            }

        # ==================================================
        # УДАЛЯЕМ ДУБЛИКАТЫ
        # ==================================================

        items_by_hash: dict[
            tuple[str, str],
            dict[str, Any],
        ] = {}

        for item in all_items:
            class_id = str(
                item.get("i_classid", "")
            )

            instance_id = str(
                item.get("i_instanceid", "")
            )

            if not class_id or not instance_id:
                continue

            items_by_hash[
                (class_id, instance_id)
            ] = item

        unique_items = list(
            items_by_hash.values()
        )

        item_hashes = [
            (
                f"{item['i_classid']}_"
                f"{item['i_instanceid']}"
            )
            for item in unique_items
        ]

        if not item_hashes:
            yield {
                "type": "result",
                "data": {
                    "count": 0,
                    "items": [],
                    "gems": [],
                    "gem_mode": gem_mode,
                },
            }
            return

        # ==================================================
        # ЭТАП 2. MASS INFO
        # ==================================================

        batches = self.chunks(
            item_hashes,
            MASS_INFO_BATCH_SIZE,
        )

        total_batches = len(batches)

        all_mass_results: list[
            dict[str, Any]
        ] = []

        yield {
            "type": "progress",
            "data": {
                "percent": 25,
                "stage": "Получение данных",
                "message": (
                    f"Подготовлено "
                    f"{len(unique_items)} "
                    f"уникальных предметов"
                ),
                "total_items": len(unique_items),
                "total_batches": total_batches,
            },
        }

        for batch_number, batch in enumerate(
            batches,
            start=1,
        ):
            mass_result = (
                await self.market_api.get_mass_info(
                    item_hashes=batch,
                    sell=0,
                    buy=0,
                    history=0,
                    info=3,
                )
            )

            batch_results = mass_result.get(
                "results",
                [],
            )

            all_mass_results.extend(
                batch_results
            )

            percent = (
                25
                + (
                    batch_number
                    / total_batches
                )
                * 55
            )

            yield {
                "type": "progress",
                "data": {
                    "percent": round(percent),
                    "stage": "Получение данных",
                    "message": (
                        f"Обрабатываем MassInfo: "
                        f"пачка {batch_number}/"
                        f"{total_batches}"
                    ),
                    "batch": batch_number,
                    "total_batches": total_batches,
                    "processed": min(
                        batch_number
                        * MASS_INFO_BATCH_SIZE,
                        len(unique_items),
                    ),
                    "total_items": len(unique_items),
                    "descriptions": len(
                        all_mass_results
                    ),
                },
            }

        # ==================================================
        # ЭТАП 3. ОБРАБОТКА ПРЕДМЕТОВ
        # ==================================================

        matched_items: list[
            dict[str, Any]
        ] = []

        total_results = len(
            all_mass_results
        )

        yield {
            "type": "progress",
            "data": {
                "percent": 82,
                "stage": "Обработка предметов",
                "message": (
                    f"Обрабатываем "
                    f"{total_results} "
                    f"предметов..."
                ),
                "checked": 0,
                "total": total_results,
                "matches": 0,
            },
        }

        for index, item_data in enumerate(
            all_mass_results,
            start=1,
        ):
            info = item_data.get(
                "info"
            ) or {}

            description = info.get(
                "description"
            )

            description_text = (
                extract_description_text(
                    description
                )
            )

            # В обычном режиме проверяем описание.
            # В gem_mode сохраняем все предметы.
            if gem_mode:
                is_match = True
            else:
                is_match = description_contains(
                    description,
                    description_query,
                )

            if is_match:
                class_id = str(
                    item_data.get(
                        "classid",
                        "",
                    )
                )

                instance_id = str(
                    item_data.get(
                        "instanceid",
                        "",
                    )
                )

                market_item = (
                    items_by_hash.get(
                        (
                            class_id,
                            instance_id,
                        ),
                        {},
                    )
                )

                market_name = info.get(
                    "market_hash_name",
                    market_item.get(
                        "market_hash_name",
                        item_name,
                    ),
                )

                price = market_item.get(
                    "price"
                )

                price_rub = None

                if price is not None:
                    price_rub = (
                        int(price) / 100
                    )

                market_url = (
                    "https://market.dota2.net/item/"
                    f"{class_id}-{instance_id}-"
                    f"{quote(market_name, safe='')}/"
                )

                gems = (
                    SearchService.extract_gems(
                        description
                    )
                )

                matched_items.append(
                    {
                        "name": market_name,
                        "class_id": class_id,
                        "instance_id": instance_id,
                        "price": price,
                        "price_rub": price_rub,
                        "offers": market_item.get(
                            "offers"
                        ),
                        "description": description,
                        "description_text": (
                            description_text
                        ),
                        "url": market_url,
                        "image": info.get(
                            "image"
                        ),
                        "gems": gems,
                    }
                )

            if (
                index == total_results
                or index % 10 == 0
            ):
                percent = (
                    82
                    + (
                        index
                        / max(
                            total_results,
                            1,
                        )
                    )
                    * 16
                )

                yield {
                    "type": "progress",
                    "data": {
                        "percent": round(
                            percent
                        ),
                        "stage": (
                            "Обработка предметов"
                        ),
                        "message": (
                            f"Проверено {index} "
                            f"из {total_results}"
                        ),
                        "checked": index,
                        "total": total_results,
                        "matches": len(
                            matched_items
                        ),
                    },
                }

        # ==================================================
        # СТАТИСТИКА ГЕМОВ
        # ==================================================

        gem_statistics = (
            self.build_gem_statistics(
                matched_items
            )
        )

        yield {
            "type": "progress",
            "data": {
                "percent": 99,
                "stage": "Формирование результата",
                "message": (
                    f"Обработано предметов: "
                    f"{len(matched_items)}"
                ),
                "matches": len(
                    matched_items
                ),
                "gems": len(
                    gem_statistics
                ),
            },
        }

        # ==================================================
        # СОРТИРОВКА
        # ==================================================

        matched_items.sort(
            key=lambda item: (
                item["price"]
                if item["price"] is not None
                else float("inf")
            )
        )

        # ==================================================
        # ГОТОВО
        # ==================================================

        yield {
            "type": "result",
            "data": {
                "count": len(
                    matched_items
                ),
                "items": matched_items,
                "gems": gem_statistics,
                "gem_mode": gem_mode,
            },
        }

        yield {
            "type": "progress",
            "data": {
                "percent": 100,
                "stage": "Готово",
                "message": (
                    f"Поиск завершён. "
                    f"Найдено: "
                    f"{len(matched_items)}"
                ),
                "matches": len(
                    matched_items
                ),
            },
        }

    @staticmethod
    def _search_percent(
        quality_number: int,
        quality_total: int,
        completed: bool = False,
    ) -> int:
        """
        Calculate progress for SEARCH ITEM stage.

        Search stage occupies 0-25%.
        """
        if quality_total <= 0:
            return 0

        base = (
            (quality_number - 1)
            / quality_total
            * 25
        )

        if completed:
            base += (
                1
                / quality_total
                * 25
            )

        return round(base)