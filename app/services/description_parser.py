from typing import Any

from bs4 import BeautifulSoup


def extract_text_from_html(html: str) -> str:
    """Convert HTML into readable plain text."""
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    return soup.get_text(
        " ",
        strip=True,
    )


def extract_description_text(
    description: list[dict[str, Any]] | None,
) -> str:
    """Extract all readable text from item description."""
    if not description:
        return ""

    parts: list[str] = []

    for entry in description:
        value = entry.get("value", "")

        if not value:
            continue

        text = extract_text_from_html(value)

        if text:
            parts.append(text)

    return " ".join(parts)


def description_contains(
    description: list[dict[str, Any]] | None,
    query: str,
) -> bool:
    """Check whether description contains the search text."""
    if not query.strip():
        return False

    description_text = extract_description_text(
        description
    )

    return query.casefold() in description_text.casefold()