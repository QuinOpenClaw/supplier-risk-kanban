from app.db import get_db, row_to_dict, rows_to_list


def get_board(board_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM boards WHERE id = ?", (board_id,)).fetchone()
        return row_to_dict(row)


def list_boards() -> list[dict]:
    with get_db() as conn:
        return rows_to_list(conn.execute("SELECT * FROM boards ORDER BY id").fetchall())
