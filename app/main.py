from datetime import datetime
from typing import Dict, Any

from .db import (
    get_origin_tables,
    ensure_target_table,
    fetch_rows_from_origin,
    insert_vector_rows,
)
from .embedding_service import embedding_service


def row_to_text(columns, row) -> str:
    """
    Chuyển 1 row (nhiều cột) thành chuỗi content_text để embed.
    Tùy chỉnh theo logic business: ở đây ghép text của tất cả cột.
    """
    parts = []
    for col, val in zip(columns, row):
        if val is None:
            continue
        # chỉ ghép các kiểu text/có thể cast
        parts.append(f"{col}: {val}")
    return "\n".join(parts)


def row_to_original_data(columns, row) -> Dict[str, Any]:
    """Lưu toàn bộ row gốc dưới dạng JSON."""
    return {col: row[i] for i, col in enumerate(columns)}


def process_table(table_name: str, limit: int | None = None, batch_size: int = 50):
    print(f"=== Processing table: {table_name} ===")
    ensure_target_table(table_name)
    columns, rows = fetch_rows_from_origin(table_name, limit=limit)
    print(f"Fetched {len(rows)} rows from origin table {table_name}")

    batch = []
    for idx, row in enumerate(rows, start=1):
        content_text = row_to_text(columns, row)
        if not content_text.strip():
            continue

        embedding = embedding_service.embed(content_text)
        original_data = row_to_original_data(columns, row)

        batch.append(
            {
                "original_data": original_data,
                "content_text": content_text,
                "embedding": embedding,
                "created_at": datetime.utcnow(),
            }
        )

        if len(batch) >= batch_size:
            insert_vector_rows(table_name, batch)
            print(f"[{table_name}] inserted batch of {len(batch)} rows (up to row {idx})")
            batch.clear()

    if batch:
        insert_vector_rows(table_name, batch)
        print(f"[{table_name}] inserted final batch of {len(batch)} rows")

    print(f"Done table {table_name}")


def main():
    tables = get_origin_tables()
    print("Origin tables:", tables)

    # nếu muốn chỉ chạy 1 vài bảng, bạn có thể filter ở đây
    for tbl in tables:
        process_table(tbl, limit=None)  # hoặc limit=100 để test trước


if __name__ == "__main__":
    main()