import asyncio
import os
from typing import Any
from urllib.parse import quote

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

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,
                read=60.0,
                write=60.0,
                pool=10.0,
            ),
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def search_item(
        self,
        market_hash_name: str,
    ) -> dict[str, Any]:
        url = (
            f"{self.BASE_URL}/SearchItemByName/"
            f"{quote(market_hash_name, safe='')}/"
        )

        params = {
            "key": self.api_key,
        }

        response = await self.client.get(
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
        item_hash = (
            f"{class_id}_{instance_id}"
        )

        url = (
            f"{self.BASE_URL}/ItemInfo/"
            f"{item_hash}/{language}/"
        )

        params = {
            "key": self.api_key,
        }

        response = await self.client.get(
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

        for attempt in range(3):
            try:
                response = await self.client.post(
                    url,
                    params=params,
                    data=data,
                )

                response.raise_for_status()

                return response.json()

            except httpx.HTTPStatusError as error:
                status_code = (
                    error.response.status_code
                )

                if (
                    status_code != 502
                    or attempt == 2
                ):
                    raise

                await asyncio.sleep(2)

        raise RuntimeError(
            "Не удалось получить данные MassInfo"
        )