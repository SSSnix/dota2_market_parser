from typing import Any
from urllib.parse import quote

from app.services.description_parser import (
    description_contains,
    extract_description_text,
)
from app.services.market_api import MarketAPI


class SearchService:
    def __init__(self) -> None:
        self.market_api = MarketAPI()

    async def search(
        self,
        item_name: str,
        description_query: str,
    ) -> list[dict[str, Any]]:
        search_result = await self.market_api.search_item(
            item_name,
        )

        items = search_result.get("data", [])

        if not items:
            return []

        items_by_hash = {
            (
                str(item["class"]),
                str(item["instance"]),
            ): item
            for item in items
        }

        item_hashes = [
            f"{item['class']}_{item['instance']}"
            for item in items
        ]

        mass_result = await self.market_api.get_mass_info(
            item_hashes=item_hashes,
            sell=0,
            buy=0,
            history=0,
            info=3,
        )

        results = []

        for item_data in mass_result.get(
            "results",
            [],
        ):
            info = item_data.get("info") or {}
            description = info.get("description")

            if not description_contains(
                description,
                description_query,
            ):
                continue

            class_id = str(item_data["classid"])
            instance_id = str(item_data["instanceid"])

            market_item = items_by_hash.get(
                (class_id, instance_id),
                {},
            )

            market_name = info.get(
                "market_hash_name",
                item_name,
            )

            price = market_item.get("price")
            count = market_item.get("count")

            market_url = (
                "https://market.dota2.net/item/"
                f"{class_id}-{instance_id}-"
                f"{quote(market_name, safe='')}/"
            )

            price_rub = None

            if price is not None:
                price_rub = int(price) / 100

            results.append(
                {
                    "name": market_name,
                    "class_id": class_id,
                    "instance_id": instance_id,
                    "price": price,
                    "price_rub": price_rub,
                    "count": count,
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

        results.sort(
            key=lambda item: (
                item["price"]
                if item["price"] is not None
                else float("inf")
            )
        )

        return results