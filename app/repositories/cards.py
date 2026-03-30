from app.db import get_db, row_to_dict, rows_to_list, utc_now


def list_cards_by_column(column_id: int) -> list[dict]:
    with get_db() as conn:
        return rows_to_list(
            conn.execute(
                "SELECT * FROM cards WHERE column_id = ? ORDER BY position",
                (column_id,),
            ).fetchall()
        )


def list_cards_by_board(board_id: int) -> list[dict]:
    with get_db() as conn:
        return rows_to_list(
            conn.execute(
                """SELECT c.* FROM cards c
                   JOIN columns_ col ON c.column_id = col.id
                   WHERE col.board_id = ?
                   ORDER BY col.position, c.position""",
                (board_id,),
            ).fetchall()
        )


def get_card(card_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
        return row_to_dict(row)


def create_card(
    column_id: int,
    title: str,
    description: str = "",
    expected_outcome: str = "",
    url: str = "",
    step: str = "",
    category: str = "",
    action: str = "",
    finding: str = "",
    link2: str = "",
    link3: str = "",
) -> dict:
    with get_db() as conn:
        max_pos = conn.execute(
            "SELECT COALESCE(MAX(position), -1) FROM cards WHERE column_id = ?",
            (column_id,),
        ).fetchone()[0]
        cur = conn.execute(
            """INSERT INTO cards
               (column_id, title, description, expected_outcome, url,
                step, category, action, finding, link2, link3, position)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (column_id, title, description, expected_outcome, url,
             step, category, action, finding, link2, link3, max_pos + 1),
        )
        return row_to_dict(
            conn.execute("SELECT * FROM cards WHERE id = ?", (cur.lastrowid,)).fetchone()
        )


def update_card(card_id: int, **fields) -> dict | None:
    allowed = {
        "title", "description", "expected_outcome", "url",
        "step", "category", "action", "finding", "link2", "link3",
    }
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        return get_card(card_id)
    updates["updated_at"] = utc_now()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [card_id]
    with get_db() as conn:
        conn.execute(f"UPDATE cards SET {set_clause} WHERE id = ?", values)
        return row_to_dict(
            conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
        )


def delete_card(card_id: int) -> bool:
    with get_db() as conn:
        cur = conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        return cur.rowcount > 0


def move_card(card_id: int, new_column_id: int, new_position: int) -> dict | None:
    with get_db() as conn:
        card = row_to_dict(
            conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
        )
        if not card:
            return None

        old_column_id = card["column_id"]
        old_position = card["position"]

        conn.execute(
            "UPDATE cards SET position = position + 1 WHERE column_id = ? AND position >= ?",
            (new_column_id, new_position),
        )

        if old_column_id == new_column_id and old_position < new_position:
            conn.execute(
                "UPDATE cards SET position = position - 1 WHERE column_id = ? AND position > ? AND position <= ?",
                (old_column_id, old_position, new_position),
            )
        elif old_column_id != new_column_id:
            conn.execute(
                "UPDATE cards SET position = position - 1 WHERE column_id = ? AND position > ?",
                (old_column_id, old_position),
            )

        conn.execute(
            "UPDATE cards SET column_id = ?, position = ?, updated_at = ? WHERE id = ?",
            (new_column_id, new_position, utc_now(), card_id),
        )

        return row_to_dict(
            conn.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
        )
