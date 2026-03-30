from fastapi import APIRouter, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json

from app.repositories import cards as cards_repo
from app.repositories import columns as columns_repo

router = APIRouter(prefix="/api")
templates = Jinja2Templates(directory="app/templates")


def _get_api_base(request: Request) -> str:
    root = request.scope.get("root_path", "").rstrip("/")
    return f"{root}/api"


def _column_response(request, column_id):
    col = columns_repo.get_column(column_id)
    col["cards"] = cards_repo.list_cards_by_column(column_id)
    return templates.TemplateResponse(
        request=request,
        name="partials/column.html",
        context={"col": col, "api_base": _get_api_base(request)},
    )


@router.post("/cards", response_class=HTMLResponse)
async def create_card(
    request: Request,
    column_id: int = Form(...),
    title: str = Form(...),
    step: str = Form(""),
    category: str = Form(""),
    action: str = Form(""),
    expected_outcome: str = Form(""),
    finding: str = Form(""),
    url: str = Form(""),
    link2: str = Form(""),
    link3: str = Form(""),
):
    cards_repo.create_card(
        column_id=column_id,
        title=title,
        step=step,
        category=category,
        action=action,
        expected_outcome=expected_outcome,
        finding=finding,
        url=url,
        link2=link2,
        link3=link3,
    )
    return _column_response(request, column_id)


@router.post("/cards/{card_id}/update", response_class=HTMLResponse)
async def update_card(
    request: Request,
    card_id: int,
    title: str = Form(...),
    step: str = Form(""),
    category: str = Form(""),
    action: str = Form(""),
    expected_outcome: str = Form(""),
    finding: str = Form(""),
    url: str = Form(""),
    link2: str = Form(""),
    link3: str = Form(""),
):
    card = cards_repo.update_card(
        card_id,
        title=title,
        step=step,
        category=category,
        action=action,
        expected_outcome=expected_outcome,
        finding=finding,
        url=url,
        link2=link2,
        link3=link3,
    )
    if not card:
        return HTMLResponse("Card not found", status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="partials/card.html",
        context={"card": card, "api_base": _get_api_base(request)},
    )


@router.delete("/cards/{card_id}", response_class=HTMLResponse)
async def delete_card(request: Request, card_id: int):
    card = cards_repo.get_card(card_id)
    if not card:
        return HTMLResponse("Card not found", status_code=404)
    column_id = card["column_id"]
    cards_repo.delete_card(card_id)
    return _column_response(request, column_id)


@router.post("/cards/{card_id}/move", response_class=JSONResponse)
async def move_card(request: Request, card_id: int):
    body = await request.json()
    new_column_id = body.get("column_id")
    new_position = body.get("position", 0)
    if new_column_id is None:
        return JSONResponse({"error": "column_id required"}, status_code=400)
    card = cards_repo.move_card(card_id, int(new_column_id), int(new_position))
    if not card:
        return JSONResponse({"error": "Card not found"}, status_code=404)
    return JSONResponse({"ok": True, "card": card})


@router.post("/boards/{board_id}/import", response_class=JSONResponse)
async def import_cards(board_id: int, file: UploadFile = File(...)):
    try:
        content = await file.read()
        cards_data = json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JSONResponse({"error": "Invalid JSON file"}, status_code=400)

    if not isinstance(cards_data, list):
        return JSONResponse({"error": "JSON must be an array of card objects"}, status_code=400)

    created = 0
    errors = []
    for i, item in enumerate(cards_data):
        if not isinstance(item, dict):
            errors.append(f"Item {i}: not an object")
            continue
        # Normalize keys: lowercase + replace spaces with underscores
        norm = {k.lower().replace(" ", "_"): v for k, v in item.items()}
        # Handle "link_1" -> "url", "link_2" -> "link2", etc.
        if "link_1" in norm and "url" not in norm:
            norm["url"] = norm.pop("link_1")
        if "link_2" in norm and "link2" not in norm:
            norm["link2"] = norm.pop("link_2")
        if "link_3" in norm and "link3" not in norm:
            norm["link3"] = norm.pop("link_3")
        if "step" in norm:
            norm["step"] = str(norm["step"]).strip()

        if "title" not in norm:
            errors.append(f"Item {i}: missing 'title'")
            continue

        column_name = norm.get("column", "")
        col = None
        if column_name:
            col = columns_repo.get_column_by_name(board_id, column_name)
        if not col:
            cols = columns_repo.list_columns(board_id)
            col = cols[0] if cols else None
        if not col:
            errors.append(f"Item {i}: no columns found on board")
            continue

        cards_repo.create_card(
            column_id=col["id"],
            title=norm["title"],
            step=norm.get("step", ""),
            category=norm.get("category", ""),
            action=norm.get("action", norm.get("description", "")),
            expected_outcome=norm.get("expected_outcome", ""),
            finding=norm.get("finding", ""),
            url=norm.get("url", norm.get("link1", "")),
            link2=norm.get("link2", ""),
            link3=norm.get("link3", ""),
        )
        created += 1

    return JSONResponse({"created": created, "errors": errors})


@router.get("/cards/{card_id}", response_class=HTMLResponse)
async def get_card_modal(request: Request, card_id: int):
    card = cards_repo.get_card(card_id)
    if not card:
        return HTMLResponse("Card not found", status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="card_modal.html",
        context={"card": card, "api_base": _get_api_base(request)},
    )
