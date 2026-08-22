from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.search_service import SearchService


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates",
)

search_service = SearchService()


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
    item_name: str,
    description: str,
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

    results = await search_service.search(
        item_name=item_name,
        description_query=description,
    )

    return {
        "count": len(results),
        "items": results,
    }