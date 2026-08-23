import logging
import re
from typing import Any, AsyncGenerator
from urllib.parse import quote

from app.services.description_parser import (
    description_contains,
    extract_description_text,
)
from app.services.market_api import MarketAPI


logger = logging.getLogger(__name__)


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


# =========================================================
# РУССКИЕ АЛИАСЫ
# =========================================================

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
    "Legacy": [
        "Legacy",
    ],
}


MASS_INFO_BATCH_SIZE = 100


class SearchService:
    def __init__(self) -> None:
        self.market_api = MarketAPI()

        self._gem_aliases = (
            self._build_gem_aliases()
        )

    @staticmethod
    def _normalize_gem_text(
        value: str,
    ) -> str:
        """Normalize gem name for comparison."""
        value = value.strip()

        value = value.replace(
            "’",
            "'",
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.casefold()

    @classmethod
    def _build_gem_aliases(
        cls,
    ) -> list[tuple[str, str]]:
        """
        Build aliases sorted from longest to shortest.

        This is important for names such as:

        Blue
        Champion's Blue

        Champion's Blue must be checked first.
        """
        aliases: list[
            tuple[str, str]
        ] = []

        for canonical_name in PRISMATIC_GEMS:
            values = PRISMATIC_GEM_ALIASES.get(
                canonical_name,
                [canonical_name],
            )

            for alias in values:
                aliases.append(
                    (
                        cls._normalize_gem_text(
                            alias
                        ),
                        canonical_name,
                    )
                )

        aliases.sort(
            key=lambda item: len(item[0]),
            reverse=True,
        )

        return aliases

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

    def _find_known_gem(
        self,
        candidate: str,
    ) -> str | None:
        """
        Find canonical gem name.

        Longest aliases are checked first so that
        Champion's Blue cannot become Blue.
        """
        normalized = self._normalize_gem_text(
            candidate
        )

        for alias, canonical_name in (
            self._gem_aliases
        ):
            if normalized == alias:
                return canonical_name

        return None

    @staticmethod
    def _clean_unknown_gem(
        candidate: str,
    ) -> str:
        """Clean a newly discovered gem name."""
        candidate = candidate.strip()

        candidate = candidate.strip(
            " \t\r\n:|,-–—"
        )

        candidate = re.sub(
            r"\s+",
            " ",
            candidate,
        )

        return candidate

    def _find_known_gem(
        self,
        candidate: str,
    ) -> str | None:
        """
        Find canonical gem name.

        Longest aliases are checked first so that
        Champion's Blue cannot become Blue.
        """
        normalized = self._normalize_gem_text(
            candidate
        )

        for alias, canonical_name in (
            self._gem_aliases
        ):
            if normalized == alias:
                return canonical_name

        return None

    @staticmethod
    def _clean_unknown_gem(
        candidate: str,
    ) -> str:
        """Clean a newly discovered gem name."""
        candidate = candidate.strip()

        candidate = candidate.strip(
            " \t\r\n:|,-–—"
        )

        candidate = re.sub(
            r"\s+",
            " ",
            candidate,
        )

        return candidate

    def _extract_unknown_from_marker(
        self,
        text: str,
        marker_match: re.Match[str],
    ) -> str | None:
        """
        Extract the gem name from a Legacy description.

        The gem is ALWAYS the text between:

            (Нельзя удалить)
        and
            Призматический самоцвет

        or their English equivalents:

            ( Not Deletable )
        and
            Prismatic Gem

        Everything after the prismatic gem marker
        is ignored completely.

        Example:

            (Нельзя удалить)Reflection's Shade
            Призматический самоцветПустое гнездоОбщий

        returns:

            Reflection's Shade

        Another example:

            (Нельзя удалить)Пустое гнездо
            Призматический самоцветПустое гнездоОбщий

        returns:

            Пустое гнездо
        """

        before = text[
            :marker_match.start()
        ]

        # -------------------------------------------------
        # Ищем начало Legacy-блока.
        #
        # Варианты:
        #
        # (Нельзя удалить)
        # ( Нельзя удалить )
        # (Not Deletable)
        # ( Not Deletable )
        # -------------------------------------------------

        legacy_pattern = re.compile(
            r"\(\s*"
            r"(?:"
            r"Нельзя\s+удалить"
            r"|"
            r"Not\s+Deletable"
            r")"
            r"\s*\)",
            re.IGNORECASE,
        )

        legacy_matches = list(
            legacy_pattern.finditer(before)
        )

        if legacy_matches:
            # Берём последний маркер.
            #
            # Это важно, если в description есть
            # несколько технических блоков.
            legacy_marker = legacy_matches[-1]

            candidate = before[
                legacy_marker.end():
            ]

            return self._clean_unknown_gem(
                candidate
            )

        # -------------------------------------------------
        # Если Legacy-маркера нет, используем
        # обычный вариант: всё непосредственно
        # перед "Призматический самоцвет".
        # -------------------------------------------------

        parts = re.split(
            r"[\r\n]+",
            before,
        )

        candidate = parts[-1].strip()

        # Убираем возможные технические разделители.
        candidate = re.split(
            r"[|:•]",
            candidate,
        )[-1].strip()

        candidate = candidate.strip(
            " \t-–—"
        )

        if not candidate:
            return None

        candidate = re.sub(
            r"<[^>]+>",
            "",
            candidate,
        ).strip()

        return self._clean_unknown_gem(
            candidate
        )

    def extract_gems(
        self,
        description: Any,
    ) -> list[str]:
        """
        Extract one prismatic gem from an item description.

        For Legacy items the gem is defined strictly as
        the text between:

            (Нельзя удалить)
        and
            Призматический самоцвет

        or:

            ( Not Deletable )
        and
            Prismatic Gem.

        Everything after the second marker is ignored.

        This intentionally allows "Пустое гнездо" to be
        returned as a gem because it is a real buggy item
        that must remain visible in the filters.
        """

        if not description:
            return []

        text = extract_description_text(
            description
        )

        if not text:
            return []

        # -------------------------------------------------
        # Маркер конца гемового блока.
        # -------------------------------------------------

        marker_pattern = re.compile(
            r"(?:"
            r"Призматический\s+самоцвет"
            r"|"
            r"Prismatic\s+Gemstone"
            r"|"
            r"Prismatic\s+Gem"
            r")",
            re.IGNORECASE,
        )

        marker_match = marker_pattern.search(
            text
        )

        if not marker_match:
            return []

        # -------------------------------------------------
        # Получаем текст гема.
        #
        # Для Legacy:
        #
        # (Нельзя удалить)Reflection's Shade
        #                           ↑
        #                      берём это
        #
        # Для обычного:
        #
        # Reflection's ShadeПризматический самоцвет
        # ↑
        # берём это
        # -------------------------------------------------

        candidate = (
            self._extract_unknown_from_marker(
                text,
                marker_match,
            )
        )

        if not candidate:
            return []

        # -------------------------------------------------
        # Защита от HTML/служебного мусора.
        # -------------------------------------------------

        candidate = re.sub(
            r"<[^>]+>",
            "",
            candidate,
        ).strip()

        candidate = self._clean_unknown_gem(
            candidate
        )

        if not candidate:
            return []

        if len(candidate) > 100:
            return []

        # -------------------------------------------------
        # Сначала проверяем нашу классификацию.
        #
        # Например:
        #
        # Champion's Blue
        # -> Champion's Blue
        #
        # Чемпионский синий
        # -> Champion's Blue
        #
        # Blue
        # -> Blue
        #
        # Благодаря сортировке aliases по длине
        # Champion's Blue не превратится в Blue.
        # -------------------------------------------------

        known_gem = self._find_known_gem(
            candidate
        )

        if known_gem:
            return [known_gem]

        # -------------------------------------------------
        # Неизвестный гем.
        #
        # Возвращаем его как есть и одновременно
        # пишем в лог.
        # -------------------------------------------------

        logger.warning(
            "Найден предмет с неизвестным "
            "призматическим гемом: %s",
            candidate,
        )

        return [candidate]

    def extract_gems(
            self,
            description: Any,
    ) -> list[str]:
        """
        Extract one prismatic gem from an item description.

        Known gems are converted to canonical English names.

        Unknown gems are returned using their actual name
        and logged.

        Legacy descriptions are supported:

            ( Not Deletable ) Reflection's ShadePrismatic Gem

        Everything after the prismatic-gem marker is ignored.
        """

        if not description:
            return []

        text = extract_description_text(
            description
        )

        if not text:
            return []


        marker_pattern = re.compile(
            r"(?:"
            r"Призматический\s+самоцвет"
            r"|"
            r"Prismatic\s+Gemstone"
            r"|"
            r"Prismatic\s+Gem"
            r")",
            re.IGNORECASE,
        )

        marker_match = marker_pattern.search(
            text
        )

        if not marker_match:
            return []

        candidate = (
            self._extract_unknown_from_marker(
                text,
                marker_match,
            )
        )

        if not candidate:
            return []


        if re.match(
                r"^Empty\s+Socket"
                r"(?:\s+Prismatic)?$",
                candidate,
                re.IGNORECASE,
        ):
            return []

        candidate = re.sub(
            r"<[^>]+>",
            "",
            candidate,
        ).strip()

        candidate = self._clean_unknown_gem(
            candidate
        )

        if not candidate:
            return []

        if len(candidate) > 100:
            return []

        known_gem = self._find_known_gem(
            candidate
        )

        if known_gem:
            return [known_gem]

        # -------------------------------------------------
        # Новый неизвестный гем.
        # -------------------------------------------------

        logger.warning(
            "Найден предмет с неизвестным "
            "призматическим гемом: %s",
            candidate,
        )

        return [candidate]

    def extract_gems(
        self,
        description: Any,
    ) -> list[str]:
        """
        Extract exactly one prismatic gem from
        an item description.

        Known gems are converted to canonical English names.

        If a gem is not present in our classification,
        its actual name is returned as-is and logged.
        """
        if not description:
            return []

        text = extract_description_text(
            description
        )

        if not text:
            return []

        # -------------------------------------------------
        # Ищем именно маркер призматического самоцвета.
        # -------------------------------------------------

        marker_pattern = re.compile(
            r"(?:"
            r"Призматический\s+самоцвет"
            r"|"
            r"Prismatic\s+Gemstone"
            r"|"
            r"Prismatic\s+Gem"
            r")",
            re.IGNORECASE,
        )

        marker_match = marker_pattern.search(
            text
        )

        if not marker_match:
            return []

        # -------------------------------------------------
        # Сначала проверяем известные гемы.
        #
        # Ищем их именно непосредственно перед
        # маркером, причём самые длинные названия
        # проверяются первыми.
        # -------------------------------------------------

        before = text[
            :marker_match.start()
        ]

        before_normalized = (
            self._normalize_gem_text(
                before
            )
        )

        for alias, canonical_name in (
            self._gem_aliases
        ):
            pattern = (
                r"(?:^|[\s|:•,\-–—])"
                + re.escape(alias)
                + r"(?:[\s|:•,\-–—])*$"
            )

            if re.search(
                pattern,
                before_normalized,
            ):
                return [canonical_name]

        # -------------------------------------------------
        # Если известного гема нет —
        # извлекаем неизвестный.
        # -------------------------------------------------

        unknown_gem = (
            self._extract_unknown_from_marker(
                text,
                marker_match,
            )
        )

        if not unknown_gem:
            return []

        # Не добавляем мусор.
        if (
            len(unknown_gem) > 100
            or len(unknown_gem) < 1
        ):
            return []

        # Если по какой-то причине после
        # извлечения название всё-таки совпало
        # с известным гемом.
        known_gem = self._find_known_gem(
            unknown_gem
        )

        if known_gem:
            return [known_gem]

        logger.warning(
            "Найден предмет с неизвестным "
            "призматическим гемом: %s",
            unknown_gem,
        )

        return [unknown_gem]

    @staticmethod
    def build_gem_statistics(
        items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Build gem counters from already loaded items.

        One item contains only one prismatic gem,
        therefore each item is counted only once.
        """
        counters: dict[str, int] = {}

        for item in items:
            gems = item.get("gems", [])

            if not gems:
                continue

            gem = gems[0]

            counters[gem] = (
                counters.get(gem, 0) + 1
            )

        result = [
            {
                "name": name,
                "count": count,
            }
            for name, count in counters.items()
        ]

        result.sort(
            key=lambda item: (
                -item["count"],
                item["name"].casefold(),
            )
        )

        return result

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

                gems = self.extract_gems(
                    description
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