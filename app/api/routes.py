import asyncio
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
    payload = {
        "event": event,
        "data": data,
    }

    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
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
    description: str = Form(...),
    qualities: str = Form("all"),
):
    item_name = item_name.strip()
    description = description.strip()

    if not item_name:
        raise HTTPException(
            status_code=400,
            detail="Введите название предмета",
        )

    if not description:
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

    async def generate() -> AsyncGenerator[
        str,
        None,
    ]:
        try:
            # Первое событие отправляем сразу.
            yield make_event(
                "progress",
                {
                    "percent": 0,
                    "stage": "Подготовка",
                    "message": (
                        "Подготавливаем поиск..."
                    ),
                },
            )

            await asyncio.sleep(0)

            async for update in (
                search_service.search(
                    item_name=item_name,
                    description_query=description,
                    qualities=selected_qualities,
                )
            ):
                update_type = update.get("type")

                if update_type == "progress":
                    yield make_event(
                        "progress",
                        update.get(
                            "data",
                            {},
                        ),
                    )

                    # Очень важно:
                    # отдаём управление event loop
                    # сразу после progress-события.
                    await asyncio.sleep(0)

                elif update_type == "result":
                    yield make_event(
                        "result",
                        update.get(
                            "data",
                            {},
                        ),
                    )

                    await asyncio.sleep(0)

        except asyncio.CancelledError:
            raise

        except Exception as error:
            yield make_event(
                "error",
                {
                    "message": str(error),
                },
            )

            await asyncio.sleep(0)

    return StreamingResponse(
        generate(),
        media_type=(
            "application/x-ndjson; "
            "charset=utf-8"
        ),
        headers={
            "Cache-Control": (
                "no-cache, no-store, "
                "must-revalidate"
            ),
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Accel-Buffering": "no",
        },
    )