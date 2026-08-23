import json
from typing import Any, AsyncGenerator

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import (
    HTMLResponse,
    StreamingResponse,
)
from fastapi.templating import Jinja2Templates

from app.services.search_service import SearchService


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates",
)

search_service = SearchService()


def make_event(
    event: str,
    data: dict[str, Any],
) -> str:
    """Create one NDJSON event."""
    return (
        json.dumps(
            {
                "event": event,
                "data": data,
            },
            ensure_ascii=False,
        )
        + "\n"
    )


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@router.post("/api/search")
async def search(
    item_name: str = Form(...),
    description: str = Form(""),
    qualities: str = Form("all"),
    gem_mode: bool = Form(False),
):
    item_name = item_name.strip()
    description = description.strip()

    if not item_name:
        raise HTTPException(
            status_code=400,
            detail="Введите название предмета",
        )

    # В обычном режиме описание обязательно.
    # В режиме "Все гемы" оно не требуется.
    if not gem_mode and not description:
        raise HTTPException(
            status_code=400,
            detail="Введите описание для поиска",
        )

    selected_qualities = [
        quality.strip()
        for quality in qualities.split(",")
        if quality.strip()
    ]

    if not selected_qualities:
        selected_qualities = ["all"]

    async def generate() -> AsyncGenerator[str, None]:
        try:
            yield make_event(
                "progress",
                {
                    "percent": 0,
                    "stage": "Подготовка",
                    "message": (
                        "Подготавливаем поиск..."
                    ),
                    "gem_mode": gem_mode,
                },
            )

            async for update in search_service.search(
                item_name=item_name,
                description_query=description,
                qualities=selected_qualities,
                gem_mode=gem_mode,
            ):
                update_type = update.get("type")

                if update_type == "progress":
                    yield make_event(
                        "progress",
                        update["data"],
                    )

                elif update_type == "result":
                    yield make_event(
                        "result",
                        update["data"],
                    )

        except Exception as error:
            yield make_event(
                "error",
                {
                    "message": str(error),
                },
            )

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache, no-store",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )