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

    async def search(
        self,
        item_name: str,
        description_query: str,
        qualities: list[str],
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
                    "processed": (
                        min(
                            batch_number
                            * MASS_INFO_BATCH_SIZE,
                            len(unique_items),
                        )
                    ),
                    "total_items": len(unique_items),
                    "descriptions": len(
                        all_mass_results
                    ),
                },
            }

        # ==================================================
        # ЭТАП 3. ПОИСК ПО ОПИСАНИЮ
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
                "stage": "Проверка описаний",
                "message": (
                    f"Проверяем {total_results} "
                    f"описаний..."
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

            if description_contains(
                description,
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
                        "description": description,
                        "description_text": (
                            extract_description_text(
                                description
                            )
                        ),
                        "url": market_url,
                        "image": info.get(
                            "image"
                        ),
                    }
                )

            # Обновляем прогресс не на каждом
            # элементе, чтобы не создавать
            # тысячи событий.
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
                            "Проверка описаний"
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
        # СОРТИРОВКА
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