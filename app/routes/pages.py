from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.repositories import boards as boards_repo
from app.repositories import columns as columns_repo
from app.repositories import cards as cards_repo

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _get_api_base(request: Request) -> str:
    """Return the correct API base URL, respecting root_path/proxy prefix."""
    root = request.scope.get("root_path", "").rstrip("/")
    return f"{root}/api"


@router.get("/", response_class=HTMLResponse, name="board_view")
async def board_view(request: Request, board_id: int = 1):
    board = boards_repo.get_board(board_id)
    if not board:
        return HTMLResponse("Board not found", status_code=404)

    cols = columns_repo.list_columns(board_id)
    for col in cols:
        col["cards"] = cards_repo.list_cards_by_column(col["id"])

    return templates.TemplateResponse(
        request=request,
        name="board.html",
        context={
            "board": board,
            "columns": cols,
            "api_base": _get_api_base(request),
        },
    )
