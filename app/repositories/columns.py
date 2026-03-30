from app.db import get_db, row_to_dict, rows_to_list


def list_columns(board_id: int) -> list[dict]:
    with get_db() as conn:
        return rows_to_list(
            conn.execute(
                "SELECT * FROM columns_ WHERE board_id = ? ORDER BY position",
                (board_id,),
            ).fetchall()
        )


def get_column(column_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM columns_ WHERE id = ?", (column_id,)).fetchone()
        return row_to_dict(row)


def get_column_by_name(board_id: int, name: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM columns_ WHERE board_id = ? AND LOWER(name) = LOWER(?)",
            (board_id, name),
        ).fetchone()
        return row_to_dict(row)
