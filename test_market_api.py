import asyncio

from app.services.description_parser import description_contains
from app.services.market_api import MarketAPI


ITEM_NAME = "Fractal Horns of Inner Abysm"
DESCRIPTION_QUERY = "Tnim S'nnam"


async def main() -> None:
    api = MarketAPI()

    search_result = await api.search_item(ITEM_NAME)
    items = search_result.get("data", [])

    print(f"Найдено вариантов: {len(items)}")

    item_hashes = [
        f"{item['class']}_{item['instance']}"
        for item in items
    ]

    mass_result = await api.get_mass_info(
        item_hashes=item_hashes,
        sell=0,
        buy=0,
        history=0,
        info=3,
    )

    results = mass_result.get("results", [])

    print(f"Получено описаний: {len(results)}")
    print()
    print(f'Поиск описания: "{DESCRIPTION_QUERY}"')
    print()

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

        class_id = result.get("classid")
        instance_id = result.get("instanceid")

        original_item = next(
            (
                item
                for item in items
                if str(item["class"]) == str(class_id)
                and str(item["instance"]) == str(instance_id)
            ),
            None,
        )

        price = (
            original_item.get("price")
            if original_item
            else None
        )

        count = (
            original_item.get("count")
            if original_item
            else None
        )

        print(f"НАЙДЕНО #{found}")
        print(f"  Class: {class_id}")
        print(f"  Instance: {instance_id}")
        print(f"  Цена: {price}")
        print(f"  Количество: {count}")
        print()

    print(f"Всего найдено: {found}")


if __name__ == "__main__":
    asyncio.run(main())