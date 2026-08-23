from typing import Any
from urllib.parse import quote

from app.services.description_parser import (
    description_contains,
    extract_description_text,
)
from app.services.market_api import MarketAPI


MASS_INFO_BATCH_SIZE = 100


QUALITIES = {
    "normal": "",
    "exalted": "Exalted",
    "inscribed": "Inscribed",
    "autographed": "Autographed",
    "heroic": "Heroic",
    "corrupted": "Corrupted",
}


def chunks(
    items: list[str],
    size: int,
) -> list[list[str]]:
    return [
        items[index:index + size]
        for index in range(0, len(items), size)
    ]


class SearchService:
    def __init__(self) -> None:
        self.market_api = MarketAPI()

    async def search(
        self,
        item_name: str,
        description_query: str,
        qualities: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        selected_qualities = self._normalize_qualities(
            qualities
        )

        items = await self._search_items(
            item_name,
            selected_qualities,
        )

        if not items:
            return []

        items_by_hash = {
            (
                str(item["i_classid"]),
                str(item["i_instanceid"]),
            ): item
            for item in items
        }

        item_hashes = [
            (
                f"{item['i_classid']}_"
                f"{item['i_instanceid']}"
            )
            for item in items
        ]

        results = await self._get_mass_info(
            item_hashes
        )

        return self._filter_results(
            results=results,
            items_by_hash=items_by_hash,
            item_name=item_name,
            description_query=description_query,
        )

    @staticmethod
    def _normalize_qualities(
        qualities: list[str] | None,
    ) -> list[str]:
        if not qualities:
            return list(QUALITIES)

        if "all" in qualities:
            return list(QUALITIES)

        valid_qualities = [
            quality
            for quality in qualities
            if quality in QUALITIES
        ]

        if not valid_qualities:
            return ["normal"]

        return valid_qualities

    async def _search_items(
        self,
        item_name: str,
        qualities: list[str],
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []

        for quality in qualities:
            prefix = QUALITIES[quality]

            if prefix:
                search_name = (
                    f"{prefix} {item_name}"
                )
            else:
                search_name = item_name

            search_result = (
                await self.market_api.search_item(
                    search_name
                )
            )

            items.extend(
                search_result.get("list", [])
            )

        return self._unique_items(items)

    @staticmethod
    def _unique_items(
        items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        unique_items = []
        seen: set[tuple[str, str]] = set()

        for item in items:
            item_hash = (
                str(item["i_classid"]),
                str(item["i_instanceid"]),
            )

            if item_hash in seen:
                continue

            seen.add(item_hash)
            unique_items.append(item)

        return unique_items

    async def _get_mass_info(
        self,
        item_hashes: list[str],
    ) -> list[dict[str, Any]]:
        batches = chunks(
            item_hashes,
            MASS_INFO_BATCH_SIZE,
        )

        results: list[dict[str, Any]] = []

        for batch in batches:
            mass_result = (
                await self.market_api.get_mass_info(
                    item_hashes=batch,
                    sell=0,
                    buy=0,
                    history=0,
                    info=3,
                )
            )

            results.extend(
                mass_result.get("results", [])
            )

        return results

    @staticmethod
    def _filter_results(
        results: list[dict[str, Any]],
        items_by_hash: dict[
            tuple[str, str],
            dict[str, Any],
        ],
        item_name: str,
        description_query: str,
    ) -> list[dict[str, Any]]:
        filtered_results = []

        for item_data in results:
            info = item_data.get("info") or {}
            description = info.get("description")

            if not description_contains(
                description,
                description_query,
            ):
                continue

            class_id = str(
                item_data["classid"]
            )
            instance_id = str(
                item_data["instanceid"]
            )

            market_item = items_by_hash.get(
                (class_id, instance_id),
                {},
            )

            market_name = info.get(
                "market_hash_name",
                market_item.get(
                    "market_hash_name",
                    item_name,
                ),
            )

            price = market_item.get("price")
            offers = market_item.get("offers")

            market_url = (
                "https://market.dota2.net/item/"
                f"{class_id}-{instance_id}-"
                f"{quote(market_name, safe='')}/"
            )

            price_rub = None

            if price is not None:
                price_rub = int(price) / 100

            filtered_results.append(
                {
                    "name": market_name,
                    "class_id": class_id,
                    "instance_id": instance_id,
                    "price": price,
                    "price_rub": price_rub,
                    "offers": offers,
                    "description": description,
                    "description_text": (
                        extract_description_text(
                            description
                        )
                    ),
                    "url": market_url,
                    "image": info.get("image"),
                }
            )

        filtered_results.sort(
            key=lambda item: (
                item["price"]
                if item["price"] is not None
                else float("inf")
            )
        )

        return filtered_results