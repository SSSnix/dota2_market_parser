import asyncio

from app.services.description_parser import description_contains
from app.services.market_api import MarketAPI


ITEM_NAME = "Fractal Horns of Inner Abysm"
DESCRIPTION_QUERY = "Tnim S'nnam"

MASS_INFO_BATCH_SIZE = 100


def chunks(
    items: list[str],
    size: int,
) -> list[list[str]]:
    return [
        items[index:index + size]
        for index in range(0, len(items), size)
    ]


async def main() -> None:
    api = MarketAPI()

    search_result = await api.search_item(ITEM_NAME)
    items = search_result.get("list", [])

    print(f"Найдено вариантов: {len(items)}")

    item_hashes = [
        f"{item['i_classid']}_{item['i_instanceid']}"
        for item in items
    ]

    batches = chunks(
        item_hashes,
        MASS_INFO_BATCH_SIZE,
    )

    print(f"Пачек MassInfo: {len(batches)}")
    print()

    results = []

    for index, batch in enumerate(batches, start=1):
        print(
            f"MassInfo: пачка {index}/{len(batches)} "
            f"({len(batch)} предметов)"
        )

        mass_result = await api.get_mass_info(
            item_hashes=batch,
            sell=0,
            buy=0,
            history=0,
            info=3,
        )

        batch_results = mass_result.get(
            "results",
            [],
        )

        print(
            f"  Получено описаний: "
            f"{len(batch_results)}"
        )

        results.extend(batch_results)

    print()
    print(f"Всего получено описаний: {len(results)}")
    print()
    print(f'Поиск описания: "{DESCRIPTION_QUERY}"')
    print()

    items_by_hash = {
        (
            str(item["i_classid"]),
            str(item["i_instanceid"]),
        ): item
        for item in items
    }

    found = 0

    for result in results:
        info = result.get("info") or {}
        description = info.get("description")

        if not description_contains(
            description,
            DESCRIPTION_QUERY,
        ):
            continue

        found += 1

        class_id = str(result["classid"])
        instance_id = str(result["instanceid"])

        original_item = items_by_hash.get(
            (class_id, instance_id),
            {},
        )

        price = original_item.get("price")
        offers = original_item.get("offers")

        print(f"НАЙДЕНО #{found}")
        print(f"  Class: {class_id}")
        print(f"  Instance: {instance_id}")
        print(f"  Цена: {price}")
        print(f"  Offers: {offers}")
        print()

    print(f"Всего найдено: {found}")


if __name__ == "__main__":
    asyncio.run(main())