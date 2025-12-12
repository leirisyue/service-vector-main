from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from datetime import datetime
from typing import List, Any, Dict

from .config import settings
import json

def make_pg_url(user, password, host, port, db):
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


origin_engine: Engine = create_engine(
    make_pg_url(
        settings.ORIGIN_DB_USER,
        settings.ORIGIN_DB_PASSWORD,
        settings.ORIGIN_DB_HOST,
        settings.ORIGIN_DB_PORT,
        settings.ORIGIN_DB_NAME,
    )
)

target_engine: Engine = create_engine(
    make_pg_url(
        settings.APP_PG_USER,
        settings.APP_PG_PASSWORD,
        settings.APP_PG_HOST,
        settings.APP_PG_PORT,
        settings.APP_PG_DATABASE,
    )
)


def get_origin_tables() -> List[str]:
    """Lấy danh sách bảng từ DB PTHSP (bỏ các bảng hệ thống)."""
    sql = """
    SELECT tablename
    FROM pg_tables
    WHERE schemaname = 'public';
    """
    with origin_engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
    return [r[0] for r in rows]


def ensure_target_table(table_name: str):
    """
    Đảm bảo trong ultimate_advisor có bảng với tên table_name
    có cấu trúc: id | original_data | content_text | embedding | created_at
    """
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS public."{table_name}" (
        id BIGSERIAL PRIMARY KEY,
        original_data JSONB,
        content_text TEXT,
        embedding DOUBLE PRECISION[],
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    with target_engine.begin() as conn:
        conn.execute(text(create_sql))


def fetch_rows_from_origin(table_name: str, limit: int | None = None):
    """Lấy toàn bộ (hoặc limit) dữ liệu từ bảng nguồn."""
    sql = f'SELECT * FROM public."{table_name}"'
    if limit:
        sql += f" LIMIT {limit}"
    with origin_engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = result.fetchall()
        columns = result.keys()
    return columns, rows


def insert_vector_rows(
    table_name: str,
    rows: List[Dict[str, Any]],
):
    """Ghi batch dữ liệu đã embedding sang bảng vector."""
    if not rows:
        return

    insert_sql = f"""
    INSERT INTO public."{table_name}" (original_data, content_text, embedding, created_at)
    VALUES (:original_data, :content_text, :embedding, :created_at)
    """
    with target_engine.begin() as conn:
        conn.execute(text(insert_sql), rows)


def insert_vector_rows(
    table_name: str,
    rows: List[Dict[str, Any]],
):
    """Ghi batch dữ liệu đã embedding sang bảng vector."""
    if not rows:
        return

    # Chuyển original_data (dict) -> JSON string
    serialized_rows = []
    for r in rows:
        r = r.copy()
        if isinstance(r.get("original_data"), dict):
            r["original_data"] = json.dumps(r["original_data"], ensure_ascii=False)
        serialized_rows.append(r)

    insert_sql = f"""
    INSERT INTO public."{table_name}" (original_data, content_text, embedding, created_at)
    VALUES (:original_data, :content_text, :embedding, :created_at)
    """
    with target_engine.begin() as conn:
        conn.execute(text(insert_sql), serialized_rows)