from typing import Any, AsyncGenerator
from urllib.parse import quote

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
    "Miasmatic Grey",
    "Pristine Platinum",
    "Vermillion Renewal",
    "Reflection's Shade",
    "Pyroclastic Flow",
    "Glacial Flow",
    "Plushy Shag",
    "Explosive Burst",
]


# Названия выше соответствуют английским названиям
# призматических самоцветов, которые могут встречаться
# в описаниях предметов.
#
# Для первых цветов Wiki использует формат
# "Призматический: Красный", "Призматический: Золотой" и т.д.
# Поэтому для анализа описаний нам также нужны варианты
# русских названий.

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
    ],
    "Deep Blue": [
        "Deep Blue",
        "Глубокий синий",
    ],
    "Sea Green": [
        "Sea Green",
        "Сине-зеленый",
    ],
    "Green": [
        "Green",
        "Зеленая сосна",
    ],
    "Deep Green": [
        "Deep Green",
        "Глубокий зеленый",
    ],
    "Bright Green": [
        "Bright Green",
        "Ярко-зеленый",
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
    def _find_gems_in_description(
        description: Any,
    ) -> list[str]:
        """
        Find all known prism gems in description.

        One item can contain more than one gem.
        """
        if not description:
            return []

        text = extract_description_text(
            description
        )

        if not text:
            return []

        text_lower = text.lower()

        found = []

        for gem_name, aliases in (
            PRISMATIC_GEM_ALIASES.items()
        ):
            for alias in aliases:
                if alias.lower() in text_lower:
                    found.append(gem_name)
                    break

        return found

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
                    "gem_mode": gem_mode,
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
                    "gem_mode": gem_mode,
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
            if gem_mode:
                yield {
                    "type": "result",
                    "data": {
                        "count": 0,
                        "items": [],
                        "gem_mode": True,
                        "gem_counts": {},
                    },
                }
            else:
                yield {
                    "type": "result",
                    "data": {
                        "count": 0,
                        "items": [],
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
                    f"Подготовлено {len(unique_items)} "
                    f"уникальных предметов"
                ),
                "total_items": len(unique_items),
                "total_batches": total_batches,
                "gem_mode": gem_mode,
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
                    "gem_mode": gem_mode,
                },
            }

        # ==================================================
        # ЭТАП 3. АНАЛИЗ
        # ==================================================

        matched_items: list[
            dict[str, Any]
        ] = []

        total_results = len(
            all_mass_results
        )

        # Счётчики гемов.
        gem_counts = {
            gem: 0
            for gem in PRISMATIC_GEM_ALIASES
        }

        unique_items_with_gems = 0

        yield {
            "type": "progress",
            "data": {
                "percent": 82,
                "stage": (
                    "Анализ гемов"
                    if gem_mode
                    else "Проверка описаний"
                ),
                "message": (
                    (
                        f"Анализируем {total_results} "
                        f"описаний на наличие гемов..."
                    )
                    if gem_mode
                    else (
                        f"Проверяем {total_results} "
                        f"описаний..."
                    )
                ),
                "checked": 0,
                "total": total_results,
                "matches": 0,
                "gem_mode": gem_mode,
            },
        }

        for index, item_data in enumerate(
            all_mass_results,
            start=1,
        ):
            info = item_data.get(
                "info"
            ) or {}

            raw_description = info.get(
                "description"
            )

            # ==================================================
            # РЕЖИМ ВСЕХ ГЕМОВ
            # ==================================================

            if gem_mode:
                found_gems = (
                    self._find_gems_in_description(
                        raw_description
                    )
                )

                if found_gems:
                    unique_items_with_gems += 1

                for gem_name in found_gems:
                    gem_counts[gem_name] += 1

            # ==================================================
            # ОБЫЧНЫЙ РЕЖИМ
            # ==================================================

            else:
                if description_contains(
                    raw_description,
                    description_query,
                ):
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
                            "description": raw_description,
                            "description_text": (
                                extract_description_text(
                                    raw_description
                                )
                            ),
                            "url": market_url,
                            "image": info.get(
                                "image"
                            ),
                        }
                    )

            # ==================================================
            # ПРОГРЕСС
            # ==================================================

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

                if gem_mode:
                    message = (
                        f"Проверено {index} "
                        f"из {total_results}. "
                        f"Найдено предметов с гемами: "
                        f"{unique_items_with_gems}"
                    )
                else:
                    message = (
                        f"Проверено {index} "
                        f"из {total_results}"
                    )

                yield {
                    "type": "progress",
                    "data": {
                        "percent": round(percent),
                        "stage": (
                            "Анализ гемов"
                            if gem_mode
                            else "Проверка описаний"
                        ),
                        "message": message,
                        "checked": index,
                        "total": total_results,
                        "matches": (
                            unique_items_with_gems
                            if gem_mode
                            else len(matched_items)
                        ),
                        "gem_mode": gem_mode,
                    },
                }

        # ==================================================
        # РЕЖИМ ВСЕХ ГЕМОВ — РЕЗУЛЬТАТ
        # ==================================================

        if gem_mode:
            # Убираем гемы, которых нет ни в одном
            # найденном предмете.
            gem_counts = {
                gem: count
                for gem, count in gem_counts.items()
                if count > 0
            }

            # Сортируем по количеству предметов.
            gem_counts = dict(
                sorted(
                    gem_counts.items(),
                    key=lambda pair: (
                        -pair[1],
                        pair[0].lower(),
                    ),
                )
            )

            yield {
                "type": "progress",
                "data": {
                    "percent": 99,
                    "stage": "Формирование результата",
                    "message": (
                        f"Найдено {len(gem_counts)} "
                        f"видов призматических гемов"
                    ),
                    "gem_types": len(gem_counts),
                    "gem_items": unique_items_with_gems,
                    "gem_mode": True,
                },
            }

            yield {
                "type": "result",
                "data": {
                    "count": unique_items_with_gems,
                    "items": [],
                    "gem_mode": True,
                    "gem_counts": gem_counts,
                },
            }

            yield {
                "type": "progress",
                "data": {
                    "percent": 100,
                    "stage": "Готово",
                    "message": (
                        f"Поиск гемов завершён. "
                        f"Найдено предметов: "
                        f"{unique_items_with_gems}"
                    ),
                    "matches": unique_items_with_gems,
                    "gem_types": len(gem_counts),
                    "gem_mode": True,
                },
            }

            return

        # ==================================================
        # ОБЫЧНЫЙ РЕЖИМ — СОРТИРОВКА
        # ==================================================

        matched_items.sort(
            key=lambda item: (
                item["price"]
                if item["price"] is not None
                else float("inf")
            )
        )

        yield {
            "type": "progress",
            "data": {
                "percent": 99,
                "stage": "Формирование результата",
                "message": (
                    f"Найдено совпадений: "
                    f"{len(matched_items)}"
                ),
                "matches": len(
                    matched_items
                ),
            },
        }

        yield {
            "type": "result",
            "data": {
                "count": len(
                    matched_items
                ),
                "items": matched_items,
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