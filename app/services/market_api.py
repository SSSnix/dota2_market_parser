import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()


class MarketAPI:
    BASE_URL = "https://market.dota2.net/api"

    def __init__(self) -> None:
        self.api_key = os.getenv("MARKET_API_KEY")

        if not self.api_key:
            raise ValueError(
                "MARKET_API_KEY не найден в файле .env"
            )

    async def search_item(
        self,
        market_hash_name: str,
    ) -> dict[str, Any]:
        url = (
            f"{self.BASE_URL}/v2/"
            "search-item-by-hash-name"
        )

        params = {
            "key": self.api_key,
            "hash_name": market_hash_name,
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:
            response = await client.get(
                url,
                params=params,
            )

        response.raise_for_status()

        return response.json()

    async def get_item_info(
        self,
        class_id: int,
        instance_id: int,
        language: str = "en",
    ) -> dict[str, Any]:
        item_hash = f"{class_id}_{instance_id}"

        url = (
            f"{self.BASE_URL}/ItemInfo/"
            f"{item_hash}/{language}/"
        )

        params = {
            "key": self.api_key,
        }

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:
            response = await client.get(
                url,
                params=params,
            )

        response.raise_for_status()

        return response.json()

    async def get_mass_info(
        self,
        item_hashes: list[str],
        sell: int = 0,
        buy: int = 0,
        history: int = 0,
        info: int = 3,
    ) -> dict[str, Any]:
        if not item_hashes:
            return {
                "success": True,
                "results": [],
            }

        if len(item_hashes) > 100:
            raise ValueError(
                "MassInfo поддерживает максимум "
                "100 предметов"
            )

        url = (
            f"{self.BASE_URL}/MassInfo/"
            f"{sell}/{buy}/{history}/{info}/"
        )

        params = {
            "key": self.api_key,
        }

        data = {
            "list": ",".join(item_hashes),
        }

        async with httpx.AsyncClient(
            timeout=60.0
        ) as client:
            response = await client.post(
                url,
                params=params,
                data=data,
            )

        response.raise_for_status()

        return response.json()